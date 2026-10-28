package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.service.IPTCourseService;
import com.PTconnect.backend.service.IPTProfileService;
import com.PTconnect.backend.service.IPTSlotService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller cho các endpoint dành riêng cho PT (Huấn luyện viên).
 * Áp dụng Interface Segregation Principle (ISP) - Tiêm các Service chuyên biệt cho từng nhóm chức năng.
 */
@RestController
@RequestMapping("/api/v1/pt")
@RequiredArgsConstructor
public class PTController {

    private final IPTProfileService profileService;
    private final IPTCourseService courseService;
    private final IPTSlotService slotService;

    // -------------------------------------------------------------
    // 1. PT Profile
    // -------------------------------------------------------------

    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<PTProfileResponse>> getProfile(Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        PTProfileResponse response = profileService.getProfile(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy hồ sơ Huấn luyện viên thành công", response));
    }

    @PutMapping("/profile")
    public ResponseEntity<ApiResponse<PTProfileResponse>> updateProfile(
            Authentication auth,
            @Valid @RequestBody UpdatePTProfileRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        PTProfileResponse response = profileService.updateProfile(email, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật hồ sơ Huấn luyện viên thành công", response));
    }

    // -------------------------------------------------------------
    // 2. PT Courses
    // -------------------------------------------------------------

    @PostMapping("/courses")
    public ResponseEntity<ApiResponse<CourseResponse>> createCourse(
            Authentication auth,
            @Valid @RequestBody CreateCourseRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        CourseResponse response = courseService.createCourse(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Tạo khóa học thành công", response));
    }

    @GetMapping("/courses")
    public ResponseEntity<ApiResponse<List<CourseResponse>>> getCourses(Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<CourseResponse> courses = courseService.getCourses(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khóa học thành công", courses));
    }

    @PutMapping("/courses/{id}")
    public ResponseEntity<ApiResponse<CourseResponse>> updateCourse(
            Authentication auth,
            @PathVariable Long id,
            @Valid @RequestBody UpdateCourseRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        CourseResponse response = courseService.updateCourse(email, id, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật khóa học thành công", response));
    }

    @DeleteMapping("/courses/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteCourse(
            Authentication auth,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        courseService.deleteCourse(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xóa khóa học thành công", null));
    }

    // -------------------------------------------------------------
    // 3. PT Availability Slots
    // -------------------------------------------------------------

    @PostMapping("/slots")
    public ResponseEntity<ApiResponse<SlotResponse>> createSlot(
            Authentication auth,
            @Valid @RequestBody CreateSlotRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        SlotResponse response = slotService.createSlot(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Tạo khung giờ rảnh thành công", response));
    }

    @GetMapping("/slots")
    public ResponseEntity<ApiResponse<List<SlotResponse>>> getSlots(Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<SlotResponse> slots = slotService.getSlots(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khung giờ rảnh thành công", slots));
    }

    @DeleteMapping("/slots/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteSlot(
            Authentication auth,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        slotService.deleteSlot(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xóa khung giờ rảnh thành công", null));
    }
}
