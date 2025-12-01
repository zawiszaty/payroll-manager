from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting application lifespan...")

    from app.shared.infrastructure.rabbitmq import get_rabbitmq_publisher

    publisher = get_rabbitmq_publisher()
    await publisher.connect()
    logger.info("RabbitMQ publisher initialized")

    yield

    logger.info("Shutting down application...")
    await publisher.close()


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

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payroll-manager"}


@app.get("/")
async def root():
    return {"message": "Payroll Manager API", "version": settings.VERSION}
