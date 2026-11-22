package com.PTconnect.backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "reviews")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Review {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "booking_id", nullable = false, unique = true)
    private Booking booking;

    @Column(nullable = false)
    private Integer rating;

    @Column(columnDefinition = "TEXT")
    private String comment;

    // Trạng thái kiểm duyệt: PUBLISHED (4-5 sao hoặc Admin giữ lại), FLAGGED (1-3 sao chờ phản biện), 
    // APPEALED (HLV đã gửi phản biện), EVIDENCE_REQUESTED (Admin yêu cầu thêm bằng chứng), REMOVED (Admin xóa bỏ đánh giá xấu)
    @Column(name = "status", length = 30)
    @Builder.Default
    private String status = "PUBLISHED";

    // Phản biện từ Huấn luyện viên
    @Column(name = "pt_appeal", columnDefinition = "TEXT")
    private String ptAppeal;

    @Column(name = "pt_evidence", columnDefinition = "TEXT")
    private String ptEvidence;

    @Column(name = "pt_appealed_at")
    private LocalDateTime ptAppealedAt;

    // Bằng chứng bổ sung từ Học viên
    @Column(name = "student_evidence", columnDefinition = "TEXT")
    private String studentEvidence;

    // Phán quyết từ Quản trị viên (Admin)
    @Column(name = "admin_decision", length = 50)
    private String adminDecision; // REMOVE, KEEP, REQUEST_EVIDENCE

    @Column(name = "admin_note", columnDefinition = "TEXT")
    private String adminNote;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
        if (this.status == null || this.status.isBlank()) {
            if (this.rating != null && this.rating <= 3) {
                this.status = "FLAGGED";
            } else {
                this.status = "PUBLISHED";
            }
        }
    }
}
