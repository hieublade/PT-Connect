package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
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

/**
 * Controller phục vụ toàn bộ luồng Đánh giá nhận xét Huấn luyện viên (Milestone 7).
 * Phụ trách bởi: Thành.
 */
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/reviews")
public class ReviewController {

    private final IReviewService reviewService;

    /**
     * Học viên tạo đánh giá cho ca tập đã hoàn thành (POST /api/v1/reviews)
     */
    @PostMapping
    public ResponseEntity<ApiResponse<ReviewResponse>> createReview(
            Authentication authentication,
            @Valid @RequestBody CreateReviewRequest request) {
        String studentEmail = SecurityUtils.getCurrentUserEmail(authentication);
        ReviewResponse response = reviewService.createReview(studentEmail, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Gửi đánh giá Huấn luyện viên thành công! Cảm ơn bạn đã phản hồi.", response));
    }

    /**
     * Lấy danh sách đánh giá của Huấn luyện viên (GET /api/v1/reviews/pt/{ptId})
     */
    @GetMapping("/pt/{ptId}")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getReviewsByPtId(@PathVariable Long ptId) {
        List<ReviewResponse> reviews = reviewService.getReviewsByPtId(ptId);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá thành công", reviews));
    }

    /**
     * Lấy danh sách đánh giá do chính học viên đã viết (GET /api/v1/reviews/my)
     */
    @GetMapping("/my")
    public ResponseEntity<ApiResponse<List<ReviewResponse>>> getMyReviews(Authentication authentication) {
        String studentEmail = SecurityUtils.getCurrentUserEmail(authentication);
        List<ReviewResponse> reviews = reviewService.getMyReviews(studentEmail);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đánh giá của tôi thành công", reviews));
    }

    /**
     * Lấy đánh giá của một ca tập cụ thể (GET /api/v1/reviews/booking/{bookingId})
     */
    @GetMapping("/booking/{bookingId}")
    public ResponseEntity<ApiResponse<ReviewResponse>> getReviewByBookingId(@PathVariable Long bookingId) {
        ReviewResponse review = reviewService.getReviewByBookingId(bookingId);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin đánh giá theo ca tập thành công", review));
    }
}
