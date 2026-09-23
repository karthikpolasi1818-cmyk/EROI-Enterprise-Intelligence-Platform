from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.ingestion import router as ingestion_router
from app.api.advanced_analytics import (
    router as advanced_analytics_router,
)


app = FastAPI(
    title="EROI 2.0",
    description=(
        "Enterprise Revenue & Operations "
        "Intelligence Platform"
    ),
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ingestion_router)
app.include_router(analytics_router)
app.include_router(advanced_analytics_router)


@app.get("/")
def root():
    return {
        "application": "EROI",
        "version": "2.0.0",
        "status": "running",
        "platform": (
            "Enterprise Revenue & "
            "Operations Intelligence Platform"
        ),
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
    }


@app.get("/system")
def system():
    return {
        "platform": "EROI",
        "modules": [
            "Data Ingestion",
            "Data Quality",
            "Semantic Detection",
            "ETL",
            "PostgreSQL Warehouse",
            "Business Analytics",
            "Advanced Analytics",
            "Forecasting",
            "AI Analyst",
        ],
    }