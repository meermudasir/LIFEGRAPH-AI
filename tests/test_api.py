import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.services.graph_service import GraphService

# Setup an isolated in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency in FastAPI
app.dependency_overrides[get_db] = override_get_db

# Create tables and seed test data
Base.metadata.create_all(bind=test_engine)
with TestingSessionLocal() as db:
    GraphService.seed_sample_data_if_empty(db)

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. CORE SYSTEM TESTS
# ------------------------------------------------------------------------------

def test_root_endpoint():
    """Verify root platform information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "LifeGraph AI"
    assert data["status"] == "online"
    assert "tagline" in data


def test_health_endpoint():
    """Verify system health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


# ------------------------------------------------------------------------------
# 2. DASHBOARD API TESTS
# ------------------------------------------------------------------------------

def test_dashboard_stats():
    """Verify aggregated dashboard statistics."""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] > 0
    assert data["total_relationships"] > 0
    assert data["total_data_sources"] >= 0
    assert "system_status" in data


def test_dashboard_activity():
    """Verify platform audit and activity logs."""
    response = client.get("/api/dashboard/activity")
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert isinstance(data["activities"], list)
    assert len(data["activities"]) > 0


# ------------------------------------------------------------------------------
# 3. GRAPH API TESTS
# ------------------------------------------------------------------------------

def test_get_graph_full():
    """Verify full graph retrieval for visualization."""
    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] > 0
    assert data["total_edges"] > 0


def test_get_all_nodes():
    """Verify nodes list retrieval."""
    response = client.get("/api/graph/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert isinstance(nodes, list)
    assert len(nodes) > 0


def test_get_node_by_id():
    """Verify single node retrieval with centrality metrics."""
    response = client.get("/api/graph/nodes/person-turing")
    assert response.status_code == 200
    data = response.json()
    assert data["node"]["id"] == "person-turing"
    assert data["degree"] >= 0
    assert "degree_centrality" in data
    assert isinstance(data["neighbors"], list)


def test_get_node_not_found():
    """Verify 404 response for nonexistent node."""
    response = client.get("/api/graph/nodes/non-existent-entity")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_and_delete_node():
    """Verify creating a node and subsequently deleting it."""
    new_node = {
        "id": "person-curie",
        "label": "Marie Curie",
        "category": "Person",
        "uri": "urn:lifegraph:person:8890",
        "description": "Nobel Laureate in Physics and Chemistry.",
        "vector_weight": 0.95,
        "attributes": {"clearance": "Level 5", "field": "Radioactivity"},
    }

    # 1. Create node
    create_res = client.post("/api/graph/nodes", json=new_node)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["id"] == "person-curie"

    # 2. Duplicate node creation should fail with 409
    dup_res = client.post("/api/graph/nodes", json=new_node)
    assert dup_res.status_code == 409

    # 3. Delete node
    del_res = client.delete("/api/graph/nodes/person-curie")
    assert del_res.status_code == 200
    assert del_res.json()["deleted_node_id"] == "person-curie"

    # 4. Confirm deleted
    get_res = client.get("/api/graph/nodes/person-curie")
    assert get_res.status_code == 404


def test_create_edge():
    """Verify relationship edge creation between two existing vertices."""
    new_edge = {
        "id": "e-turing-lin-collab",
        "source": "person-turing",
        "target": "person-lin",
        "label": "ADVISES",
        "weight": 0.91,
        "attributes": {"mentorship_type": "Doctoral"},
    }
    response = client.post("/api/graph/edges", json=new_edge)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "e-turing-lin-collab"
    assert data["label"] == "ADVISES"


def test_explore_khop():
    """Verify K-Hop neighborhood traversal."""
    response = client.get("/api/graph/explore/hub-root?hops=2&direction=both")
    assert response.status_code == 200
    data = response.json()
    assert data["root_node"]["id"] == "hub-root"
    assert data["hops"] == 2
    assert data["total_vertices"] > 1
    assert data["total_edges"] > 0
    assert data["traversal_latency_ms"] >= 0.0


# ------------------------------------------------------------------------------
# 4. VECTOR SEARCH API TESTS
# ------------------------------------------------------------------------------

def test_vector_status():
    """Verify vector index status report."""
    response = client.get("/api/vector/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "unindexed")
    assert "vocabulary_size" in data


def test_vector_search():
    """Verify semantic similarity vector search."""
    payload = {
        "query": "Quantum graph algorithms and annealing",
        "top_k": 5,
        "threshold": 0.50,
        "metric": "cosine",
    }
    response = client.post("/api/vector/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert isinstance(data["results"], list)
    assert data["total_matches"] >= 0


def test_vector_reindex():
    """Verify vector reindexing trigger."""
    response = client.post("/api/vector/index")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reindexed"


# ------------------------------------------------------------------------------
# 5. QUERY CONSOLE API TESTS
# ------------------------------------------------------------------------------

def test_query_execute_gremlin():
    """Verify Gremlin query simulation."""
    payload = {
        "query": "g.V().hasLabel('Person').outE('COLLABORATES_WITH').inV().path()",
        "dialect": "gremlin",
        "limit": 10,
    }
    response = client.post("/api/query/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["dialect"] == "gremlin"
    assert data["row_count"] > 0
    assert isinstance(data["records"], list)


def test_query_execute_empty_fails():
    """Verify empty query rejection."""
    payload = {"query": "   ", "dialect": "gremlin"}
    response = client.post("/api/query/execute", json=payload)
    assert response.status_code == 400


# ------------------------------------------------------------------------------
# 6. AI INTELLIGENCE API TESTS
# ------------------------------------------------------------------------------

def test_intelligence_patterns():
    """Verify structural pattern and motif discovery."""
    response = client.get("/api/intelligence/patterns")
    assert response.status_code == 200
    data = response.json()
    assert data["total_motifs"] >= 1
    assert "patterns" in data


def test_intelligence_anomalies():
    """Verify anomaly detection output."""
    response = client.get("/api/intelligence/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert isinstance(data["anomalies"], list)


def test_intelligence_risk_analysis():
    """Verify Monte Carlo systemic risk analysis simulation."""
    payload = {"simulation_runs": 500}
    response = client.post("/api/intelligence/risk-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["systemic_risk_score"] <= 100.0
    assert data["risk_level"] in ("Low", "Medium", "High")
    assert "cut_vertices_count" in data


def test_intelligence_insights():
    """Verify synthesized topological insights."""
    response = client.get("/api/intelligence/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["total_insights"] > 0
    assert len(data["insights"]) > 0


# ------------------------------------------------------------------------------
# 7. ANALYTICS API TESTS
# ------------------------------------------------------------------------------

def test_analytics_overview():
    """Verify graph topological analytics overview."""
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] > 0
    assert "density" in data
    assert "average_degree" in data


def test_analytics_query_metrics():
    """Verify query latency and throughput metrics."""
    response = client.get("/api/analytics/query-metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["p50_latency_ms"] > 0
    assert data["p99_latency_ms"] > 0
    assert "timeline_labels" in data


def test_analytics_storage():
    """Verify storage utilization breakdown."""
    response = client.get("/api/analytics/storage")
    assert response.status_code == 200
    data = response.json()
    assert data["graph_db_gb"] > 0
    assert data["total_capacity_gb"] > 0
    assert 0.0 <= data["utilization_percentage"] <= 100.0
