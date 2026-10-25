from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class StudentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if value is None:
            raise ValueError("Full name cannot be empty.")
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Full name cannot be empty.")
        return cleaned

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = _clean_optional_text(str(value))
        if cleaned is None:
            return None
        if len(cleaned) < 7:
            raise ValueError("Phone number must contain at least 7 characters.")
        if not cleaned.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone number must contain digits, spaces, +, or - only.")
        return cleaned

    @field_validator("email", "course", "address", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return _clean_optional_text(value)
        return value

    @model_validator(mode="after")
    def ensure_contact_info(self):
        if self.email is None and self.phone is None:
            raise ValueError("Either email or phone number is required.")
        return self


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date


class StudentPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Full name cannot be empty.")
        return cleaned

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = _clean_optional_text(str(value))
        if cleaned is None:
            return None
        if len(cleaned) < 7:
            raise ValueError("Phone number must contain at least 7 characters.")
        if not cleaned.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone number must contain digits, spaces, +, or - only.")
        return cleaned

    @field_validator("email", "course", "address", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return _clean_optional_text(value)
        return value


class StudentResponse(StudentBase):
    student_id: int


class StudentListFilter(BaseModel):
    name: Optional[str] = None
    course: Optional[str] = None
    date_of_birth: Optional[date] = None
