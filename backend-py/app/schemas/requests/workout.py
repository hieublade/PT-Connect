from datetime import date
from decimal import Decimal

from pydantic import field_validator

from app.schemas.base import CamelModel


class CreateWorkoutPlanRequest(CamelModel):
    enrollment_id: int
    title: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tiêu đề giáo án không được để trống")
        return v.strip()


class CreateWorkoutRequest(CamelModel):
    exercise_order: int | None = None
    exercise_name: str
    target_muscle: str | None = None
    sets: int
    reps: int
    weight_kg: Decimal | None = None
    rest_seconds: int
    video_demo_url: str | None = None

    @field_validator("exercise_name")
    @classmethod
    def validate_exercise_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên bài tập không được để trống")
        return v.strip()

    @field_validator("sets")
    @classmethod
    def validate_sets(cls, v: int) -> int:
        if v is None:
            raise ValueError("Số hiệp (sets) không được để trống")
        if v < 1:
            raise ValueError("Số hiệp phải lớn hơn 0")
        return v

    @field_validator("reps")
    @classmethod
    def validate_reps(cls, v: int) -> int:
        if v is None:
            raise ValueError("Số lần lặp (reps) không được để trống")
        if v < 1:
            raise ValueError("Số lần lặp phải lớn hơn 0")
        return v

    @field_validator("rest_seconds")
    @classmethod
    def validate_rest_seconds(cls, v: int) -> int:
        if v is None:
            raise ValueError("Thời gian nghỉ không được để trống")
        if v < 0:
            raise ValueError("Thời gian nghỉ không được âm")
        return v
