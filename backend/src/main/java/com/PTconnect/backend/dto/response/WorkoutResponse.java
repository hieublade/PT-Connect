package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Workout;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkoutResponse {

    private Long id;
    private Long planId;
    private String exerciseName;
    private String targetMuscle;
    private Integer sets;
    private Integer reps;
    private BigDecimal weightKg;
    private Integer restSeconds;
    private String videoDemoUrl;

    public static WorkoutResponse fromEntity(Workout w) {
        if (w == null) return null;
        return WorkoutResponse.builder()
                .id(w.getId())
                .planId(w.getPlan() != null ? w.getPlan().getId() : null)
                .exerciseName(w.getExerciseName())
                .targetMuscle(w.getTargetMuscle())
                .sets(w.getSets())
                .reps(w.getReps())
                .weightKg(w.getWeightKg())
                .restSeconds(w.getRestSeconds())
                .videoDemoUrl(w.getVideoDemoUrl())
                .build();
    }
}
