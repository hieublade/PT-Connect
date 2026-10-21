package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTPublicDTO;
import com.PTconnect.backend.dto.response.SlotResponse;

import java.util.List;

public interface IPTProfileService {

    List<PTPublicDTO> getPublicPTProfiles(String name);

    PTPublicDTO getPublicPTProfileById(Long id);

    List<CourseResponse> getActiveCoursesByPTProfileId(Long profileId);

    List<SlotResponse> getAvailableSlotsByPTProfileId(Long profileId);
}
