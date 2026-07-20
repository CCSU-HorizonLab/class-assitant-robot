"""Authentication request and response schemas."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., min_length=6, max_length=120)
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)
    verification_code: str = Field(..., min_length=4, max_length=12)
    display_name: Optional[str] = Field(default=None, max_length=80)
    classroom_id: Optional[str] = Field(default=None, max_length=80)
    classroom_name: Optional[str] = Field(default=None, max_length=120)


class EmailCodeRequest(BaseModel):
    email: str = Field(..., min_length=6, max_length=120)


class UserCreateRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=6)
    role: str = "teacher"
    classroom_id: Optional[str] = None
    classroom_name: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: str


class UserUpdateRequest(BaseModel):
    """Fields that can be updated by admin for a user."""
    display_name: Optional[str] = Field(default=None, max_length=80)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)


class ClassroomCreateRequest(BaseModel):
    """Create or update a classroom."""
    classroom_id: str = Field(..., min_length=1, max_length=80)
    classroom_name: Optional[str] = Field(default=None, max_length=120)


class ClassroomBindRequest(BaseModel):
    """Bind a teacher to a classroom."""
    user_id: str
    classroom_id: str
    classroom_name: Optional[str] = Field(default=None, max_length=120)


class AISummaryRequest(BaseModel):
    result_id: str
