from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    age: int | None = Field(default=None, ge=0, le=120)
    state: str | None = Field(default=None, max_length=80)
    district: str | None = Field(default=None, max_length=80)
    annual_income: float | None = Field(default=None, ge=0)
    occupation: str | None = Field(default=None, max_length=80)
    education_level: str | None = Field(default=None, max_length=80)
    social_category: str | None = Field(default=None, max_length=30)
    residence_type: str | None = Field(default=None, max_length=20)
    housing_status: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=30)
    marital_status: str | None = Field(default=None, max_length=30)
    family_size: int | None = Field(default=None, ge=1, le=50)
    land_acres: float | None = Field(default=None, ge=0)
    disability: bool | None = None
    disability_percent: float | None = Field(default=None, ge=0, le=100)
    pregnant: bool | None = None
    girl_children: int | None = Field(default=None, ge=0, le=30)
    only_girl_children: bool | None = None
    marks_percentage: float | None = Field(default=None, ge=0, le=100)
    has_family_id: bool | None = None
    breadwinner_deceased: bool | None = None
    student: bool | None = None
    has_bank_account: bool | None = None
    existing_benefits: list[str] | None = None


class ProfileOut(ProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class SchemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    department: str
    category: str
    scope: str
    summary: str
    benefits: str
    application_steps: list[Any]
    required_documents: list[Any]
    rules: list[Any]
    conflicts: list[Any]
    official_url: str
    application_portal_url: str | None = None
    source_verified_on: str
    eligibility_status: str | None = None
    eligibility_score: float | None = None


class AdminSchemeCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=180)
    department: str = Field(min_length=2, max_length=180)
    category: str = Field(min_length=2, max_length=80)
    scope: str = Field(pattern="^(Central Government|Haryana Government)$")
    summary: str = Field(min_length=2)
    benefits: str = Field(min_length=2)
    application_steps: list[Any] = Field(default_factory=list)
    required_documents: list[Any] = Field(default_factory=list)
    rules: list[Any] = Field(default_factory=list)
    conflicts: list[Any] = Field(default_factory=list)
    official_url: str = Field(min_length=5, max_length=500)
    application_portal_url: str | None = Field(default=None, max_length=500)
    source_verified_on: str = Field(min_length=4, max_length=20)
    is_active: bool = True


class AdminSchemeUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    name: str | None = Field(default=None, min_length=2, max_length=180)
    department: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    scope: str | None = Field(default=None, pattern="^(Central Government|Haryana Government)$")
    summary: str | None = Field(default=None, min_length=2)
    benefits: str | None = Field(default=None, min_length=2)
    application_steps: list[Any] | None = None
    required_documents: list[Any] | None = None
    rules: list[Any] | None = None
    conflicts: list[Any] | None = None
    official_url: str | None = Field(default=None, min_length=5, max_length=500)
    application_portal_url: str | None = Field(default=None, max_length=500)
    source_verified_on: str | None = Field(default=None, min_length=4, max_length=20)
    is_active: bool | None = None


class RecommendationRequest(BaseModel):
    query: str = Field(min_length=2, max_length=800)


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str
    file_name: str
    validation_status: str
    extracted_text: str | None
    extracted_fields: dict
    uploaded_at: datetime
    expiry_date: str | None

