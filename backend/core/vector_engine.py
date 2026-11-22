import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.config import settings
from backend.core.similarity_engine import SimilarityEngine


class VectorEngine:
    """
    Vector Search & Embedding Index Engine for LifeGraph AI.
    
    Current implementation uses a lightweight Scikit-Learn TF-IDF vectorizer
    and vector space similarity baseline. Built to be modular and ready for
    future drop-in replacement with SentenceTransformers and FAISS / Milvus.
    """

    def __init__(self, max_features: int = 2048):
        self.max_features = max_features
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_matrix = None
        self.indexed_docs: List[Dict[str, Any]] = []
        self.last_indexed_at: Optional[datetime] = None
        self.is_indexed = False

    def build_document_text(self, node: Any) -> str:
        """Composes a rich textual document representation from a graph node."""
        parts = [
            str(node.label or ""),
            str(node.category or ""),
            str(node.description or ""),
        ]
        if hasattr(node, "attributes") and isinstance(node.attributes, dict):
            for k, v in node.attributes.items():
                parts.append(f"{k} {v}")
        return " ".join(parts).strip()

    def index_nodes(self, nodes: List[Any]):
        """Indexes all graph nodes into the high-dimensional TF-IDF vector space."""
        if not nodes:
            self.indexed_docs = []
            self.doc_matrix = None
            self.is_indexed = False
            return

        corpus = []
        doc_metadata = []

        for node in nodes:
            text = self.build_document_text(node)
            corpus.append(text)
            doc_metadata.append({
                "id": node.id,
                "label": node.label,
                "category": node.category,
                "uri": node.uri,
                "description": node.description or "",
                "vector_weight": float(node.vector_weight or 0.5),
            })

        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words="english",
            ngram_range=(1, 2),
            norm="l2",
        )

        self.doc_matrix = self.vectorizer.fit_transform(corpus)
        self.indexed_docs = doc_metadata
        self.last_indexed_at = datetime.utcnow()
        self.is_indexed = True

    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.80,
        metric: str = "cosine",
    ) -> Dict[str, Any]:
        """
        Executes vector search against indexed documents using similarity metrics.
        Returns matched documents sorted by descending similarity score.
        """
        start_time = time.perf_counter()

        if not self.is_indexed or not self.indexed_docs or self.vectorizer is None:
            return {
                "query": query,
                "threshold": threshold,
                "metric": metric,
                "execution_time_sec": 0.001,
                "total_matches": 0,
                "indexed_documents_count": 0,
                "results": [],
            }

        # Vectorize the incoming search query
        query_vec = self.vectorizer.transform([query])

        # Compute similarity matrix
        sim_matrix = SimilarityEngine.calculate_similarity(query_vec, self.doc_matrix, metric=metric)
        scores = sim_matrix[0]

        # Blend TF-IDF similarity with node vector_weight baseline
        scored_results = []
        for idx, doc in enumerate(self.indexed_docs):
            text_sim = float(scores[idx])
            # Boost score based on pre-computed graph authority vector weight
            combined_score = (text_sim * 0.70) + (doc["vector_weight"] * 0.30)
            
            # Normalize between 0 and 0.995
            bounded_score = round(min(0.995, max(0.0, combined_score)), 4)
            distance = round(1.0 - bounded_score, 4)

            if bounded_score >= threshold:
                scored_results.append({
                    "id": doc["id"],
                    "title": doc["label"],
                    "uri": doc["uri"],
                    "category": doc["category"],
                    "snippet": doc["description"],
                    "similarity_score": bounded_score,
                    "distance": distance,
                })

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_results = scored_results[:top_k]

        duration = round(time.perf_counter() - start_time, 4)

        return {
            "query": query,
            "threshold": threshold,
            "metric": metric,
            "execution_time_sec": max(0.001, duration),
            "total_matches": len(scored_results),
            "indexed_documents_count": len(self.indexed_docs),
            "results": top_results,
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current vector engine index status."""
        vocab_size = len(self.vectorizer.vocabulary_) if self.vectorizer else 0
        return {
            "status": "ready" if self.is_indexed else "unindexed",
            "engine_name": "TF-IDF Vector Space Index (Scikit-Learn Baseline)",
            "indexed_documents": len(self.indexed_docs),
            "vocabulary_size": vocab_size,
            "vector_dimension": vocab_size,
            "last_indexed_at": self.last_indexed_at,
        }


# Global singleton instance of VectorEngine
vector_engine = VectorEngine(max_features=settings.VECTOR_MAX_FEATURES)
