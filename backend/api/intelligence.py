from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    PatternDiscoveryResponse,
    AnomalyDetectionResponse,
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    InsightsResponse,
)
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/intelligence", tags=["AI Intelligence"])


@router.get("/patterns", response_model=PatternDiscoveryResponse)
def get_patterns(db: Session = Depends(get_db)):
    """
    Identifies recurrent structural graph motifs, dense triadic closures,
    and hub vertices using NetworkX clique analysis and degree distribution.
    """
    return IntelligenceService.get_patterns(db)


@router.get("/anomalies", response_model=AnomalyDetectionResponse)
def get_anomalies(db: Session = Depends(get_db)):
    """
    Detects structural graph outliers, high-degree anomalies, pendant vertices,
    and active topology drift incident alerts.
    """
    return IntelligenceService.get_anomalies(db)


@router.post("/risk-analysis", response_model=RiskAnalysisResponse)
def run_risk_analysis(
    request: RiskAnalysisRequest,
    db: Session = Depends(get_db),
):
    """
    Executes graph fragility assessments, articulation point identification,
    and Monte Carlo simulations of cascading dependency failures.
    """
    return IntelligenceService.analyze_risk(db, request)


@router.get("/insights", response_model=InsightsResponse)
def get_insights(db: Session = Depends(get_db)):
    """
    Synthesizes actionable, explainable topological recommendations with
    quantifiable confidence metrics and structural graph evidence.
    """
    return IntelligenceService.get_insights(db)


# Frontend compatibility alias for script.js endpoint `/ai/insights`
@router.get("/ai/insights", response_model=InsightsResponse, include_in_schema=False)
def get_ai_insights_alias(db: Session = Depends(get_db)):
    return IntelligenceService.get_insights(db)
