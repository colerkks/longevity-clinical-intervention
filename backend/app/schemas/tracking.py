"""Pydantic schemas for effect tracking"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class InterventTrackingCreate(BaseModel):
    user_id: int
    intervention_id: int
    status: str = Field("active", pattern="^(active|paused|completed|stopped)$")
    notes: Optional[str] = None


class InterventTrackingUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(active|paused|completed|stopped)$")
    adherence_rate: Optional[float] = Field(None, ge=0, le=100)
    end_date: Optional[str] = None
    notes: Optional[str] = None


class InterventTrackingResponse(BaseModel):
    id: int
    user_id: int
    intervention_id: int
    start_date: str
    end_date: Optional[str]
    status: str
    adherence_rate: Optional[float]
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EffectMeasurementCreate(BaseModel):
    intervient_tracking_id: int
    metric_name: str = Field(..., max_length=100)
    metric_value: float
    unit: Optional[str] = Field(None, max_length=50)
    baseline_value: Optional[float] = None
    notes: Optional[str] = None


class EffectMeasurementResponse(EffectMeasurementCreate):
    id: int
    measurement_date: str
    created_at: str

    class Config:
        from_attributes = True


class HealthGoalCreate(BaseModel):
    user_id: int
    goal_type: str = Field(..., max_length=50)
    target_value: float
    unit: Optional[str] = Field(None, max_length=50)
    start_date: str
    target_date: str
    interventions: Optional[List[int]] = None


class HealthGoalUpdate(BaseModel):
    current_value: Optional[float] = None
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|achieved|missed)$")
    target_date: Optional[str] = None


class HealthGoalResponse(HealthGoalCreate):
    id: int
    current_value: Optional[float]
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BiomarkerMeasurementCreate(BaseModel):
    user_id: int
    biomarker_name: str = Field(..., max_length=100)
    value: float
    unit: Optional[str] = Field(None, max_length=50)
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    source: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class BiomarkerMeasurementResponse(BaseModel):
    id: int
    is_normal: bool
    measurement_date: str
    created_at: str

    class Config:
        from_attributes = True
