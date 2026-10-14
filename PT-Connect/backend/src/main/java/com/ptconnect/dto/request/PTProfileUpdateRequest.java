package com.ptconnect.dto.request;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PTProfileUpdateRequest {

    @NotBlank(message = "Bio không được để trống")
    private String bio;

    @Min(value = 0, message = "Số năm kinh nghiệm không hợp lệ")
    private Integer experienceYears;

    private String availableLocations;
    private String locationPricingNote;
    private List<Long> specializationIds;
}