import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, Response

from ..db import get_db, fetchall, fetchone
from ..auth import require_user, require_feature, get_user_context
from ..services.export_service import export_analytics_xlsx
from ..templates_cfg import templates

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _ctx(request, uid, db):
    return {"request": request, **get_user_context(uid, db)}


@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "analytics.view", db)

    # KPI Cards
    total_quotes = fetchone(db, "SELECT COUNT(*) as n FROM quotes WHERE status='confirmed'")["n"]
    total_revenue_inr = fetchone(db,
        "SELECT COALESCE(SUM(li.subtotal_inr),0) as total FROM quote_line_items li JOIN quotes q ON q.id=li.quote_id WHERE q.status='confirmed'"
    )["total"]
    avg_margin = fetchone(db,
        "SELECT COALESCE(AVG(li.margin_pct),0) as avg FROM quote_line_items li JOIN quotes q ON q.id=li.quote_id WHERE q.status='confirmed'"
    )["avg"]

    # Quotes over time (last 30 days)
    quotes_over_time = fetchall(db, """
        SELECT date(created_at) as day, COUNT(*) as n FROM quotes
        WHERE status='confirmed' GROUP BY day ORDER BY day DESC LIMIT 30
    """)
    quotes_chart = {
        "labels": [r["day"] for r in reversed(quotes_over_time)],
        "values": [r["n"] for r in reversed(quotes_over_time)],
    }

    # Top products by revenue
    top_products = fetchall(db, """
        SELECT p.name, SUM(li.subtotal_inr) as revenue FROM quote_line_items li
        JOIN products p ON p.id=li.product_id
        JOIN quotes q ON q.id=li.quote_id WHERE q.status='confirmed'
        GROUP BY p.id ORDER BY revenue DESC LIMIT 10
    """)

    # Revenue by country
    by_country = fetchall(db, """
        SELECT co.name, SUM(li.subtotal_inr) as revenue FROM quote_line_items li
        JOIN quotes q ON q.id=li.quote_id JOIN countries co ON co.id=q.country_id
        WHERE q.status='confirmed' GROUP BY co.id ORDER BY revenue DESC LIMIT 10
    """)

    return templates.TemplateResponse("analytics/dashboard.html", {
        **_ctx(request, uid, db),
        "total_quotes": total_quotes,
        "total_revenue_inr": round(total_revenue_inr, 2),
        "avg_margin": round(avg_margin, 2),
        "quotes_chart": quotes_chart,
        "top_products": [dict(r) for r in top_products],
        "by_country": [dict(r) for r in by_country],
    })


@router.get("/export/xlsx")
async def export_analytics(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "analytics.export", db)
    rows = fetchall(db, """
        SELECT q.quote_number, cl.name as client, co.name as country,
               cu.code as currency, p.name as product, li.quantity_kg,
               li.cost_per_kg_inr, li.margin_pct, li.selling_price_fx,
               q.created_at
        FROM quote_line_items li
        JOIN quotes q ON q.id=li.quote_id JOIN clients cl ON cl.id=q.client_id
        JOIN countries co ON co.id=q.country_id JOIN currencies cu ON cu.id=q.currency_id
        JOIN products p ON p.id=li.product_id
        WHERE q.status='confirmed' ORDER BY q.created_at DESC
    """)
    columns = ["quote_number", "client", "country", "currency", "product",
               "quantity_kg", "cost_per_kg_inr", "margin_pct", "selling_price_fx", "created_at"]
    xlsx_bytes = export_analytics_xlsx([dict(r) for r in rows], columns)
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=analytics.xlsx"},
    )
