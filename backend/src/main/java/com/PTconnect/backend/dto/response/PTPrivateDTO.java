package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO hồ sơ đầy đủ (riêng tư) của Huấn luyện viên dành cho chính PT và Quản trị viên (Admin).
 * Bao gồm cả chứng chỉ nghề nghiệp (certificateUrls) và trạng thái hệ thống.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTPrivateDTO {

    private Long id;
    private Long userId;
    private String fullName;
    private String email;
    private String phone;
    private String avatarUrl;
    private String bio;
    private Integer experienceYears;
    private String availableLocations;
    private String locationPricingNote;
    private String certificateUrls;
    private BigDecimal averageRating;
    private Integer totalReviews;
    private VerificationStatus verificationStatus;
    private UserStatus userStatus;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static PTPrivateDTO fromEntity(PTProfile profile) {
        if (profile == null) {
            return null;
        }

        Long uId = null;
        String name = null;
        String mail = null;
        String tel = null;
        String avatar = null;
        UserStatus uStatus = null;

        if (profile.getPt() != null) {
            uId = profile.getPt().getId();
            name = profile.getPt().getFullName();
            mail = profile.getPt().getEmail();
            tel = profile.getPt().getPhone();
            avatar = profile.getPt().getAvatarUrl();
            uStatus = profile.getPt().getStatus();
        }

        return PTPrivateDTO.builder()
                .id(profile.getId())
                .userId(uId)
                .fullName(name)
                .email(mail)
                .phone(tel)
                .avatarUrl(avatar)
                .bio(profile.getBio())
                .experienceYears(profile.getExperienceYears())
                .availableLocations(profile.getAvailableLocations())
                .locationPricingNote(profile.getLocationPricingNote())
                .certificateUrls(profile.getCertificateUrls())
                .averageRating(profile.getAverageRating() != null ? profile.getAverageRating() : BigDecimal.ZERO)
                .totalReviews(profile.getTotalReviews() != null ? profile.getTotalReviews() : 0)
                .verificationStatus(profile.getVerificationStatus())
                .userStatus(uStatus)
                .createdAt(profile.getCreatedAt())
                .updatedAt(profile.getUpdatedAt())
                .build();
    }
}
