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

    /**
     * Gửi hồ sơ khiếu nại ca tập (Học viên hoặc PT)
     * POST /api/v1/disputes
     */
    @PostMapping
    public ResponseEntity<ApiResponse<DisputeResponse>> createDispute(
            Authentication authentication,
            @Valid @RequestBody CreateDisputeRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.createDispute(email, request);
        return ResponseEntity.ok(ApiResponse.success("Đã tiếp nhận hồ sơ khiếu nại! Ban Quản Trị sẽ xử lý trong 24h.", response));
    }

    /**
     * Quản trị viên xem tất cả các vụ tranh chấp
     * GET /api/v1/disputes
     */
    @GetMapping
    public ResponseEntity<ApiResponse<List<DisputeResponse>>> getAllDisputes() {
        List<DisputeResponse> list = disputeService.getAllDisputes();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách tranh chấp thành công", list));
    }

    /**
     * Xem các vụ tranh chấp liên quan tới bản thân
     * GET /api/v1/disputes/my
     */
    @GetMapping("/my")
    public ResponseEntity<ApiResponse<List<DisputeResponse>>> getMyDisputes(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        List<DisputeResponse> list = disputeService.getMyDisputes(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách tranh chấp của tôi thành công", list));
    }

    /**
     * Quản trị viên ban hành phán quyết trọng tài
     * POST /api/v1/disputes/{id}/verdict
     */
    @PostMapping("/{id}/verdict")
    public ResponseEntity<ApiResponse<DisputeResponse>> issueVerdict(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody ArbitrationVerdictRequest request) {
        String adminEmail = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.issueVerdict(adminEmail, id, request);
        return ResponseEntity.ok(ApiResponse.success("Đã ban hành phán quyết trọng tài thành công!", response));
    }

    /**
     * Gửi phản biện / tường trình đối chứng (cho bên bị khiếu nại)
     * POST /api/v1/disputes/{id}/counter-statement
     */
    @PostMapping("/{id}/counter-statement")
    public ResponseEntity<ApiResponse<DisputeResponse>> submitCounterStatement(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody CounterStatementRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        DisputeResponse response = disputeService.submitCounterStatement(email, id, request.getCounterStatement());
        return ResponseEntity.ok(ApiResponse.success("Đã gửi phản biện đối chứng thành công!", response));
    }
}
