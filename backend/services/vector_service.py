from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models import GraphNode
from backend.schemas import VectorSearchRequest
from backend.core.vector_engine import vector_engine


class VectorService:
    """Service handling Vector search queries, embedding indexing, and index status."""

    @staticmethod
    def search_vectors(db: Session, request: VectorSearchRequest) -> Dict[str, Any]:
        """Performs vector search across indexed node documents."""
        query_text = request.get_query()
        if not query_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty. Please provide 'query' or 'prompt'.",
            )

        # Ensure vector engine is populated
        if not vector_engine.is_indexed:
            nodes = db.query(GraphNode).all()
            vector_engine.index_nodes(nodes)

        results = vector_engine.search(
            query=query_text,
            top_k=request.top_k,
            threshold=request.threshold,
            metric=request.metric,
        )

        return results

    @staticmethod
    def get_status(db: Session) -> Dict[str, Any]:
        """Returns the current vector indexing status and vocabulary dimension."""
        if not vector_engine.is_indexed:
            nodes = db.query(GraphNode).all()
            vector_engine.index_nodes(nodes)

        return vector_engine.get_status()

    @staticmethod
    def reindex_all_nodes(db: Session) -> Dict[str, Any]:
        """Forces a full re-indexing of all graph nodes in the vector space."""
        nodes = db.query(GraphNode).all()
        vector_engine.index_nodes(nodes)

        status_info = vector_engine.get_status()
        return {
            "status": "reindexed",
            "message": f"Successfully indexed {len(nodes)} node documents.",
            "details": status_info,
        }
