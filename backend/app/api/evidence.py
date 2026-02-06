"""Evidence API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Evidence, Intervention
from app.schemas import EvidenceCreate, EvidenceResponse


router = APIRouter()


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db)
):
    """添加新的证据"""
    # Verify intervention exists
    intervention = db.query(Intervention).filter(Intervention.id == evidence.intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    db_evidence = Evidence(**evidence.model_dump())
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence


@router.get("/intervention/{intervention_id}", response_model=List[EvidenceResponse])
async def get_evidence_by_intervention(
    intervention_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取特定干预措施的所有证据"""
    evidence_list = db.query(Evidence).filter(
        Evidence.intervention_id == intervention_id
    ).offset(skip).limit(limit).all()
    return evidence_list


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db)
):
    """获取单个证据详情"""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.get("/by-quality")
async def get_evidence_by_quality(
    min_quality: float = 70.0,
    db: Session = Depends(get_db)
):
    """按质量分数筛选证据"""
    evidence_list = db.query(Evidence).filter(
        Evidence.quality_score >= min_quality
    ).order_by(Evidence.quality_score.desc()).all()
    return evidence_list


@router.get("/meta-analyses")
async def get_meta_analyses(
    db: Session = Depends(get_db)
):
    """获取所有 Meta 分析证据"""
    evidence_list = db.query(Evidence).filter(
        Evidence.source_type == "meta_analysis"
    ).all()
    return evidence_list


@router.get("/randomized-trials")
async def get_randomized_trials(
    db: Session = Depends(get_db)
):
    """获取所有随机对照试验"""
    evidence_list = db.query(Evidence).filter(
        Evidence.source_type == "randomized_trial"
    ).all()
    return evidence_list
