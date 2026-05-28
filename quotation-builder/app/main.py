from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .auth import AuthRedirect
from .db import init_app_db
from .routes import auth as auth_router
from .routes import admin as admin_router
from .routes import master_data as master_data_router
from .routes import prices as prices_router
from .routes import quotes as quotes_router
from .routes import uploads as uploads_router
from .routes import overrides as overrides_router
from .routes import rule_engine as rule_engine_router
from .routes import analytics as analytics_router
from .routes import exports as exports_router
from .templates_cfg import templates  # noqa: F401 — ensures templates module initialised

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not Path(settings.database_path).exists():
        init_app_db()
    yield


app = FastAPI(title="S&G Exports Quotation Builder", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, max_age=settings.session_max_age)
app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "static")), name="static")


@app.exception_handler(AuthRedirect)
async def auth_redirect_handler(request: Request, exc: AuthRedirect):
    return RedirectResponse(url=exc.redirect_to, status_code=302)


app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(master_data_router.router)
app.include_router(prices_router.router)
app.include_router(quotes_router.router)
app.include_router(uploads_router.router)
app.include_router(overrides_router.router)
app.include_router(rule_engine_router.router)
app.include_router(analytics_router.router)
app.include_router(exports_router.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/quotes", status_code=302)
