import sqlite3
from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pathlib import Path

from ..db import get_db, execute, fetchone
from ..auth import require_user, require_feature, get_user_context
from ..services.excel_parser import parse_order_xlsx
from ..templates_cfg import templates

router = APIRouter(tags=["uploads"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


@router.get("/quotes/template")
async def download_template(request: Request):
    require_user(request)
    template_path = Path(__file__).parent.parent.parent / "order_template.xlsx"
    return FileResponse(str(template_path), filename="order_template.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/quotes/{quote_id}/upload", response_class=HTMLResponse)
async def upload_get(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    quote = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    return templates.TemplateResponse("quotes/upload.html", {
        **_ctx(request, uid, db), "quote": dict(quote),
    })


@router.post("/quotes/{quote_id}/upload", response_class=HTMLResponse)
async def upload_post(quote_id: int, request: Request,
                      file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.create", db)
    contents = await file.read()
    result = parse_order_xlsx(contents, db=db)

    quote = fetchone(db, "SELECT * FROM quotes WHERE id=?", (quote_id,))
    for row in result["valid"]:
        if row["product_id"] and row["quality_id"] and row["package_size_id"]:
            from ..services.cost_engine import calculate_line_costs
            from ..services.margin_engine import calculate_margin
            from ..services.rule_resolver import resolve_sanitization
            from ..services.fx_service import convert_inr_to_fx
            from ..services.cbm_engine import calculate_cbm

            sanit = resolve_sanitization(quote["country_id"], row["product_id"], db)
            vp = db.execute(
                "SELECT price_per_kg FROM vendor_prices WHERE product_id=? AND quality_id=? ORDER BY created_at DESC LIMIT 1",
                (row["product_id"], row["quality_id"])
            ).fetchone()
            vendor_price = vp["price_per_kg"] if vp else 0.0
            costs = calculate_line_costs(
                product_id=row["product_id"], quality_id=row["quality_id"],
                package_size_id=row["package_size_id"], quantity_kg=row["quantity_kg"],
                sanitization_type=sanit, certifications=[], label_sides=1,
                vendor_price_per_kg=vendor_price,
                cha_allocated_inr=0, customs_allocated_inr=0, db=db,
            )
            margin = calculate_margin(costs["per_kg_inr"], quote["client_id"], quote["country_id"], row["product_id"],
                                      {"volume_kg": row["quantity_kg"], "advance_pct": 30, "client_order_count": 1,
                                       "competition_level": 2, "price_volatility_pct": 1, "urgency_days": 1}, db)
            try:
                fx = convert_inr_to_fx(margin["selling_price_per_kg_inr"], quote["currency_id"], db)
                fx_amount, fx_rate = fx["fx_amount"], fx["rate_used"]
            except Exception:
                fx_amount, fx_rate = 0, 1
            cbm = calculate_cbm(row["package_size_id"], costs["num_cartons"], row["quantity_kg"], db)
            execute(db, """
                INSERT INTO quote_line_items(quote_id,product_id,quality_id,package_size_id,quantity_kg,
                    sanitization_type,label_sides,vendor_price_per_kg,raw_material_inr,labour_inr,
                    packaging_inr,sanitization_inr,certification_inr,loading_inr,transport_inr,
                    subtotal_inr,cost_per_kg_inr,margin_pct,selling_price_per_kg_inr,
                    selling_price_fx,fx_rate_used,cbm_per_carton,num_cartons,total_cbm)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (quote_id, row["product_id"], row["quality_id"], row["package_size_id"],
                  row["quantity_kg"], sanit, 1, vendor_price,
                  costs["raw_material_inr"], costs["labour_inr"], costs["packaging_inr"],
                  costs["sanitization_inr"], costs["certification_inr"], costs["loading_inr"],
                  costs["transport_inr"], costs["subtotal_inr"], costs["per_kg_inr"],
                  margin["margin_pct"], margin["selling_price_per_kg_inr"],
                  fx_amount, fx_rate, cbm["cbm_per_carton"], costs["num_cartons"], cbm["total_cbm"]))
    db.commit()

    return templates.TemplateResponse("components/upload_result.html", {
        "request": request,
        "valid": result["valid"], "flagged": result["flagged"], "quote_id": quote_id,
    })
