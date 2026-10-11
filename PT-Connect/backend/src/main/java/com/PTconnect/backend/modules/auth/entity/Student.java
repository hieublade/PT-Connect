package com.PTconnect.backend.modules.auth.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Size;
import lombok.*;

@Entity
@Table(name = "students")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Student extends User {

    @Column(length = 200)
    private String trainingGoal;

    @Column(length = 100)
    private String experienceLevel;

    @Column(length = 200)
    private String preferredWorkoutStyle;

    @Column(length = 200)
    private String healthCondition;

    @Size(max = 500)
    @Column(length = 500)
    private String note;

    @Column(nullable = false)
    private Integer rewardPoints = 0;
}