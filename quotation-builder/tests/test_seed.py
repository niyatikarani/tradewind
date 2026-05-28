import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
SCHEMA = (Path(__file__).parent.parent / "schema.sql").read_text()


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def test_seed_features():
    from seed import seed_features
    conn = make_db()
    seed_features(conn)
    rows = conn.execute("SELECT key FROM features").fetchall()
    keys = {r["key"] for r in rows}
    expected = {
        "price.entry", "price.bulk", "price.stale", "price.trends",
        "quote.create", "quote.manual_override", "quote.stale_override",
        "quote.export", "rule_engine.view", "rule_engine.edit",
        "analytics.view", "analytics.export",
        "admin.master_data", "admin.users", "admin.system",
    }
    assert expected == keys


def test_seed_currencies():
    from seed import seed_currencies
    conn = make_db()
    seed_currencies(conn)
    rows = conn.execute("SELECT code FROM currencies").fetchall()
    codes = {r["code"] for r in rows}
    assert {"USD", "INR", "EUR", "GBP", "AED", "CAD", "AUD"} == codes


def test_seed_system_settings():
    from seed import seed_system_settings
    conn = make_db()
    seed_system_settings(conn)
    row = conn.execute("SELECT value FROM system_settings WHERE key='stale_days'").fetchone()
    assert row is not None
    assert row["value"] == "7"


def test_seed_margin_factors():
    from seed import seed_margin_factors
    conn = make_db()
    seed_margin_factors(conn)
    rows = conn.execute("SELECT factor_key FROM margin_factors").fetchall()
    keys = {r["factor_key"] for r in rows}
    assert len(keys) == 7
    assert "volume" in keys
    assert "advance_payment" in keys


def test_seed_feature_templates():
    from seed import seed_features, seed_feature_templates
    conn = make_db()
    seed_features(conn)
    seed_feature_templates(conn)
    rows = conn.execute("SELECT name FROM feature_templates").fetchall()
    names = {r["name"] for r in rows}
    assert {"Price Updater", "Quote Builder", "Super User", "Admin"} == names
