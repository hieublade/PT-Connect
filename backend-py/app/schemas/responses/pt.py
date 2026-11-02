from decimal import Decimal
from typing import Any

from app.models.availability_slot import AvailabilitySlot
from app.models.course import Course
from app.models.enums import CourseStatus, SlotStatus, UserStatus, VerificationStatus
from app.models.pt_profile import PTProfile
from app.schemas.base import CamelModel, LocalDateTime, Money


class PTProfileResponse(CamelModel):
    id: int
    user_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    experience_years: int = 0
    available_locations: str | None = None
    location_pricing_note: str | None = None
    certificate_urls: Any | None = None
    average_rating: float = 0.0
    total_reviews: int = 0
    verification_status: VerificationStatus
    user_status: UserStatus | None = None
    created_at: LocalDateTime | None = None
    updated_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, profile: PTProfile | None) -> "PTProfileResponse | None":
        if profile is None:
            return None

        u_id = None
        name = None
        mail = None
        tel = None
        avatar = None
        u_status = None

        if profile.pt is not None:
            u_id = profile.pt.id
            name = profile.pt.full_name
            mail = profile.pt.email
            tel = profile.pt.phone
            avatar = profile.pt.avatar_url
            u_status = profile.pt.status

        rating_val = float(profile.average_rating) if profile.average_rating is not None else 0.0
        reviews_val = profile.total_reviews if profile.total_reviews is not None else 0

        return cls(
            id=profile.id,
            user_id=u_id,
            full_name=name,
            email=mail,
            phone=tel,
            avatar_url=avatar,
            bio=profile.bio,
            experience_years=profile.experience_years if profile.experience_years is not None else 0,
            available_locations=profile.available_locations,
            location_pricing_note=profile.location_pricing_note,
            certificate_urls=profile.certificate_urls,
            average_rating=rating_val,
            total_reviews=reviews_val,
            verification_status=profile.verification_status,
            user_status=u_status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )


class PTPublicDTO(CamelModel):
    id: int
    user_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    experience_years: int = 0
    available_locations: str | None = None
    location_pricing_note: str | None = None
    average_rating: float = 0.0
    total_reviews: int = 0
    lowest_price: Money | None = None
    verification_status: VerificationStatus

    @classmethod
    def from_entity(cls, profile: PTProfile | None, lowest_price: Decimal | None = None) -> "PTPublicDTO | None":
        if profile is None:
            return None

        u_id = None
        name = None
        mail = None
        tel = None
        avatar = None

        if profile.pt is not None:
            u_id = profile.pt.id
            name = profile.pt.full_name
            mail = profile.pt.email
            tel = profile.pt.phone
            avatar = profile.pt.avatar_url

        rating_val = float(profile.average_rating) if profile.average_rating is not None else 0.0
        reviews_val = profile.total_reviews if profile.total_reviews is not None else 0

        return cls(
            id=profile.id,
            user_id=u_id,
            full_name=name,
            email=mail,
            phone=tel,
            avatar_url=avatar,
            bio=profile.bio,
            experience_years=profile.experience_years if profile.experience_years is not None else 0,
            available_locations=profile.available_locations,
            location_pricing_note=profile.location_pricing_note,
            average_rating=rating_val,
            total_reviews=reviews_val,
            lowest_price=lowest_price,
            verification_status=profile.verification_status,
        )


class CourseResponse(CamelModel):
    id: int
    pt_id: int | None = None
    pt_name: str | None = None
    title: str
    description: str | None = None
    total_sessions: int
    validity_days: int
    base_price: Money
    status: CourseStatus
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, course: Course | None) -> "CourseResponse | None":
        if course is None:
            return None

        pt_id = None
        pt_name = None
        if course.pt is not None:
            pt_id = course.pt.id
            if course.pt.pt is not None:
                pt_name = course.pt.pt.full_name

        return cls(
            id=course.id,
            pt_id=pt_id,
            pt_name=pt_name,
            title=course.title,
            description=course.description,
            total_sessions=course.total_sessions,
            validity_days=course.validity_days,
            base_price=course.base_price,
            status=course.status,
            created_at=course.created_at,
        )


class SlotResponse(CamelModel):
    id: int
    pt_id: int | None = None
    pt_name: str | None = None
    start_time: LocalDateTime
    end_time: LocalDateTime
    status: SlotStatus
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, slot: AvailabilitySlot | None) -> "SlotResponse | None":
        if slot is None:
            return None

        pt_id = None
        pt_name = None
        if slot.pt is not None:
            pt_id = slot.pt.id
            if slot.pt.pt is not None:
                pt_name = slot.pt.pt.full_name

        return cls(
            id=slot.id,
            pt_id=pt_id,
            pt_name=pt_name,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status=slot.status,
            created_at=slot.created_at,
        )


class PendingPTResponse(CamelModel):
    id: int
    user_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    experience_years: int = 0
    available_locations: str | None = None
    location_pricing_note: str | None = None
    certificate_urls: Any | None = None
    verification_status: VerificationStatus
    user_status: UserStatus | None = None
    created_at: LocalDateTime | None = None

    @classmethod
    def from_entity(cls, profile: PTProfile | None) -> "PendingPTResponse | None":
        if profile is None:
            return None

        u_id = None
        name = None
        mail = None
        tel = None
        avatar = None
        u_status = None

        if profile.pt is not None:
            u_id = profile.pt.id
            name = profile.pt.full_name
            mail = profile.pt.email
            tel = profile.pt.phone
            avatar = profile.pt.avatar_url
            u_status = profile.pt.status

        return cls(
            id=profile.id,
            user_id=u_id,
            full_name=name,
            email=mail,
            phone=tel,
            avatar_url=avatar,
            bio=profile.bio,
            experience_years=profile.experience_years if profile.experience_years is not None else 0,
            available_locations=profile.available_locations,
            location_pricing_note=profile.location_pricing_note,
            certificate_urls=profile.certificate_urls,
            verification_status=profile.verification_status,
            user_status=u_status,
            created_at=profile.created_at,
        )
