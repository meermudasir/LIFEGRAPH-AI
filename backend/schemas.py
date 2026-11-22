from datetime import datetime as DateTime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------
# GRAPH NODES & EDGES SCHEMAS
# ------------------------------------------------------------------------------

class NodeBase(BaseModel):
    id: str = Field(..., max_length=64, description="Unique node identifier")
    label: str = Field(..., max_length=128, description="Display name or entity label")
    category: str = Field(..., max_length=64, description="Node category, e.g. Person, Organization")
    uri: str = Field(..., max_length=256, description="Unique Resource Identifier / URN")
    description: Optional[str] = Field(None, description="Detailed text description for search")
    vector_weight: float = Field(0.5, ge=0.0, le=1.0, description="Vector embedding priority weight")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata dictionary")


class NodeCreate(NodeBase):
    pass


class NodeResponse(NodeBase):
    created_at: Optional[DateTime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class EdgeBase(BaseModel):
    id: str = Field(..., max_length=64, description="Unique edge identifier")
    source: str = Field(..., max_length=64, description="Source node ID")
    target: str = Field(..., max_length=64, description="Target node ID")
    label: str = Field("RELATED_TO", max_length=64, description="Relationship type")
    weight: float = Field(1.0, ge=0.0, description="Relationship strength/weight")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EdgeCreate(EdgeBase):
    pass


class EdgeResponse(EdgeBase):
    created_at: Optional[DateTime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class GraphResponse(BaseModel):
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]
    total_nodes: int
    total_edges: int


class NodeDetailResponse(BaseModel):
    node: NodeResponse
    degree: int
    in_degree: int
    out_degree: int
    degree_centrality: float
    neighbors: List[NodeResponse]


class KHopResponse(BaseModel):
    root_node: NodeResponse
    hops: int
    direction: str
    discovered_nodes: List[NodeResponse]
    connecting_edges: List[EdgeResponse]
    total_vertices: int
    total_edges: int
    traversal_latency_ms: float


# ------------------------------------------------------------------------------
# VECTOR SEARCH SCHEMAS
# ------------------------------------------------------------------------------

class VectorSearchRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=512, description="Semantic text query")
    prompt: Optional[str] = Field(None, max_length=512, description="Alternative alias for query")
    top_k: int = Field(10, ge=1, le=100, description="Maximum results to return")
    threshold: float = Field(0.80, ge=0.0, le=1.0, description="Minimum similarity score")
    metric: str = Field("cosine", description="Distance metric: cosine, euclidean, dot")

    def get_query(self) -> str:
        return (self.query or self.prompt or "").strip()


class VectorMatchItem(BaseModel):
    id: str
    title: str
    uri: str
    category: str
    snippet: str
    similarity_score: float
    distance: float


class VectorSearchResponse(BaseModel):
    query: str
    engine: str = "TF-IDF Baseline with Cosine Similarity"
    threshold: float
    metric: str
    execution_time_sec: float
    total_matches: int
    indexed_documents_count: int
    results: List[VectorMatchItem]


class VectorStatusResponse(BaseModel):
    status: str
    engine_name: str
    indexed_documents: int
    vocabulary_size: int
    vector_dimension: int
    last_indexed_at: Optional[DateTime] = None


# ------------------------------------------------------------------------------
# QUERY CONSOLE SCHEMAS
# ------------------------------------------------------------------------------

class QueryExecuteRequest(BaseModel):
    query: str = Field(..., max_length=4096, description="Gremlin, SPARQL, or Cypher query string")
    dialect: str = Field("gremlin", description="Dialect: gremlin, sparql, or cypher")
    limit: int = Field(50, ge=1, le=1000, description="Max rows returned")


class QueryRecordItem(BaseModel):
    index: int
    entity_id: str
    label: str
    properties: str
    connected_nodes: str
    vector_weight: float


class QueryExecuteResponse(BaseModel):
    status: str
    dialect: str
    execution_time_ms: float
    row_count: int
    records: List[QueryRecordItem]
    engine_note: str = "Executed via LifeGraph Prototype Safe AST Query Engine"


# ------------------------------------------------------------------------------
# DASHBOARD SCHEMAS
# ------------------------------------------------------------------------------

class DashboardStatsResponse(BaseModel):
    total_nodes: int
    total_relationships: int
    total_data_sources: int
    total_queries: int
    total_patterns: int
    vector_embeddings: int
    system_status: str
    neptune_cluster: str
    dual_region_replication: bool


class ActivityItem(BaseModel):
    id: int
    bullet_color: str
    action: str
    actor: str
    timestamp: str
    datetime: Optional[DateTime] = None


class ActivityResponse(BaseModel):
    activities: List[ActivityItem]


# ------------------------------------------------------------------------------
# AI INTELLIGENCE SCHEMAS
# ------------------------------------------------------------------------------

class PatternItem(BaseModel):
    id: str
    pattern_type: str
    description: str
    confidence: float
    evidence: str
    participating_nodes: List[str]


class PatternDiscoveryResponse(BaseModel):
    total_motifs: int
    patterns: List[PatternItem]
    method: str = "Graph Motif Mining & Clique Detection"


class AnomalyItem(BaseModel):
    id: str
    target_entity: str
    anomaly_type: str
    severity: str
    score: float
    explanation: str
    evidence: str


class AnomalyDetectionResponse(BaseModel):
    total_anomalies: int
    anomalies: List[AnomalyItem]
    method: str = "Z-Score Degree Outlier & Structural Isolation Detection"


class RiskAnalysisRequest(BaseModel):
    simulation_runs: int = Field(1000, ge=100, le=10000)
    target_subgraph: Optional[str] = None


class RiskAnalysisResponse(BaseModel):
    systemic_risk_score: float
    risk_level: str
    fragility_index: float
    cut_vertices_count: int
    critical_bridges_count: int
    simulation_runs: int
    evidence: str


class InsightItem(BaseModel):
    id: str
    category: str
    title: str
    recommendation: str
    confidence: float
    impact: str
    structural_evidence: str


class InsightsResponse(BaseModel):
    total_insights: int
    insights: List[InsightItem]


# ------------------------------------------------------------------------------
# ANALYTICS SCHEMAS
# ------------------------------------------------------------------------------

class AnalyticsOverviewResponse(BaseModel):
    total_nodes: int
    total_edges: int
    density: float
    average_degree: float
    connected_components: int
    largest_component_size: int
    storage_allocated_gb: float
    active_queries_qps: float


class QueryMetricsResponse(BaseModel):
    p50_latency_ms: float
    p90_latency_ms: float
    p99_latency_ms: float
    peak_qps: float
    current_qps: float
    read_ratio: float
    write_ratio: float
    timeline_labels: List[str]
    timeline_p99: List[float]
    timeline_p50: List[float]


class StorageMetricsResponse(BaseModel):
    graph_db_gb: float
    vector_index_gb: float
    wal_cache_gb: float
    total_capacity_gb: float
    utilization_percentage: float