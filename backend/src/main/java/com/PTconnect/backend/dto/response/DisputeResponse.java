package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.DisputeCase;
import lombok.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DisputeResponse {

    private Long id;
    private Long bookingId;
    private Long enrollmentId;
    private Boolean isContractDispute;
    private String studentName;
    private String studentEmail;
    private String studentPhone;
    private String ptName;
    private String ptEmail;
    private String courseTitle;
    private BigDecimal sessionFee;
    private String scheduledTime;
    private String disputeType;
    private String disputeTypeLabel;
    private String severity;
    private String complainant; // STUDENT or PT
    private String summary;
    private String studentStatement;
    private String ptStatement;
    private String evidenceNote;
    private String counterStatement;
    private Boolean evidenceRequested;
    private String evidenceRequestTarget; // BOTH, PT, STUDENT
    private String evidenceRequestNote;
    private String additionalEvidencePt;
    private String additionalEvidenceStudent;
    private Boolean studentEvidenceSubmitted;
    private Boolean ptEvidenceSubmitted;
    private String status;
    private String verdictType;
    private String resolutionDecision;
    private String verdictReason;
    private LocalDateTime resolvedAt;
    private LocalDateTime createdAt;
    private LocalDateTime counterDeadline;
    private Boolean canAdminArbitrate;
    private String waitingReason;
    private Long hoursRemaining;
    private Integer minutesRemaining;

    public static DisputeResponse fromEntity(DisputeCase entity) {
        if (entity == null) return null;

        String studentName = "Học viên";
        String studentEmail = "";
        String studentPhone = "";
        String ptName = "Huấn luyện viên";
        String ptEmail = "";
        String courseTitle = "Ca tập cá nhân";
        String scheduledTime = "Chưa rõ thời gian";
        boolean isContract = entity.getEnrollment() != null &&
                ("CONTRACT_TERMINATION".equalsIgnoreCase(entity.getDisputeType())
                        || (entity.getDisputeType() != null && entity.getDisputeType().toUpperCase().contains("CONTRACT"))
                        || (entity.getDisputeTypeLabel() != null && entity.getDisputeTypeLabel().toLowerCase().contains("hợp đồng")));

        if (entity.getBooking() != null && !isContract) {
            var b = entity.getBooking();
            if (b.getStudent() != null) {
                studentName = b.getStudent().getFullName();
                studentEmail = b.getStudent().getEmail();
                studentPhone = b.getStudent().getPhone() != null ? b.getStudent().getPhone() : "";
            }
            if (b.getPt() != null && b.getPt().getPt() != null) {
                ptName = b.getPt().getPt().getFullName();
                ptEmail = b.getPt().getPt().getEmail();
            }
            if (b.getSlot() != null) {
                DateTimeFormatter dtf = DateTimeFormatter.ofPattern("HH:mm dd/MM/yyyy");
                scheduledTime = b.getSlot().getStartTime().format(dtf) + " - " + b.getSlot().getEndTime().format(dtf);
            }
            if (b.getEnrollment() != null && b.getEnrollment().getCourse() != null) {
                courseTitle = b.getEnrollment().getCourse().getTitle();
            }
        }

        BigDecimal disputeAmount = entity.getSessionFee();

        if (entity.getEnrollment() != null) {
            var enr = entity.getEnrollment();
            if (enr.getStudent() != null) {
                studentName = enr.getStudent().getFullName();
                studentEmail = enr.getStudent().getEmail();
                studentPhone = enr.getStudent().getPhone() != null ? enr.getStudent().getPhone() : studentPhone;
            }
            if (enr.getPt() != null && enr.getPt().getPt() != null) {
                ptName = enr.getPt().getPt().getFullName();
                ptEmail = enr.getPt().getPt().getEmail();
            }
            if (enr.getCourse() != null) {
                courseTitle = enr.getCourse().getTitle();
            }
            scheduledTime = String.format("Hợp đồng khóa học (#%d) • Còn %d/%d buổi",
                    enr.getId(), enr.getRemainingSessions() != null ? enr.getRemainingSessions() : 0,
                    enr.getTotalSessions() != null ? enr.getTotalSessions() : 0);

            // Tính chính xác giá trị các buổi còn lại theo hợp đồng thay vì chỉ 1 ca tập 300k
            if (isContract) {
                int total = (enr.getTotalSessions() != null && enr.getTotalSessions() > 0) ? enr.getTotalSessions() : 1;
                int remain = enr.getRemainingSessions() != null ? enr.getRemainingSessions() : total;
                if (enr.getFinalPrice() != null) {
                    disputeAmount = enr.getFinalPrice().multiply(BigDecimal.valueOf(remain))
                            .divide(BigDecimal.valueOf(total), 0, RoundingMode.HALF_UP);
                }
            }
        }

        if (disputeAmount == null) {
            disputeAmount = BigDecimal.valueOf(350000);
        }

        String studentStatement = "";
        String ptStatement = "";
        if ("STUDENT".equalsIgnoreCase(entity.getComplainantRole().name())) {
            studentStatement = entity.getStatement();
            ptStatement = entity.getCounterStatement() != null ? entity.getCounterStatement() : "Chờ HLV phản hồi tường trình đối chứng.";
        } else {
            ptStatement = entity.getStatement();
            studentStatement = entity.getCounterStatement() != null ? entity.getCounterStatement() : "Chờ học viên phản hồi tường trình đối chứng.";
        }

        LocalDateTime createdAt = entity.getCreatedAt() != null ? entity.getCreatedAt() : LocalDateTime.now();
        LocalDateTime counterDeadline = createdAt.plusHours(48);
        boolean hasCounter = entity.getCounterStatement() != null && !entity.getCounterStatement().trim().isEmpty();
        boolean isPastDeadline = LocalDateTime.now().isAfter(counterDeadline);
        boolean canArbitrate = hasCounter || isPastDeadline;

        long hoursRemaining = isPastDeadline ? 0 : java.time.Duration.between(LocalDateTime.now(), counterDeadline).toHours();
        long minutesRemaining = isPastDeadline ? 0 : Math.max(0, java.time.Duration.between(LocalDateTime.now(), counterDeadline).toMinutesPart());

        String waitingReason;
        if (entity.getStatus() != null && entity.getStatus().startsWith("RESOLVED")) {
            waitingReason = "Vụ việc đã được Ban Quản Trị ban hành phán quyết.";
        } else if (Boolean.TRUE.equals(entity.getEvidenceRequested())) {
            waitingReason = String.format("Admin đang yêu cầu bổ sung bằng chứng từ: %s (%s)",
                    "BOTH".equals(entity.getEvidenceRequestTarget()) ? "Cả 2 bên" :
                    "PT".equals(entity.getEvidenceRequestTarget()) ? "Huấn luyện viên" : "Học viên",
                    entity.getEvidenceRequestNote() != null ? entity.getEvidenceRequestNote() : "Chờ cung cấp tài liệu");
        } else if (hasCounter) {
            waitingReason = "Đã nhận được bản phản biện đối chứng. Đủ điều kiện ban hành phán quyết.";
        } else if (isPastDeadline) {
            waitingReason = "Đã quá thời hạn 48 giờ đối chất (Bên bị khiếu nại không gửi phản biện). Admin có toàn quyền quyết định.";
        } else {
            waitingReason = String.format("Đang trong thời hạn 48 giờ chờ phản biện đối chứng (Còn %d giờ %d phút).", hoursRemaining, minutesRemaining);
        }

        return DisputeResponse.builder()
                .id(entity.getId())
                .bookingId(isContract ? null : (entity.getBooking() != null ? entity.getBooking().getId() : null))
                .enrollmentId(entity.getEnrollment() != null ? entity.getEnrollment().getId() : null)
                .isContractDispute(isContract)
                .studentName(studentName)
                .studentEmail(studentEmail)
                .studentPhone(studentPhone)
                .ptName(ptName)
                .ptEmail(ptEmail)
                .courseTitle(courseTitle)
                .sessionFee(disputeAmount)
                .scheduledTime(scheduledTime)
                .disputeType(entity.getDisputeType())
                .disputeTypeLabel(entity.getDisputeTypeLabel())
                .severity(entity.getSeverity())
                .complainant(entity.getComplainantRole().name())
                .summary(entity.getSummary())
                .studentStatement(studentStatement)
                .ptStatement(ptStatement)
                .counterStatement(entity.getCounterStatement())
                .evidenceNote(entity.getEvidenceNote())
                .evidenceRequested(Boolean.TRUE.equals(entity.getEvidenceRequested()))
                .evidenceRequestTarget(entity.getEvidenceRequestTarget())
                .evidenceRequestNote(entity.getEvidenceRequestNote())
                .additionalEvidencePt(entity.getAdditionalEvidencePt())
                .additionalEvidenceStudent(entity.getAdditionalEvidenceStudent())
                .studentEvidenceSubmitted(Boolean.TRUE.equals(entity.getStudentEvidenceSubmitted()))
                .ptEvidenceSubmitted(Boolean.TRUE.equals(entity.getPtEvidenceSubmitted()))
                .status(entity.getStatus())
                .verdictType(entity.getVerdictType())
                .resolutionDecision(entity.getResolutionDecision())
                .verdictReason(entity.getVerdictReason() != null ? entity.getVerdictReason() : entity.getResolutionDecision())
                .resolvedAt(entity.getResolvedAt())
                .createdAt(entity.getCreatedAt())
                .counterDeadline(counterDeadline)
                .canAdminArbitrate(canArbitrate)
                .waitingReason(waitingReason)
                .hoursRemaining(hoursRemaining)
                .minutesRemaining((int) minutesRemaining)
                .build();
    }
}
