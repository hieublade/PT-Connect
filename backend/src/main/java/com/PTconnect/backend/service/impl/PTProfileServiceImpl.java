package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTPublicDTO;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IPTProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Service chuyên biệt quản lý thông tin hồ sơ Huấn luyện viên (PT Profile).
 * Đảm bảo nguyên lý Đơn nhiệm (SRP) cho miền Hồ sơ PT.
 */
@Service
@RequiredArgsConstructor
public class PTProfileServiceImpl implements IPTProfileService {

    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;
    private final CourseRepository courseRepository;
    private final AvailabilitySlotRepository availabilitySlotRepository;

    // -------------------------------------------------------------
    // 1. Public PT Profiles
    // -------------------------------------------------------------

    @Override
    @Transactional(readOnly = true)
    public List<PTPublicDTO> getPublicPTProfiles(String name) {
        List<PTProfile> profiles;
        if (name != null && !name.trim().isEmpty()) {
            profiles = ptProfileRepository.searchVerifiedPTs(
                    name.trim(),
                    VerificationStatus.VERIFIED,
                    UserStatus.ACTIVE
            );
        } else {
            profiles = ptProfileRepository.findVerifiedAndActivePTs(
                    VerificationStatus.VERIFIED,
                    UserStatus.ACTIVE
            );
        }

        return profiles.stream()
                .map(this::mapToPublicDTO)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public PTPublicDTO getPublicPTProfileById(Long id) {
        PTProfile profile = ptProfileRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + id));

        return mapToPublicDTO(profile);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CourseResponse> getActiveCoursesByPTProfileId(Long profileId) {
        if (!ptProfileRepository.existsById(profileId)) {
            throw new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + profileId);
        }

        List<Course> courses = courseRepository.findByPtIdAndStatus(profileId, CourseStatus.ACTIVE);
        return courses.stream()
                .map(CourseResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<SlotResponse> getAvailableSlotsByPTProfileId(Long profileId) {
        if (!ptProfileRepository.existsById(profileId)) {
            throw new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + profileId);
        }

        List<AvailabilitySlot> slots = availabilitySlotRepository
                .findByPtIdAndStatusAndStartTimeAfterOrderByStartTimeAsc(
                        profileId,
                        SlotStatus.AVAILABLE,
                        LocalDateTime.now()
                );

        return slots.stream()
                .map(SlotResponse::fromEntity)
                .toList();
    }

    private PTPublicDTO mapToPublicDTO(PTProfile profile) {
        List<Course> activeCourses = courseRepository.findByPtIdAndStatus(profile.getId(), CourseStatus.ACTIVE);
        BigDecimal lowestPrice = activeCourses.stream()
                .map(Course::getBasePrice)
                .filter(p -> p != null && p.compareTo(BigDecimal.ZERO) > 0)
                .min(BigDecimal::compareTo)
                .orElse(null);

        return PTPublicDTO.fromEntity(profile, lowestPrice);
    }

    // -------------------------------------------------------------
    // 2. Private PT Profile Management
    // -------------------------------------------------------------

    @Override
    @Transactional(readOnly = true)
    public PTProfile getPTProfileEntity(String userEmail) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        if (user.getRole() != Role.PT) {
            throw new IllegalArgumentException("Người dùng không phải là Huấn luyện viên (PT)");
        }

        if (user.getStatus() == UserStatus.SUSPENDED) {
            throw new UnauthorizedException("Tài khoản của bạn đang bị tạm ngưng (SUSPENDED)");
        }

        return ptProfileRepository.findByPtId(user.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Hồ sơ Huấn luyện viên chưa được khởi tạo. Vui lòng liên hệ quản trị viên!"));
    }

    @Override
    @Transactional(readOnly = true)
    public PTProfileResponse getProfile(String userEmail) {
        PTProfile profile = getPTProfileEntity(userEmail);
        return PTProfileResponse.fromEntity(profile);
    }

    @Override
    @Transactional
    public PTProfileResponse updateProfile(String userEmail, UpdatePTProfileRequest request) {
        PTProfile profile = getPTProfileEntity(userEmail);

        if (request.getExperienceYears() != null && request.getExperienceYears() < 0) {
            throw new IllegalArgumentException("Số năm kinh nghiệm phải lớn hơn hoặc bằng 0");
        }

        if (request.getAvailableLocations() == null || request.getAvailableLocations().trim().isEmpty()) {
            throw new IllegalArgumentException("Địa điểm nhận dạy không được để trống");
        }

        if (request.getBio() != null) {
            profile.setBio(request.getBio().trim());
        }
        if (request.getExperienceYears() != null) {
            profile.setExperienceYears(request.getExperienceYears());
        }
        profile.setAvailableLocations(request.getAvailableLocations().trim());

        if (request.getLocationPricingNote() != null) {
            profile.setLocationPricingNote(request.getLocationPricingNote().trim());
        }

        if (request.getCertificateUrls() != null) {
            profile.setCertificateUrls(request.getCertificateUrls());
        }

        PTProfile saved = ptProfileRepository.save(profile);
        return PTProfileResponse.fromEntity(saved);
    }
}

