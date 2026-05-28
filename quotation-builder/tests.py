#!/usr/bin/env python3
"""
Comprehensive test suite for quotation-builder.
Tests seed data integrity, all services, and end-to-end flows.

Run:  python tests.py
"""
import json
import math
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# Setup: build an in-memory DB from schema + seed (using demo password)
# ---------------------------------------------------------------------------

BASE = Path(__file__).parent
SCHEMA_PATH = BASE / "schema.sql"
sys.path.insert(0, str(BASE))

PASS_FAIL = {"pass": 0, "fail": 0}


def ok(name, detail=""):
    PASS_FAIL["pass"] += 1
    print(f"  PASS  {name}")


def fail(name, detail=""):
    PASS_FAIL["fail"] += 1
    print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))


def check(name, condition, detail=""):
    (ok if condition else fail)(name, detail)


# ---------------------------------------------------------------------------
# Build a seeded DB without admin-password prompt (patch getpass)
# ---------------------------------------------------------------------------

def build_seeded_db() -> sqlite3.Connection:
    import getpass as _gp
    import unittest.mock as mock

    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tf.close()
    db_path = tf.name

    product_lib = BASE / "Product Library.xlsx"

    with mock.patch.object(_gp, "getpass", return_value="TestAdmin1!"):
        import importlib, seed as s
        importlib.reload(s)
        s.run_seed(db_path, product_lib)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Section helper
# ---------------------------------------------------------------------------

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("=" * 60)


# ===========================================================================
# 1. SEED DATA INTEGRITY
# ===========================================================================

def test_seed_data(conn):
    section("1. Seed Data Integrity")

    # Features
    n = conn.execute("SELECT COUNT(*) FROM features").fetchone()[0]
    check("features: at least 14 seeded", n >= 14, f"got {n}")

    # Currencies
    n = conn.execute("SELECT COUNT(*) FROM currencies").fetchone()[0]
    check("currencies: 7 seeded", n == 7, f"got {n}")

    # System settings
    n = conn.execute("SELECT COUNT(*) FROM system_settings").fetchone()[0]
    check("system_settings: at least 13 keys", n >= 13, f"got {n}")

    # Margin factors
    n = conn.execute("SELECT COUNT(*) FROM margin_factors").fetchone()[0]
    check("margin_factors: 7 seeded", n == 7, f"got {n}")

    # Products
    n = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    check("products: at least 10 seeded", n >= 10, f"got {n}")

    # Package sizes
    n = conn.execute("SELECT COUNT(*) FROM package_sizes").fetchone()[0]
    check("package_sizes: 13 seeded", n == 13, f"got {n}")

    # Every package_size has labour_rates, packaging_materials, cbm_dimensions
    orphan_labour = conn.execute(
        "SELECT COUNT(*) FROM package_sizes WHERE id NOT IN (SELECT package_size_id FROM labour_rates)"
    ).fetchone()[0]
    check("package_sizes: all have labour_rates", orphan_labour == 0, f"{orphan_labour} missing")

    orphan_pkg = conn.execute(
        "SELECT COUNT(*) FROM package_sizes WHERE id NOT IN (SELECT package_size_id FROM packaging_materials)"
    ).fetchone()[0]
    check("package_sizes: all have packaging_materials", orphan_pkg == 0, f"{orphan_pkg} missing")

    orphan_cbm = conn.execute(
        "SELECT COUNT(*) FROM package_sizes WHERE id NOT IN (SELECT package_size_id FROM cbm_dimensions)"
    ).fetchone()[0]
    check("package_sizes: all have cbm_dimensions", orphan_cbm == 0, f"{orphan_cbm} missing")

    # Countries
    n = conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    check("countries: 10 seeded", n == 10, f"got {n}")

    # Clients
    n = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    check("clients: 7 seeded", n == 7, f"got {n}")

    # Users (4 demo + 1 admin)
    n = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    check("users: 5 seeded", n == 5, f"got {n}")

    # Vendor prices
    n = conn.execute("SELECT COUNT(*) FROM vendor_prices").fetchone()[0]
    check("vendor_prices: at least 100 seeded", n >= 100, f"got {n}")

    # FX rates
    n = conn.execute("SELECT COUNT(*) FROM fx_rates").fetchone()[0]
    check("fx_rates: at least 6 seeded", n >= 6, f"got {n}")

    # Sample quotes
    n = conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
    check("quotes: 3 sample quotes seeded", n >= 3, f"got {n}")

    # Quote line items
    n = conn.execute("SELECT COUNT(*) FROM quote_line_items").fetchone()[0]
    check("quote_line_items: at least 3 seeded", n >= 3, f"got {n}")

    # Certification types
    n = conn.execute("SELECT COUNT(*) FROM certification_types").fetchone()[0]
    check("certification_types: at least 5 seeded", n >= 5, f"got {n}")


# ===========================================================================
# 2. QUOTE NUMBER COUNTER
# ===========================================================================

def test_quote_number_counter(conn):
    section("2. Quote Number Counter")

    row = conn.execute("SELECT value FROM system_settings WHERE key='quote_number_next'").fetchone()
    check("quote_number_next setting exists", row is not None)

    if row:
        next_n = int(row["value"])
        max_existing = conn.execute(
            "SELECT MAX(CAST(SUBSTR(quote_number, 5) AS INTEGER)) FROM quotes WHERE quote_number LIKE 'SGE-%'"
        ).fetchone()[0] or 0

        check(
            f"quote_number_next ({next_n}) > max existing quote# ({max_existing})",
            next_n > max_existing,
            f"next={next_n}, max_existing={max_existing} — would produce duplicate on first new quote",
        )


# ===========================================================================
# 3. USER FEATURE ASSIGNMENTS
# ===========================================================================

def test_user_features(conn):
    section("3. User Feature Assignments")

    role_requirements = {
        "ravi@sandgexports.com":      {"price.entry", "price.bulk", "price.stale", "price.trends"},
        "priya@sandgexports.com":     {"quote.create", "quote.export"},
        "suresh@sandgexports.com":    {"quote.create", "analytics.view", "price.entry"},
        "marketing@sandgexports.com": {"quote.create", "quote.export"},
        "admin@sandgexports.com":     {"admin.users", "rule_engine.edit"},
    }

    for email, required_features in role_requirements.items():
        user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            fail(f"{email}: user exists", "user not found in DB")
            continue

        assigned = {
            r[0] for r in conn.execute(
                "SELECT f.key FROM user_features uf JOIN features f ON f.id=uf.feature_id WHERE uf.user_id=?",
                (user["id"],),
            ).fetchall()
        }

        missing = required_features - assigned
        check(
            f"{email}: required features assigned",
            len(missing) == 0,
            f"missing: {missing}",
        )
        check(f"{email}: has at least 1 feature", len(assigned) > 0, f"got {len(assigned)}")


# ===========================================================================
# 4. FX RATES
# ===========================================================================

def test_fx_rates(conn):
    section("4. FX Rates")

    required_currencies = ["USD", "EUR", "GBP", "AED", "CAD", "AUD"]
    for code in required_currencies:
        row = conn.execute(
            """
            SELECT f.rate_vs_inr FROM fx_rates f
            JOIN currencies c ON c.id=f.currency_id
            WHERE c.code=?
            ORDER BY f.created_at DESC LIMIT 1
            """,
            (code,),
        ).fetchone()
        check(f"FX rate exists for {code}", row is not None, "no rate seeded")
        if row:
            check(f"FX rate for {code} is positive", row["rate_vs_inr"] > 0, f"got {row['rate_vs_inr']}")


# ===========================================================================
# 5. COST ENGINE
# ===========================================================================

def test_cost_engine(conn):
    section("5. Cost Engine")

    from app.services.cost_engine import calculate_line_costs

    product = conn.execute("SELECT id FROM products LIMIT 1").fetchone()
    quality = conn.execute("SELECT id FROM qualities WHERE product_id=?", (product["id"],)).fetchone()
    pkg = conn.execute("SELECT id FROM package_sizes ORDER BY weight_grams LIMIT 1").fetchone()

    costs = calculate_line_costs(
        product_id=product["id"],
        quality_id=quality["id"],
        package_size_id=pkg["id"],
        quantity_kg=100.0,
        sanitization_type="steam",
        certifications=[],
        label_sides=1,
        vendor_price_per_kg=200.0,
        cha_allocated_inr=0,
        customs_allocated_inr=0,
        db=conn,
    )

    check("cost_engine: raw_material_inr = vendor_price * qty",
          abs(costs["raw_material_inr"] - 20000.0) < 0.01)
    check("cost_engine: subtotal_inr > raw_material (labour/transport added)",
          costs["subtotal_inr"] > 20000.0)
    check("cost_engine: per_kg_inr > vendor_price (overheads added)",
          costs["per_kg_inr"] > 200.0)
    check("cost_engine: num_cartons >= 1", costs["num_cartons"] >= 1)
    check("cost_engine: all cost fields present",
          all(k in costs for k in ["labour_inr", "packaging_inr", "sanitization_inr",
                                    "transport_inr", "loading_inr"]))
    check("cost_engine: no negative costs",
          all(v >= 0 for k, v in costs.items() if k.endswith("_inr")))


# ===========================================================================
# 6. MARGIN ENGINE
# ===========================================================================

def test_margin_engine(conn):
    section("6. Margin Engine")

    from app.services.margin_engine import calculate_margin

    client = conn.execute("SELECT id, country_id FROM clients LIMIT 1").fetchone()
    product = conn.execute("SELECT id FROM products LIMIT 1").fetchone()

    result = calculate_margin(
        cost_per_kg_inr=200.0,
        client_id=client["id"],
        country_id=client["country_id"],
        product_id=product["id"],
        context={"volume_kg": 500, "advance_pct": 50, "client_order_count": 3,
                 "competition_level": 2, "price_volatility_pct": 1, "urgency_days": 2},
        db=conn,
    )

    check("margin_engine: margin_pct present", "margin_pct" in result)
    check("margin_engine: selling_price_per_kg_inr present", "selling_price_per_kg_inr" in result)

    floor = 3.0
    cap = 25.0
    check(f"margin_engine: margin >= floor ({floor})", result["margin_pct"] >= floor,
          f"got {result['margin_pct']}")
    check(f"margin_engine: margin <= cap ({cap})", result["margin_pct"] <= cap,
          f"got {result['margin_pct']}")
    check("margin_engine: selling_price > cost",
          result["selling_price_per_kg_inr"] > 200.0)
    check("margin_engine: 7 factor_scores returned",
          len(result["factor_scores"]) == 7, f"got {len(result['factor_scores'])}")


# ===========================================================================
# 7. STALE CHECKER
# ===========================================================================

def test_stale_checker(conn):
    section("7. Stale Checker")

    from app.services.stale_checker import check_price_stale

    # Product with vendor prices seeded today — should NOT be stale
    vp = conn.execute(
        "SELECT product_id, quality_id FROM vendor_prices ORDER BY created_at DESC LIMIT 1"
    ).fetchone()

    result = check_price_stale(vp["product_id"], vp["quality_id"], conn)
    check("stale_checker: returns dict with required keys",
          all(k in result for k in ["is_stale", "age_days", "latest_price"]))
    check("stale_checker: latest seeded price is NOT stale (seeded today)",
          result["is_stale"] is False, f"age_days={result['age_days']}")

    # Non-existent product quality → stale=True (no data = stale)
    result2 = check_price_stale(999999, 999999, conn)
    check("stale_checker: missing product/quality -> is_stale=True", result2["is_stale"] is True)


# ===========================================================================
# 8. FX SERVICE
# ===========================================================================

def test_fx_service(conn):
    section("8. FX Service")

    from app.services.fx_service import convert_inr_to_fx, get_latest_rate

    usd = conn.execute("SELECT id FROM currencies WHERE code='USD'").fetchone()
    check("FX service: USD currency exists", usd is not None)

    if usd:
        rate = get_latest_rate(usd["id"], conn)
        check("FX service: USD rate available", rate is not None and rate > 0, f"got {rate}")

        result = convert_inr_to_fx(8350.0, usd["id"], conn)
        check("FX service: returns fx_amount", "fx_amount" in result)
        check("FX service: fx_amount > 0", result["fx_amount"] > 0)
        check("FX service: rate_used > 0", result["rate_used"] > 0)
        # 8350 INR @ ~83.5 USD/INR ≈ 100 USD
        check("FX service: conversion approximately correct",
              90 < result["fx_amount"] < 110,
              f"got {result['fx_amount']} USD for 8350 INR")

    # Missing currency raises ValueError
    try:
        convert_inr_to_fx(100.0, 99999, conn)
        fail("FX service: missing currency raises ValueError")
    except ValueError:
        ok("FX service: missing currency raises ValueError")


# ===========================================================================
# 9. CBM ENGINE
# ===========================================================================

def test_cbm_engine(conn):
    section("9. CBM Engine")

    from app.services.cbm_engine import calculate_cbm, recommend_container

    pkg = conn.execute("SELECT id FROM package_sizes LIMIT 1").fetchone()

    result = calculate_cbm(pkg["id"], 10, 50.0, conn)
    check("cbm_engine: cbm_per_carton > 0", result["cbm_per_carton"] > 0)
    check("cbm_engine: total_cbm = cbm_per_carton * num_cartons",
          abs(result["total_cbm"] - result["cbm_per_carton"] * 10) < 0.0001)

    rec = recommend_container(5.0, 500.0, conn)
    check("cbm_engine: recommend_container returns recommended key", "recommended" in rec)
    check("cbm_engine: small order fits 20ft", rec["recommended"] == "20ft",
          f"got {rec['recommended']}")

    rec40 = recommend_container(35.0, 5000.0, conn)
    check("cbm_engine: large order fits 40ft", rec40["recommended"] == "40ft",
          f"got {rec40['recommended']}")

    rec_multi = recommend_container(100.0, 30000.0, conn)
    check("cbm_engine: over-capacity returns 'multiple'", rec_multi["recommended"] == "multiple",
          f"got {rec_multi['recommended']}")


# ===========================================================================
# 10. RULE RESOLVER
# ===========================================================================

def test_rule_resolver(conn):
    section("10. Rule Resolver")

    from app.services.rule_resolver import (
        resolve_sanitization, resolve_margin_floor, resolve_margin_cap, resolve_currency,
    )

    country = conn.execute("SELECT id FROM countries LIMIT 1").fetchone()
    product = conn.execute("SELECT id FROM products LIMIT 1").fetchone()

    san = resolve_sanitization(country["id"], product["id"], conn)
    check("rule_resolver: sanitization returns valid type",
          san in ("steam", "chemical", "none"), f"got {san!r}")

    floor = resolve_margin_floor(1, conn)
    check("rule_resolver: margin floor >= 0", floor >= 0, f"got {floor}")

    cap = resolve_margin_cap(conn)
    check("rule_resolver: margin cap > floor", cap > floor, f"cap={cap}, floor={floor}")

    cur_id = resolve_currency(1, country["id"], conn)
    check("rule_resolver: resolve_currency returns int > 0", isinstance(cur_id, int) and cur_id > 0,
          f"got {cur_id}")


# ===========================================================================
# 11. QUOTE CREATION FLOW (quote_number uniqueness)
# ===========================================================================

def test_quote_creation_flow(conn):
    section("11. Quote Creation Flow")

    # Read current counter
    row = conn.execute("SELECT value FROM system_settings WHERE key='quote_number_next'").fetchone()
    n = int(row["value"])
    prefix = conn.execute("SELECT value FROM system_settings WHERE key='quote_number_prefix'").fetchone()["value"]

    client = conn.execute("SELECT id, country_id FROM clients LIMIT 1").fetchone()
    currency = conn.execute("SELECT id FROM currencies WHERE code='USD'").fetchone()
    user = conn.execute("SELECT id FROM users WHERE email='admin@sandgexports.com'").fetchone()

    # Simulate _next_quote_number — generate 3 quotes
    created = []
    for _ in range(3):
        n_row = conn.execute("SELECT value FROM system_settings WHERE key='quote_number_next'").fetchone()
        num = int(n_row["value"])
        qnum = f"{prefix}-{num}"
        conn.execute(
            "UPDATE system_settings SET value=? WHERE key='quote_number_next'", (num + 1,)
        )
        try:
            conn.execute(
                "INSERT INTO quotes(quote_number,client_id,country_id,currency_id,created_by) VALUES(?,?,?,?,?)",
                (qnum, client["id"], client["country_id"], currency["id"], user["id"]),
            )
            conn.commit()
            created.append(qnum)
            ok(f"quote_creation: inserted {qnum} without conflict")
        except sqlite3.IntegrityError as e:
            conn.rollback()
            fail(f"quote_creation: UNIQUE constraint on {qnum}", str(e))

    check("quote_creation: 3 new quotes created", len(created) == 3, f"only {len(created)}")


# ===========================================================================
# 12. DATABASE CONSTRAINT CHECKS (referential integrity)
# ===========================================================================

def test_referential_integrity(conn):
    section("12. Referential Integrity")

    # quotes → clients (all client_ids exist)
    orphan_quotes = conn.execute(
        "SELECT COUNT(*) FROM quotes q WHERE NOT EXISTS (SELECT 1 FROM clients c WHERE c.id=q.client_id)"
    ).fetchone()[0]
    check("quotes: no orphaned client_id references", orphan_quotes == 0, f"{orphan_quotes} orphans")

    # quote_line_items → quotes
    orphan_items = conn.execute(
        "SELECT COUNT(*) FROM quote_line_items li WHERE NOT EXISTS (SELECT 1 FROM quotes q WHERE q.id=li.quote_id)"
    ).fetchone()[0]
    check("quote_line_items: no orphaned quote_id references", orphan_items == 0, f"{orphan_items} orphans")

    # vendor_prices → products
    orphan_vp = conn.execute(
        "SELECT COUNT(*) FROM vendor_prices vp WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.id=vp.product_id)"
    ).fetchone()[0]
    check("vendor_prices: no orphaned product_id references", orphan_vp == 0, f"{orphan_vp} orphans")

    # vendor_prices → qualities
    orphan_vq = conn.execute(
        "SELECT COUNT(*) FROM vendor_prices vp WHERE NOT EXISTS (SELECT 1 FROM qualities q WHERE q.id=vp.quality_id)"
    ).fetchone()[0]
    check("vendor_prices: no orphaned quality_id references", orphan_vq == 0, f"{orphan_vq} orphans")

    # labour_rates → package_sizes
    orphan_lr = conn.execute(
        "SELECT COUNT(*) FROM labour_rates lr WHERE NOT EXISTS (SELECT 1 FROM package_sizes ps WHERE ps.id=lr.package_size_id)"
    ).fetchone()[0]
    check("labour_rates: no orphaned package_size_id", orphan_lr == 0, f"{orphan_lr} orphans")

    # user_features → users AND features
    orphan_uf_user = conn.execute(
        "SELECT COUNT(*) FROM user_features uf WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=uf.user_id)"
    ).fetchone()[0]
    check("user_features: no orphaned user_id", orphan_uf_user == 0, f"{orphan_uf_user} orphans")

    orphan_uf_feat = conn.execute(
        "SELECT COUNT(*) FROM user_features uf WHERE NOT EXISTS (SELECT 1 FROM features f WHERE f.id=uf.feature_id)"
    ).fetchone()[0]
    check("user_features: no orphaned feature_id", orphan_uf_feat == 0, f"{orphan_uf_feat} orphans")


# ===========================================================================
# 13. SANITIZATION CHECK CONSTRAINT
# ===========================================================================

def test_sanitization_constraint(conn):
    section("13. Schema CHECK Constraints")

    # sanitization_costs.type must be in ('steam','chemical','none')
    invalid_types = conn.execute(
        "SELECT COUNT(*) FROM sanitization_costs WHERE type NOT IN ('steam','chemical','none')"
    ).fetchone()[0]
    check("sanitization_costs: all types are valid", invalid_types == 0, f"{invalid_types} invalid")

    # quote_line_items.sanitization_type
    invalid_san = conn.execute(
        "SELECT COUNT(*) FROM quote_line_items WHERE sanitization_type NOT IN ('steam','chemical','none')"
    ).fetchone()[0]
    check("quote_line_items: all sanitization_types are valid", invalid_san == 0, f"{invalid_san} invalid")

    # quotes.status
    invalid_status = conn.execute(
        "SELECT COUNT(*) FROM quotes WHERE status NOT IN ('draft','confirmed','cancelled')"
    ).fetchone()[0]
    check("quotes: all statuses are valid", invalid_status == 0, f"{invalid_status} invalid")

    # countries.risk_score BETWEEN 1 AND 5
    invalid_risk = conn.execute(
        "SELECT COUNT(*) FROM countries WHERE risk_score < 1 OR risk_score > 5"
    ).fetchone()[0]
    check("countries: all risk_scores are 1-5", invalid_risk == 0, f"{invalid_risk} invalid")

    # vendor_prices.price_per_kg > 0
    zero_prices = conn.execute(
        "SELECT COUNT(*) FROM vendor_prices WHERE price_per_kg <= 0"
    ).fetchone()[0]
    check("vendor_prices: all price_per_kg > 0", zero_prices == 0, f"{zero_prices} zero/negative")


# ===========================================================================
# 14. SYSTEM SETTINGS VALUES
# ===========================================================================

def test_system_settings(conn):
    section("14. System Settings Values")

    required_settings = {
        "base_margin": (0, 100),
        "margin_floor": (0, 100),
        "margin_cap": (0, 100),
        "stale_days": (1, 365),
        "transport_per_kg": (0, 100),
        "loading_per_kg": (0, 100),
        "container_20ft_cbm": (1, 100),
        "container_40ft_cbm": (1, 200),
        "quote_number_next": (1000, 99999),
    }

    for key, (lo, hi) in required_settings.items():
        row = conn.execute("SELECT value FROM system_settings WHERE key=?", (key,)).fetchone()
        check(f"system_settings: {key} exists", row is not None, "missing key")
        if row:
            val = float(row["value"])
            check(f"system_settings: {key} in range [{lo}, {hi}]",
                  lo <= val <= hi, f"got {val}")

    # margin_floor < base_margin < margin_cap
    rows = {
        r["key"]: float(r["value"])
        for r in conn.execute(
            "SELECT key, value FROM system_settings WHERE key IN ('base_margin','margin_floor','margin_cap')"
        ).fetchall()
    }
    if len(rows) == 3:
        check("system_settings: floor < base_margin",
              rows["margin_floor"] < rows["base_margin"],
              f"floor={rows['margin_floor']} base={rows['base_margin']}")
        check("system_settings: base_margin < cap",
              rows["base_margin"] < rows["margin_cap"],
              f"base={rows['base_margin']} cap={rows['margin_cap']}")


# ===========================================================================
# 15. QUALITIES BELONG TO VALID PRODUCTS
# ===========================================================================

def test_qualities_integrity(conn):
    section("15. Qualities Integrity")

    n_qual = conn.execute("SELECT COUNT(*) FROM qualities").fetchone()[0]
    check("qualities: at least 1 quality seeded", n_qual >= 1, f"got {n_qual}")

    orphan_qual = conn.execute(
        "SELECT COUNT(*) FROM qualities q WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.id=q.product_id)"
    ).fetchone()[0]
    check("qualities: no orphaned product_id", orphan_qual == 0, f"{orphan_qual} orphans")

    # Each product that has vendor_prices also has a quality for that quality_id
    bad_vp = conn.execute(
        "SELECT COUNT(*) FROM vendor_prices vp WHERE NOT EXISTS (SELECT 1 FROM qualities q WHERE q.id=vp.quality_id AND q.product_id=vp.product_id)"
    ).fetchone()[0]
    check("vendor_prices: quality_id matches product_id", bad_vp == 0, f"{bad_vp} mismatched")


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    print("\n" + "=" * 60)
    print("  QUOTATION BUILDER — FULL TEST SUITE")
    print("=" * 60)

    print("\nBuilding seeded test database...")
    try:
        conn = build_seeded_db()
        print("  DB ready.\n")
    except Exception:
        print("FATAL: Could not seed database:")
        traceback.print_exc()
        sys.exit(1)

    tests = [
        test_seed_data,
        test_quote_number_counter,
        test_user_features,
        test_fx_rates,
        test_cost_engine,
        test_margin_engine,
        test_stale_checker,
        test_fx_service,
        test_cbm_engine,
        test_rule_resolver,
        test_quote_creation_flow,
        test_referential_integrity,
        test_sanitization_constraint,
        test_system_settings,
        test_qualities_integrity,
    ]

    for t in tests:
        try:
            t(conn)
        except Exception:
            section(f"ERROR in {t.__name__}")
            traceback.print_exc()

    conn.close()

    print("\n" + "=" * 60)
    passed = PASS_FAIL["pass"]
    failed = PASS_FAIL["fail"]
    total = passed + failed
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60 + "\n")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
