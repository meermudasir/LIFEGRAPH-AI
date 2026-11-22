from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    VectorSearchRequest,
    VectorSearchResponse,
    VectorStatusResponse,
)
from backend.services.vector_service import VectorService

router = APIRouter(prefix="/vector", tags=["Vector Search"])


@router.post("/search", response_model=VectorSearchResponse)
def search_vectors(
    request: VectorSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Executes high-dimensional semantic search across graph entity embeddings.
    Uses Scikit-Learn TF-IDF baseline with Cosine, Euclidean, or Dot Product similarity.
    """
    return VectorService.search_vectors(db, request)


@router.get("/status", response_model=VectorStatusResponse)
def get_vector_status(db: Session = Depends(get_db)):
    """Returns vector engine indexing status, vocabulary size, and vector dimension."""
    return VectorService.get_status(db)


@router.post("/index")
def trigger_vector_indexing(db: Session = Depends(get_db)):
    """Triggers complete re-indexing of all database entities into the vector space."""
    return VectorService.reindex_all_nodes(db)
