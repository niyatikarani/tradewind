import sqlite3
import json
from ..db import fetchone, fetchall


def _score_factor(value: float, tiers: list[dict]) -> float:
    for tier in tiers:
        min_v = tier.get("min")
        max_v = tier.get("max")
        if min_v is not None and max_v is not None:
            if min_v <= value < max_v:
                return tier["adjustment"]
        elif min_v is not None:
            if value >= min_v:
                return tier["adjustment"]
        elif max_v is not None:
            if value < max_v:
                return tier["adjustment"]
    return 0.0


def calculate_margin(
    cost_per_kg_inr: float,
    client_id: int,
    country_id: int,
    product_id: int | None,
    context: dict,
    db: sqlite3.Connection,
) -> dict:
    settings = {
        r["key"]: float(r["value"])
        for r in fetchall(
            db,
            "SELECT key, value FROM system_settings WHERE key IN ('base_margin','margin_floor','margin_cap')",
        )
    }
    base = settings.get("base_margin", 10.0)
    floor = settings.get("margin_floor", 3.0)
    cap = settings.get("margin_cap", 25.0)

    client = fetchone(db, "SELECT margin_floor_override FROM clients WHERE id=?", (client_id,))
    if client and client["margin_floor_override"] is not None:
        floor = client["margin_floor_override"]

    country = fetchone(db, "SELECT risk_score FROM countries WHERE id=?", (country_id,))
    risk_score = country["risk_score"] if country else 3

    factor_input = {
        "volume":           context.get("volume_kg", 0),
        "advance_payment":  context.get("advance_pct", 0),
        "client_history":   context.get("client_order_count", 0),
        "competition":      context.get("competition_level", 2),
        "price_volatility": context.get("price_volatility_pct", 0),
        "country_risk":     risk_score,
        "urgency":          context.get("urgency_days", 1),
    }

    factors = fetchall(db, "SELECT * FROM margin_factors")
    factor_scores = {}
    weighted_adjustment = 0.0

    for f in factors:
        tiers = json.loads(f["scoring_tiers"])
        value = factor_input.get(f["factor_key"], 0)
        adjustment = _score_factor(value, tiers)
        factor_scores[f["factor_key"]] = adjustment
        weighted_adjustment += adjustment * f["weight"]

    margin_pct = base + weighted_adjustment
    is_floored = margin_pct < floor
    is_capped = margin_pct > cap
    margin_pct = max(floor, min(cap, margin_pct))

    selling_price = round(cost_per_kg_inr * (1 + margin_pct / 100), 4)

    return {
        "margin_pct": round(margin_pct, 4),
        "selling_price_per_kg_inr": selling_price,
        "factor_scores": factor_scores,
        "is_floored": is_floored,
        "is_capped": is_capped,
    }
