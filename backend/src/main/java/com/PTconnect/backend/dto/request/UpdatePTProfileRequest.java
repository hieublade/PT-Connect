package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdatePTProfileRequest {

    private String bio;

    @Min(value = 0, message = "Số năm kinh nghiệm phải lớn hơn hoặc bằng 0")
    private Integer experienceYears;

    @NotBlank(message = "Địa điểm nhận dạy không được để trống")
    private String availableLocations;

    private String locationPricingNote;

    // Chuỗi JSON hoặc danh sách các đường link chứng chỉ
    private String certificateUrls;
}
