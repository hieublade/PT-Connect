package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.service.IPTService;
import com.PTconnect.backend.util.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller cho các endpoint dành riêng cho PT (Huấn luyện viên).
 * Hỗ trợ các chức năng Milestone 4: Profile, Courses, Availability Slots.
 */
@RestController
@RequestMapping({"/api/v1/pt", "/api/pt"})
@RequiredArgsConstructor
public class PTController {

    private final IPTService ptService;

    private String getCurrentUserEmail(Authentication auth) {
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("Chưa đăng nhập");
        }
        Object principal = auth.getPrincipal();
        if (principal instanceof User user) {
            return user.getEmail();
        }
        if (principal instanceof String email) {
            return email;
        }
        return auth.getName();
    }

    // -------------------------------------------------------------
    // 1. PT Profile
    // -------------------------------------------------------------

    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<PTProfileResponse>> getProfile(Authentication auth) {
        String email = getCurrentUserEmail(auth);
        PTProfileResponse response = ptService.getProfile(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy hồ sơ Huấn luyện viên thành công", response));
    }

    @PutMapping("/profile")
    public ResponseEntity<ApiResponse<PTProfileResponse>> updateProfile(
            Authentication auth,
            @Valid @RequestBody UpdatePTProfileRequest request) {
        String email = getCurrentUserEmail(auth);
        PTProfileResponse response = ptService.updateProfile(email, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật hồ sơ Huấn luyện viên thành công", response));
    }

    // -------------------------------------------------------------
    // 2. PT Courses
    // -------------------------------------------------------------

    @PostMapping("/courses")
    public ResponseEntity<ApiResponse<CourseResponse>> createCourse(
            Authentication auth,
            @Valid @RequestBody CreateCourseRequest request) {
        String email = getCurrentUserEmail(auth);
        CourseResponse response = ptService.createCourse(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Tạo khóa học thành công", response));
    }

    @GetMapping("/courses")
    public ResponseEntity<ApiResponse<List<CourseResponse>>> getCourses(Authentication auth) {
        String email = getCurrentUserEmail(auth);
        List<CourseResponse> courses = ptService.getCourses(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khóa học thành công", courses));
    }

    @PutMapping("/courses/{id}")
    public ResponseEntity<ApiResponse<CourseResponse>> updateCourse(
            Authentication auth,
            @PathVariable Long id,
            @Valid @RequestBody UpdateCourseRequest request) {
        String email = getCurrentUserEmail(auth);
        CourseResponse response = ptService.updateCourse(email, id, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật khóa học thành công", response));
    }

    @DeleteMapping("/courses/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteCourse(
            Authentication auth,
            @PathVariable Long id) {
        String email = getCurrentUserEmail(auth);
        ptService.deleteCourse(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xóa khóa học thành công", null));
    }

    // -------------------------------------------------------------
    // 3. PT Availability Slots
    // -------------------------------------------------------------

    @PostMapping("/slots")
    public ResponseEntity<ApiResponse<SlotResponse>> createSlot(
            Authentication auth,
            @Valid @RequestBody CreateSlotRequest request) {
        String email = getCurrentUserEmail(auth);
        SlotResponse response = ptService.createSlot(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Tạo khung giờ rảnh thành công", response));
    }

    @GetMapping("/slots")
    public ResponseEntity<ApiResponse<List<SlotResponse>>> getSlots(Authentication auth) {
        String email = getCurrentUserEmail(auth);
        List<SlotResponse> slots = ptService.getSlots(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khung giờ rảnh thành công", slots));
    }

    @DeleteMapping("/slots/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteSlot(
            Authentication auth,
            @PathVariable Long id) {
        String email = getCurrentUserEmail(auth);
        ptService.deleteSlot(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xóa khung giờ rảnh thành công", null));
    }
}
