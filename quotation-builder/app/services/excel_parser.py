import io
import sqlite3
import openpyxl
from thefuzz import process as fuzz_process
from ..db import fetchone, fetchall

FUZZY_THRESHOLD = 80


def parse_order_xlsx(xlsx_bytes: bytes, db: sqlite3.Connection) -> dict:
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {"valid": [], "flagged": [], "error": "Empty file"}

    headers = [str(h).strip().lower() if h else "" for h in rows[0]]
    col = {h: i for i, h in enumerate(headers)}

    products = fetchall(db, "SELECT id, name FROM products WHERE is_active=1")
    product_names = {p["name"]: p["id"] for p in products}

    valid = []
    flagged = []

    for row_num, row in enumerate(rows[1:], start=2):
        def get(col_name):
            idx = col.get(col_name)
            return row[idx] if idx is not None and idx < len(row) else None

        raw_product = str(get("product") or "").strip()
        raw_quality = str(get("quality") or "").strip()
        raw_pkg = str(get("package_size") or "").strip()
        raw_qty = get("quantity_kg")

        if not raw_qty:
            flagged.append({
                "row": row_num, "raw_product": raw_product,
                "reason": "missing_quantity", "input": dict(zip(headers, row)),
            })
            continue

        try:
            quantity_kg = float(raw_qty)
        except (ValueError, TypeError):
            flagged.append({
                "row": row_num, "raw_product": raw_product,
                "reason": "invalid_quantity", "input": dict(zip(headers, row)),
            })
            continue

        if raw_product in product_names:
            product_id = product_names[raw_product]
            confidence = 100
        else:
            match = fuzz_process.extractOne(raw_product, list(product_names.keys()))
            if match and match[1] >= FUZZY_THRESHOLD:
                product_id = product_names[match[0]]
                confidence = match[1]
            else:
                flagged.append({
                    "row": row_num, "raw_product": raw_product,
                    "reason": "low_confidence",
                    "best_match": match[0] if match else None,
                    "confidence": match[1] if match else 0,
                    "input": dict(zip(headers, row)),
                })
                continue

        quality = fetchone(
            db,
            "SELECT id FROM qualities WHERE product_id=? AND name=?",
            (product_id, raw_quality),
        )
        pkg = fetchone(db, "SELECT id FROM package_sizes WHERE display_name=?", (raw_pkg,))

        valid.append({
            "row": row_num,
            "product_id": product_id,
            "quality_id": quality["id"] if quality else None,
            "package_size_id": pkg["id"] if pkg else None,
            "quantity_kg": quantity_kg,
            "confidence": confidence,
            "raw_product": raw_product,
        })

    return {"valid": valid, "flagged": flagged}
