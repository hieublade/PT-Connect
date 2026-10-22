package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "enrollments")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private User student;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pt_id", nullable = false)
    private PTProfile pt;

    @Column(name = "training_location", nullable = false, length = 255)
    private String trainingLocation;

    @Column(name = "final_price", nullable = false, precision = 12, scale = 2)
    private BigDecimal finalPrice;

    @Column(name = "total_sessions", nullable = false)
    private Integer totalSessions;

    @Column(name = "remaining_sessions", nullable = false)
    private Integer remainingSessions;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;

    @Column(name = "contract_url", nullable = false, length = 500)
    private String contractUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private EnrollmentStatus status = EnrollmentStatus.ACTIVE;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    // Phương thức nghiệp vụ quản lý kho buổi tập (Encapsulation)
    public void consumeSession() {
        if (this.status != EnrollmentStatus.ACTIVE) {
            throw new IllegalStateException("Hợp đồng không ở trạng thái hoạt động (ACTIVE)");
        }
        if (this.remainingSessions == null || this.remainingSessions <= 0) {
            throw new IllegalStateException("Hợp đồng đã sử dụng hết số buổi tập khả dụng");
        }
        this.remainingSessions--;
    }

    public void restoreSession() {
        if (this.remainingSessions != null && this.totalSessions != null) {
            if (this.remainingSessions < this.totalSessions) {
                this.remainingSessions++;
            }
        }
    }
}
