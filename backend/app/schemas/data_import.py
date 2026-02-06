"""Pydantic schemas for data import/export"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InterventionBulkImport(BaseModel):
    name: str = Field(..., max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(nutrition|exercise|sleep|supplement|medical)$")
    mechanism: Optional[str] = None
    evidence_level: int = Field(..., ge=1, le=4)
    source_type: Optional[str] = None
    citation: Optional[str] = None
    sample_size: Optional[int] = Field(None, ge=1)
    duration_days: Optional[int] = Field(None, ge=1)
    effect_size_value: Optional[float] = None
    effect_size_ci_low: Optional[float] = None
    effect_size_ci_high: Optional[float] = None
    outcomes: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    risk_name: Optional[str] = None
    risk_severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")
    risk_frequency: Optional[float] = Field(None, ge=0, le=100)
    risk_description: Optional[str] = None
    benefit_name: Optional[str] = None
    benefit_category: Optional[str] = None
    benefit_effect_size: Optional[float] = None
    benefit_confidence: Optional[float] = Field(None, ge=0, le=100)
    benefit_description: Optional[str] = None


class BulkImportResult(BaseModel):
    success: List[dict]
    failed: List[dict]
    total: int


class ExportFormat(str):
    csv = "csv"
    json = "json"
    excel = "excel"


class HealthDataExportRequest(BaseModel):
    user_id: int
    format: ExportFormat = ExportFormat.csv
    include_measurements: bool = True
    include_goals: bool = True
    include_tracking: bool = True
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class ImportValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    row_count: int
