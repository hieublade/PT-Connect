package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.PurchaseCourseRequest;
import com.PTconnect.backend.dto.response.EnrollmentResponse;
import com.PTconnect.backend.service.IEnrollmentService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping({"/api/v1", "/api"})
@RequiredArgsConstructor
public class EnrollmentController {

    private final IEnrollmentService enrollmentService;

    @PostMapping("/enrollments")
    public ResponseEntity<ApiResponse<EnrollmentResponse>> purchaseCourse(
            Authentication authentication,
            @Valid @RequestBody PurchaseCourseRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        EnrollmentResponse response = enrollmentService.purchaseCourse(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Mua khóa học thành công", response));
    }

    @GetMapping("/enrollments/my")
    public ResponseEntity<ApiResponse<List<EnrollmentResponse>>> getMyEnrollments(
            Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        List<EnrollmentResponse> enrollments = enrollmentService.getMyEnrollments(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách khóa học của tôi thành công", enrollments));
    }

    @GetMapping("/enrollments/{id}")
    public ResponseEntity<ApiResponse<EnrollmentResponse>> getEnrollmentById(
            Authentication authentication,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        EnrollmentResponse response = enrollmentService.getEnrollmentById(email, id);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin hợp đồng thành công", response));
    }

    @GetMapping("/enrollments/{id}/contract")
    public ResponseEntity<byte[]> getContractPdf(
            Authentication authentication,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        byte[] pdfBytes = enrollmentService.getContractPdf(email, id);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("inline", "contract_" + id + ".pdf");
        headers.setCacheControl("must-revalidate, post-check=0, pre-check=0");

        return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);
    }

    @GetMapping({"/pt/enrollments", "/enrollments/pt"})
    public ResponseEntity<ApiResponse<List<EnrollmentResponse>>> getPtEnrollments(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        List<EnrollmentResponse> enrollments = enrollmentService.getPtEnrollments(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách hợp đồng học viên thành công", enrollments));
    }
}
