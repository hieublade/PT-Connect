package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTPublicDTO;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.service.IPTProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PTProfileServiceImpl implements IPTProfileService {

    private final PTProfileRepository ptProfileRepository;
    private final CourseRepository courseRepository;
    private final AvailabilitySlotRepository availabilitySlotRepository;

    @Override
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
    public PTPublicDTO getPublicPTProfileById(Long id) {
        PTProfile profile = ptProfileRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + id));

        return mapToPublicDTO(profile);
    }

    @Override
    public List<CourseResponse> getActiveCoursesByPTProfileId(Long profileId) {
        // Kiem tra profile ton tai
        if (!ptProfileRepository.existsById(profileId)) {
            throw new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + profileId);
        }

        List<Course> courses = courseRepository.findByPtIdAndStatus(profileId, CourseStatus.ACTIVE);
        return courses.stream()
                .map(CourseResponse::fromEntity)
                .toList();
    }

    @Override
    public List<SlotResponse> getAvailableSlotsByPTProfileId(Long profileId) {
        // Kiem tra profile ton tai
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
}
