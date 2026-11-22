from typing import Dict, Any, List, Set, Tuple, Optional
import networkx as nx
import numpy as np


class GraphEngine:
    """Core NetworkX-powered Graph Analysis Engine for LifeGraph AI."""

    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()

    def sync_graph(self, nodes: List[Any], edges: List[Any]):
        """Rebuilds the in-memory NetworkX graph from database models."""
        self.graph.clear()

        for node in nodes:
            self.graph.add_node(
                node.id,
                label=node.label,
                category=node.category,
                uri=node.uri,
                description=node.description or "",
                vector_weight=float(node.vector_weight or 0.5),
                attributes=node.attributes if hasattr(node, "attributes") else {},
            )

        for edge in edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                id=edge.id,
                label=edge.label,
                weight=float(edge.weight or 1.0),
                attributes=edge.attributes if hasattr(edge, "attributes") else {},
            )

    def add_node(self, node_id: str, **attrs):
        self.graph.add_node(node_id, **attrs)

    def remove_node(self, node_id: str):
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)

    def add_edge(self, source_id: str, target_id: str, edge_id: str, label: str, weight: float = 1.0, **attrs):
        self.graph.add_edge(source_id, target_id, id=edge_id, label=label, weight=weight, **attrs)

    def get_node_stats(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Returns degree metrics and centrality for a specific node."""
        if not self.graph.has_node(node_id):
            return None

        in_deg = self.graph.in_degree(node_id)
        out_deg = self.graph.out_degree(node_id)
        total_deg = in_deg + out_deg

        # Degree centrality relative to total nodes
        n = self.graph.number_of_nodes()
        centrality = total_deg / (2 * (n - 1)) if n > 1 else 0.0

        return {
            "node_id": node_id,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "degree": total_deg,
            "degree_centrality": round(centrality, 4),
        }

    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        """Returns direct neighbors of a node based on edge direction."""
        if not self.graph.has_node(node_id):
            return []

        if direction == "outgoing":
            return list(self.graph.successors(node_id))
        elif direction == "incoming":
            return list(self.graph.predecessors(node_id))
        else:
            return list(set(self.graph.successors(node_id)) | set(self.graph.predecessors(node_id)))

    def get_khop_subgraph(
        self, root_id: str, hops: int = 2, direction: str = "both"
    ) -> Tuple[Set[str], Set[str]]:
        """
        Explores k-hop neighborhood from root_id using BFS.
        Returns:
            discovered_nodes: set of node IDs in the k-hop scope
            connecting_edges: set of edge IDs connecting discovered nodes
        """
        if not self.graph.has_node(root_id):
            return set(), set()

        discovered_nodes: Set[str] = {root_id}
        current_layer: Set[str] = {root_id}

        for _ in range(max(1, hops)):
            next_layer: Set[str] = set()
            for curr in current_layer:
                neighbors = self.get_neighbors(curr, direction=direction)
                for nbr in neighbors:
                    if nbr not in discovered_nodes:
                        discovered_nodes.add(nbr)
                        next_layer.add(nbr)
            current_layer = next_layer
            if not current_layer:
                break

        # Collect edges between discovered vertices
        connecting_edges: Set[str] = set()
        subgraph = self.graph.subgraph(discovered_nodes)
        for u, v, data in subgraph.edges(data=True):
            edge_id = data.get("id")
            if edge_id:
                connecting_edges.add(edge_id)

        return discovered_nodes, connecting_edges

    def calculate_global_metrics(self) -> Dict[str, Any]:
        """Calculates global structural metrics across the graph."""
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()

        if n == 0:
            return {
                "nodes": 0,
                "edges": 0,
                "density": 0.0,
                "avg_degree": 0.0,
                "components": 0,
                "largest_component_size": 0,
            }

        density = nx.density(self.graph)
        degrees = [d for _, d in self.graph.degree()]
        avg_degree = float(np.mean(degrees)) if degrees else 0.0

        undirected = self.graph.to_undirected()
        components = list(nx.connected_components(undirected))
        largest_comp = max(len(c) for c in components) if components else 0

        return {
            "nodes": n,
            "edges": m,
            "density": round(density, 4),
            "avg_degree": round(avg_degree, 2),
            "components": len(components),
            "largest_component_size": largest_comp,
        }

    def detect_motifs(self) -> List[Dict[str, Any]]:
        """Identifies triadic closures, dense cliques, and topological hub structures."""
        motifs = []
        undirected = self.graph.to_undirected()

        # 1. 3-Cliques (Triadic closures)
        cliques = list(nx.find_cliques(undirected))
        triangles = [c for c in cliques if len(c) >= 3]
        for idx, tri in enumerate(triangles[:5]):
            motifs.append({
                "id": f"motif-tri-{idx + 1}",
                "pattern_type": "Triadic Closure (Dense Triangle)",
                "description": f"Recurrent 3-node feedback cluster found between {', '.join(tri)}.",
                "confidence": 0.94,
                "evidence": f"Mutual triangular connectivity in undirected projection: {len(tri)} nodes.",
                "participating_nodes": tri,
            })

        # 2. Hub Vertices (high degree outliers)
        degrees = dict(self.graph.degree())
        if degrees:
            mean_deg = np.mean(list(degrees.values()))
            std_deg = np.std(list(degrees.values())) or 1.0
            for node, deg in degrees.items():
                if deg >= mean_deg + 1.2 * std_deg:
                    motifs.append({
                        "id": f"motif-hub-{node}",
                        "pattern_type": "Central Star / Hub Nexus",
                        "description": f"Vertex '{node}' exhibits unusually high degree centrality ({deg} links).",
                        "confidence": 0.98,
                        "evidence": f"Degree is {round((deg - mean_deg) / std_deg, 2)} standard deviations above network average.",
                        "participating_nodes": [node],
                    })

        return motifs

    def analyze_vulnerabilities(self) -> Dict[str, Any]:
        """Calculates articulation points, bridges, and systemic fragility."""
        undirected = self.graph.to_undirected()
        cut_vertices = list(nx.articulation_points(undirected))
        bridges = list(nx.bridges(undirected))

        n = self.graph.number_of_nodes()
        # Fragility score based on ratio of cut vertices to total nodes
        fragility = (len(cut_vertices) / n) if n > 0 else 0.0
        fragility = round(min(1.0, fragility * 2.5), 3)

        return {
            "cut_vertices": cut_vertices,
            "cut_vertices_count": len(cut_vertices),
            "bridges": bridges,
            "bridges_count": len(bridges),
            "fragility_index": fragility,
        }


# Global singleton instance of GraphEngine
graph_engine = GraphEngine()
