package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTPublicDTO;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.service.IPTProfileService;
import com.PTconnect.backend.util.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping({"/api/v1/pt-profiles", "/api/pt-profiles"})
@RequiredArgsConstructor
public class PTProfileController {

    private final IPTProfileService ptProfileService;

    @GetMapping
    public ResponseEntity<ApiResponse<List<PTPublicDTO>>> getPublicPTList(
            @RequestParam(required = false) String name) {
        List<PTPublicDTO> profiles = ptProfileService.getPublicPTProfiles(name);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách Huấn luyện viên thành công", profiles));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<PTPublicDTO>> getPublicPTProfile(@PathVariable Long id) {
        PTPublicDTO profile = ptProfileService.getPublicPTProfileById(id);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin Huấn luyện viên thành công", profile));
    }

    @GetMapping("/{id}/courses")
    public ResponseEntity<ApiResponse<List<CourseResponse>>> getActiveCourses(@PathVariable Long id) {
        List<CourseResponse> courses = ptProfileService.getActiveCoursesByPTProfileId(id);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khóa học của Huấn luyện viên thành công", courses));
    }

    @GetMapping("/{id}/slots")
    public ResponseEntity<ApiResponse<List<SlotResponse>>> getAvailableSlots(@PathVariable Long id) {
        List<SlotResponse> slots = ptProfileService.getAvailableSlotsByPTProfileId(id);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khung giờ rảnh khả dụng thành công", slots));
    }
}
