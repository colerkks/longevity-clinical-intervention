"""Effect tracking models"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, func as sql_func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class InterventTracking(Base):
    """干预执行追踪"""
    __tablename__ = "intervent_tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20))  # active, paused, completed, stopped
    adherence_rate = Column(Float)  # 0-100
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    measurements = relationship("EffectMeasurement", back_populates="intervent_tracking", cascade="all, delete-orphan")


class EffectMeasurement(Base):
    """效果测量记录"""
    __tablename__ = "effect_measurements"

    id = Column(Integer, primary_key=True, index=True)
    intervient_tracking_id = Column(Integer, ForeignKey("intervent_tracking.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)  # e.g., "blood_pressure", "sleep_duration"
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50))  # e.g., "mmHg", "hours"
    measurement_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    baseline_value = Column(Float)  # Baseline for comparison
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    intervient_tracking = relationship("InterventTracking", back_populates="measurements")


class HealthGoal(Base):
    """健康目标设定"""
    __tablename__ = "health_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)  # e.g., "weight_loss", "bp_control"
    target_value = Column(Float, nullable=False)
    current_value = Column(Float)
    unit = Column(String(50))
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    status = Column(String(20))  # not_started, in_progress, achieved, missed
    interventions = Column(JSON)  # Related intervention IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BiomarkerMeasurement(Base):
    """生物标志物测量"""
    __tablename__ = "biomarker_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    biomarker_name = Column(String(100), nullable=False)  # e.g., "c_reactive_protein", "cholesterol", "glucose"
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # e.g., "mg/L", "mmol/L"
    reference_range_low = Column(Float)
    reference_range_high = Column(Float)
    is_normal = Column(Boolean, default=True)
    measurement_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(50))  # lab, home_test, wearable
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
