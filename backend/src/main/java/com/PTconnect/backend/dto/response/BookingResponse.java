package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.Cancellation;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO phản hồi thông tin chi tiết đơn đặt lịch ca tập (Milestone 6 - Hưng).
 * Ghép đầy đủ thông tin Học viên, Huấn luyện viên, Khung giờ và Hợp đồng.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookingResponse {

    private Long id;

    // Thông tin học viên
    private Long studentId;
    private String studentName;
    private String studentEmail;
    private String studentPhone;
    private String studentAvatarUrl;

    // Thông tin Huấn luyện viên
    private Long ptId;
    private Long ptUserId;
    private String ptName;
    private String ptEmail;
    private String ptPhone;
    private String ptAvatarUrl;

    // Thông tin khung giờ (Slot)
    private Long slotId;
    private LocalDateTime startTime;
    private LocalDateTime endTime;

    // Chi tiết ca tập
    private BookingType bookingType;
    private BookingStatus status;
    private BigDecimal sessionFee;
    private String studentNote;
    private String trainingLocation;

    // Hợp đồng liên kết (nếu là PACKAGE)
    private Long enrollmentId;
    private String courseTitle;

    // Thông tin hủy lịch (nếu booking đã bị hủy)
    private String cancellationReason;
    private String cancelledByRole;
    private LocalDateTime cancelledAt;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static BookingResponse fromEntity(Booking booking) {
        return fromEntity(booking, null);
    }

    public static BookingResponse fromEntity(Booking booking, Cancellation cancellation) {
        if (booking == null) {
            return null;
        }

        BookingResponseBuilder builder = BookingResponse.builder()
                .id(booking.getId())
                .bookingType(booking.getBookingType())
                .status(booking.getStatus())
                .sessionFee(booking.getSessionFee())
                .studentNote(booking.getStudentNote())
                .trainingLocation(booking.getTrainingLocation())
                .createdAt(booking.getCreatedAt())
                .updatedAt(booking.getUpdatedAt());

        if (booking.getStudent() != null) {
            builder.studentId(booking.getStudent().getId())
                    .studentName(booking.getStudent().getFullName())
                    .studentEmail(booking.getStudent().getEmail())
                    .studentPhone(booking.getStudent().getPhone())
                    .studentAvatarUrl(booking.getStudent().getAvatarUrl());
        }

        if (booking.getPt() != null) {
            builder.ptId(booking.getPt().getId());
            if (booking.getPt().getPt() != null) {
                builder.ptUserId(booking.getPt().getPt().getId())
                        .ptName(booking.getPt().getPt().getFullName())
                        .ptEmail(booking.getPt().getPt().getEmail())
                        .ptPhone(booking.getPt().getPt().getPhone())
                        .ptAvatarUrl(booking.getPt().getPt().getAvatarUrl());
            }
        }

        if (booking.getSlot() != null) {
            builder.slotId(booking.getSlot().getId())
                    .startTime(booking.getSlot().getStartTime())
                    .endTime(booking.getSlot().getEndTime());
        }

        if (booking.getEnrollment() != null) {
            builder.enrollmentId(booking.getEnrollment().getId());
            if (booking.getEnrollment().getCourse() != null) {
                builder.courseTitle(booking.getEnrollment().getCourse().getTitle());
            }
            if (builder.trainingLocation == null && booking.getEnrollment().getTrainingLocation() != null) {
                builder.trainingLocation(booking.getEnrollment().getTrainingLocation());
            }
        } else if (booking.getBookingType() == BookingType.TRIAL && booking.getPt() != null) {
            if (builder.trainingLocation == null) {
                builder.trainingLocation(booking.getPt().getAvailableLocations());
            }
        }

        if (cancellation != null) {
            builder.cancellationReason(cancellation.getReason())
                    .cancelledByRole(cancellation.getCancelledByRole())
                    .cancelledAt(cancellation.getCancelledAt());
        }

        return builder.build();
    }
}
