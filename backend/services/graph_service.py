import os
import json
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models import GraphNode, GraphEdge, DataSource, QueryHistory, IncidentRecord
from backend.schemas import NodeCreate, EdgeCreate
from backend.core.graph_engine import graph_engine
from backend.core.vector_engine import vector_engine


class GraphService:
    """Business logic for Graph operations, NetworkX synchronization, and persistence."""

    @staticmethod
    def seed_sample_data_if_empty(db: Session):
        """Seeds initial realistic sample graph and vector data if DB is empty."""
        node_count = db.query(GraphNode).count()
        if node_count > 0:
            # Sync existing data into graph_engine & vector_engine
            nodes = db.query(GraphNode).all()
            edges = db.query(GraphEdge).all()
            graph_engine.sync_graph(nodes, edges)
            vector_engine.index_nodes(nodes)
            return

        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.json")
        if not os.path.exists(json_path):
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Insert Nodes
            for n_data in data.get("nodes", []):
                node = GraphNode(
                    id=n_data["id"],
                    label=n_data["label"],
                    category=n_data["category"],
                    uri=n_data["uri"],
                    description=n_data.get("description", ""),
                    vector_weight=n_data.get("vector_weight", 0.5),
                    attributes_json=json.dumps(n_data.get("attributes", {})),
                )
                db.add(node)

            db.commit()

            # Insert Edges
            for e_data in data.get("edges", []):
                edge = GraphEdge(
                    id=e_data["id"],
                    source=e_data["source"],
                    target=e_data["target"],
                    label=e_data.get("label", "RELATED_TO"),
                    weight=e_data.get("weight", 1.0),
                    attributes_json=json.dumps(e_data.get("attributes", {})),
                )
                db.add(edge)

            # Insert DataSources
            for ds in data.get("data_sources", []):
                db.add(
                    DataSource(
                        name=ds["name"],
                        type=ds["type"],
                        status=ds["status"],
                        endpoint=ds["endpoint"],
                        records_count=ds["records_count"],
                    )
                )

            # Insert Incidents
            for inc in data.get("incidents", []):
                db.add(
                    IncidentRecord(
                        title=inc["title"],
                        severity=inc["severity"],
                        category=inc["category"],
                        target_entity_id=inc["target_entity_id"],
                        description=inc["description"],
                        status=inc["status"],
                    )
                )

            # Insert Query History
            for qh in data.get("query_history", []):
                db.add(
                    QueryHistory(
                        query_text=qh["query_text"],
                        dialect=qh["dialect"],
                        execution_time_ms=qh["execution_time_ms"],
                        status=qh["status"],
                        rows_returned=qh["rows_returned"],
                    )
                )

            db.commit()

            # Sync in-memory engines
            nodes = db.query(GraphNode).all()
            edges = db.query(GraphEdge).all()
            graph_engine.sync_graph(nodes, edges)
            vector_engine.index_nodes(nodes)

        except Exception as e:
            db.rollback()
            print(f"[LifeGraph AI] Warning during sample data seeding: {e}")

    @staticmethod
    def get_full_graph(db: Session) -> Dict[str, Any]:
        """Retrieves all graph nodes and edges for frontend visualization."""
        nodes = db.query(GraphNode).all()
        edges = db.query(GraphEdge).all()
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    @staticmethod
    def get_all_nodes(db: Session) -> List[GraphNode]:
        """Returns all graph nodes."""
        return db.query(GraphNode).all()

    @staticmethod
    def get_node_by_id(db: Session, node_id: str) -> Dict[str, Any]:
        """Retrieves detailed information for a single node."""
        node = db.query(GraphNode).filter(GraphNode.id == node_id).first()
        if not node:
            # Fallback check by URI
            node = db.query(GraphNode).filter(GraphNode.uri == node_id).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with identifier '{node_id}' not found.",
            )

        stats = graph_engine.get_node_stats(node.id) or {
            "degree": 0,
            "in_degree": 0,
            "out_degree": 0,
            "degree_centrality": 0.0,
        }

        # Retrieve neighbor node models
        neighbor_ids = graph_engine.get_neighbors(node.id, direction="both")
        neighbors = db.query(GraphNode).filter(GraphNode.id.in_(neighbor_ids)).all() if neighbor_ids else []

        return {
            "node": node,
            "degree": stats["degree"],
            "in_degree": stats["in_degree"],
            "out_degree": stats["out_degree"],
            "degree_centrality": stats["degree_centrality"],
            "neighbors": neighbors,
        }

    @staticmethod
    def get_neighbors(db: Session, node_id: str, direction: str = "both") -> List[GraphNode]:
        """Returns neighbor node objects for a given node."""
        node = db.query(GraphNode).filter(GraphNode.id == node_id).first()
        if not node:
            node = db.query(GraphNode).filter(GraphNode.uri == node_id).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node '{node_id}' not found.",
            )

        neighbor_ids = graph_engine.get_neighbors(node.id, direction=direction)
        if not neighbor_ids:
            return []
        return db.query(GraphNode).filter(GraphNode.id.in_(neighbor_ids)).all()

    @staticmethod
    def explore_khop(db: Session, node_id: str, hops: int = 2, direction: str = "both") -> Dict[str, Any]:
        """Performs K-Hop neighborhood expansion from a starting root node."""
        start_time = time.perf_counter()

        node = db.query(GraphNode).filter(GraphNode.id == node_id).first()
        if not node:
            node = db.query(GraphNode).filter(GraphNode.uri == node_id).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Root node '{node_id}' not found.",
            )

        discovered_ids, edge_ids = graph_engine.get_khop_subgraph(
            node.id, hops=hops, direction=direction
        )

        discovered_nodes = db.query(GraphNode).filter(GraphNode.id.in_(discovered_ids)).all()
        connecting_edges = db.query(GraphEdge).filter(GraphEdge.id.in_(edge_ids)).all()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "root_node": node,
            "hops": hops,
            "direction": direction,
            "discovered_nodes": discovered_nodes,
            "connecting_edges": connecting_edges,
            "total_vertices": len(discovered_nodes),
            "total_edges": len(connecting_edges),
            "traversal_latency_ms": latency_ms,
        }

    @staticmethod
    def create_node(db: Session, node_in: NodeCreate) -> GraphNode:
        """Creates a new graph node and updates graph & vector indexes."""
        existing = db.query(GraphNode).filter(
            (GraphNode.id == node_in.id) | (GraphNode.uri == node_in.uri)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Node with ID '{node_in.id}' or URI '{node_in.uri}' already exists.",
            )

        node = GraphNode(
            id=node_in.id,
            label=node_in.label,
            category=node_in.category,
            uri=node_in.uri,
            description=node_in.description,
            vector_weight=node_in.vector_weight,
            attributes_json=json.dumps(node_in.attributes or {}),
        )

        db.add(node)
        db.commit()
        db.refresh(node)

        # Update NetworkX in-memory graph
        graph_engine.add_node(
            node.id,
            label=node.label,
            category=node.category,
            uri=node.uri,
            description=node.description or "",
            vector_weight=node.vector_weight,
            attributes=node.attributes,
        )

        # Re-index vectors
        vector_engine.index_nodes(db.query(GraphNode).all())

        return node

    @staticmethod
    def create_edge(db: Session, edge_in: EdgeCreate) -> GraphEdge:
        """Creates a new relationship edge between two existing nodes."""
        source = db.query(GraphNode).filter(GraphNode.id == edge_in.source).first()
        target = db.query(GraphNode).filter(GraphNode.id == edge_in.target).first()

        if not source or not target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Both source node '{edge_in.source}' and target node '{edge_in.target}' must exist.",
            )

        existing = db.query(GraphEdge).filter(GraphEdge.id == edge_in.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Edge with ID '{edge_in.id}' already exists.",
            )

        edge = GraphEdge(
            id=edge_in.id,
            source=edge_in.source,
            target=edge_in.target,
            label=edge_in.label,
            weight=edge_in.weight,
            attributes_json=json.dumps(edge_in.attributes or {}),
        )

        db.add(edge)
        db.commit()
        db.refresh(edge)

        # Update NetworkX graph
        graph_engine.add_edge(
            edge.source,
            edge.target,
            edge_id=edge.id,
            label=edge.label,
            weight=edge.weight,
            attributes=edge.attributes,
        )

        return edge

    @staticmethod
    def delete_node(db: Session, node_id: str) -> Dict[str, Any]:
        """Deletes a node and associated edges from database and in-memory indexes."""
        node = db.query(GraphNode).filter(GraphNode.id == node_id).first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with ID '{node_id}' not found.",
            )

        db.delete(node)
        db.commit()

        # Update in-memory graph
        graph_engine.remove_node(node_id)
        vector_engine.index_nodes(db.query(GraphNode).all())

        return {
            "status": "success",
            "message": f"Node '{node_id}' and all connected relationships deleted.",
            "deleted_node_id": node_id,
        }
