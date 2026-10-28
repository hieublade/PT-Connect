package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "bookings")
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Booking {

    @Id
    @Setter
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // N-1 với users (student_id trỏ users.id)
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "student_id", nullable = false)
    private User student;

    // N-1 với pt_profiles (pt_id trỏ pt_profiles.id, KHÔNG phải users.id)
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "pt_id", nullable = false)
    private PTProfile pt;

    // N-1 với availability_slots (slot_id trỏ availability_slots.id)
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "slot_id", nullable = false)
    private AvailabilitySlot slot;

    // N-1 với enrollments (NULL nếu là TRIAL; Bắt buộc có nếu là PACKAGE)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "enrollment_id")
    private Enrollment enrollment;

    @Enumerated(EnumType.STRING)
    @Column(name = "booking_type", nullable = false)
    @Builder.Default
    private BookingType bookingType = BookingType.PACKAGE;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private BookingStatus status = BookingStatus.PENDING;

    @Column(name = "session_fee", nullable = false, precision = 12, scale = 2)
    private BigDecimal sessionFee;

    @Setter
    @Column(name = "student_note", length = 255)
    private String studentNote;

    // active_slot_id: cột sinh tự động (generated), chỉ đọc
    // Chỉ khác NULL khi booking còn hiệu lực (status IN PENDING, CONFIRMED, COMPLETED)
    @Column(name = "active_slot_id", insertable = false, updatable = false)
    private Long activeSlotId;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", insertable = false, updatable = false)
    private LocalDateTime updatedAt;

    // Địa điểm tập tự động lấy theo hợp đồng (đối với PACKAGE)
    public String getTrainingLocation() {
        return this.enrollment != null ? this.enrollment.getTrainingLocation() : null;
    }

    // Phương thức nghiệp vụ tự bảo vệ trạng thái (Encapsulation / State Transition)
    public void confirm() {
        if (this.status != BookingStatus.PENDING) {
            throw new IllegalStateException("Chỉ có thể xác nhận đơn đặt lịch đang ở trạng thái PENDING. Trạng thái hiện tại: " + this.status);
        }
        this.status = BookingStatus.CONFIRMED;
    }

    public void cancel() {
        if (this.status == BookingStatus.CANCELLED) {
            throw new IllegalStateException("Đơn đặt lịch đã ở trạng thái CANCELLED trước đó.");
        }
        if (this.status == BookingStatus.COMPLETED) {
            throw new IllegalStateException("Không thể hủy ca tập đã hoàn thành (COMPLETED).");
        }
        this.status = BookingStatus.CANCELLED;
    }

    public void complete() {
        if (this.status != BookingStatus.CONFIRMED) {
            throw new IllegalStateException("Chỉ có thể hoàn thành ca tập đã được xác nhận (CONFIRMED). Trạng thái hiện tại: " + this.status);
        }
        this.status = BookingStatus.COMPLETED;
    }
}

