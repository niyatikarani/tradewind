#!/usr/bin/env python3
"""
demo_data.py — Insert realistic demo data for S&G Exports UI showcase.
Run: py demo_data.py
Safe to re-run — uses INSERT OR IGNORE / upserts throughout.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

DB = Path(__file__).parent / "quotation.db"


def upsert(conn, table, data, conflict_cols):
    cols = list(data.keys())
    ph = ", ".join("?" * len(cols))
    update = ", ".join(f"{c}=excluded.{c}" for c in cols if c not in conflict_cols)
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({ph}) ON CONFLICT({', '.join(conflict_cols)}) DO UPDATE SET {update}"
    cur = conn.execute(sql, list(data.values()))
    return cur.lastrowid


def ago(days=0, hours=0):
    return (datetime.now() - timedelta(days=days, hours=hours)).strftime("%Y-%m-%d %H:%M:%S")


def run():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row

    # ── PRODUCTS ──────────────────────────────────────────────────────────────
    products = [
        ("Turmeric",        "Spices",     "medium"),
        ("Black Pepper",    "Spices",     "high"),
        ("Cumin",           "Spices",     "medium"),
        ("Coriander",       "Spices",     "low"),
        ("Cardamom",        "Spices",     "low"),
        ("Red Chilli",      "Spices",     "high"),
    ]
    prod_ids = {}
    for name, cat, comp in products:
        pid = upsert(conn, "products", {"name": name, "category": cat, "competition_level": comp}, ["name"])
        prod_ids[name] = pid
    print(f"  Products: {len(prod_ids)}")

    # ── QUALITIES ─────────────────────────────────────────────────────────────
    qualities_map = {
        "Turmeric":     ["Finger", "Bulb", "Rajapuri"],
        "Black Pepper": ["MG1", "FAQ", "Garbled"],
        "Cumin":        ["Bold", "Medium", "Small"],
        "Coriander":    ["Eagle", "Badami"],
        "Cardamom":     ["Bold 8mm", "Medium 7mm", "Small 6mm"],
        "Red Chilli":   ["S4", "Teja", "Byadagi"],
    }
    qual_ids = {}
    for prod, quals in qualities_map.items():
        qual_ids[prod] = {}
        for i, q in enumerate(quals):
            qid = upsert(conn, "qualities",
                         {"product_id": prod_ids[prod], "name": q, "sort_order": i},
                         ["product_id", "name"])
            qual_ids[prod][q] = qid
    print(f"  Qualities seeded")

    # ── PACKAGE SIZES + related tables ────────────────────────────────────────
    sizes = [
        # display_name,   grams, standard
        ("100g",          100,   1),
        ("250g",          250,   1),
        ("500g",          500,   1),
        ("1kg",           1000,  1),
        ("5kg",           5000,  0),
        ("25kg Bulk",     25000, 0),
    ]
    size_ids = {}
    for dname, grams, std in sizes:
        sid = upsert(conn, "package_sizes",
                     {"display_name": dname, "weight_grams": grams, "is_standard": std},
                     ["display_name"])
        size_ids[dname] = sid

        pkts = max(1, 25000 // grams)
        upsert(conn, "labour_rates",
               {"package_size_id": sid,
                "packing_cost": round(0.5 + grams / 2000, 2),
                "sticker_1side": 0.10, "sticker_2side": 0.18},
               ["package_size_id"])

        upsert(conn, "packaging_materials",
               {"package_size_id": sid,
                "pkts_per_carton": pkts,
                "carton_rate": round(35 + pkts * 0.5, 2),
                "sticker_rate": 0.12,
                "pouch_price": round(0.80 + grams / 2000, 2)},
               ["package_size_id"])

        upsert(conn, "cbm_dimensions",
               {"package_size_id": sid,
                "length_cm": round(20 + grams / 500, 1),
                "breadth_cm": round(10 + grams / 1000, 1),
                "height_cm": round(8 + grams / 1000, 1)},
               ["package_size_id"])
    print(f"  Package sizes: {len(size_ids)}")

    # ── SANITIZATION COSTS ───────────────────────────────────────────────────
    san_costs = {"steam": 1.20, "chemical": 0.80, "none": 0.0}
    for prod, pid in prod_ids.items():
        for stype, cost in san_costs.items():
            upsert(conn, "sanitization_costs",
                   {"product_id": pid, "type": stype, "cost_per_kg": cost},
                   ["product_id", "type"])
    print(f"  Sanitization costs seeded")

    # ── CERTIFICATION TYPES ──────────────────────────────────────────────────
    certs = [
        ("FSSAI",      0.50),
        ("ISO 22000",  1.20),
        ("Organic",    2.50),
        ("Halal",      0.80),
        ("Kosher",     1.00),
    ]
    for name, cost in certs:
        upsert(conn, "certification_types",
               {"name": name, "cost_per_kg": cost}, ["name"])
    print(f"  Certification types: {len(certs)}")

    # ── CURRENCIES + FX RATES ─────────────────────────────────────────────────
    admin_id = conn.execute("SELECT id FROM users LIMIT 1").fetchone()["id"]

    currencies = [
        ("USD", "US Dollar",          83.50, 0.02),
        ("EUR", "Euro",               90.20, 0.02),
        ("GBP", "British Pound",     105.80, 0.02),
        ("AED", "UAE Dirham",         22.73, 0.01),
        ("CAD", "Canadian Dollar",    61.40, 0.02),
        ("AUD", "Australian Dollar",  54.90, 0.02),
        ("INR", "Indian Rupee",        1.00, 0.00),
    ]
    cur_ids = {}
    for code, name, rate, buf in currencies:
        cid = upsert(conn, "currencies",
                     {"code": code, "name": name, "fx_variation_buffer": buf}, ["code"])
        cur_ids[code] = cid
        conn.execute(
            "INSERT INTO fx_rates(currency_id, rate_vs_inr, source, entered_by, created_at) VALUES(?,?,?,?,?)",
            (cid, rate, "demo", admin_id, ago(1))
        )
    print(f"  Currencies + FX rates seeded")

    # ── COUNTRIES ─────────────────────────────────────────────────────────────
    countries = [
        ("Germany",      "DE", "EUR", "steam",    2),
        ("United States","US", "USD", "none",     1),
        ("UAE",          "AE", "AED", "steam",    2),
        ("United Kingdom","GB","GBP", "steam",    2),
        ("Australia",    "AU", "AUD", "chemical", 3),
        ("Canada",       "CA", "CAD", "none",     1),
    ]
    country_ids = {}
    for name, code, cur_code, san, risk in countries:
        cid = upsert(conn, "countries",
                     {"name": name, "code": code,
                      "default_currency_id": cur_ids[cur_code],
                      "default_sanitization": san,
                      "risk_score": risk},
                     ["code"])
        country_ids[name] = cid
    print(f"  Countries: {len(country_ids)}")

    # ── CLIENTS ───────────────────────────────────────────────────────────────
    clients = [
        ("Euro Spices GmbH",         "Germany",       "medium", "Net 30",  None),
        ("Al Barakah Trading",        "UAE",           "low",    "Advance", 0.08),
        ("Spice World UK",            "United Kingdom","medium", "Net 45",  None),
        ("American Spice Imports",    "United States", "low",    "Net 15",  None),
        ("Sydney Spice Co.",          "Australia",     "high",   "Net 60",  0.12),
        ("Canadian Herb & Spice Ltd", "Canada",        "medium", "Net 30",  None),
    ]
    client_ids = {}
    for name, country, risk, terms, floor in clients:
        row = conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone()
        if row:
            client_ids[name] = row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO clients(name, country_id, payment_risk, credit_terms, margin_floor_override) VALUES(?,?,?,?,?)",
                (name, country_ids[country], risk, terms, floor)
            )
            client_ids[name] = cur.lastrowid
    print(f"  Clients: {len(client_ids)}")

    # ── LIST PRICES ───────────────────────────────────────────────────────────
    list_price_map = {
        "Turmeric":     {"Finger": 85, "Bulb": 78, "Rajapuri": 92},
        "Black Pepper": {"MG1": 550, "FAQ": 480, "Garbled": 420},
        "Cumin":        {"Bold": 310, "Medium": 280, "Small": 250},
        "Coriander":    {"Eagle": 95, "Badami": 85},
        "Cardamom":     {"Bold 8mm": 1800, "Medium 7mm": 1600, "Small 6mm": 1400},
        "Red Chilli":   {"S4": 120, "Teja": 145, "Byadagi": 160},
    }
    for prod, qual_prices in list_price_map.items():
        for qual, base_price in qual_prices.items():
            qid = qual_ids[prod][qual]
            for size_name, sid in size_ids.items():
                mult = 1.0 if "kg" in size_name.lower() or "bulk" in size_name.lower() else 1.05
                upsert(conn, "list_prices",
                       {"product_id": prod_ids[prod],
                        "quality_id": qid,
                        "package_size_id": sid,
                        "list_price": round(base_price * mult, 2)},
                       ["product_id", "quality_id", "package_size_id"])
    print(f"  List prices seeded")

    # ── VENDOR PRICES ─────────────────────────────────────────────────────────
    vendor_price_map = {
        "Turmeric":     {"Finger": 72, "Bulb": 65, "Rajapuri": 79},
        "Black Pepper": {"MG1": 490, "FAQ": 430, "Garbled": 370},
        "Cumin":        {"Bold": 270, "Medium": 245, "Small": 215},
        "Coriander":    {"Eagle": 82, "Badami": 73},
        "Cardamom":     {"Bold 8mm": 1650, "Medium 7mm": 1480, "Small 6mm": 1290},
        "Red Chilli":   {"S4": 105, "Teja": 128, "Byadagi": 142},
    }
    vendors = ["Mehta Traders", "Patel Agro", "Singh & Sons", "Kumar Spices"]
    for prod, qual_prices in vendor_price_map.items():
        for qual, price in qual_prices.items():
            conn.execute(
                "INSERT INTO vendor_prices(product_id, quality_id, price_per_kg, vendor_name, entered_by, created_at) VALUES(?,?,?,?,?,?)",
                (prod_ids[prod], qual_ids[prod][qual],
                 price, vendors[hash(prod + qual) % len(vendors)],
                 admin_id, ago(3))
            )
            # one older entry for trend
            conn.execute(
                "INSERT INTO vendor_prices(product_id, quality_id, price_per_kg, vendor_name, entered_by, created_at) VALUES(?,?,?,?,?,?)",
                (prod_ids[prod], qual_ids[prod][qual],
                 round(price * 0.95, 2), vendors[(hash(prod + qual) + 1) % len(vendors)],
                 admin_id, ago(10))
            )
    print(f"  Vendor prices seeded")

    # ── CLIENT PRICE LOCK ─────────────────────────────────────────────────────
    # Euro Spices GmbH has a locked price on Black Pepper MG1
    conn.execute(
        "INSERT OR IGNORE INTO client_price_locks(client_id, product_id, quality_id, locked_price, valid_from, valid_to) VALUES(?,?,?,?,?,?)",
        (client_ids["Euro Spices GmbH"],
         prod_ids["Black Pepper"], qual_ids["Black Pepper"]["MG1"],
         490.0, "2026-01-01", "2026-12-31")
    )
    print(f"  Client price locks seeded")

    # ── QUOTES ───────────────────────────────────────────────────────────────
    quote_number = conn.execute("SELECT COALESCE(MAX(CAST(SUBSTR(quote_number,5) AS INT)),1000) FROM quotes").fetchone()[0]

    quotes_spec = [
        # client,                    currency, status,      days_ago, notes
        ("Euro Spices GmbH",         "EUR", "confirmed",   15, "Annual contract Q1"),
        ("Al Barakah Trading",       "AED", "confirmed",   10, "Festival season order"),
        ("Spice World UK",           "GBP", "draft",        3, "Pending client approval"),
        ("American Spice Imports",   "USD", "draft",        1, "First order — new client"),
        ("Sydney Spice Co.",         "AUD", "cancelled",   20, "Client postponed to Q3"),
        ("Canadian Herb & Spice Ltd","CAD", "confirmed",    7, "Regular monthly supply"),
    ]

    q_ids = []
    for client_name, cur_code, status, days, notes in quotes_spec:
        quote_number += 1
        qnum = f"SGE-{quote_number}"
        client = conn.execute("SELECT * FROM clients WHERE name=?", (client_name,)).fetchone()
        confirmed_at = ago(days - 2) if status == "confirmed" else None
        conn.execute(
            """INSERT OR IGNORE INTO quotes
               (quote_number, client_id, country_id, currency_id, status,
                has_stale_override, created_by, created_at, confirmed_at, notes)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (qnum, client["id"], client["country_id"], cur_ids[cur_code],
             status, 0, admin_id, ago(days), confirmed_at, notes)
        )
        qid = conn.execute("SELECT id FROM quotes WHERE quote_number=?", (qnum,)).fetchone()["id"]
        q_ids.append((qid, client["country_id"], cur_ids[cur_code]))

    print(f"  Quotes: {len(q_ids)}")
    # Keep quote_number_next ahead of demo data so new quotes don't collide
    conn.execute(
        "INSERT INTO system_settings(key,value) VALUES('quote_number_next',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (quote_number + 1,)
    )

    # ── QUOTE LINE ITEMS ──────────────────────────────────────────────────────
    fx_lookup = {code: rate for code, _, rate, _ in currencies}
    cur_code_by_id = {v: k for k, v in cur_ids.items()}

    line_specs = [
        # (product, quality, size, qty_kg, san, label_sides)
        [("Turmeric",    "Finger",   "1kg",  2000, "steam",    1),
         ("Black Pepper","MG1",      "500g", 1000, "steam",    1),
         ("Cumin",       "Bold",     "250g",  500, "none",     2)],
        [("Cardamom",    "Bold 8mm", "100g",  300, "steam",    2),
         ("Black Pepper","FAQ",      "1kg",  1500, "steam",    1)],
        [("Red Chilli",  "Teja",     "500g",  800, "steam",    1),
         ("Coriander",  "Eagle",    "250g",  600, "none",     1),
         ("Turmeric",   "Rajapuri", "1kg",  1200, "chemical", 1)],
        [("Cumin",       "Medium",   "500g",  400, "none",     1),
         ("Cardamom",    "Medium 7mm","100g", 200, "steam",    2)],
        [("Black Pepper","Garbled",  "25kg Bulk",5000,"steam", 1),
         ("Red Chilli",  "S4",       "25kg Bulk",3000,"none",  1)],
        [("Turmeric",    "Bulb",     "1kg",  1800, "steam",    1),
         ("Coriander",  "Badami",   "500g",  900, "none",     1),
         ("Cumin",      "Small",    "250g",  600, "none",     1)],
    ]

    for (qid, country_id, currency_id), lines in zip(q_ids, line_specs):
        cur_code = cur_code_by_id[currency_id]
        fx = fx_lookup.get(cur_code, 1.0)

        for prod, qual, size, qty_kg, san, label_sides in lines:
            pid = prod_ids[prod]
            ql_id = qual_ids[prod][qual]
            sid = size_ids[size]

            vp = vendor_price_map[prod][qual]
            raw = vp * qty_kg
            labour = conn.execute("SELECT packing_cost, sticker_1side, sticker_2side FROM labour_rates WHERE package_size_id=?", (sid,)).fetchone()
            pkg    = conn.execute("SELECT pkts_per_carton, carton_rate, pouch_price FROM packaging_materials WHERE package_size_id=?", (sid,)).fetchone()
            cbm_d  = conn.execute("SELECT length_cm, breadth_cm, height_cm FROM cbm_dimensions WHERE package_size_id=?", (sid,)).fetchone()

            sticker_cost = labour["sticker_2side"] if label_sides == 2 else labour["sticker_1side"]
            labour_inr   = (labour["packing_cost"] + sticker_cost) * qty_kg
            weight_g     = conn.execute("SELECT weight_grams FROM package_sizes WHERE id=?", (sid,)).fetchone()["weight_grams"]
            num_pkts     = (qty_kg * 1000) / weight_g
            num_cartons  = max(1, int(num_pkts / pkg["pkts_per_carton"]))
            pkg_inr      = (pkg["carton_rate"] * num_cartons) + (pkg["pouch_price"] * num_pkts)
            san_inr      = (san_costs.get(san, 0)) * qty_kg
            transport_inr = 1.50 * qty_kg
            loading_inr   = 0.80 * qty_kg
            subtotal      = raw + labour_inr + pkg_inr + san_inr + transport_inr + loading_inr
            cost_per_kg   = subtotal / qty_kg
            margin_pct    = 12.0
            selling_inr   = cost_per_kg * (1 + margin_pct / 100)
            selling_fx    = round(selling_inr / fx, 4) if fx > 0 else selling_inr

            cbm_per_carton = (cbm_d["length_cm"] * cbm_d["breadth_cm"] * cbm_d["height_cm"]) / 1_000_000
            total_cbm = round(cbm_per_carton * num_cartons, 4)

            conn.execute(
                """INSERT INTO quote_line_items
                   (quote_id, product_id, quality_id, package_size_id, quantity_kg,
                    sanitization_type, label_sides, certifications,
                    vendor_price_per_kg, raw_material_inr, labour_inr, packaging_inr,
                    sanitization_inr, certification_inr, loading_inr, transport_inr,
                    subtotal_inr, cost_per_kg_inr, margin_pct,
                    selling_price_per_kg_inr, selling_price_fx, fx_rate_used,
                    cbm_per_carton, num_cartons, total_cbm,
                    is_overridden, override_values, original_calc_values)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (qid, pid, ql_id, sid, qty_kg,
                 san, label_sides, '["FSSAI"]',
                 vp, round(raw, 2), round(labour_inr, 2), round(pkg_inr, 2),
                 round(san_inr, 2), 0.0, round(loading_inr, 2), round(transport_inr, 2),
                 round(subtotal, 2), round(cost_per_kg, 2), margin_pct,
                 round(selling_inr, 2), selling_fx, fx,
                 round(cbm_per_carton, 6), num_cartons, total_cbm,
                 "{}", "{}", "{}")
            )
    print(f"  Quote line items seeded")

    # ── RULE CHANGE LOG (audit trail) ─────────────────────────────────────────
    audit_entries = [
        ("margin",    "base_margin",       "10",  "12",  "Increased due to rising input costs"),
        ("margin",    "margin_floor",      "3",   "5",   "Board directive Q1 2026"),
        ("countries", "country.DE.risk",   "2",   "1",   "Germany upgraded to low risk"),
        ("factors",   "volume.weight",     "1.2", "1.5", "Recalibrated after annual review"),
        ("system",    "stale_days",        "14",  "7",   "Reduced stale window for price accuracy"),
        ("prices",    "transport_per_kg",  "1.20","1.50","Fuel surcharge effective May 2026"),
    ]
    for cat, key, old, new, reason in audit_entries:
        conn.execute(
            "INSERT INTO rule_change_log(user_id, rule_category, rule_key, old_value, new_value, reason, created_at) VALUES(?,?,?,?,?,?,?)",
            (admin_id, cat, key, old, new, reason, ago(hash(key) % 30 + 1))
        )
    print(f"  Audit log: {len(audit_entries)} entries")

    conn.commit()
    conn.close()
    print("\nDemo data loaded. Restart server and open http://localhost:8000")


if __name__ == "__main__":
    run()
