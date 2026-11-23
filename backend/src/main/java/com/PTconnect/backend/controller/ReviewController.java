package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.request.ReviewAppealRequest;
import com.PTconnect.backend.dto.request.ReviewStudentEvidenceRequest;
import com.PTconnect.backend.dto.request.ReviewVerdictRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;
import com.PTconnect.backend.service.IReviewService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/reviews")
public class ReviewController {

    private final IReviewService reviewService;

    @PostMapping
    public ResponseEntity<ApiResponse<ReviewResponse>> createReview(
            Authentication authentication,
            @Valid @RequestBody CreateReviewRequest request) {
        String studentEmail = SecurityUtils.getCurrentUserEmail(authentication);
        ReviewResponse response = reviewService.createReview(studentEmail, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Gửi đánh giá Huấn luyện viên thành công! Cảm ơn bạn đã phản hồi.", response));
    }

    @GetMapping("/pt/{ptId}")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getReviewsByPtId(@PathVariable Long ptId) {
        List<ReviewResponse> reviews = reviewService.getReviewsByPtId(ptId);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá thành công", reviews));
    }

    @GetMapping("/pt/my")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getMyPtReviews(Authentication authentication) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        List<ReviewResponse> reviews = reviewService.getMyPtReviews(ptEmail);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá HLV thành công", reviews));
    }

    @PostMapping("/{id}/appeal")
    public ResponseEntity<ApiResponse<ReviewResponse>> appealReview(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody ReviewAppealRequest request) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        ReviewResponse response = reviewService.appealReview(ptEmail, id, request);
        return ResponseEntity.ok(ApiResponse.success("Gửi phản biện giải trình thành công. Đang chờ Quản trị viên xử lý.", response));
    }

    @PostMapping("/{id}/student-evidence")
    public ResponseEntity<ApiResponse<ReviewResponse>> submitStudentEvidence(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody ReviewStudentEvidenceRequest request) {
        String studentEmail = SecurityUtils.getCurrentUserEmail(authentication);
        ReviewResponse response = reviewService.submitStudentEvidence(studentEmail, id, request);
        return ResponseEntity.ok(ApiResponse.success("Bổ sung bằng chứng đánh giá thành công.", response));
    }

    @GetMapping("/moderation")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getModerationReviews() {
        List<ReviewResponse> reviews = reviewService.getModerationReviews();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá cần kiểm duyệt thành công", reviews));
    }

    @PostMapping("/{id}/verdict")
    public ResponseEntity<ApiResponse<ReviewResponse>> adminVerdict(
            @PathVariable Long id,
            @Valid @RequestBody ReviewVerdictRequest request) {
        ReviewResponse response = reviewService.adminVerdict(id, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật phán quyết đánh giá thành công.", response));
    }

    @GetMapping("/my")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getMyReviews(Authentication authentication) {
        String studentEmail = SecurityUtils.getCurrentUserEmail(authentication);
        List<ReviewResponse> reviews = reviewService.getMyReviews(studentEmail);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá của tôi thành công", reviews));
    }

    @GetMapping("/booking/{bookingId}")
    public ResponseEntity<ApiResponse<ReviewResponse>> getReviewByBookingId(@PathVariable Long bookingId) {
        ReviewResponse review = reviewService.getReviewByBookingId(bookingId);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin đánh giá theo ca tập thành công", review));
    }
}

