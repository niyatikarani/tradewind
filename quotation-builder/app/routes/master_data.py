import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import get_db, fetchall, execute
from ..auth import require_user, require_feature, get_user_context
from ..templates_cfg import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


@router.get("/products", response_class=HTMLResponse)
async def list_products(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.master_data", db)
    products = fetchall(db, "SELECT * FROM products ORDER BY name")
    return templates.TemplateResponse("admin/master_data.html", {
        **_ctx(request, uid, db),
        "section": "products",
        "items": [dict(p) for p in products],
        "columns": ["name", "category", "competition_level", "is_active"],
    })


@router.post("/products/new")
async def add_product(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.master_data", db)
    form = await request.form()
    execute(db, "INSERT INTO products(name,category,competition_level) VALUES(?,?,?)",
            (form["name"], form["category"], form.get("competition_level", "medium")))
    db.commit()
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/{product_id}/toggle")
async def toggle_product(product_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.master_data", db)
    execute(db, "UPDATE products SET is_active = 1 - is_active WHERE id=?", (product_id,))
    db.commit()
    return RedirectResponse("/admin/products", status_code=302)


@router.get("/package-sizes", response_class=HTMLResponse)
async def list_package_sizes(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.master_data", db)
    sizes = fetchall(db, "SELECT * FROM package_sizes ORDER BY weight_grams")
    return templates.TemplateResponse("admin/master_data.html", {
        **_ctx(request, uid, db),
        "section": "package_sizes",
        "items": [dict(s) for s in sizes],
        "columns": ["display_name", "weight_grams", "is_standard"],
    })


@router.post("/package-sizes/new")
async def add_package_size(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.master_data", db)
    form = await request.form()
    execute(db, "INSERT INTO package_sizes(display_name,weight_grams) VALUES(?,?)",
            (form["display_name"], int(form["weight_grams"])))
    db.commit()
    return RedirectResponse("/admin/package-sizes", status_code=302)
