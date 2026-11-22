from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import GraphNode, GraphEdge
from backend.schemas import (
    AnalyticsOverviewResponse,
    QueryMetricsResponse,
    StorageMetricsResponse,
)
from backend.core.graph_engine import graph_engine
from backend.core.analytics_engine import AnalyticsEngine

router = APIRouter(prefix="/analytics", tags=["Analytics & Telemetry"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Returns global graph topology analytics, density, component metrics,
    and storage allocation.
    """
    node_count = db.query(GraphNode).count()
    edge_count = db.query(GraphEdge).count()

    metrics = graph_engine.calculate_global_metrics()
    storage = AnalyticsEngine.calculate_storage_breakdown(node_count, edge_count)

    return {
        "total_nodes": node_count,
        "total_edges": edge_count,
        "density": metrics["density"],
        "average_degree": metrics["avg_degree"],
        "connected_components": metrics["components"],
        "largest_component_size": metrics["largest_component_size"],
        "storage_allocated_gb": storage["total_capacity_gb"],
        "active_queries_qps": 1842.6,
    }


@router.get("/query-metrics", response_model=QueryMetricsResponse)
def get_query_metrics(db: Session = Depends(get_db)):
    """
    Returns query execution latency percentiles (P50, P90, P99),
    peak throughput, and time-series performance data for dashboard charts.
    """
    return AnalyticsEngine.calculate_throughput_metrics(total_queries=1842)


@router.get("/storage", response_model=StorageMetricsResponse)
def get_storage_metrics(db: Session = Depends(get_db)):
    """
    Returns storage allocation and capacity utilization across Graph DB,
    Vector Index, and WAL Cache.
    """
    node_count = db.query(GraphNode).count()
    edge_count = db.query(GraphEdge).count()
    return AnalyticsEngine.calculate_storage_breakdown(node_count, edge_count)


# Frontend compatibility alias for script.js endpoint `/analytics/telemetry`
@router.get("/telemetry", response_model=QueryMetricsResponse, include_in_schema=False)
def get_telemetry_alias(db: Session = Depends(get_db)):
    return AnalyticsEngine.calculate_throughput_metrics(total_queries=1842)
