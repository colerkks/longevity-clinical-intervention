"""Intervention API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Intervention
from app.schemas import InterventionCreate, InterventionUpdate, InterventionResponse


router = APIRouter()


@router.post("/", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
async def create_intervention(
    intervention: InterventionCreate,
    db: Session = Depends(get_db)
):
    """创建新的干预措施"""
    db_intervention = Intervention(**intervention.model_dump())
    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)
    return db_intervention


@router.get("/", response_model=List[InterventionResponse])
async def list_interventions(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取干预措施列表"""
    query = db.query(Intervention)

    if category:
        query = query.filter(Intervention.category == category)

    interventions = query.offset(skip).limit(limit).all()
    return interventions


@router.get("/{intervention_id}", response_model=InterventionResponse)
async def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db)
):
    """获取单个干预措施详情"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return intervention


@router.put("/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(
    intervention_id: int,
    intervention_update: InterventionUpdate,
    db: Session = Depends(get_db)
):
    """更新干预措施"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    for field, value in intervention_update.model_dump(exclude_unset=True).items():
        setattr(intervention, field, value)

    db.commit()
    db.refresh(intervention)
    return intervention


@router.delete("/{intervention_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intervention(
    intervention_id: int,
    db: Session = Depends(get_db)
):
    """删除干预措施"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    db.delete(intervention)
    db.commit()
    return None


@router.get("/search/by-name", response_model=List[InterventionResponse])
async def search_interventions_by_name(
    query: str,
    db: Session = Depends(get_db)
):
    """按名称搜索干预措施"""
    interventions = db.query(Intervention).filter(
        Intervention.name.contains(query)
    ).limit(20).all()
    return interventions


@router.get("/by-evidence-level/{level}", response_model=List[InterventionResponse])
async def get_interventions_by_evidence_level(
    level: int,
    db: Session = Depends(get_db)
):
    """按证据等级获取干预措施"""
    if level < 1 or level > 4:
        raise HTTPException(status_code=400, detail="Evidence level must be between 1 and 4")

    interventions = db.query(Intervention).filter(
        Intervention.evidence_level == level
    ).all()
    return interventions
