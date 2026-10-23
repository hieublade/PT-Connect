package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;

import java.util.List;

/**
 * Service xử lý đánh giá nhận xét Huấn luyện viên sau buổi tập (Milestone 7).
 * Phụ trách bởi: Thành.
 */
public interface IReviewService {

    /**
     * Tạo đánh giá cho ca tập đã hoàn thành (COMPLETED).
     * Chỉ học viên sở hữu đơn đặt lịch mới được đánh giá, mỗi ca chỉ đánh giá 1 lần.
     * Điểm trung bình và tổng lượt review do MySQL Trigger tự động tính toán.
     */
    ReviewResponse createReview(String studentEmail, CreateReviewRequest request);

    /**
     * Lấy danh sách đánh giá của một Huấn luyện viên theo ptId.
     */
    List<ReviewResponse> getReviewsByPtId(Long ptId);

    /**
     * Lấy danh sách các đánh giá do học viên hiện tại đã viết.
     */
    List<ReviewResponse> getMyReviews(String studentEmail);

    /**
     * Lấy đánh giá của một ca tập cụ thể (nếu có).
     */
    ReviewResponse getReviewByBookingId(Long bookingId);
}
