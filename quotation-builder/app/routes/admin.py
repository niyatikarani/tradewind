import sqlite3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import get_db, fetchall, fetchone, execute
from ..auth import require_user, require_feature, get_user_context, hash_password
from ..templates_cfg import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def _ctx(request, user_id, db):
    return {"request": request, **get_user_context(user_id, db)}


@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.users", db)
    users = fetchall(db, "SELECT id, name, email, is_active FROM users ORDER BY name")
    return templates.TemplateResponse("admin/users.html", {
        **_ctx(request, uid, db),
        "users": [dict(u) for u in users],
    })


@router.get("/users/new", response_class=HTMLResponse)
async def new_user_form(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.users", db)
    features = fetchall(db, "SELECT * FROM features ORDER BY category, label")
    templates_list = fetchall(db, "SELECT * FROM feature_templates ORDER BY name")
    return templates.TemplateResponse("admin/user_edit.html", {
        **_ctx(request, uid, db),
        "edit_user": None,
        "features": [dict(f) for f in features],
        "feature_templates": [dict(t) for t in templates_list],
        "assigned_feature_ids": [],
    })


@router.post("/users/new")
async def create_user(request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.users", db)
    form = await request.form()
    name = str(form.get("name", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))
    feature_ids = form.getlist("feature_ids")

    pw_hash = hash_password(password)
    execute(db, "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)", (name, email, pw_hash))
    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    for fid in feature_ids:
        execute(db, "INSERT OR IGNORE INTO user_features(user_id,feature_id) VALUES(?,?)", (new_id, int(fid)))
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(user_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.users", db)
    edit_user = fetchone(db, "SELECT * FROM users WHERE id=?", (user_id,))
    features = fetchall(db, "SELECT * FROM features ORDER BY category, label")
    templates_list = fetchall(db, "SELECT * FROM feature_templates ORDER BY name")
    assigned = fetchall(db, "SELECT feature_id FROM user_features WHERE user_id=?", (user_id,))
    assigned_ids = [r["feature_id"] for r in assigned]
    return templates.TemplateResponse("admin/user_edit.html", {
        **_ctx(request, uid, db),
        "edit_user": dict(edit_user),
        "features": [dict(f) for f in features],
        "feature_templates": [dict(t) for t in templates_list],
        "assigned_feature_ids": assigned_ids,
    })


@router.post("/users/{user_id}/edit")
async def update_user(user_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    uid = require_user(request)
    require_feature(request, "admin.users", db)
    form = await request.form()
    name = str(form.get("name", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    is_active = 1 if form.get("is_active") else 0
    feature_ids = form.getlist("feature_ids")

    execute(db, "UPDATE users SET name=?,email=?,is_active=? WHERE id=?", (name, email, is_active, user_id))
    execute(db, "DELETE FROM user_features WHERE user_id=?", (user_id,))
    for fid in feature_ids:
        execute(db, "INSERT OR IGNORE INTO user_features(user_id,feature_id) VALUES(?,?)", (user_id, int(fid)))
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)
