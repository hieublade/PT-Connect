package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PendingPTResponse {

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
    private VerificationStatus verificationStatus;
    private UserStatus userStatus;
    private LocalDateTime createdAt;

    public static PendingPTResponse fromEntity(PTProfile profile) {
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

        return PendingPTResponse.builder()
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
                .verificationStatus(profile.getVerificationStatus())
                .userStatus(uStatus)
                .createdAt(profile.getCreatedAt())
                .build();
    }
}
