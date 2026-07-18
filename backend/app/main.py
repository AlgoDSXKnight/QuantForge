from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="QuantForge API",
    version="0.1.0",
    description="Production-grade Options Pricing Platform",
)

app.include_router(health_router)