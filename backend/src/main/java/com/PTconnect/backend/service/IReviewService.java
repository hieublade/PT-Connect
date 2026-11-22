package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.request.ReviewAppealRequest;
import com.PTconnect.backend.dto.request.ReviewStudentEvidenceRequest;
import com.PTconnect.backend.dto.request.ReviewVerdictRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;

import java.util.List;

/**
 * Service xử lý đánh giá nhận xét Huấn luyện viên sau buổi tập và quy trình phản biện/kiểm duyệt (Milestone 7).
 */
public interface IReviewService {

    /**
     * Tạo đánh giá cho ca tập đã hoàn thành (COMPLETED).
     * Đánh giá 4-5 sao: PUBLISHED ngay.
     * Đánh giá 1-3 sao: FLAGGED (chờ HLV phản biện và Admin kiểm duyệt).
     */
    ReviewResponse createReview(String studentEmail, CreateReviewRequest request);

    /**
     * Lấy danh sách đánh giá công khai của PT (chỉ lấy PUBLISHED).
     */
    List<ReviewResponse> getReviewsByPtId(Long ptId);

    /**
     * Lấy toàn bộ đánh giá của chính PT (kèm theo các đánh giá 1-3 sao để phản biện).
     */
    List<ReviewResponse> getMyPtReviews(String ptEmail);

    /**
     * Lấy danh sách các đánh giá do học viên hiện tại đã viết.
     */
    List<ReviewResponse> getMyReviews(String studentEmail);

    /**
     * Lấy đánh giá của một ca tập cụ thể.
     */
    ReviewResponse getReviewByBookingId(Long bookingId);

    /**
     * HLV gửi giải trình / phản biện cho đánh giá xấu 1-3 sao.
     */
    ReviewResponse appealReview(String ptEmail, Long reviewId, ReviewAppealRequest request);

    /**
     * Học viên gửi bổ sung bằng chứng khi Admin yêu cầu.
     */
    ReviewResponse submitStudentEvidence(String studentEmail, Long reviewId, ReviewStudentEvidenceRequest request);

    /**
     * Lấy danh sách đánh giá tiêu cực (1-3 sao) cần kiểm duyệt cho Quản trị viên (Admin).
     */
    List<ReviewResponse> getModerationReviews();

    /**
     * Admin đưa ra phán quyết: REMOVE (Xóa bỏ đánh giá xấu), KEEP (Giữ lại đánh giá xấu), REQUEST_EVIDENCE (Yêu cầu thêm bằng chứng).
     */
    ReviewResponse adminVerdict(Long reviewId, ReviewVerdictRequest request);
}
