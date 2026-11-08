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
    private String certificateUrl;
    private String certificateUrls;

    public String getCleanCertificateUrl() {
        if (certificateUrl != null && !certificateUrl.isBlank()) {
            return cleanUrl(certificateUrl);
        }
        if (certificateUrls != null && !certificateUrls.isBlank()) {
            return cleanUrl(certificateUrls);
        }
        return null;
    }

    private String cleanUrl(String raw) {
        String s = raw.trim();
        if (s.startsWith("[\"") && s.endsWith("\"]")) {
            return s.substring(2, s.length() - 2).trim();
        }
        if (s.startsWith("[") && s.endsWith("]")) {
            return s.substring(1, s.length() - 1).replace("\"", "").replace("'", "").trim();
        }
        return s;
    }
}
