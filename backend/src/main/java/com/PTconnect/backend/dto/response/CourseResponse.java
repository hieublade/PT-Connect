package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.enums.CourseStatus;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CourseResponse {

    private Long id;
    private Long ptId;
    private String ptName;
    private String title;
    private String description;
    private Integer totalSessions;
    private Integer validityDays;
    private BigDecimal basePrice;
    private CourseStatus status;
    private LocalDateTime createdAt;

    public static CourseResponse fromEntity(Course course) {
        if (course == null) {
            return null;
        }

        Long ptId = null;
        String ptName = null;
        if (course.getPt() != null) {
            ptId = course.getPt().getId();
            if (course.getPt().getPt() != null) {
                ptName = course.getPt().getPt().getFullName();
            }
        }

        return CourseResponse.builder()
                .id(course.getId())
                .ptId(ptId)
                .ptName(ptName)
                .title(course.getTitle())
                .description(course.getDescription())
                .totalSessions(course.getTotalSessions())
                .validityDays(course.getValidityDays())
                .basePrice(course.getBasePrice())
                .status(course.getStatus())
                .createdAt(course.getCreatedAt())
                .build();
    }
}
