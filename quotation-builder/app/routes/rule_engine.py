import sqlite3
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import get_db, fetchall, fetchone, execute
from ..auth import require_user, require_feature, get_user_context
from ..templates_cfg import templates

router = APIRouter(prefix="/rule-engine", tags=["rule_engine"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


def _log_change(db, user_id, category, key, scope_type, old_val, new_val, reason):
    execute(db,
        "INSERT INTO rule_change_log(user_id,rule_category,rule_key,scope_type,old_value,new_value,reason) VALUES(?,?,?,?,?,?,?)",
        (user_id, category, key, scope_type, str(old_val), str(new_val), reason),
    )


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def rule_engine_index(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    return templates.TemplateResponse("rule_engine/index.html", _ctx(request, uid, db))


# ── 1. Margin Rules ───────────────────────────────────────────────────────────
@router.get("/margin", response_class=HTMLResponse)
async def margin_rules(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    settings_rows = fetchall(db, "SELECT key, value FROM system_settings WHERE key IN ('base_margin','margin_floor','margin_cap')")
    settings = {r["key"]: r["value"] for r in settings_rows}
    clients = fetchall(db, "SELECT id, name, margin_floor_override FROM clients ORDER BY name")
    return templates.TemplateResponse("rule_engine/margin.html", {
        **_ctx(request, uid, db),
        "settings": settings,
        "clients": [dict(c) for c in clients],
    })


@router.post("/margin")
async def update_margin_rules(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    for key in ["base_margin", "margin_floor", "margin_cap"]:
        old = fetchone(db, "SELECT value FROM system_settings WHERE key=?", (key,))
        new_val = str(form.get(key, ""))
        execute(db,
            "INSERT INTO system_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, new_val))
        _log_change(db, uid, "margin", key, "global", old["value"] if old else None, new_val, str(form.get("reason", "")))
    db.commit()
    return RedirectResponse("/rule-engine/margin", status_code=302)


# ── 2. Margin Factors ─────────────────────────────────────────────────────────
@router.get("/factors", response_class=HTMLResponse)
async def margin_factors(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    factors = fetchall(db, "SELECT * FROM margin_factors ORDER BY id")
    return templates.TemplateResponse("rule_engine/factors.html", {
        **_ctx(request, uid, db),
        "factors": [dict(f) for f in factors],
    })


@router.post("/factors/{factor_id}")
async def update_factor(factor_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    weight = float(form.get("weight", 1.0))
    old = fetchone(db, "SELECT weight FROM margin_factors WHERE id=?", (factor_id,))
    execute(db, "UPDATE margin_factors SET weight=? WHERE id=?", (weight, factor_id))
    _log_change(db, uid, "margin_factor", str(factor_id), "global",
                old["weight"] if old else None, weight, str(form.get("reason", "")))
    db.commit()
    return RedirectResponse("/rule-engine/factors", status_code=302)


# ── 3. List Prices ────────────────────────────────────────────────────────────
@router.get("/list-prices", response_class=HTMLResponse)
async def list_prices_page(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    prices = fetchall(db, """
        SELECT lp.*, p.name as product_name, q.name as quality_name, ps.display_name as package_name
        FROM list_prices lp JOIN products p ON p.id=lp.product_id
        JOIN qualities q ON q.id=lp.quality_id JOIN package_sizes ps ON ps.id=lp.package_size_id
        ORDER BY p.name, q.name, ps.display_name
    """)
    return templates.TemplateResponse("rule_engine/list_prices.html", {
        **_ctx(request, uid, db),
        "prices": [dict(p) for p in prices],
    })


# ── 4. Country Profiles ───────────────────────────────────────────────────────
@router.get("/countries", response_class=HTMLResponse)
async def country_profiles(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    countries = fetchall(db,
        "SELECT c.*, cu.code as currency_code FROM countries c LEFT JOIN currencies cu ON cu.id=c.default_currency_id ORDER BY c.name")
    currencies = fetchall(db, "SELECT id, code FROM currencies WHERE is_active=1")
    return templates.TemplateResponse("rule_engine/countries.html", {
        **_ctx(request, uid, db),
        "countries": [dict(c) for c in countries],
        "currencies": [dict(c) for c in currencies],
    })


@router.post("/countries/new")
async def add_country(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    execute(db, "INSERT INTO countries(name,code,default_currency_id,default_sanitization,risk_score) VALUES(?,?,?,?,?)",
            (form["name"], form["code"], int(form["currency_id"]), form["sanitization"], int(form["risk_score"])))
    db.commit()
    return RedirectResponse("/rule-engine/countries", status_code=302)


# ── 5. Country Exceptions ─────────────────────────────────────────────────────
@router.get("/country-exceptions", response_class=HTMLResponse)
async def country_exceptions(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    overrides = fetchall(db, """
        SELECT cpo.*, c.name as country_name, p.name as product_name
        FROM country_product_overrides cpo JOIN countries c ON c.id=cpo.country_id
        JOIN products p ON p.id=cpo.product_id
        ORDER BY c.name, p.name
    """)
    countries = fetchall(db, "SELECT id, name FROM countries ORDER BY name")
    products = fetchall(db, "SELECT id, name FROM products WHERE is_active=1 ORDER BY name")
    return templates.TemplateResponse("rule_engine/country_exceptions.html", {
        **_ctx(request, uid, db),
        "overrides": [dict(o) for o in overrides],
        "countries": [dict(c) for c in countries],
        "products": [dict(p) for p in products],
    })


@router.post("/country-exceptions/new")
async def add_country_exception(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    execute(db,
        "INSERT INTO country_product_overrides(country_id,product_id,override_sanitization) VALUES(?,?,?)",
        (int(form["country_id"]), int(form["product_id"]),
         form.get("sanitization_override") or "steam"))
    db.commit()
    return RedirectResponse("/rule-engine/country-exceptions", status_code=302)


# ── 6. Client Profiles ────────────────────────────────────────────────────────
@router.get("/clients", response_class=HTMLResponse)
async def client_profiles(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    clients = fetchall(db,
        "SELECT cl.*, co.name as country_name FROM clients cl JOIN countries co ON co.id=cl.country_id ORDER BY cl.name")
    countries = fetchall(db, "SELECT id, name FROM countries ORDER BY name")
    return templates.TemplateResponse("rule_engine/clients.html", {
        **_ctx(request, uid, db),
        "clients": [dict(c) for c in clients],
        "countries": [dict(c) for c in countries],
    })


@router.post("/clients/new")
async def add_client(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    execute(db, "INSERT INTO clients(name,country_id,payment_risk,credit_terms) VALUES(?,?,?,?)",
            (form["name"], int(form["country_id"]), form["payment_risk"], form.get("credit_terms", "")))
    db.commit()
    return RedirectResponse("/rule-engine/clients", status_code=302)


# ── 7. Client Price Locks ─────────────────────────────────────────────────────
@router.get("/price-locks", response_class=HTMLResponse)
async def price_locks(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    locks = fetchall(db, """
        SELECT cpl.*, cl.name as client_name, p.name as product_name, q.name as quality_name
        FROM client_price_locks cpl JOIN clients cl ON cl.id=cpl.client_id
        JOIN products p ON p.id=cpl.product_id JOIN qualities q ON q.id=cpl.quality_id
        ORDER BY cl.name, p.name
    """)
    clients = fetchall(db, "SELECT id, name FROM clients WHERE is_active=1 ORDER BY name")
    products = fetchall(db, "SELECT id, name FROM products WHERE is_active=1 ORDER BY name")
    return templates.TemplateResponse("rule_engine/price_locks.html", {
        **_ctx(request, uid, db),
        "locks": [dict(lg) for lg in locks],
        "clients": [dict(c) for c in clients],
        "products": [dict(p) for p in products],
    })


# ── 8. Cost Defaults ──────────────────────────────────────────────────────────
@router.get("/cost-defaults", response_class=HTMLResponse)
async def cost_defaults(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    keys = ["transport_per_kg", "loading_per_kg", "cha_flat", "customs_flat"]
    settings_rows = fetchall(db,
        f"SELECT key, value FROM system_settings WHERE key IN ({','.join('?'*len(keys))})", tuple(keys))
    settings = {r["key"]: r["value"] for r in settings_rows}
    return templates.TemplateResponse("rule_engine/cost_defaults.html", {
        **_ctx(request, uid, db),
        "settings": settings,
    })


@router.post("/cost-defaults")
async def update_cost_defaults(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    for key in ["transport_per_kg", "loading_per_kg", "cha_flat", "customs_flat"]:
        if form.get(key) is not None:
            execute(db,
                "INSERT INTO system_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(form[key])))
    db.commit()
    return RedirectResponse("/rule-engine/cost-defaults", status_code=302)


# ── 9. Alert Thresholds ───────────────────────────────────────────────────────
@router.get("/thresholds", response_class=HTMLResponse)
async def alert_thresholds(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    row = fetchone(db, "SELECT value FROM system_settings WHERE key='stale_days'")
    return templates.TemplateResponse("rule_engine/thresholds.html", {
        **_ctx(request, uid, db),
        "stale_days": row["value"] if row else "7",
    })


@router.post("/thresholds")
async def update_thresholds(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    execute(db,
        "INSERT INTO system_settings(key,value) VALUES('stale_days',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (str(form["stale_days"]),))
    db.commit()
    return RedirectResponse("/rule-engine/thresholds", status_code=302)


# ── 10. Currency Settings ─────────────────────────────────────────────────────
@router.get("/currencies", response_class=HTMLResponse)
async def currency_settings(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    currencies = fetchall(db, "SELECT * FROM currencies ORDER BY code")
    latest_rates = {}
    for c in currencies:
        rate = fetchone(db,
            "SELECT rate_vs_inr, created_at FROM fx_rates WHERE currency_id=? ORDER BY created_at DESC LIMIT 1",
            (c["id"],))
        latest_rates[c["id"]] = dict(rate) if rate else None
    return templates.TemplateResponse("rule_engine/currencies.html", {
        **_ctx(request, uid, db),
        "currencies": [dict(c) for c in currencies],
        "latest_rates": latest_rates,
    })


@router.post("/currencies/{currency_id}/rate")
async def add_fx_rate(currency_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    execute(db, "INSERT INTO fx_rates(currency_id,rate_vs_inr,source,entered_by) VALUES(?,?,?,?)",
            (currency_id, float(form["rate_vs_inr"]), "manual", uid))
    db.commit()
    return RedirectResponse("/rule-engine/currencies", status_code=302)


# ── 11. Container Settings ────────────────────────────────────────────────────
@router.get("/containers", response_class=HTMLResponse)
async def container_settings(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    keys = ["container_20ft_cbm", "container_20ft_kg", "container_40ft_cbm", "container_40ft_kg"]
    settings_rows = fetchall(db,
        f"SELECT key, value FROM system_settings WHERE key IN ({','.join('?'*len(keys))})", tuple(keys))
    settings = {r["key"]: r["value"] for r in settings_rows}
    return templates.TemplateResponse("rule_engine/containers.html", {
        **_ctx(request, uid, db),
        "settings": settings,
    })


@router.post("/containers")
async def update_container_settings(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.edit", db)
    form = await request.form()
    for key in ["container_20ft_cbm", "container_20ft_kg", "container_40ft_cbm", "container_40ft_kg"]:
        if form.get(key):
            execute(db,
                "INSERT INTO system_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(form[key])))
    db.commit()
    return RedirectResponse("/rule-engine/containers", status_code=302)


# ── 12. System Settings ───────────────────────────────────────────────────────
@router.get("/system", response_class=HTMLResponse)
async def system_settings_page(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.system", db)
    keys = ["pdf_company_name", "pdf_company_address", "pdf_terms", "quote_number_prefix"]
    settings_rows = fetchall(db,
        f"SELECT key, value FROM system_settings WHERE key IN ({','.join('?'*len(keys))})", tuple(keys))
    settings = {r["key"]: r["value"] for r in settings_rows}
    return templates.TemplateResponse("rule_engine/system.html", {
        **_ctx(request, uid, db),
        "settings": settings,
    })


@router.post("/system")
async def update_system_settings(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.system", db)
    form = await request.form()
    for key in ["pdf_company_name", "pdf_company_address", "pdf_terms", "quote_number_prefix"]:
        if form.get(key) is not None:
            execute(db,
                "INSERT INTO system_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(form[key])))
    db.commit()
    return RedirectResponse("/rule-engine/system", status_code=302)


# ── 13. Audit Log ─────────────────────────────────────────────────────────────
@router.get("/audit", response_class=HTMLResponse)
async def audit_log(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "rule_engine.view", db)
    category = request.query_params.get("category", "")
    params = (f"%{category}%",) if category else ("%",)
    logs = fetchall(db, """
        SELECT rcl.*, u.name as user_name FROM rule_change_log rcl
        JOIN users u ON u.id=rcl.user_id
        WHERE rcl.rule_category LIKE ?
        ORDER BY rcl.created_at DESC LIMIT 200
    """, params)
    return templates.TemplateResponse("rule_engine/audit.html", {
        **_ctx(request, uid, db),
        "logs": [dict(lg) for lg in logs],
        "filter_category": category,
    })
