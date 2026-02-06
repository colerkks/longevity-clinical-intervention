"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== Intervention Schemas ====================

class InterventionBase(BaseModel):
    name: str = Field(..., max_length=200, description="干预措施名称")
    name_en: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., description="分类: nutrition, exercise, sleep, supplement, medical")
    mechanism: Optional[str] = None
    evidence_level: int = Field(default=4, ge=1, le=4, description="证据等级 1-4")

    @validator('category')
    def validate_category(cls, v):
        allowed = ['nutrition', 'exercise', 'sleep', 'supplement', 'medical']
        if v not in allowed:
            raise ValueError(f'Category must be one of {allowed}')
        return v


class InterventionCreate(InterventionBase):
    pass


class InterventionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    mechanism: Optional[str] = None
    evidence_level: Optional[int] = Field(None, ge=1, le=4)


class InterventionResponse(InterventionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Evidence Schemas ====================

class EvidenceBase(BaseModel):
    intervention_id: int
    source_type: Optional[str] = Field(None, description="randomized_trial, cohort_study, case_control, meta_analysis, expert")
    pubmed_id: Optional[str] = Field(None, max_length=50)
    citation: Optional[str] = None
    sample_size: Optional[int] = Field(None, ge=1)
    duration_days: Optional[int] = Field(None, ge=1)
    effect_size: Optional[Dict[str, Any]] = None
    outcomes: Optional[List[str]] = None
    quality_score: Optional[float] = Field(None, ge=0, le=100)


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceResponse(EvidenceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Recommendation Schemas ====================

class RecommendationCreate(BaseModel):
    user_id: str
    intervention_id: int
    priority: int = Field(default=5, ge=1, le=10)
    reasoning: Optional[str] = None


class RecommendationResponse(RecommendationCreate):
    id: int
    risk_score: Optional[float] = None
    benefit_score: Optional[float] = None
    net_benefit: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
