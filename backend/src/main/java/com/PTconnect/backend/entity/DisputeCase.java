package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.Role;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Thực thể Lưu trữ Hồ sơ Tranh chấp & Khiếu nại giữa Huấn luyện viên và Học viên.
 */
@Entity
@Table(name = "dispute_cases")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DisputeCase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "booking_id")
    private Booking booking;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "enrollment_id")
    private Enrollment enrollment;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "complainant_id", nullable = false)
    private User complainant;

    @Enumerated(EnumType.STRING)
    @Column(name = "complainant_role", nullable = false)
    private Role complainantRole;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "defendant_id")
    private User defendant;

    @Column(name = "dispute_type", nullable = false)
    private String disputeType; // PT_ABSENT, LATE_CANCEL_STUDENT, OTP_PREMATURE, QUALITY_ISSUE, CONTRACT_TERMINATION, OTHER

    @Column(name = "dispute_type_label", nullable = false)
    private String disputeTypeLabel;

    @Column(name = "severity", nullable = false)
    private String severity; // HIGH, MEDIUM, LOW

    @Column(name = "summary", length = 500)
    private String summary;

    @Column(name = "statement", columnDefinition = "TEXT", nullable = false)
    private String statement;

    @Column(name = "counter_statement", columnDefinition = "TEXT")
    private String counterStatement;

    @Column(name = "evidence_note", columnDefinition = "TEXT")
    private String evidenceNote;

    @Column(name = "evidence_requested")
    private Boolean evidenceRequested;

    @Column(name = "evidence_request_target")
    private String evidenceRequestTarget; // BOTH, PT, STUDENT

    @Column(name = "evidence_request_note", columnDefinition = "TEXT")
    private String evidenceRequestNote;

    @Column(name = "additional_evidence_pt", columnDefinition = "TEXT")
    private String additionalEvidencePt;

    @Column(name = "additional_evidence_student", columnDefinition = "TEXT")
    private String additionalEvidenceStudent;

    @Column(name = "student_evidence_submitted")
    private Boolean studentEvidenceSubmitted;

    @Column(name = "pt_evidence_submitted")
    private Boolean ptEvidenceSubmitted;

    @Column(name = "session_fee")
    private BigDecimal sessionFee;

    @Column(name = "status", nullable = false)
    private String status; // PENDING_ARBITRATION, AWAITING_EVIDENCE, RESOLVED_REFUND_STUDENT, RESOLVED_PAID_PT, RESOLVED_FORCE_MAJEURE, RESOLVED_CONTRACT_TERMINATION

    @Column(name = "verdict_type")
    private String verdictType; // REFUND_STUDENT, PAID_PT, FORCE_MAJEURE, CANCEL_CONTRACT_REFUND_STUDENT, CANCEL_CONTRACT_PAID_PT

    @Column(name = "resolution_decision", columnDefinition = "TEXT")
    private String resolutionDecision;

    @Column(name = "verdict_reason", columnDefinition = "TEXT")
    private String verdictReason;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
        if (this.status == null) {
            this.status = "PENDING_ARBITRATION";
        }
        if (this.severity == null) {
            this.severity = "MEDIUM";
        }
    }
}
