"""User authentication and authorization models"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RefreshToken(Base):
    """Refresh token for JWT"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserHealthProfile(Base):
    """用户健康档案"""
    __tablename__ = "user_health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    age = Column(Integer)
    gender = Column(String(10))
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    medical_conditions = Column(JSON)  # List of conditions
    allergies = Column(JSON)  # List of allergies
    current_medications = Column(JSON)  # List of medications
    family_history = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
