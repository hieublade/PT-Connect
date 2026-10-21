package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import lombok.*;

import java.math.BigDecimal;

/**
 * DTO hồ sơ công khai của Huấn luyện viên dành cho Học viên (Student) và Khách.
 * TUYỆT ĐỐI KHÔNG chứa thông tin nhạy cảm như certificateUrls, mật khẩu hoặc thông tin nội bộ.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTPublicDTO {

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
    private BigDecimal averageRating;
    private Integer totalReviews;
    private BigDecimal lowestPrice;
    private VerificationStatus verificationStatus;

    public static PTPublicDTO fromEntity(PTProfile profile, BigDecimal lowestPrice) {
        if (profile == null) {
            return null;
        }

        Long uId = null;
        String name = null;
        String mail = null;
        String tel = null;
        String avatar = null;

        if (profile.getPt() != null) {
            uId = profile.getPt().getId();
            name = profile.getPt().getFullName();
            mail = profile.getPt().getEmail();
            tel = profile.getPt().getPhone();
            avatar = profile.getPt().getAvatarUrl();
        }

        return PTPublicDTO.builder()
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
                .averageRating(profile.getAverageRating() != null ? profile.getAverageRating() : BigDecimal.ZERO)
                .totalReviews(profile.getTotalReviews() != null ? profile.getTotalReviews() : 0)
                .lowestPrice(lowestPrice)
                .verificationStatus(profile.getVerificationStatus())
                .build();
    }
}
