"""SQLAlchemy models for database"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Intervention(Base):
    """干预措施模型"""
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    description = Column(Text)
    category = Column(String(50), nullable=False)  # nutrition, exercise, sleep, supplement, medical
    mechanism = Column(Text)
    evidence_level = Column(Integer, default=4)  # 1-4
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evidence = relationship("Evidence", back_populates="intervention", cascade="all, delete-orphan")


class Evidence(Base):
    """证据模型"""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    source_type = Column(String(50))  # randomized_trial, cohort_study, case_control, meta_analysis, expert
    pubmed_id = Column(String(50))
    citation = Column(Text)
    sample_size = Column(Integer)
    duration_days = Column(Integer)
    effect_size = Column(JSON)  # {"metric": "hazard_ratio|mean_difference", "value": 0.85, "ci_95": [0.78, 0.92]}
    outcomes = Column(JSON)  # List of outcomes
    quality_score = Column(Float)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    intervention = relationship("Intervention", back_populates="evidence")


class RiskFactor(Base):
    """风险因素模型"""
    __tablename__ = "risk_factors"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    name = Column(String(200))
    severity = Column(String(20))  # mild, moderate, severe
    frequency = Column(Float)  # percentage
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Benefit(Base):
    """收益模型"""
    __tablename__ = "benefits"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    name = Column(String(200))
    category = Column(String(50))  # longevity, health, disease_prevention
    effect_size = Column(Float)
    confidence = Column(Float)  # 0-100
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """推荐模型"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    intervention_id = Column(Integer, ForeignKey("interventions.id"))
    priority = Column(Integer, default=5)  # 1-10
    reasoning = Column(Text)
    risk_score = Column(Float)
    benefit_score = Column(Float)
    net_benefit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
