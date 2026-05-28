import sqlite3
from ..db import fetchone


def check_price_stale(
    product_id: int, quality_id: int, db: sqlite3.Connection
) -> dict:
    threshold_row = fetchone(db, "SELECT value FROM system_settings WHERE key='stale_days'")
    threshold_days = int(threshold_row["value"]) if threshold_row else 7

    row = fetchone(
        db,
        """
        SELECT price_per_kg, created_at,
               CAST(julianday('now') - julianday(created_at) AS INTEGER) AS age_days
        FROM vendor_prices
        WHERE product_id=? AND quality_id=?
        ORDER BY created_at DESC LIMIT 1
        """,
        (product_id, quality_id),
    )

    if not row:
        return {"is_stale": True, "age_days": None, "latest_price": None, "latest_at": None}

    age_days = row["age_days"]
    return {
        "is_stale": age_days >= threshold_days,
        "age_days": age_days,
        "latest_price": row["price_per_kg"],
        "latest_at": row["created_at"],
    }


def check_items_stale(
    items: list[dict], db: sqlite3.Connection
) -> list[dict]:
    results = []
    for item in items:
        status = check_price_stale(item["product_id"], item["quality_id"], db)
        results.append({**item, **status})
    return results
