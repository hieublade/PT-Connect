package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateWorkoutRequest {

    @NotBlank(message = "Tên bài tập không được để trống")
    private String exerciseName;

    private String targetMuscle;

    @NotNull(message = "Số hiệp (sets) không được để trống")
    @Min(value = 1, message = "Số hiệp phải lớn hơn 0")
    private Integer sets;

    @NotNull(message = "Số lần lặp (reps) không được để trống")
    @Min(value = 1, message = "Số lần lặp phải lớn hơn 0")
    private Integer reps;

    private BigDecimal weightKg;

    @NotNull(message = "Thời gian nghỉ không được để trống")
    @Min(value = 0, message = "Thời gian nghỉ không được âm")
    private Integer restSeconds;

    private String videoDemoUrl;
}
