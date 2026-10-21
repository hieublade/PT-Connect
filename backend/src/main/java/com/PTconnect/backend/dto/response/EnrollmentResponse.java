package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EnrollmentResponse {

    private Long id;
    private Long studentId;
    private String studentName;
    private String studentEmail;
    private Long courseId;
    private String courseTitle;
    private Long ptId;
    private String ptName;
    private String trainingLocation;
    private BigDecimal finalPrice;
    private Integer totalSessions;
    private Integer remainingSessions;
    private LocalDate startDate;
    private LocalDate endDate;
    private String contractUrl;
    private EnrollmentStatus status;
    private LocalDateTime createdAt;

    public static EnrollmentResponse fromEntity(Enrollment enrollment) {
        if (enrollment == null) {
            return null;
        }

        Long sId = null;
        String sName = null;
        String sEmail = null;
        if (enrollment.getStudent() != null) {
            sId = enrollment.getStudent().getId();
            sName = enrollment.getStudent().getFullName();
            sEmail = enrollment.getStudent().getEmail();
        }

        Long cId = null;
        String cTitle = null;
        if (enrollment.getCourse() != null) {
            cId = enrollment.getCourse().getId();
            cTitle = enrollment.getCourse().getTitle();
        }

        Long pId = null;
        String pName = null;
        if (enrollment.getPt() != null) {
            pId = enrollment.getPt().getId();
            if (enrollment.getPt().getPt() != null) {
                pName = enrollment.getPt().getPt().getFullName();
            }
        }

        return EnrollmentResponse.builder()
                .id(enrollment.getId())
                .studentId(sId)
                .studentName(sName)
                .studentEmail(sEmail)
                .courseId(cId)
                .courseTitle(cTitle)
                .ptId(pId)
                .ptName(pName)
                .trainingLocation(enrollment.getTrainingLocation())
                .finalPrice(enrollment.getFinalPrice())
                .totalSessions(enrollment.getTotalSessions())
                .remainingSessions(enrollment.getRemainingSessions())
                .startDate(enrollment.getStartDate())
                .endDate(enrollment.getEndDate())
                .contractUrl(enrollment.getContractUrl())
                .status(enrollment.getStatus())
                .createdAt(enrollment.getCreatedAt())
                .build();
    }
}
