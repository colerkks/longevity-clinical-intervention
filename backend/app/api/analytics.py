from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics import AnalyticsService


router = APIRouter()


@router.get("/health-trends/{user_id}/{biomari_name}")
async def get_health_trends(
    user_id: int,
    biomarker_name: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取生物标志物趋势数据
    
    Args:
        user_id: 用户 ID
        biomarker_name: 生物标志物名称（如 "c_reative_protein"）
        days: 时间范围（天）
    
    Returns:
        趋势数据
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_health_trends(
        user_id=user_id,
        biomarker_name=biomarker_name,
        days=days
    )


@router.get("/intervention-effectiveness/{user_id}")
async def get_intervention_effectiveness(
    user_id: int,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """
    获取干预措施效果分析
    
    Args:
        user_id: 用户 ID
        days: 时间范围（天）
    
    Returns:
        效果分析结果
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_intervention_effectiveness(
        user_id=user_id,
        days=days
    )


@router.get("/goal-progress/{user_id}")
async def get_goal_progress(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户目标进度
    
    Args:
        user_id: 用户 ID
    
    Returns:
        目标进度
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_goal_progress(user_id=user_id)


@router.get("/comparison/{user_id}")
async def get_comparison_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取对比较数据（如多个干预措施对比）
    
    Args:
        user_id: 用户 ID
    
    Returns:
        对比数据
    """
    # This could compare interventions, biomarkers, etc.
    # For now, return a placeholder
    return {
        "user_id": user_id,
        "message": "Comparison endpoint - feature under development"
    }
