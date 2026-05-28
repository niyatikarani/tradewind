import sqlite3
import bcrypt
from fastapi import Request, HTTPException
from .db import fetchone, fetchall


class AuthRedirect(Exception):
    def __init__(self, redirect_to: str = "/login"):
        self.redirect_to = redirect_to


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def get_current_user_id(request: Request) -> int | None:
    return request.session.get("user_id")


def require_user(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise AuthRedirect("/login")
    return user_id


def check_feature(user_id: int, feature_key: str, db: sqlite3.Connection) -> bool:
    row = fetchone(
        db,
        """
        SELECT 1 FROM user_features uf
        JOIN features f ON f.id = uf.feature_id
        WHERE uf.user_id = ? AND f.key = ?
        """,
        (user_id, feature_key),
    )
    return row is not None


def require_feature(request: Request, feature_key: str, db: sqlite3.Connection) -> None:
    user_id = require_user(request)
    if not check_feature(user_id, feature_key, db):
        raise HTTPException(status_code=403, detail="Access denied")


def get_user_context(user_id: int, db: sqlite3.Connection) -> dict:
    user = fetchone(db, "SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    if not user:
        return {}
    features = fetchall(
        db,
        """
        SELECT f.key FROM user_features uf
        JOIN features f ON f.id = uf.feature_id
        WHERE uf.user_id = ?
        """,
        (user_id,),
    )
    return {
        "user": dict(user),
        "user_features": {row["key"] for row in features},
    }
