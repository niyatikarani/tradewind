import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import get_db, fetchall, fetchone, execute
from ..auth import require_user, require_feature, get_user_context
from ..services.stale_checker import check_items_stale
from ..templates_cfg import templates

router = APIRouter(prefix="/prices", tags=["prices"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


@router.get("/entry", response_class=HTMLResponse)
async def price_entry_get(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.entry", db)
    products = fetchall(db, "SELECT * FROM products WHERE is_active=1 ORDER BY name")
    all_qualities = fetchall(db,
        "SELECT id, product_id, name FROM qualities ORDER BY product_id, sort_order"
    )
    import json as _json
    qualities_by_product = {}
    for q in all_qualities:
        pid = str(q["product_id"])
        qualities_by_product.setdefault(pid, []).append({"id": q["id"], "name": q["name"]})
    return templates.TemplateResponse("prices/entry.html", {
        **_ctx(request, uid, db),
        "products": [dict(p) for p in products],
        "qualities_json": _json.dumps(qualities_by_product),
        "success": request.query_params.get("success"),
    })


@router.post("/entry")
async def price_entry_post(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.entry", db)
    form = await request.form()
    product_id = int(form["product_id"])
    quality_id = int(form["quality_id"])
    price_per_kg = float(form["price_per_kg"])
    vendor_name = str(form.get("vendor_name", "")).strip()

    execute(db,
        "INSERT INTO vendor_prices(product_id,quality_id,price_per_kg,vendor_name,entered_by) VALUES(?,?,?,?,?)",
        (product_id, quality_id, price_per_kg, vendor_name, uid),
    )
    db.commit()
    return RedirectResponse(url="/prices/entry?success=1", status_code=302)


@router.get("/qualities/{product_id}", response_class=HTMLResponse)
async def get_qualities(product_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    require_user(request)
    qualities = fetchall(db, "SELECT id, name FROM qualities WHERE product_id=? ORDER BY sort_order", (product_id,))
    opts = "".join(f'<option value="{q["id"]}">{q["name"]}</option>' for q in qualities)
    return HTMLResponse(f'<select name="quality_id" class="form-select">{opts}</select>')


@router.get("/bulk", response_class=HTMLResponse)
async def bulk_entry_get(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.bulk", db)
    products = fetchall(db,
        "SELECT p.*, GROUP_CONCAT(q.id||':'||q.name,'|') as qualities "
        "FROM products p LEFT JOIN qualities q ON q.product_id=p.id "
        "WHERE p.is_active=1 GROUP BY p.id ORDER BY p.name"
    )
    saved = request.query_params.get("saved")
    return templates.TemplateResponse("prices/bulk.html", {
        **_ctx(request, uid, db),
        "products": [dict(p) for p in products],
        "saved": saved,
    })


@router.post("/bulk")
async def bulk_entry_post(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.bulk", db)
    form = await request.form()
    inserted = 0
    for key, value in form.items():
        if key.startswith("price_") and value:
            parts = key.split("_")
            if len(parts) == 3:
                _, product_id, quality_id = parts
                execute(db,
                    "INSERT INTO vendor_prices(product_id,quality_id,price_per_kg,entered_by) VALUES(?,?,?,?)",
                    (int(product_id), int(quality_id), float(value), uid),
                )
                inserted += 1
    db.commit()
    return RedirectResponse(url=f"/prices/bulk?saved={inserted}", status_code=302)


@router.get("/stale", response_class=HTMLResponse)
async def stale_dashboard(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.stale", db)
    combos = fetchall(db, """
        SELECT DISTINCT p.id as product_id, q.id as quality_id,
               p.name as product_name, q.name as quality_name
        FROM products p JOIN qualities q ON q.product_id=p.id
        WHERE p.is_active=1 ORDER BY p.name, q.name
    """)
    items = [{"product_id": r["product_id"], "quality_id": r["quality_id"],
              "product_name": r["product_name"], "quality_name": r["quality_name"]} for r in combos]
    stale_results = check_items_stale(items, db)
    return templates.TemplateResponse("prices/stale.html", {
        **_ctx(request, uid, db), "items": stale_results,
    })


@router.get("/trends", response_class=HTMLResponse)
async def price_trends(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.trends", db)
    products = fetchall(db, "SELECT id, name FROM products WHERE is_active=1 ORDER BY name")
    product_id = request.query_params.get("product_id")
    quality_id = request.query_params.get("quality_id")
    chart_data = None
    qualities = []
    if product_id:
        qualities = fetchall(db, "SELECT id, name FROM qualities WHERE product_id=? ORDER BY sort_order", (int(product_id),))
    if product_id and quality_id:
        rows = fetchall(db,
            "SELECT price_per_kg, created_at FROM vendor_prices WHERE product_id=? AND quality_id=? ORDER BY created_at DESC LIMIT 30",
            (int(product_id), int(quality_id)),
        )
        chart_data = {
            "labels": [r["created_at"][:10] for r in reversed(rows)],
            "values": [r["price_per_kg"] for r in reversed(rows)],
        }
    return templates.TemplateResponse("prices/trends.html", {
        **_ctx(request, uid, db),
        "products": [dict(p) for p in products],
        "qualities": [dict(q) for q in qualities],
        "selected_product": product_id,
        "selected_quality": quality_id,
        "chart_data": chart_data,
    })


@router.post("/inline-entry", response_class=HTMLResponse)
async def inline_price_entry(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "price.entry", db)
    form = await request.form()
    product_id = int(form["product_id"])
    quality_id = int(form["quality_id"])
    price_per_kg = float(form["price_per_kg"])
    execute(db,
        "INSERT INTO vendor_prices(product_id,quality_id,price_per_kg,entered_by) VALUES(?,?,?,?)",
        (product_id, quality_id, price_per_kg, uid),
    )
    db.commit()
    return HTMLResponse('<div class="alert alert-success py-1">Price saved.</div>')
