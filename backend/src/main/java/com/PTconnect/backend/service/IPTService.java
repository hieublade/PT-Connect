package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;

import java.util.List;

public interface IPTService {

    PTProfileResponse getProfile(String userEmail);

    PTProfileResponse updateProfile(String userEmail, UpdatePTProfileRequest request);

    CourseResponse createCourse(String userEmail, CreateCourseRequest request);

    List<CourseResponse> getCourses(String userEmail);

    CourseResponse updateCourse(String userEmail, Long courseId, UpdateCourseRequest request);

    void deleteCourse(String userEmail, Long courseId);

    SlotResponse createSlot(String userEmail, CreateSlotRequest request);

    List<SlotResponse> getSlots(String userEmail);

    void deleteSlot(String userEmail, Long slotId);
}
