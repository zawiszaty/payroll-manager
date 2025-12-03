from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.modules.auth.infrastructure.middleware import AuthContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting application lifespan...")

    yield

    logger.info("Shutting down application...")


settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication context middleware
app.add_middleware(AuthContextMiddleware)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payroll-manager"}


@app.get("/")
async def root():
    return {"message": "Payroll Manager API", "version": settings.VERSION}
