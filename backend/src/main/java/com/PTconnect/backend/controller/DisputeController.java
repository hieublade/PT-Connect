package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.ArbitrationVerdictRequest;
import com.PTconnect.backend.dto.request.CounterStatementRequest;
import com.PTconnect.backend.dto.request.CreateDisputeRequest;
import com.PTconnect.backend.dto.response.DisputeResponse;
import com.PTconnect.backend.service.IDisputeService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/disputes")
public class DisputeController {

    private final IDisputeService disputeService;

    @PostMapping
    public ResponseEntity<ApiResponse<DisputeResponse>> createDispute(
            Authentication authentication,
            @Valid @RequestBody CreateDisputeRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.createDispute(email, request);
        return ResponseEntity.ok(ApiResponse.success("Đã tiếp nhận hồ sơ khiếu nại! Ban Quản Trị sẽ xử lý trong 24h.", response));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<DisputeResponse>>> getAllDisputes() {
        List<DisputeResponse> list = disputeService.getAllDisputes();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách tranh chấp thành công", list));
    }

    @GetMapping("/my")
    public ResponseEntity<ApiResponse<List<DisputeResponse>>> getMyDisputes(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        List<DisputeResponse> list = disputeService.getMyDisputes(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách tranh chấp của tôi thành công", list));
    }

    @PostMapping("/{id}/verdict")
    public ResponseEntity<ApiResponse<DisputeResponse>> issueVerdict(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody ArbitrationVerdictRequest request) {
        String adminEmail = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.issueVerdict(adminEmail, id, request);
        return ResponseEntity.ok(ApiResponse.success("Đã ban hành phán quyết trọng tài thành công!", response));
    }

    @PostMapping("/{id}/counter-statement")
    public ResponseEntity<ApiResponse<DisputeResponse>> submitCounterStatement(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody CounterStatementRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.submitCounterStatement(email, id, request.getCounterStatement());
        return ResponseEntity.ok(ApiResponse.success("Đã gửi phản biện đối chứng thành công!", response));
    }

    @PostMapping("/{id}/request-evidence")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse<DisputeResponse>> requestAdditionalEvidence(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody com.PTconnect.backend.dto.request.RequestEvidenceRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.requestAdditionalEvidence(email, id, request.getTarget(), request.getNote());
        return ResponseEntity.ok(ApiResponse.success("Đã gửi yêu cầu bổ sung bằng chứng tới các bên liên quan!", response));
    }

    @PostMapping("/{id}/additional-evidence")
    public ResponseEntity<ApiResponse<DisputeResponse>> submitAdditionalEvidence(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody com.PTconnect.backend.dto.request.SubmitAdditionalEvidenceRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.submitAdditionalEvidence(email, id, request.getEvidence());
        return ResponseEntity.ok(ApiResponse.success("Đã gửi bổ sung bằng chứng lên Ban Quản Trị thành công!", response));
    }

    @PostMapping(value = "/upload-evidence", consumes = org.springframework.http.MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<java.util.Map<String, String>>> uploadEvidence(
            @RequestParam("file") org.springframework.web.multipart.MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new com.PTconnect.backend.exception.BadRequestException("Tập tin hình ảnh không được để trống!");
        }
        String contentType = file.getContentType();
        if (contentType != null && !contentType.startsWith("image/")) {
            throw new com.PTconnect.backend.exception.BadRequestException("Chỉ chấp nhận các định dạng tệp hình ảnh (JPEG, PNG, WEBP, GIF)!");
        }
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new com.PTconnect.backend.exception.BadRequestException("Dung lượng tập tin ảnh không được vượt quá 5MB!");
        }
        try {
            java.nio.file.Path uploadDir = java.nio.file.Paths.get("uploads", "disputes");
            if (!java.nio.file.Files.exists(uploadDir)) {
                java.nio.file.Files.createDirectories(uploadDir);
            }
            String originalFilename = file.getOriginalFilename();
            String extension = ".png";
            if (originalFilename != null && originalFilename.contains(".")) {
                extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String newFilename = "evidence_" + System.currentTimeMillis() + "_" + java.util.UUID.randomUUID().toString().substring(0, 8) + extension;
            java.nio.file.Path destination = uploadDir.resolve(newFilename);
            file.transferTo(destination.toFile());

            String fileUrl = "/uploads/disputes/" + newFilename;
            return ResponseEntity.ok(ApiResponse.success("Tải ảnh bằng chứng thành công", java.util.Map.of("url", fileUrl)));
        } catch (java.io.IOException e) {
            throw new com.PTconnect.backend.exception.BadRequestException("Lỗi lưu trữ tập tin hình ảnh: " + e.getMessage());
        }
    }
}

