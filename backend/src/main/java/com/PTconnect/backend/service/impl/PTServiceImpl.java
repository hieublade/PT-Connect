package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.service.IPTCourseService;
import com.PTconnect.backend.service.IPTProfileService;
import com.PTconnect.backend.service.IPTService;
import com.PTconnect.backend.service.IPTSlotService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Facade Service điều phối và ủy quyền tới các service chuyên biệt (Profile, Course, Slot).
 * Tuân thủ nguyên lý Đơn nhiệm (SRP) và Mẫu thiết kế Facade (Facade Pattern).
 * Đảm bảo tính tương thích ngược cho toàn bộ hệ thống.
 */
@Service
@RequiredArgsConstructor
public class PTServiceImpl implements IPTService {

    private final IPTProfileService profileService;
    private final IPTCourseService courseService;
    private final IPTSlotService slotService;

    @Override
    public PTProfileResponse getProfile(String userEmail) {
        return profileService.getProfile(userEmail);
    }

    @Override
    public PTProfileResponse updateProfile(String userEmail, UpdatePTProfileRequest request) {
        return profileService.updateProfile(userEmail, request);
    }

    @Override
    public CourseResponse createCourse(String userEmail, CreateCourseRequest request) {
        return courseService.createCourse(userEmail, request);
    }

    @Override
    public List<CourseResponse> getCourses(String userEmail) {
        return courseService.getCourses(userEmail);
    }

    @Override
    public CourseResponse updateCourse(String userEmail, Long courseId, UpdateCourseRequest request) {
        return courseService.updateCourse(userEmail, courseId, request);
    }

    @Override
    public void deleteCourse(String userEmail, Long courseId) {
        courseService.deleteCourse(userEmail, courseId);
    }

    @Override
    public SlotResponse createSlot(String userEmail, CreateSlotRequest request) {
        return slotService.createSlot(userEmail, request);
    }

    @Override
    public List<SlotResponse> getSlots(String userEmail) {
        return slotService.getSlots(userEmail);
    }

    @Override
    public void deleteSlot(String userEmail, Long slotId) {
        slotService.deleteSlot(userEmail, slotId);
    }
}
