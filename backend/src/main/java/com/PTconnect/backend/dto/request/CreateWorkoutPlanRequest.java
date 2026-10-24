package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateWorkoutPlanRequest {

    @NotNull(message = "enrollmentId không được để trống")
    private Long enrollmentId;

    @NotBlank(message = "Tiêu đề giáo án không được để trống")
    private String title;

    private String goal;

    private LocalDate startDate;

    private LocalDate endDate;
}
