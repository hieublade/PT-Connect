package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.CancellationStatus;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "cancellations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Cancellation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 1-1 với bookings (booking_id UNIQUE)
    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "booking_id", nullable = false, unique = true)
    private Booking booking;

    // cancelled_by_id trỏ users.id (có thể NULL nếu hệ thống tự hủy)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cancelled_by_id")
    private User cancelledBy;

    @Column(name = "cancelled_by_role", nullable = false, length = 20)
    @Builder.Default
    private String cancelledByRole = "STUDENT";

    @Column(nullable = false, length = 500)
    private String reason;

    @Column(name = "cancelled_at", insertable = false, updatable = false)
    private LocalDateTime cancelledAt;

    @Column(name = "hours_before_session", nullable = false, precision = 5, scale = 2)
    private BigDecimal hoursBeforeSession;

    @Column(name = "refund_amount", nullable = false, precision = 12, scale = 2)
    @Builder.Default
    private BigDecimal refundAmount = BigDecimal.ZERO;

    @Column(name = "compensation_amount", nullable = false, precision = 12, scale = 2)
    @Builder.Default
    private BigDecimal compensationAmount = BigDecimal.ZERO;

    @Column(name = "penalty_amount", nullable = false, precision = 12, scale = 2)
    @Builder.Default
    private BigDecimal penaltyAmount = BigDecimal.ZERO;

    @Column(name = "evidence_url", length = 500)
    private String evidenceUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private CancellationStatus status = CancellationStatus.PROCESSED;
}

