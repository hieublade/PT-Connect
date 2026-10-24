package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.WorkoutPlan;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkoutPlanResponse {

    private Long id;
    private Long enrollmentId;
    private Long ptId;
    private String ptName;
    private String studentName;
    private String courseName;
    private String title;
    private String goal;
    private LocalDate startDate;
    private LocalDate endDate;
    private LocalDateTime createdAt;
    private List<WorkoutResponse> workouts;

    public static WorkoutPlanResponse fromEntity(WorkoutPlan p) {
        if (p == null) return null;
        return WorkoutPlanResponse.builder()
                .id(p.getId())
                .enrollmentId(p.getEnrollment() != null ? p.getEnrollment().getId() : null)
                .ptId(p.getPt() != null ? p.getPt().getId() : null)
                .ptName(p.getPt() != null && p.getPt().getPt() != null ? p.getPt().getPt().getFullName() : null)
                .studentName(p.getEnrollment() != null && p.getEnrollment().getStudent() != null ? p.getEnrollment().getStudent().getFullName() : null)
                .courseName(p.getEnrollment() != null && p.getEnrollment().getCourse() != null ? p.getEnrollment().getCourse().getTitle() : null)
                .title(p.getTitle())
                .goal(p.getGoal())
                .startDate(p.getStartDate())
                .endDate(p.getEndDate())
                .createdAt(p.getCreatedAt())
                .workouts(p.getWorkouts() != null
                        ? p.getWorkouts().stream().map(WorkoutResponse::fromEntity).collect(Collectors.toList())
                        : Collections.emptyList())
                .build();
    }
}
