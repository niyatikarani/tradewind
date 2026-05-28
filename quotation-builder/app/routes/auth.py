from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

from ..db import get_db, fetchone
from ..auth import verify_password, get_user_context
from ..templates_cfg import templates

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/quotes", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login")
async def login_post(request: Request, db: sqlite3.Connection = Depends(get_db)):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))

    user = fetchone(db, "SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "error": "Invalid credentials"}, status_code=401
        )

    request.session["user_id"] = user["id"]
    return RedirectResponse(url="/quotes", status_code=302)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
