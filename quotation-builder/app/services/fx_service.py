import sqlite3
from ..db import fetchone


def get_latest_rate(currency_id: int, db: sqlite3.Connection) -> float | None:
    row = fetchone(
        db,
        "SELECT rate_vs_inr FROM fx_rates WHERE currency_id=? ORDER BY created_at DESC LIMIT 1",
        (currency_id,),
    )
    return float(row["rate_vs_inr"]) if row else None


def convert_inr_to_fx(
    amount_inr: float, currency_id: int, db: sqlite3.Connection
) -> dict:
    rate = get_latest_rate(currency_id, db)
    if rate is None:
        raise ValueError(f"No FX rate available for currency_id={currency_id}")

    cur = fetchone(db, "SELECT fx_variation_buffer FROM currencies WHERE id=?", (currency_id,))
    buffer = float(cur["fx_variation_buffer"]) if cur else 0.0

    rate_with_buffer = rate * (1 - buffer)
    fx_amount = amount_inr / rate_with_buffer

    return {
        "fx_amount": round(fx_amount, 4),
        "rate_used": round(rate_with_buffer, 4),
        "raw_rate": round(rate, 4),
        "buffer_applied": buffer,
    }


def fetch_and_store_rate(
    currency_code: str, api_key: str, db: sqlite3.Connection, system_user_id: int = 1
) -> float | None:
    import requests
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{currency_code}/INR"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("result") != "success":
            return None
        rate = float(data["conversion_rate"])
        cur = fetchone(db, "SELECT id FROM currencies WHERE code=?", (currency_code,))
        if cur:
            db.execute(
                "INSERT INTO fx_rates(currency_id, rate_vs_inr, source, entered_by) VALUES(?,?,?,?)",
                (cur["id"], rate, "exchangerate-api.com", system_user_id),
            )
            db.commit()
        return rate
    except Exception:
        return None
