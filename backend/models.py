import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id = Column(String(64), primary_key=True, index=True)
    label = Column(String(128), nullable=False, index=True)
    category = Column(String(64), nullable=False, index=True)
    uri = Column(String(256), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    vector_weight = Column(Float, default=0.5, nullable=False)
    attributes_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships to edges
    out_edges = relationship(
        "GraphEdge",
        foreign_keys="GraphEdge.source",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    in_edges = relationship(
        "GraphEdge",
        foreign_keys="GraphEdge.target",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )

    @property
    def attributes(self):
        try:
            return json.loads(self.attributes_json) if self.attributes_json else {}
        except Exception:
            return {}

    @attributes.setter
    def attributes(self, val):
        self.attributes_json = json.dumps(val or {})


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(String(64), primary_key=True, index=True)
    source = Column(
        String(64), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target = Column(
        String(64), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    label = Column(String(64), nullable=False, index=True, default="RELATED_TO")
    weight = Column(Float, default=1.0, nullable=False)
    attributes_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_node = relationship("GraphNode", foreign_keys=[source], back_populates="out_edges")
    target_node = relationship("GraphNode", foreign_keys=[target], back_populates="in_edges")

    @property
    def attributes(self):
        try:
            return json.loads(self.attributes_json) if self.attributes_json else {}
        except Exception:
            return {}

    @attributes.setter
    def attributes(self, val):
        self.attributes_json = json.dumps(val or {})


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    type = Column(String(64), nullable=False)
    status = Column(String(32), default="Connected", nullable=False)
    endpoint = Column(String(256), nullable=False)
    records_count = Column(Integer, default=0, nullable=False)
    last_sync = Column(DateTime, default=datetime.utcnow, nullable=False)


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    dialect = Column(String(32), default="gremlin", nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    status = Column(String(32), default="success", nullable=False)
    rows_returned = Column(Integer, default=0, nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IncidentRecord(Base):
    __tablename__ = "incident_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), default="warning", nullable=False)
    category = Column(String(64), default="topology", nullable=False)
    target_entity_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(32), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
