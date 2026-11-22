import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


class SimilarityEngine:
    """Computes geometric distance and similarity metrics between high-dimensional vectors."""

    @staticmethod
    def compute_cosine(vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        """Computes pairwise cosine similarity matrix between two 2D numpy arrays."""
        return cosine_similarity(vec_a, vec_b)

    @staticmethod
    def compute_euclidean(vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        """
        Computes pairwise Euclidean distance and converts to a bounded similarity metric
        using the exponential decay transform: sim = exp(-dist).
        """
        distances = euclidean_distances(vec_a, vec_b)
        similarities = np.exp(-distances)
        return similarities

    @staticmethod
    def compute_dot_product(vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        """Computes dot product (inner product) similarity between two vectors."""
        # Convert sparse or dense arrays to dot product
        if hasattr(vec_a, "toarray"):
            vec_a = vec_a.toarray()
        if hasattr(vec_b, "toarray"):
            vec_b = vec_b.toarray()
        return np.dot(vec_a, vec_b.T)

    @classmethod
    def calculate_similarity(cls, query_vec: np.ndarray, doc_matrix: np.ndarray, metric: str = "cosine") -> np.ndarray:
        """
        Dispatches calculation according to requested distance metric:
        - 'cosine': Cosine similarity [0, 1]
        - 'euclidean': Inverted Euclidean distance [0, 1]
        - 'dot': Normalized dot product
        """
        m = metric.lower().strip()
        if m in ("euclidean", "l2"):
            return cls.compute_euclidean(query_vec, doc_matrix)
        elif m in ("dot", "ip"):
            return cls.compute_dot_product(query_vec, doc_matrix)
        else:
            return cls.compute_cosine(query_vec, doc_matrix)
