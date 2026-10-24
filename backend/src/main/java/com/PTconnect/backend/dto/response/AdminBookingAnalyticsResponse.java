package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AdminBookingAnalyticsResponse {

    private Long id;
    private Long studentId;
    private String studentName;
    private Long ptId;
    private String ptName;
    private BookingType bookingType;
    private BookingStatus status;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private BigDecimal sessionFee;
    private LocalDateTime createdAt;
    private String cancelledBy;
    private String cancellationReason;

    public static AdminBookingAnalyticsResponse fromEntity(Booking b) {
        return fromEntity(b, null, null);
    }

    public static AdminBookingAnalyticsResponse fromEntity(Booking b, String cancelledBy, String cancellationReason) {
        if (b == null) return null;
        return AdminBookingAnalyticsResponse.builder()
                .id(b.getId())
                .studentId(b.getStudent() != null ? b.getStudent().getId() : null)
                .studentName(b.getStudent() != null ? b.getStudent().getFullName() : null)
                .ptId(b.getPt() != null ? b.getPt().getId() : null)
                .ptName(b.getPt() != null && b.getPt().getPt() != null ? b.getPt().getPt().getFullName() : null)
                .bookingType(b.getBookingType())
                .status(b.getStatus())
                .startTime(b.getSlot() != null ? b.getSlot().getStartTime() : null)
                .endTime(b.getSlot() != null ? b.getSlot().getEndTime() : null)
                .sessionFee(b.getSessionFee())
                .createdAt(b.getCreatedAt())
                .cancelledBy(cancelledBy)
                .cancellationReason(cancellationReason)
                .build();
    }
}
