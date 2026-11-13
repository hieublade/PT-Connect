package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.DisputeCase;
import lombok.*;

import java.math.BigDecimal;
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
    private String status;
    private String verdictType;
    private String resolutionDecision;
    private LocalDateTime resolvedAt;
    private LocalDateTime createdAt;

    public static DisputeResponse fromEntity(DisputeCase entity) {
        if (entity == null) return null;

        String studentName = "Học viên";
        String studentEmail = "";
        String studentPhone = "";
        String ptName = "Huấn luyện viên";
        String ptEmail = "";
        String courseTitle = "Ca tập cá nhân";
        String scheduledTime = "Chưa rõ thời gian";

        if (entity.getBooking() != null) {
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

        return DisputeResponse.builder()
                .id(entity.getId())
                .bookingId(entity.getBooking() != null ? entity.getBooking().getId() : null)
                .studentName(studentName)
                .studentEmail(studentEmail)
                .studentPhone(studentPhone)
                .ptName(ptName)
                .ptEmail(ptEmail)
                .courseTitle(courseTitle)
                .sessionFee(entity.getSessionFee() != null ? entity.getSessionFee() : BigDecimal.valueOf(350000))
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
                .status(entity.getStatus())
                .verdictType(entity.getVerdictType())
                .resolutionDecision(entity.getResolutionDecision())
                .resolvedAt(entity.getResolvedAt())
                .createdAt(entity.getCreatedAt())
                .build();
    }
}
