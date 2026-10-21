package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.DecimalMin;
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
public class CreateCourseRequest {

    @NotBlank(message = "Tên khóa học không được để trống")
    private String title;

    private String description;

    @NotNull(message = "Số buổi học không được để trống")
    @Min(value = 1, message = "Tổng số buổi học phải lớn hơn 0")
    private Integer totalSessions;

    @NotNull(message = "Thời hạn khóa học không được để trống")
    @Min(value = 1, message = "Thời hạn sử dụng phải lớn hơn 0 ngày")
    private Integer validityDays;

    @NotNull(message = "Giá khóa học không được để trống")
    @DecimalMin(value = "0.0", inclusive = true, message = "Giá khóa học phải lớn hơn hoặc bằng 0")
    private BigDecimal basePrice;
}
