# tests/test_integration.py
"""
Full-stack integration tests. Drives the HTTP layer, verifies DB state.
Uses in-memory SQLite via dependency override.
"""
import sqlite3
import json
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.db import get_db

SCHEMA = (ROOT / "schema.sql").read_text()


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def seed_minimal(conn: sqlite3.Connection) -> dict:
    import bcrypt
    from seed import (
        seed_features, seed_feature_templates, seed_currencies,
        seed_system_settings, seed_margin_factors,
    )
    seed_features(conn)
    seed_feature_templates(conn)
    seed_currencies(conn)
    seed_system_settings(conn)
    seed_margin_factors(conn)

    pw = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
    conn.execute("INSERT INTO users(name,email,password_hash) VALUES('Admin','admin@test.com',?)", (pw,))
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    for fid in conn.execute("SELECT id FROM features").fetchall():
        conn.execute("INSERT OR IGNORE INTO user_features(user_id,feature_id) VALUES(?,?)", (user_id, fid["id"]))

    conn.execute("INSERT INTO countries(name,code,default_currency_id,risk_score) VALUES('USA','US',1,2)")
    conn.execute("INSERT INTO clients(name,country_id,payment_risk) VALUES('ACME Corp',1,'low')")
    conn.execute("INSERT INTO products(name,category,competition_level) VALUES('Turmeric Powder','Spices','medium')")
    conn.execute("INSERT INTO qualities(product_id,name,sort_order) VALUES(1,'Premium',1)")
    conn.execute("INSERT INTO package_sizes(display_name,weight_grams) VALUES('500g',500)")
    conn.execute("INSERT INTO labour_rates(package_size_id,packing_cost,sticker_1side,sticker_2side) VALUES(1,2.0,0.5,0.8)")
    conn.execute("INSERT INTO packaging_materials(package_size_id,pkts_per_carton,carton_rate,sticker_rate,pouch_price) VALUES(1,24,45.0,0.3,2.5)")
    conn.execute("INSERT INTO cbm_dimensions(package_size_id,length_cm,breadth_cm,height_cm) VALUES(1,30,20,15)")
    conn.execute("INSERT INTO sanitization_costs(product_id,type,cost_per_kg) VALUES(1,'steam',3.0)")
    conn.execute("INSERT INTO vendor_prices(product_id,quality_id,price_per_kg,entered_by) VALUES(1,1,180.0,1)")
    conn.execute("INSERT INTO fx_rates(currency_id,rate_vs_inr,source,entered_by) VALUES(1,83.5,'manual',1)")
    conn.commit()
    return {"user_id": user_id, "client_id": 1, "country_id": 1, "currency_id": 1}


@pytest.fixture
def db():
    conn = make_db()
    yield conn
    conn.close()


@pytest.fixture
def client_with_session(db):
    ids = seed_minimal(db)

    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app, raise_server_exceptions=True) as tc:
        resp = tc.post("/login", data={"email": "admin@test.com", "password": "testpass"}, follow_redirects=True)
        assert resp.status_code == 200, f"Login failed: {resp.status_code}"
        yield tc, db, ids
    app.dependency_overrides.clear()


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_login_redirects_to_quotes(db):
    import bcrypt
    pw = bcrypt.hashpw(b"pw", bcrypt.gensalt()).decode()
    db.execute("INSERT INTO users(name,email,password_hash) VALUES('U','u@test.com',?)", (pw,))
    db.commit()

    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as tc:
        resp = tc.post("/login", data={"email": "u@test.com", "password": "pw"}, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/quotes"
    app.dependency_overrides.clear()


def test_unauthenticated_redirects_to_login(db):
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app, follow_redirects=False) as tc:
        resp = tc.get("/quotes")
        assert resp.status_code == 302
        assert "/login" in resp.headers["location"]
    app.dependency_overrides.clear()


# ── Prices ────────────────────────────────────────────────────────────────────

def test_price_entry_creates_record(client_with_session):
    tc, db, ids = client_with_session
    initial_count = db.execute("SELECT COUNT(*) FROM vendor_prices").fetchone()[0]
    resp = tc.post("/prices/entry", data={
        "product_id": 1, "quality_id": 1,
        "price_per_kg": 195.0, "vendor_name": "Test Vendor",
    }, follow_redirects=True)
    assert resp.status_code == 200
    new_count = db.execute("SELECT COUNT(*) FROM vendor_prices").fetchone()[0]
    assert new_count == initial_count + 1


def test_stale_dashboard_renders(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.get("/prices/stale")
    assert resp.status_code == 200


# ── Quote Wizard ──────────────────────────────────────────────────────────────

def test_create_quote_step1(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.post("/quotes/new", data={
        "client_id": ids["client_id"],
        "country_id": ids["country_id"],
        "currency_id": ids["currency_id"],
    }, follow_redirects=False)
    assert resp.status_code == 302
    quote = db.execute("SELECT * FROM quotes ORDER BY id DESC LIMIT 1").fetchone()
    assert quote is not None
    assert quote["status"] == "draft"


def test_add_line_item_to_quote(client_with_session):
    tc, db, ids = client_with_session
    tc.post("/quotes/new", data={
        "client_id": ids["client_id"],
        "country_id": ids["country_id"],
        "currency_id": ids["currency_id"],
    })
    quote = db.execute("SELECT id FROM quotes ORDER BY id DESC LIMIT 1").fetchone()
    quote_id = quote["id"]

    resp = tc.post(f"/quotes/{quote_id}/items/add", data={
        "product_id": 1, "quality_id": 1,
        "package_size_id": 1, "quantity_kg": 100.0, "label_sides": 1,
    }, follow_redirects=False)
    assert resp.status_code in (200, 302)

    item = db.execute("SELECT * FROM quote_line_items WHERE quote_id=?", (quote_id,)).fetchone()
    assert item is not None
    assert item["raw_material_inr"] == pytest.approx(18000.0, rel=1e-2)


def test_confirm_quote(client_with_session):
    tc, db, ids = client_with_session
    tc.post("/quotes/new", data={"client_id": 1, "country_id": 1, "currency_id": 1})
    quote = db.execute("SELECT id FROM quotes ORDER BY id DESC LIMIT 1").fetchone()
    qid = quote["id"]
    tc.post(f"/quotes/{qid}/items/add", data={
        "product_id": 1, "quality_id": 1, "package_size_id": 1, "quantity_kg": 50.0, "label_sides": 1,
    })
    resp = tc.post(f"/quotes/{qid}/confirm", follow_redirects=False)
    assert resp.status_code in (200, 302)


# ── Override ──────────────────────────────────────────────────────────────────

def test_apply_and_reset_override(client_with_session):
    tc, db, ids = client_with_session
    tc.post("/quotes/new", data={"client_id": 1, "country_id": 1, "currency_id": 1})
    qid = db.execute("SELECT id FROM quotes ORDER BY id DESC LIMIT 1").fetchone()["id"]
    tc.post(f"/quotes/{qid}/items/add", data={"product_id": 1, "quality_id": 1, "package_size_id": 1, "quantity_kg": 50.0, "label_sides": 1})
    lid = db.execute("SELECT id FROM quote_line_items WHERE quote_id=?", (qid,)).fetchone()["id"]

    resp = tc.post(f"/quotes/{qid}/items/{lid}/override", data={
        "field_name": "margin_pct", "override_value": 20.0, "reason": "Client request",
    })
    assert resp.status_code == 200
    row = db.execute("SELECT is_overridden FROM quote_line_items WHERE id=?", (lid,)).fetchone()
    assert json.loads(row["is_overridden"] or "{}").get("margin_pct") is True

    resp = tc.post(f"/quotes/{qid}/items/{lid}/override/reset", data={"field_name": "margin_pct"})
    assert resp.status_code == 200


# ── Analytics ─────────────────────────────────────────────────────────────────

def test_analytics_dashboard_renders(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.get("/analytics")
    assert resp.status_code == 200


# ── Rule Engine ───────────────────────────────────────────────────────────────

def test_rule_engine_margin_renders(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.get("/rule-engine/margin")
    assert resp.status_code == 200


def test_audit_log_renders(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.get("/rule-engine/audit")
    assert resp.status_code == 200


# ── Admin ─────────────────────────────────────────────────────────────────────

def test_admin_users_renders(client_with_session):
    tc, db, ids = client_with_session
    resp = tc.get("/admin/users")
    assert resp.status_code == 200


def test_create_user(client_with_session):
    tc, db, ids = client_with_session
    initial = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    resp = tc.post("/admin/users/new", data={
        "name": "New User", "email": "new@test.com", "password": "pass123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == initial + 1
