"""Longevity Clinical Intervention Model - Backend API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.api import interventions, evidence, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Cleanup if needed
    pass


app = FastAPI(
    title="长寿医学临床干预模型 API",
    description="基于科学证据的长寿医学临床干预模型系统",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interventions.router, prefix="/api/v1/interventions", tags=["干预措施"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["证据"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["推荐"])


@app.get("/")
async def root():
    return {
        "message": "长寿医学临床干预模型 API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
