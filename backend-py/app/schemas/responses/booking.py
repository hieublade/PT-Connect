
from app.models.booking import Booking
from app.models.cancellation import Cancellation
from app.models.enums import BookingStatus, BookingType
from app.schemas.base import CamelModel, LocalDateTime, Money


class CancelPreviewResponse(CamelModel):
    booking_id: int
    cancelled_by_role: str
    hours_before_session: Money
    restore_session: bool
    refund_amount: Money
    compensation_amount: Money
    penalty_amount: Money
    explanation: str


class BookingResponse(CamelModel):
    id: int

    # Student info
    student_id: int | None = None
    student_name: str | None = None
    student_email: str | None = None
    student_phone: str | None = None
    student_avatar_url: str | None = None

    # PT info
    pt_id: int | None = None
    pt_user_id: int | None = None
    pt_name: str | None = None
    pt_email: str | None = None
    pt_phone: str | None = None
    pt_avatar_url: str | None = None

    # Slot info
    slot_id: int | None = None
    start_time: LocalDateTime | None = None
    end_time: LocalDateTime | None = None

    # Booking details
    booking_type: BookingType
    status: BookingStatus
    session_fee: Money
    student_note: str | None = None
    training_location: str | None = None

    # Enrollment info
    enrollment_id: int | None = None
    course_title: str | None = None

    # Cancellation info
    cancellation_reason: str | None = None
    cancelled_by_role: str | None = None
    cancelled_at: LocalDateTime | None = None

    created_at: LocalDateTime | None = None
    updated_at: LocalDateTime | None = None

    @classmethod
    def from_entity(
        cls,
        booking: Booking | None,
        cancellation: Cancellation | None = None,
    ) -> "BookingResponse | None":
        if booking is None:
            return None

        # Student info
        s_id = booking.student.id if booking.student else None
        s_name = booking.student.full_name if booking.student else None
        s_email = booking.student.email if booking.student else None
        s_phone = booking.student.phone if booking.student else None
        s_avatar = booking.student.avatar_url if booking.student else None

        # PT info
        p_id = booking.pt.id if booking.pt else None
        p_u_id = None
        p_name = None
        p_email = None
        p_phone = None
        p_avatar = None
        if booking.pt and booking.pt.pt:
            p_u_id = booking.pt.pt.id
            p_name = booking.pt.pt.full_name
            p_email = booking.pt.pt.email
            p_phone = booking.pt.pt.phone
            p_avatar = booking.pt.pt.avatar_url

        # Slot info
        slot_id = booking.slot.id if booking.slot else None
        start_time = booking.slot.start_time if booking.slot else None
        end_time = booking.slot.end_time if booking.slot else None

        # Location & course
        enrollment_id = None
        course_title = None
        location = booking.get_training_location()

        if booking.enrollment is not None:
            enrollment_id = booking.enrollment.id
            if booking.enrollment.course is not None:
                course_title = booking.enrollment.course.title
            if not location:
                location = booking.enrollment.training_location
        elif booking.booking_type == BookingType.TRIAL and booking.pt is not None:
            if not location:
                location = booking.pt.available_locations

        # Cancellation info
        canc = cancellation or booking.cancellation
        canc_reason = None
        canc_role = None
        canc_at = None
        if canc is not None:
            canc_reason = canc.reason
            canc_role = canc.cancelled_by_role
            canc_at = canc.cancelled_at

        return cls(
            id=booking.id,
            student_id=s_id,
            student_name=s_name,
            student_email=s_email,
            student_phone=s_phone,
            student_avatar_url=s_avatar,
            pt_id=p_id,
            pt_user_id=p_u_id,
            pt_name=p_name,
            pt_email=p_email,
            pt_phone=p_phone,
            pt_avatar_url=p_avatar,
            slot_id=slot_id,
            start_time=start_time,
            end_time=end_time,
            booking_type=booking.booking_type,
            status=booking.status,
            session_fee=booking.session_fee,
            student_note=booking.student_note,
            training_location=location,
            enrollment_id=enrollment_id,
            course_title=course_title,
            cancellation_reason=canc_reason,
            cancelled_by_role=canc_role,
            cancelled_at=canc_at,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
