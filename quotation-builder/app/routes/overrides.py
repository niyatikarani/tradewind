import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from ..db import get_db, fetchall, fetchone
from ..auth import require_user, require_feature
from ..services.override_service import apply_override, reset_override

router = APIRouter(tags=["overrides"])

OVERRIDABLE_FIELDS = [
    "vendor_price_per_kg", "cost_per_kg_inr", "margin_pct",
    "selling_price_per_kg_inr", "selling_price_fx",
]


@router.post("/quotes/{quote_id}/items/{line_id}/override", response_class=HTMLResponse)
async def apply_field_override(quote_id: int, line_id: int, request: Request,
                                db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.manual_override", db)
    form = await request.form()
    field_name = str(form["field_name"])
    override_value = float(form["override_value"])
    reason = str(form["reason"]).strip()
    if field_name not in OVERRIDABLE_FIELDS:
        return HTMLResponse("<div class='alert alert-danger'>Invalid field</div>", status_code=400)
    apply_override(line_id, field_name, override_value, reason, uid, db)
    return HTMLResponse(
        f'<span class="badge bg-warning text-dark">Overridden: {override_value}</span> '
        f'<span class="field-overridden">&#9999;</span>'
    )


@router.post("/quotes/{quote_id}/items/{line_id}/override/reset", response_class=HTMLResponse)
async def reset_field_override(quote_id: int, line_id: int, request: Request,
                                db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.manual_override", db)
    form = await request.form()
    field_name = str(form["field_name"])
    reset_override(line_id, field_name, uid, db)
    item = fetchone(db, f"SELECT {field_name} FROM quote_line_items WHERE id=?", (line_id,))
    val = item[field_name] if item else "—"
    return HTMLResponse(f'<span class="text-muted">Calculated: {val}</span>')


@router.get("/quotes/{quote_id}/items/{line_id}/override-log", response_class=HTMLResponse)
async def override_log(quote_id: int, line_id: int, request: Request,
                        db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.manual_override", db)
    logs = fetchall(db, """
        SELECT fol.*, u.name as user_name FROM field_override_log fol
        JOIN users u ON u.id=fol.user_id
        WHERE fol.quote_line_item_id=? ORDER BY fol.created_at DESC
    """, (line_id,))
    rows = "".join(
        f"<tr><td>{lg['field_name']}</td><td>{lg['original_value']}</td>"
        f"<td>{lg['override_value']}</td><td>{lg['reason']}</td>"
        f"<td>{lg['user_name']}</td><td>{lg['created_at'][:16]}</td></tr>"
        for lg in logs
    )
    return HTMLResponse(
        f"<table class='table table-sm'><thead><tr><th>Field</th><th>Original</th>"
        f"<th>Override</th><th>Reason</th><th>By</th><th>At</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )
