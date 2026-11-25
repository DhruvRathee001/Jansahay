from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="citizen")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    profile: Mapped["CitizenProfile | None"] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class CitizenProfile(Base):
    __tablename__ = "citizen_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    annual_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(80), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    social_category: Mapped[str | None] = mapped_column(String(30), nullable=True)
    residence_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    housing_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    family_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    land_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    disability: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    disability_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    pregnant: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    girl_children: Mapped[int | None] = mapped_column(Integer, nullable=True)
    only_girl_children: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    marks_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_family_id: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    breadwinner_deceased: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    student: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_bank_account: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    existing_benefits: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="profile")


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    department: Mapped[str] = mapped_column(String(180))
    category: Mapped[str] = mapped_column(String(80), index=True)
    scope: Mapped[str] = mapped_column(String(80), default="Central Government")
    summary: Mapped[str] = mapped_column(Text)
    benefits: Mapped[str] = mapped_column(Text)
    application_steps: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    rules: Mapped[list] = mapped_column(JSON, default=list)
    conflicts: Mapped[list] = mapped_column(JSON, default=list)
    official_url: Mapped[str] = mapped_column(String(500))
    application_portal_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_verified_on: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    checks: Mapped[list["EligibilityCheck"]] = relationship(back_populates="scheme")


class EligibilityCheck(Base):
    __tablename__ = "eligibility_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    score: Mapped[float] = mapped_column(Float, default=0)
    matched_conditions: Mapped[list] = mapped_column(JSON, default=list)
    failed_conditions: Mapped[list] = mapped_column(JSON, default=list)
    missing_information: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    scheme: Mapped[Scheme] = relationship(back_populates="checks")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("user_id", "document_type", "file_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(80))
    file_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_fields: Mapped[dict] = mapped_column(JSON, default=dict)
    validation_status: Mapped[str] = mapped_column(String(40), default="UPLOADED")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expiry_date: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped[User] = relationship(back_populates="documents")

