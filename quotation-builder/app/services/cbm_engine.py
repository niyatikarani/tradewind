import sqlite3
from ..db import fetchone, fetchall


def calculate_cbm(
    package_size_id: int, num_cartons: int, quantity_kg: float, db: sqlite3.Connection
) -> dict:
    dims = fetchone(
        db,
        "SELECT length_cm, breadth_cm, height_cm FROM cbm_dimensions WHERE package_size_id=?",
        (package_size_id,),
    )
    if not dims:
        return {"cbm_per_carton": 0, "total_cbm": 0, "total_kg": quantity_kg}

    cbm_per_carton = (dims["length_cm"] * dims["breadth_cm"] * dims["height_cm"]) / 1_000_000
    total_cbm = cbm_per_carton * num_cartons

    return {
        "cbm_per_carton": round(cbm_per_carton, 6),
        "total_cbm": round(total_cbm, 4),
        "total_kg": quantity_kg,
    }


def recommend_container(
    total_cbm: float, total_kg: float, db: sqlite3.Connection
) -> dict:
    settings = {
        r["key"]: float(r["value"])
        for r in fetchall(
            db,
            "SELECT key, value FROM system_settings WHERE key IN ('container_20ft_cbm','container_20ft_kg','container_40ft_cbm','container_40ft_kg')",
        )
    }
    c20_cbm = settings.get("container_20ft_cbm", 28)
    c20_kg = settings.get("container_20ft_kg", 21700)
    c40_cbm = settings.get("container_40ft_cbm", 56)
    c40_kg = settings.get("container_40ft_kg", 26500)

    fits_20ft = total_cbm <= c20_cbm and total_kg <= c20_kg
    fits_40ft = total_cbm <= c40_cbm and total_kg <= c40_kg

    if fits_20ft:
        recommended = "20ft"
        utilization_cbm = total_cbm / c20_cbm * 100
        utilization_kg = total_kg / c20_kg * 100
    elif fits_40ft:
        recommended = "40ft"
        utilization_cbm = total_cbm / c40_cbm * 100
        utilization_kg = total_kg / c40_kg * 100
    else:
        recommended = "multiple"
        utilization_cbm = total_cbm / c40_cbm * 100
        utilization_kg = total_kg / c40_kg * 100

    return {
        "recommended": recommended,
        "utilization_cbm_pct": round(utilization_cbm, 1),
        "utilization_kg_pct": round(utilization_kg, 1),
        "total_cbm": total_cbm,
        "total_kg": total_kg,
    }
