import logging
from contextlib import asynccontextmanager
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .config import JWT_AUDIENCE, JWT_ISSUER, JWT_KEY
from .database import Base, engine, get_db
from .schemas import LoginRequest, RegisterRequest
from .services import auth_service, dashboard_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # odpowiednik EnsureCreated()
    yield


app = FastAPI(title="Smart Travel API", version="v1", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _dump(model) -> dict:
    return model.model_dump(by_alias=True, mode="json")


def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    """Walidacja JWT Bearer – odpowiednik [Authorize]."""
    from fastapi import HTTPException

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Brak autoryzacji.")
    try:
        payload = jwt.decode(
            authorization[7:].strip(), JWT_KEY, algorithms=["HS256"],
            audience=JWT_AUDIENCE, issuer=JWT_ISSUER,
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Nieprawidłowy token.")


# ----------------------------- Auth -----------------------------

def _base_url(request: Request) -> str:
    return f"{request.url.scheme}://{request.headers.get('host', request.url.netloc)}"


@app.post("/api/auth/register")
def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    result = auth_service.register(db, body, _base_url(request))
    return JSONResponse(_dump(result), status_code=200 if result.success else 400)


@app.get("/api/auth/confirm-email")
def confirm_email(token: str = Query(default=""), db: Session = Depends(get_db)):
    result = auth_service.confirm_email(db, token)
    return JSONResponse(_dump(result), status_code=200 if result.success else 400)


@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, body)
    return JSONResponse(_dump(result), status_code=200 if result.success else 401)


@app.get("/api/auth/me")
def me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    profile = auth_service.get_user_profile(db, user_id)
    if profile is None:
        return JSONResponse({"message": "Nie znaleziono profilu."}, status_code=404)
    return _dump(profile)


# --------------------------- Dashboard ---------------------------

@app.get("/api/dashboard/destination")
async def destination(
    country: str = "Poland",
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    data = await dashboard_service.get_dashboard_data(db, country, user_id)
    return _dump(data)


@app.get("/api/dashboard/history")
def history(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return [_dump(h) for h in dashboard_service.get_search_history(db, user_id)]


# ------------------------- Frontend (static) -------------------------

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


for _sub in ("css", "js", "fonts"):
    app.mount(f"/{_sub}", StaticFiles(directory=STATIC_DIR / _sub), name=_sub)
