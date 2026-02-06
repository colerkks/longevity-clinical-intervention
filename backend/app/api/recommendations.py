"""Recommendation API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Recommendation, Intervention
from app.schemas import RecommendationCreate, RecommendationResponse


router = APIRouter()


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db)
):
    """创建新的推荐"""
    # Verify intervention exists
    intervention = db.query(Intervention).filter(Intervention.id == recommendation.intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    # Calculate risk-benefit scores (simplified version)
    risk_score = calculate_risk_score(intervention, db)
    benefit_score = calculate_benefit_score(intervention, db)
    net_benefit = benefit_score - risk_score

    db_recommendation = Recommendation(**recommendation.model_dump())
    db_recommendation.risk_score = risk_score
    db_recommendation.benefit_score = benefit_score
    db_recommendation.net_benefit = net_benefit

    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


@router.get("/user/{user_id}", response_model=List[RecommendationResponse])
async def get_user_recommendations(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的推荐列表"""
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).order_by(Recommendation.net_benefit.desc()).offset(skip).limit(limit).all()
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """获取单个推荐详情"""
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


@router.get("/top-interventions")
async def get_top_interventions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取基于证据质量的顶级干预措施"""
    interventions = db.query(Intervention).order_by(
        Intervention.evidence_level.asc()
    ).limit(limit).all()

    results = []
    for intervention in interventions:
        risk_score = calculate_risk_score(intervention, db)
        benefit_score = calculate_benefit_score(intervention, db)
        results.append({
            "id": intervention.id,
            "name": intervention.name,
            "category": intervention.category,
            "evidence_level": intervention.evidence_level,
            "risk_score": risk_score,
            "benefit_score": benefit_score,
            "net_benefit": benefit_score - risk_score
        })

    return sorted(results, key=lambda x: x['net_benefit'], reverse=True)[:limit]


# Helper functions
def calculate_risk_score(intervention: Intervention, db: Session) -> float:
    """计算风险分数（简化版本）"""
    from app.models import RiskFactor

    risk_factors = db.query(RiskFactor).filter(
        RiskFactor.intervention_id == intervention.id
    ).all()

    if not risk_factors:
        return 0.0

    total_risk = sum(rf.frequency or 0 for rf in risk_factors)
    return min(total_risk, 100.0) / 100.0


def calculate_benefit_score(intervention: Intervention, db: Session) -> float:
    """计算收益分数（简化版本）"""
    from app.models import Benefit

    benefits = db.query(Benefit).filter(
        Benefit.intervention_id == intervention.id
    ).all()

    if not benefits:
        return 0.0

    total_benefit = sum(b.effect_size or 0 for b in benefits)
    evidence_boost = (5 - intervention.evidence_level) * 0.2  # Level 1 gets 0.8 boost

    return min(total_benefit * evidence_boost, 100.0) / 100.0
