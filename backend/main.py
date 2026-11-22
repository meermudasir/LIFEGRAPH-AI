import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db, SessionLocal
from backend.services.graph_service import GraphService
from backend.api import (
    dashboard_router,
    graph_router,
    vector_router,
    query_router,
    intelligence_router,
    analytics_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lifegraph-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    - Runs on startup: Initializes database tables and seeds demo data if empty.
    - Runs on shutdown: Cleanly closes resources.
    """
    logger.info("Initializing LifeGraph AI Backend...")
    try:
        init_db()
        logger.info("Database tables verified and initialized.")

        db = SessionLocal()
        try:
            GraphService.seed_sample_data_if_empty(db)
            logger.info("Initial sample dataset verified/seeded into database.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during startup database initialization: {e}", exc_info=True)

    yield

    logger.info("Shutting down LifeGraph AI Backend.")


# Initialize FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "LifeGraph AI – Connected Intelligence Platform\n\n"
        "Graph Analytics • Vector Search • AI Intelligence\n\n"
        "An enterprise-inspired Graph and Vector analytics platform offering high-performance "
        "topological traversals, semantic text similarity search, and explainable graph AI."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred while processing the graph request.",
            "detail": str(exc) if settings.DEBUG else "Internal server error",
            "path": request.url.path,
        },
    )


# ------------------------------------------------------------------------------
# CORE APPLICATION ENDPOINTS
# ------------------------------------------------------------------------------

@app.get("/", tags=["System"])
def root():
    """Root platform entry point."""
    return {
        "name": settings.APP_NAME,
        "tagline": "Graph Analytics • Vector Search • AI Intelligence",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"], include_in_schema=False)
@app.get("/api/v1/health", tags=["System"], include_in_schema=False)
def health_check():
    """Health check endpoint for container probes and load balancers."""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "graph_engine": "NetworkX ready",
        "vector_engine": "TF-IDF index ready",
    }


# ------------------------------------------------------------------------------
# ROUTER REGISTRATION
# Mounted under both /api and /api/v1 for full frontend and REST compatibility
# ------------------------------------------------------------------------------

api_routers = [
    dashboard_router,
    graph_router,
    vector_router,
    query_router,
    intelligence_router,
    analytics_router,
]

for router in api_routers:
    app.include_router(router, prefix="/api")
    app.include_router(router, prefix="/api/v1", include_in_schema=False)
