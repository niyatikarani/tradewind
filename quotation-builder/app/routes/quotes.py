import sqlite3
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import get_db, fetchall, fetchone, execute
from ..auth import require_user, require_feature, get_user_context
from ..services.cost_engine import calculate_line_costs
from ..services.margin_engine import calculate_margin
from ..services.rule_resolver import resolve_sanitization
from ..services.stale_checker import check_price_stale
from ..services.cbm_engine import calculate_cbm, recommend_container
from ..services.fx_service import convert_inr_to_fx
from ..templates_cfg import templates

router = APIRouter(prefix="/quotes", tags=["quotes"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


def _next_quote_number(db) -> str:
    row = fetchone(db, "SELECT value FROM system_settings WHERE key='quote_number_next'")
    prefix_row = fetchone(db, "SELECT value FROM system_settings WHERE key='quote_number_prefix'")
    n = int(row["value"]) if row else 1001
    prefix = prefix_row["value"] if prefix_row else "SGE"
    execute(db, "INSERT INTO system_settings(key,value) VALUES('quote_number_next',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (n + 1,))
    return f"{prefix}-{n}"


@router.get("", response_class=HTMLResponse)
async def list_quotes(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    quotes = fetchall(db, """
        SELECT q.*, cl.name as client_name, co.name as country_name, cu.code as currency_code
        FROM quotes q JOIN clients cl ON cl.id=q.client_id
        JOIN countries co ON co.id=q.country_id JOIN currencies cu ON cu.id=q.currency_id
        ORDER BY q.created_at DESC LIMIT 100
    """)
    return templates.TemplateResponse("quotes/list.html", {
        **_ctx(request, uid, db), "quotes": [dict(q) for q in quotes],
    })


@router.get("/new", response_class=HTMLResponse)
async def new_quote_get(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    clients = fetchall(db, "SELECT id, name FROM clients WHERE is_active=1 ORDER BY name")
    countries = fetchall(db, "SELECT id, name FROM countries ORDER BY name")
    currencies = fetchall(db, "SELECT id, code, name FROM currencies WHERE is_active=1 ORDER BY code")
    return templates.TemplateResponse("quotes/step1_client.html", {
        **_ctx(request, uid, db),
        "clients": [dict(c) for c in clients],
        "countries": [dict(c) for c in countries],
        "currencies": [dict(c) for c in currencies],
    })


@router.post("/new")
async def new_quote_post(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    form = await request.form()
    client_id = int(form["client_id"])
    country_id = int(form["country_id"])
    currency_id = int(form["currency_id"])
    quote_number = _next_quote_number(db)
    execute(db,
        "INSERT INTO quotes(quote_number,client_id,country_id,currency_id,created_by) VALUES(?,?,?,?,?)",
        (quote_number, client_id, country_id, currency_id, uid),
    )
    quote_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.commit()
    return RedirectResponse(url=f"/quotes/{quote_id}/items", status_code=302)


@router.get("/{quote_id}/items", response_class=HTMLResponse)
async def quote_items_get(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    quote = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    items = fetchall(db, """
        SELECT li.*, p.name as product_name, q.name as quality_name, ps.display_name as package_name
        FROM quote_line_items li JOIN products p ON p.id=li.product_id
        JOIN qualities q ON q.id=li.quality_id JOIN package_sizes ps ON ps.id=li.package_size_id
        WHERE li.quote_id=?
    """, (quote_id,))
    products = fetchall(db, "SELECT id, name FROM products WHERE is_active=1 ORDER BY name")
    package_sizes = fetchall(db, "SELECT id, display_name FROM package_sizes ORDER BY weight_grams")
    all_qualities = fetchall(db,
        "SELECT id, product_id, name FROM qualities ORDER BY product_id, sort_order"
    )
    qualities_by_product = {}
    for q in all_qualities:
        pid = str(q["product_id"])
        qualities_by_product.setdefault(pid, []).append({"id": q["id"], "name": q["name"]})
    return templates.TemplateResponse("quotes/step2_items.html", {
        **_ctx(request, uid, db),
        "quote": dict(quote), "items": [dict(i) for i in items],
        "products": [dict(p) for p in products],
        "package_sizes": [dict(s) for s in package_sizes],
        "qualities_json": json.dumps(qualities_by_product),
    })


@router.post("/{quote_id}/items/add")
async def add_line_item(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    form = await request.form()
    product_id = int(form["product_id"])
    quality_id = int(form["quality_id"])
    package_size_id = int(form["package_size_id"])
    quantity_kg = float(form["quantity_kg"])
    label_sides = int(form.get("label_sides", 1))

    quote = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    sanitization_type = resolve_sanitization(quote["country_id"], product_id, db)

    vp = fetchone(db,
        "SELECT price_per_kg FROM vendor_prices WHERE product_id=? AND quality_id=? ORDER BY created_at DESC LIMIT 1",
        (product_id, quality_id),
    )
    vendor_price = vp["price_per_kg"] if vp else 0.0

    costs = calculate_line_costs(
        product_id=product_id, quality_id=quality_id, package_size_id=package_size_id,
        quantity_kg=quantity_kg, sanitization_type=sanitization_type,
        certifications=[], label_sides=label_sides,
        vendor_price_per_kg=vendor_price,
        cha_allocated_inr=0, customs_allocated_inr=0,
        db=db,
    )
    margin_result = calculate_margin(
        cost_per_kg_inr=costs["per_kg_inr"],
        client_id=quote["client_id"], country_id=quote["country_id"],
        product_id=product_id,
        context={"volume_kg": quantity_kg, "advance_pct": 30, "client_order_count": 1,
                 "competition_level": 2, "price_volatility_pct": 1, "urgency_days": 1},
        db=db,
    )

    fx_result = None
    if quote["currency_id"]:
        try:
            fx_result = convert_inr_to_fx(margin_result["selling_price_per_kg_inr"], quote["currency_id"], db)
        except ValueError:
            pass

    cbm = calculate_cbm(package_size_id, costs["num_cartons"], quantity_kg, db)

    execute(db, """
        INSERT INTO quote_line_items(
            quote_id, product_id, quality_id, package_size_id, quantity_kg,
            sanitization_type, label_sides, vendor_price_per_kg,
            raw_material_inr, labour_inr, packaging_inr, sanitization_inr,
            certification_inr, loading_inr, transport_inr, subtotal_inr,
            cost_per_kg_inr, margin_pct, selling_price_per_kg_inr,
            selling_price_fx, fx_rate_used, cbm_per_carton, num_cartons, total_cbm
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        quote_id, product_id, quality_id, package_size_id, quantity_kg,
        sanitization_type, label_sides, vendor_price,
        costs["raw_material_inr"], costs["labour_inr"], costs["packaging_inr"],
        costs["sanitization_inr"], costs["certification_inr"],
        costs["loading_inr"], costs["transport_inr"], costs["subtotal_inr"],
        costs["per_kg_inr"], margin_result["margin_pct"],
        margin_result["selling_price_per_kg_inr"],
        fx_result["fx_amount"] if fx_result else 0,
        fx_result["rate_used"] if fx_result else 1,
        cbm["cbm_per_carton"], costs["num_cartons"], cbm["total_cbm"],
    ))
    db.commit()
    return RedirectResponse(url=f"/quotes/{quote_id}/items", status_code=302)


@router.get("/{quote_id}/review", response_class=HTMLResponse)
async def quote_review(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    quote = fetchone(db, """
        SELECT q.*, cl.name as client_name, co.name as country_name, cu.code as currency_code
        FROM quotes q JOIN clients cl ON cl.id=q.client_id
        JOIN countries co ON co.id=q.country_id JOIN currencies cu ON cu.id=q.currency_id
        WHERE q.id=?
    """, (quote_id,))
    items = fetchall(db, """
        SELECT li.*, p.name as product_name, q.name as quality_name, ps.display_name as package_name
        FROM quote_line_items li JOIN products p ON p.id=li.product_id
        JOIN qualities q ON q.id=li.quality_id JOIN package_sizes ps ON ps.id=li.package_size_id
        WHERE li.quote_id=?
    """, (quote_id,))

    items_list = [dict(i) for i in items]
    for item in items_list:
        stale = check_price_stale(item["product_id"], item["quality_id"], db)
        item["is_stale"] = stale["is_stale"]
        item["price_age_days"] = stale["age_days"]
        try:
            item["is_overridden"] = json.loads(item.get("is_overridden") or "{}")
        except (TypeError, ValueError):
            item["is_overridden"] = {}

    any_stale = any(i["is_stale"] for i in items_list)
    total_cbm = sum(i["total_cbm"] or 0 for i in items_list)
    total_kg = sum(i["quantity_kg"] or 0 for i in items_list)
    container_rec = recommend_container(total_cbm, total_kg, db) if items_list else None

    stale_error = request.query_params.get("stale_error")
    return templates.TemplateResponse("quotes/step3_review.html", {
        **_ctx(request, uid, db),
        "quote": dict(quote), "items": items_list,
        "any_stale": any_stale, "container_rec": container_rec,
        "stale_error": stale_error,
    })


@router.post("/{quote_id}/confirm")
async def confirm_quote(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    form = await request.form()
    stale_override_reason = str(form.get("stale_override_reason", "")).strip()

    items = fetchall(db, "SELECT product_id, quality_id FROM quote_line_items WHERE quote_id=?", (quote_id,))
    has_stale = any(check_price_stale(i["product_id"], i["quality_id"], db)["is_stale"] for i in items)

    if has_stale and not stale_override_reason:
        return RedirectResponse(url=f"/quotes/{quote_id}/review?stale_error=1", status_code=302)

    execute(db, """
        UPDATE quotes SET status='confirmed', confirmed_at=datetime('now'),
        has_stale_override=?, stale_override_reason=? WHERE id=?
    """, (1 if stale_override_reason else 0, stale_override_reason or None, quote_id))
    db.commit()
    return RedirectResponse(url=f"/quotes/{quote_id}/export", status_code=302)


@router.get("/{quote_id}/export", response_class=HTMLResponse)
async def export_options(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.export", db)
    quote = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    return templates.TemplateResponse("quotes/step4_confirm.html", {
        **_ctx(request, uid, db), "quote": dict(quote),
    })


@router.post("/{quote_id}/duplicate")
async def duplicate_quote(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    original = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    new_number = _next_quote_number(db)
    execute(db,
        "INSERT INTO quotes(quote_number,client_id,country_id,currency_id,created_by,parent_quote_id) VALUES(?,?,?,?,?,?)",
        (new_number, original["client_id"], original["country_id"], original["currency_id"], uid, quote_id),
    )
    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    old_items = fetchall(db, "SELECT * FROM quote_line_items WHERE quote_id=?", (quote_id,))
    for item in old_items:
        execute(db, """
            INSERT INTO quote_line_items(quote_id,product_id,quality_id,package_size_id,quantity_kg,
                sanitization_type,label_sides,vendor_price_per_kg,raw_material_inr,labour_inr,
                packaging_inr,sanitization_inr,certification_inr,loading_inr,transport_inr,
                subtotal_inr,cost_per_kg_inr,margin_pct,selling_price_per_kg_inr,
                selling_price_fx,fx_rate_used,cbm_per_carton,num_cartons,total_cbm)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (new_id, item["product_id"], item["quality_id"], item["package_size_id"],
              item["quantity_kg"], item["sanitization_type"], item["label_sides"],
              item["vendor_price_per_kg"], item["raw_material_inr"], item["labour_inr"],
              item["packaging_inr"], item["sanitization_inr"], item["certification_inr"],
              item["loading_inr"], item["transport_inr"], item["subtotal_inr"],
              item["cost_per_kg_inr"], item["margin_pct"], item["selling_price_per_kg_inr"],
              item["selling_price_fx"], item["fx_rate_used"], item["cbm_per_carton"],
              item["num_cartons"], item["total_cbm"]))
    db.commit()
    return RedirectResponse(url=f"/quotes/{new_id}/items", status_code=302)
