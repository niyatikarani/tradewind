import sqlite3
from pathlib import Path

SCHEMA = (Path(__file__).parent.parent / "schema.sql").read_text()
EXPECTED_TABLES = [
    "products", "qualities", "package_sizes", "labour_rates",
    "packaging_materials", "cbm_dimensions", "sanitization_costs", "certification_types",
    "users", "features", "user_features", "feature_templates",
    "countries", "country_product_overrides", "clients", "client_price_locks",
    "currencies", "margin_factors", "list_prices", "system_settings",
    "vendor_prices", "fx_rates", "quotes", "quote_line_items",
    "field_override_log", "rule_change_log",
]

def test_all_26_tables_created():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    names = {r[0] for r in rows}
    for t in EXPECTED_TABLES:
        assert t in names, f"Missing table: {t}"

def test_foreign_keys_defined():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    conn.execute("INSERT INTO products(name,category,competition_level) VALUES('P1','Spices','low')")
    conn.execute("INSERT INTO qualities(product_id,name,sort_order) VALUES(1,'Standard',1)")
    conn.commit()
    import pytest
    with pytest.raises(Exception):
        conn.execute("INSERT INTO qualities(product_id,name,sort_order) VALUES(999,'Bad',1)")
        conn.commit()
