package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTPublicDTO;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.PTProfile;

import java.util.List;

public interface IPTProfileService {

    List<PTPublicDTO> getPublicPTProfiles(String name);

    PTPublicDTO getPublicPTProfileById(Long id);

    List<CourseResponse> getActiveCoursesByPTProfileId(Long profileId);

    List<SlotResponse> getAvailableSlotsByPTProfileId(Long profileId);

    PTProfileResponse getProfile(String userEmail);

    PTProfileResponse updateProfile(String userEmail, UpdatePTProfileRequest request);

    PTProfileResponse uploadCertificate(String userEmail, org.springframework.web.multipart.MultipartFile file);

    PTProfile getPTProfileEntity(String userEmail);
}

