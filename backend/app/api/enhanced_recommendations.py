"""Enhanced recommendations API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.recommendation_engine import RecommendationEngine
from app.services.auth import get_current_active_user


router = APIRouter()


@router.get("/personalized/{user_id}")
async def get_personalized_recommendations(
    user_id: int,
    limit: int = 10,
    exclude_categories: str = None,
    db: Session = Depends(get_db)
):
    """
    获取个性化推荐
    
    Args:
        user_id: 用户 ID
        limit: 返回推荐数量限制
        exclude_categories: 排除的分类（逗号分隔，如 "nutrition,supplement"）
    """
    # Parse exclude categories
    exclude_list = None
    if exclude_categories:
        exclude_list = [cat.strip() for cat in exclude_categories.split(",")]
    
    # Initialize recommendation engine
    engine = RecommendationEngine(db)
    
    # Generate personalized recommendations
    recommendations = engine.generate_personalized_recommendations(
        user_id=user_id,
        limit=limit,
        exclude_categories=exclude_list
    )
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "total": len(recommendations)
    }


@router.get("/explain/{user_id}/{intervention_id}")
async def explain_recommendation(
    user_id: int,
    intervention_id: int,
    db: Session = Depends(get_db)
):
    """
    解释推荐原因
    
    Returns detailed explanation of why an intervention is recommended
    """
    engine = RecommendationEngine(db)
    
    explanation = engine.explain_recommendation(
        intervention_id=intervention_id,
        user_id=user_id
    )
    
    return explanation


@router.get("/compare/{user_id}")
async def compare_interventions(
    user_id: int,
    intervention_ids: str,
    db: Session = Depends(get_db)
):
    """
    比较多个干预措施
    
    Args:
        user_id: 用户 ID
        intervention_ids: 干预措施 ID 列表（逗号分隔）
    """
    try:
        ids = [int(id.strip()) for id in intervention_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid intervention IDs")
    
    engine = RecommendationEngine(db)
    comparisons = []
    
    for intervention_id in ids:
        explanation = engine.explain_recommendation(intervention_id, user_id)
        if "error" not in explanation:
            comparisons.append(explanation)
    
    return {
        "user_id": user_id,
        "comparisons": comparisons,
        "total": len(comparisons)
    }


@router.get("/my-recommendations")
async def get_my_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取当前用户的个性化推荐
    """
    current_user = await get_current_active_user(db)
    
    engine = RecommendationEngine(db)
    recommendations = engine.generate_personalized_recommendations(
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "recommendations": recommendations
    }
