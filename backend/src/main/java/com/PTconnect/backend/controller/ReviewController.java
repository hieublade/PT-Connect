package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.service.IReviewService;
import com.PTconnect.backend.util.ApiResponse;
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
@RequestMapping({"/api/v1/reviews", "/api/reviews"})
public class ReviewController {

    private final IReviewService reviewService;

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

    /**
     * Học viên tạo đánh giá cho ca tập đã hoàn thành (POST /api/v1/reviews)
     */
    @PostMapping
    public ResponseEntity<ApiResponse<ReviewResponse>> createReview(
            Authentication authentication,
            @Valid @RequestBody CreateReviewRequest request) {
        String studentEmail = getCurrentUserEmail(authentication);
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
        String studentEmail = getCurrentUserEmail(authentication);
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
