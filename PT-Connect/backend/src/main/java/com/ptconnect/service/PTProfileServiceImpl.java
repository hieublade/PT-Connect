package com.ptconnect.service.impl;

import com.ptconnect.dto.request.PTProfileUpdateRequest;
import com.ptconnect.dto.response.PTProfileResponse;
import com.ptconnect.entity.PTProfile;
import com.ptconnect.entity.PTSpecialization;
import com.ptconnect.entity.Specialization;
import com.ptconnect.enums.UserStatus;
import com.ptconnect.enums.VerificationStatus;
import com.ptconnect.exception.AppException;
import com.ptconnect.exception.ErrorCode;
import com.ptconnect.repository.PTProfileRepository;
import com.ptconnect.repository.PTSpecializationRepository;
import com.ptconnect.repository.SpecializationRepository;
import com.ptconnect.service.PTProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PTProfileServiceImpl implements PTProfileService {

    private final PTProfileRepository ptProfileRepository;
    private final SpecializationRepository specializationRepository;
    private final PTSpecializationRepository ptSpecializationRepository;

    @Override
    public List<PTProfileResponse> getAllVerifiedPTs(String nameSearch) {
        return ptProfileRepository.searchVerifiedPTs(nameSearch).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public PTProfileResponse getPTProfileById(Long ptId) {
        PTProfile profile = ptProfileRepository.findById(ptId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
        return mapToResponse(profile);
    }

    @Override
    @Transactional
    public PTProfileResponse updatePTProfile(Long userId, PTProfileUpdateRequest request) {
        PTProfile profile = ptProfileRepository.findByUserId(userId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        profile.setBio(request.getBio());
        profile.setExperienceYears(request.getExperienceYears());
        profile.setAvailableLocations(request.getAvailableLocations());
        profile.setLocationPricingNote(request.getLocationPricingNote());

        if (request.getSpecializationIds() != null) {
            ptSpecializationRepository.deleteByPtProfileId(profile.getId());
            for (Long specId : request.getSpecializationIds()) {
                Specialization spec = specializationRepository.findById(specId)
                        .orElseThrow(() -> new AppException(ErrorCode.INVALID_KEY));
                PTSpecialization ptSpec = PTSpecialization.builder()
                        .ptProfile(profile)
                        .specialization(spec)
                        .build();
                ptSpecializationRepository.save(ptSpec);
            }
        }

        PTProfile updatedProfile = ptProfileRepository.save(profile);
        return mapToResponse(updatedProfile);
    }

    @Override
    public List<PTProfileResponse> getPendingPTs() {
        return ptProfileRepository.findByVerificationStatus(VerificationStatus.PENDING).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void approvePT(Long ptId) {
        PTProfile profile = ptProfileRepository.findById(ptId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
        profile.setVerificationStatus(VerificationStatus.VERIFIED);
        profile.getUser().setStatus(UserStatus.ACTIVE);
        ptProfileRepository.save(profile);
    }

    private PTProfileResponse mapToResponse(PTProfile profile) {
        List<String> specs = ptSpecializationRepository.findByPtProfileId(profile.getId()).stream()
                .map(pts -> pts.getSpecialization().getName())
                .collect(Collectors.toList());

        return PTProfileResponse.builder()
                .id(profile.getId())
                .userId(profile.getUser().getId())
                .fullName(profile.getUser().getFullName())
                .email(profile.getUser().getEmail())
                .phone(profile.getUser().getPhone())
                .avatarUrl(profile.getUser().getAvatarUrl())
                .bio(profile.getBio())
                .experienceYears(profile.getExperienceYears())
                .availableLocations(profile.getAvailableLocations())
                .locationPricingNote(profile.getLocationPricingNote())
                .averageRating(profile.getAverageRating())
                .totalReviews(profile.getTotalReviews())
                .verificationStatus(profile.getVerificationStatus().name())
                .specializations(specs)
                .build();
    }
}