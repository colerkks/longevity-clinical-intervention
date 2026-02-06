"""Pydantic schemas for authentication"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class HealthProfileCreate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    weight: Optional[float] = Field(None, ge=0, le=500)
    height: Optional[float] = Field(None, ge=0, le=300)
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=150)
    heart_rate: Optional[int] = Field(None, ge=30, le=220)
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    family_history: Optional[dict] = None


class HealthProfileResponse(HealthProfileCreate):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
