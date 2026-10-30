package com.PTconnect.backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

@Entity
@Table(name = "workouts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Workout {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "plan_id", nullable = false)
    private WorkoutPlan plan;

    @Column(name = "exercise_name", nullable = false, length = 150)
    private String exerciseName;

    @Column(name = "target_muscle", length = 100)
    private String targetMuscle;

    @Column(nullable = false)
    @Builder.Default
    private Integer sets = 3;

    @Column(nullable = false)
    @Builder.Default
    private Integer reps = 10;

    @Column(name = "weight_kg", precision = 5, scale = 2)
    private BigDecimal weightKg;

    @Column(name = "rest_seconds", nullable = false)
    @Builder.Default
    private Integer restSeconds = 60;

    @Column(name = "video_demo_url", length = 500)
    private String videoDemoUrl;
}
