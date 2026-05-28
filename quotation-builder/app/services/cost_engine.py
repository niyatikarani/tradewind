import math
import sqlite3
from ..db import fetchone, fetchall


def calculate_line_costs(
    product_id: int,
    quality_id: int,
    package_size_id: int,
    quantity_kg: float,
    sanitization_type: str,
    certifications: list[int],
    label_sides: int,
    vendor_price_per_kg: float,
    cha_allocated_inr: float,
    customs_allocated_inr: float,
    db: sqlite3.Connection,
) -> dict:
    pkg = fetchone(db, "SELECT * FROM package_sizes WHERE id=?", (package_size_id,))
    labour = fetchone(db, "SELECT * FROM labour_rates WHERE package_size_id=?", (package_size_id,))
    materials = fetchone(db, "SELECT * FROM packaging_materials WHERE package_size_id=?", (package_size_id,))

    weight_grams = pkg["weight_grams"] if pkg else 500
    packing_cost = labour["packing_cost"] if labour else 0
    sticker_cost = (labour["sticker_2side"] if label_sides == 2 else labour["sticker_1side"]) if labour else 0
    pkts_per_carton = materials["pkts_per_carton"] if materials else 1
    carton_rate = materials["carton_rate"] if materials else 0
    sticker_rate = materials["sticker_rate"] if materials else 0
    pouch_price = materials["pouch_price"] if materials else 0

    num_pkts = math.ceil(quantity_kg * 1000 / weight_grams)
    num_cartons = math.ceil(num_pkts / pkts_per_carton)

    raw_material_inr = vendor_price_per_kg * quantity_kg
    labour_inr = (packing_cost + sticker_cost) * num_pkts
    packaging_inr = (carton_rate + pouch_price * pkts_per_carton) * num_cartons + sticker_rate * num_pkts

    san_row = fetchone(
        db,
        "SELECT cost_per_kg FROM sanitization_costs WHERE product_id=? AND type=?",
        (product_id, sanitization_type),
    )
    sanitization_inr = (san_row["cost_per_kg"] if san_row else 0) * quantity_kg

    cert_inr = 0.0
    for cert_id in certifications:
        cert = fetchone(db, "SELECT cost_per_kg FROM certification_types WHERE id=?", (cert_id,))
        if cert:
            cert_inr += cert["cost_per_kg"] * quantity_kg

    settings = {
        r["key"]: float(r["value"])
        for r in fetchall(db, "SELECT key, value FROM system_settings WHERE key IN ('transport_per_kg','loading_per_kg')")
    }
    transport_inr = settings.get("transport_per_kg", 1.50) * quantity_kg
    loading_inr = settings.get("loading_per_kg", 0.80) * quantity_kg

    subtotal_inr = (
        raw_material_inr + labour_inr + packaging_inr +
        sanitization_inr + cert_inr + transport_inr + loading_inr +
        cha_allocated_inr + customs_allocated_inr
    )
    per_kg_inr = subtotal_inr / quantity_kg if quantity_kg else 0

    return {
        "raw_material_inr": round(raw_material_inr, 4),
        "labour_inr": round(labour_inr, 4),
        "packaging_inr": round(packaging_inr, 4),
        "sanitization_inr": round(sanitization_inr, 4),
        "certification_inr": round(cert_inr, 4),
        "transport_inr": round(transport_inr, 4),
        "loading_inr": round(loading_inr, 4),
        "subtotal_inr": round(subtotal_inr, 4),
        "per_kg_inr": round(per_kg_inr, 4),
        "num_pkts": num_pkts,
        "num_cartons": num_cartons,
    }
