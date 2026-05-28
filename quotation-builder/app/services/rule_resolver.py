import sqlite3
from ..db import fetchone


def resolve_sanitization(country_id: int, product_id: int, db: sqlite3.Connection) -> str:
    override = fetchone(
        db,
        "SELECT override_sanitization FROM country_product_overrides WHERE country_id=? AND product_id=?",
        (country_id, product_id),
    )
    if override:
        return override["override_sanitization"]
    country = fetchone(db, "SELECT default_sanitization FROM countries WHERE id=?", (country_id,))
    return country["default_sanitization"] if country else "steam"


def resolve_margin_floor(client_id: int, db: sqlite3.Connection) -> float:
    client = fetchone(db, "SELECT margin_floor_override FROM clients WHERE id=?", (client_id,))
    if client and client["margin_floor_override"] is not None:
        return float(client["margin_floor_override"])
    row = fetchone(db, "SELECT value FROM system_settings WHERE key='margin_floor'")
    return float(row["value"]) if row else 3.0


def resolve_margin_cap(db: sqlite3.Connection) -> float:
    row = fetchone(db, "SELECT value FROM system_settings WHERE key='margin_cap'")
    return float(row["value"]) if row else 25.0


def resolve_currency(client_id: int, country_id: int, db: sqlite3.Connection) -> int:
    country = fetchone(db, "SELECT default_currency_id FROM countries WHERE id=?", (country_id,))
    if country and country["default_currency_id"]:
        return country["default_currency_id"]
    inr = fetchone(db, "SELECT id FROM currencies WHERE code='INR'")
    return inr["id"] if inr else 1


def resolve_client_price_lock(
    client_id: int, product_id: int, quality_id: int, db: sqlite3.Connection
) -> float | None:
    row = fetchone(
        db,
        """
        SELECT locked_price FROM client_price_locks
        WHERE client_id=? AND product_id=? AND quality_id=?
          AND valid_from <= date('now') AND valid_to >= date('now')
        ORDER BY valid_from DESC LIMIT 1
        """,
        (client_id, product_id, quality_id),
    )
    return float(row["locked_price"]) if row else None
