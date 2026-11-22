from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    GraphResponse,
    NodeResponse,
    NodeDetailResponse,
    NodeCreate,
    EdgeResponse,
    EdgeCreate,
    KHopResponse,
)
from backend.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Graph Analytics"])


@router.get("", response_model=GraphResponse)
def get_graph(db: Session = Depends(get_db)):
    """Retrieves all graph nodes and relationships for frontend visualization."""
    return GraphService.get_full_graph(db)


@router.get("/nodes", response_model=List[NodeResponse])
def get_nodes(db: Session = Depends(get_db)):
    """Lists all registered graph entities."""
    return GraphService.get_all_nodes(db)


@router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
def get_node(
    node_id: str = Path(..., description="Node ID or URN"),
    db: Session = Depends(get_db),
):
    """
    Retrieves a single node's detailed attributes, degrees, centrality,
    and immediate connected neighbors.
    """
    return GraphService.get_node_by_id(db, node_id)


@router.get("/neighbors/{node_id}", response_model=List[NodeResponse])
def get_neighbors(
    node_id: str = Path(..., description="Node ID or URN"),
    direction: str = Query("both", regex="^(both|outgoing|incoming)$"),
    db: Session = Depends(get_db),
):
    """Retrieves directly adjacent neighbor nodes."""
    return GraphService.get_neighbors(db, node_id, direction=direction)


@router.get("/explore/{node_id}", response_model=KHopResponse)
def explore_khop(
    node_id: str = Path(..., description="Root Node ID or URN"),
    hops: int = Query(2, ge=1, le=5, description="Neighborhood depth (1-5 hops)"),
    direction: str = Query("both", regex="^(both|outgoing|incoming)$"),
    db: Session = Depends(get_db),
):
    """
    Performs K-Hop BFS neighborhood expansion from a starting root node.
    Returns all discovered nodes and interconnecting edges.
    """
    return GraphService.explore_khop(db, node_id, hops=hops, direction=direction)


# Alias route for frontend script.js /graph/khop compatibility
@router.get("/khop", response_model=KHopResponse, include_in_schema=False)
def explore_khop_alias(
    root: str = Query(..., description="Root Node ID or URN"),
    hops: int = Query(2, ge=1, le=5),
    direction: str = Query("both"),
    db: Session = Depends(get_db),
):
    return GraphService.explore_khop(db, root, hops=hops, direction=direction)


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(node_in: NodeCreate, db: Session = Depends(get_db)):
    """Creates a new graph vertex and updates vector & topological indices."""
    return GraphService.create_node(db, node_in)


@router.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge(edge_in: EdgeCreate, db: Session = Depends(get_db)):
    """Creates a new relationship edge between two existing vertices."""
    return GraphService.create_edge(db, edge_in)


@router.delete("/nodes/{node_id}")
def delete_node(
    node_id: str = Path(..., description="Node ID to remove"),
    db: Session = Depends(get_db),
):
    """Deletes a node and cascades deletion across all connected edges."""
    return GraphService.delete_node(db, node_id)
