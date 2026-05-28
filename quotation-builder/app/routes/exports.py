import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from ..db import get_db
from ..auth import require_user, require_feature
from ..services.export_service import export_pdf, export_xlsx, export_csv

router = APIRouter(tags=["exports"])


@router.get("/quotes/{quote_id}/export/pdf")
async def quote_pdf(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.export", db)
    pdf_bytes = export_pdf(quote_id, db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=quote-{quote_id}.pdf"},
    )


@router.get("/quotes/{quote_id}/export/xlsx")
async def quote_xlsx(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.export", db)
    xlsx_bytes = export_xlsx(quote_id, db)
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=quote-{quote_id}.xlsx"},
    )


@router.get("/quotes/{quote_id}/export/csv")
async def quote_csv(quote_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "quote.export", db)
    csv_content = export_csv(quote_id, db)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=quote-{quote_id}.csv"},
    )
