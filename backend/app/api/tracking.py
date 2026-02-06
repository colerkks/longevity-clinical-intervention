"""Effect tracking API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.tracking import InterventTracking, EffectMeasurement, HealthGoal, BiomarkerMeasurement
from app.schemas.tracking import (
    InterventTrackingCreate, InterventTrackingUpdate, InterventTrackingResponse,
    EffectMeasurementCreate, EffectMeasurementResponse,
    HealthGoalCreate, HealthGoalUpdate, HealthGoalResponse,
    BiomarkerMeasurementCreate, BiomarkerMeasurementResponse
)


router = APIRouter()


# ==================== Intervention Tracking ====================

@router.post("/tracking/start", response_model=InterventTrackingResponse, status_code=status.HTTP_201_CREATED)
async def start_intervent(
    tracking_data: InterventTrackingCreate,
    db: Session = Depends(get_db)
):
    """开始新的干预追踪"""
    db_tracking = InterventTracking(
        user_id=tracking_data.user_id,
        intervention_id=tracking_data.intervention_id,
        start_date=datetime.utcnow(),
        status="active",
        notes=tracking_data.notes
    )
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking


@router.get("/tracking/{tracking_id}", response_model=InterventTrackingResponse)
async def get_tracking(
    tracking_id: int,
    db: Session = Depends(get_db)
):
    """获取干预追踪详情"""
    tracking = db.query(InterventTracking).filter(InterventTracking.id == tracking_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    return tracking


@router.put("/tracking/{tracking_id}", response_model=InterventTrackingResponse)
async def update_tracking(
    tracking_id: int,
    update_data: InterventTrackingUpdate,
    db: Session = Depends(get_db)
):
    """更新干预追踪"""
    tracking = db.query(InterventTracking).filter(InterventTracking.id == tracking_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if field == "end_date" and value:
            setattr(tracking, field, datetime.fromisoformat(value))
        elif hasattr(tracking, field):
            setattr(tracking, field, value)
    
    db.commit()
    db.refresh(tracking)
    return tracking


@router.get("/tracking/user/{user_id}")
async def get_user_tracking(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的干预追踪列表"""
    query = db.query(InterventTracking).filter(InterventTracking.user_id == user_id)
    
    if status:
        query = query.filter(InterventTracking.status == status)
    
    tracking_list = query.order_by(InterventTracking.start_date.desc()).offset(skip).limit(limit).all()
    return tracking_list


@router.get("/tracking/{tracking_id}/measurements", response_model=list[EffectMeasurementResponse])
async def get_tracking_measurements(
    tracking_id: int,
    db: Session = Depends(get_db)
):
    """获取追踪的测量记录"""
    measurements = db.query(EffectMeasurement).filter(
        EffectMeasurement.intervent_tracking_id == tracking_id
    ).order_by(EffectMeasurement.measurement_date.desc()).all()
    return measurements


# ==================== Effect Measurements ====================

@router.post("/measurements", response_model=EffectMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement_data: EffectMeasurementCreate,
    db: Session = Depends(get_db)
):
    """创建效果测量记录"""
    db_measurement = EffectMeasurement(**measurement_data.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@router.get("/measurements/user/{user_id}")
async def get_user_measurements(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    metric_name: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的测量记录"""
    # Join with tracking table to filter by user
    query = db.query(EffectMeasurement).join(InterventTracking).filter(
        InterventTracking.user_id == user_id
    )
    
    if metric_name:
        query = query.filter(EffectMeasurement.metric_name == metric_name)
    
    measurements = query.order_by(EffectMeasurement.measurement_date.desc()).offset(skip).limit(limit).all()
    return measurements


@router.get("/measurements/{tracking_id}/progress")
async def get_measurement_progress(
    tracking_id: int,
    db: Session = Depends(get_db)
):
    """获取测量进展（基线对比）"""
    measurements = db.query(EffectMeasurement).filter(
        EffectMeasurement.intervent_tracking_id == tracking_id
    ).order_by(EffectMeasurement.measurement_date.asc()).all()
    
    # Group by metric name
    progress = {}
    for measurement in measurements:
        metric_name = measurement.metric_name
        if metric_name not in progress:
            progress[metric_name] = {
                "baseline": measurement.baseline_value,
                "measurements": []
            }
        progress[metric_name]["measurements"].append({
            "value": measurement.metric_value,
            "date": measurement.measurement_date.isoformat(),
            "notes": measurement.notes
        })
    
    return progress


# ==================== Health Goals ====================

@router.post("/goals", response_model=HealthGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: HealthGoalCreate,
    db: Session = Depends(get_db)
):
    """创建健康目标"""
    db_goal = HealthGoal(
        user_id=goal_data.user_id,
        goal_type=goal_data.goal_type,
        target_value=goal_data.target_value,
        unit=goal_data.unit,
        start_date=datetime.fromisoformat(goal_data.start_date),
        target_date=datetime.fromisoformat(goal_data.target_date),
        status="not_started",
        interventions=goal_data.interventions
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/goals/user/{user_id}")
async def get_user_goals(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户的健康目标"""
    goals = db.query(HealthGoal).filter(HealthGoal.user_id == user_id).order_by(
        HealthGoal.created_at.desc()
    ).all()
    return goals


@router.put("/goals/{goal_id}", response_model=HealthGoalResponse)
async def update_goal(
    goal_id: int,
    update_data: HealthGoalUpdate,
    db: Session = Depends(get_db)
):
    """更新健康目标"""
    goal = db.query(HealthGoal).filter(HealthGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if field == "target_date" and value:
            setattr(goal, field, datetime.fromisoformat(value))
        elif hasattr(goal, field):
            setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/goals/active/user/{user_id}")
async def get_active_goals(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户的活动目标"""
    active_statuses = ["not_started", "in_progress"]
    goals = db.query(HealthGoal).filter(
        HealthGoal.user_id == user_id,
        HealthGoal.status.in_(active_statuses)
    ).order_by(HealthGoal.target_date.asc()).all()
    return goals


# ==================== Biomarker Measurements ====================

@router.post("/biomarkers", response_model=BiomarkerMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_biomarker_measurement(
    measurement_data: BiomarkerMeasurementCreate,
    db: Session = Depends(get_db)
):
    """创建生物标志物测量"""
    db_measurement = BiomarkerMeasurement(**measurement_data.model_dump())
    
    # Determine if value is within normal range
    if measurement_data.reference_range_low and measurement_data.reference_range_high:
        db_measurement.is_normal = (
            measurement_data.reference_range_low <= measurement_data.value <= measurement_data.reference_range_high
        )
    
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@router.get("/biomarkers/user/{user_id}")
async def get_user_biomarkers(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    biomarker_name: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的生物标志物测量"""
    query = db.query(BiomarkerMeasurement).filter(BiomarkerMeasurement.user_id == user_id)
    
    if biomarker_name:
        query = query.filter(BiomarkerMeasurement.biomarker_name == biomarker_name)
    
    measurements = query.order_by(BiomarkerMeasurement.measurement_date.desc()).offset(skip).limit(limit).all()
    return measurements


@router.get("/biomarkers/trends/{user_id}")
async def get_biomarker_trends(
    user_id: int,
    biomarker_name: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取生物标志物趋势数据"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    measurements = db.query(BiomarkerMeasurement).filter(
        BiomarkerMeasurement.user_id == user_id,
        BiomarkerMeasurement.biomarker_name == biomarker_name,
        BiomarkerMeasurement.measurement_date >= start_date
    ).order_by(BiomarkerMeasurement.measurement_date.asc()).all()
    
    return {
        "biomarker_name": biomarker_name,
        "period_days": days,
        "measurements": [{
            "value": m.value,
            "date": m.measurement_date.isoformat(),
            "is_normal": m.is_normal
        } for m in measurements]
    }
