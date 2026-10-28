package com.PTconnect.backend.handler;

import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.PTRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class PtRegistrationHandler implements UserRegistrationHandler {

    private final PTRepository ptRepository;
    private final PTProfileRepository profileRepository;

    @Override
    public boolean supports(Role role) {
        return role == Role.PT;
    }

    @Override
    public User register(RegisterRequest request, String encodedPassword) {
        PT pt = PT.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .passwordHash(encodedPassword)
                .phone(request.getPhone())
                .role(Role.PT)
                .status(UserStatus.PENDING)
                .build();
        PT savedPt = ptRepository.save(pt);

        String locations = (request.getAvailableLocations() != null && !request.getAvailableLocations().isBlank())
                ? request.getAvailableLocations()
                : "Chưa cập nhật địa điểm";

        PTProfile profile = PTProfile.builder()
                .pt(savedPt)
                .bio(request.getBio())
                .experienceYears(request.getExperienceYears() != null ? request.getExperienceYears() : 0)
                .availableLocations(locations)
                .locationPricingNote(request.getLocationPricingNote())
                .certificateUrls(request.getCertificateUrls())
                .verificationStatus(VerificationStatus.PENDING)
                .build();

        profileRepository.save(profile);
        savedPt.setProfile(profile);
        return savedPt;
    }
}
