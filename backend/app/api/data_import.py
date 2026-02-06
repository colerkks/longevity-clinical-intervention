"""Data import/export API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.data_import import (
    InterventionBulkImport, BulkImportResult, ExportFormat,
    HealthDataExportRequest, ImportValidationResult
)
from app.services.data_import_export import DataImportService, DataExportService


router = APIRouter()


@router.post("/import/interventions/bulk", response_model=BulkImportResult)
async def bulk_import_interventions(
    data: InterventionBulkImport,
    db: Session = Depends(get_db)
):
    """
    批量导入干预措施
    
    预期格式（CSV/Excel）:
    ```json
    {
      "name": "维生素D补充",
      "category": "supplement",
      "evidence_level": 1,
      "source_type": "randomized_trial",
      "citation": "Study reference...",
      "sample_size": 1000,
      "risk_duration_days": 365,
      "effect_size_value": 0.85,
      "effect_size_ci_low": 0.78,
      "effect_size_ci_high": 0.92,
      "outcomes": "reduced_mortality,improved_bone_health",
      "quality_score": 85,
      "risk_name": "hypercalcemia",
      "risk_severity": "mild",
      "risk_frequency": 5.0,
      "benefit_name": "Improved immune function",
      "benefit_category": "health",
      "benefit_effect_size": 0.3,
      "benefit_confidence": 80
    }
    ```
    """
    import_service = DataImportService(db)
    
    result = import_service.validate_and_import_interventions([data])
    
    return result


@router.post("/import/interventions/validate", response_model=ImportValidationResult)
async def validate_import_data(
    data: InterventionBulkImport,
    db: Session = Depends(get_db)
):
    """验证单条导入数据（不保存）"""
    import_service = DataImportService(db)
    
    result = import_service._validate_intervention_data(data)
    
    return result


@router.get("/export/health-data")
async def export_health_data(
    user_id: int,
    format: ExportFormat = ExportFormat.json,
    include_measurements: bool = True,
    include_goals: bool = True,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    导出用户健康数据
    
    Args:
        user_id: 用户 ID
        format: 导出格式
        include_measurements: 是否包含测量记录
        include_goals: 是否包含目标
        date_from: 开始日期 (ISO format)
        date_to: 结束日期 (ISO format)
    
    Returns:
        CSV 或 JSON 格式的数据
    """
    export_service = DataExportService(db)
    
    if format == ExportFormat.csv:
        csv_content = export_service.export_to_csv(
            user_id=user_id,
            include_measurements=include_measurements,
            include_goals=include_goals,
            date_from=date_from,
            date_to=date_to
        )
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=health_data.csv"}
        )
    else:
        json_data = export_service.export_to_json(
            user_id=user_id,
            include_measurements=include_measurements,
            include_goals=include_goals,
            date_from=date_from,
            date_to=date_to
        )
        
        return json_data


@router.get("/export/template")
async def get_import_template():
    """获取导入数据模板（JSON 格式）"""
    template = {
      "description": "长寿医学干预措施数据导入模板",
      "version": "1.0",
      "schema": {
        "interventions": {
          "type": "array",
          "items": {
            "name": "string",
            "name_en": "string (optional)",
            "description": "string (optional)",
            "category": "string",  # nutrition, exercise, sleep, supplement, medical
            "mechanism": "string (optional)",
            "evidence_level": "integer",  # 1-4
            "source_type": "string (optional)",  # randomized_trial, cohort_study, case_control, meta_analysis, expert
            "citation": "string (optional)",
            "sample_size": "integer (optional)",
            "duration_days": "integer (optional)",
            "effect_size_value": "number (optional)",
            "effect_size_ci_low": "number (optional)",
            "effect_size_ci_high": "number (optional)",
            "outcomes": "string (optional, comma-separated)",
            "quality_score": "number (0-100, optional)",
            "risk_name": "string (optional)",
            "risk_severity": "string (optional)",  # mild, moderate, severe
            "r  isk_frequency": "number (0-100, optional)",
            "risk_description": "string (optional)",
            "benefit_name": "string (optional)",
            "benefit_category": "string (optional)",  # longevity, health, disease_prevention
            "benefit_effect_size": "number (optional)",
            "benefit_confidence": "number (0-100, optional)",
            "benefit_description": "string (optional)"
          }
        }
      },
      "example": {
        "name": "维生素D3补充",
        "name_en": "Vitamin D3 Supplementation",
        "description": "对骨骼健康和免疫系统有重要作用",
        "category": "supplement",
        "mechanism": "维生素D受体调节钙磷代谢",
        "evidence_level": 1,
        "source_type": "randomized_trial",
        "citation": "Smith JC et al. NEJM. 2023;382(9):2003-2012.",
        "sample_size": 25871,
        "duration_days": 730,
        "effect_size_value": 0.87,
        "effect_size_ci_low": 0.81,
        "effect_size_ci_high": 0.93,
        "outcomes": "reduced_respiratory_infections,improved_bone_density",
        "quality_score": 92,
        "risk_name": "Hypercalcemia (rare)",
        "risk_severity": "mild",
        "risk_frequency": 2.5,
        "risk_description": "在高剂量情况下可能出现",
        "benefit_name": "增强骨密度",
        "benefit_category": "health",
        "benefit_effect_size": 0.4,
        "benefit_confidence": 88,
        "benefit_description": "提高脊柱和髋部骨密度，降低骨折风险"
      }
    }
    
    return template
