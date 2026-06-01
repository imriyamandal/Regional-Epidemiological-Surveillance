from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.database.base import Base
from app.database.models import Disease, User, UserRole
from app.database.session import AsyncSessionLocal, engine
from app.services.prediction_service import PredictionService

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@dopewis.health"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@dopewis.health",
                hashed_password=get_password_hash("Admin@12345"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
            )
            db.add(admin)
        diseases = [
            ("DENGUE", "Dengue Fever", "Vector-borne"),
            ("MALARIA", "Malaria", "Vector-borne"),
            ("CHOLERA", "Cholera", "Waterborne"),
            ("CHIKUNGUNYA", "Chikungunya", "Vector-borne"),
            ("AES", "Acute Encephalitis Syndrome", "Neurological"),
            ("ADD", "Acute Diarrheal Disease", "Waterborne"),
        ]
        for code, name, cat in diseases:
            exists = await db.execute(select(Disease).where(Disease.code == code))
            if not exists.scalar_one_or_none():
                db.add(Disease(code=code, name=name, category=cat, is_notifiable=True))
        await db.commit()
    PredictionService.load_models()
    yield
    await engine.dispose()


app = FastAPI(
    title="DOPEWIS API",
    description="Disease Outbreak Prediction & Early Warning Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
@limiter.limit("60/minute")
async def health(request: Request):
    return {"status": "healthy", "service": settings.app_name}


app.include_router(api_router, prefix=settings.api_v1_prefix)
