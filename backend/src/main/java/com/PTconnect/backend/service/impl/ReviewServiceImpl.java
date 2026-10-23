package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.Review;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.ReviewRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IReviewService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Triển khai nghiệp vụ Đánh giá nhận xét Huấn luyện viên (Milestone 7).
 * Phụ trách bởi: Thành.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ReviewServiceImpl implements IReviewService {

    private final ReviewRepository reviewRepository;
    private final BookingRepository bookingRepository;
    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ReviewResponse createReview(String studentEmail, CreateReviewRequest request) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        Booking booking = bookingRepository.findById(request.getBookingId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ca tập với ID: " + request.getBookingId()));

        if (!booking.getStudent().getId().equals(student.getId())) {
            throw new BadRequestException("Bạn không có quyền đánh giá đơn đặt lịch của học viên khác");
        }

        if (booking.getStatus() != BookingStatus.COMPLETED) {
            throw new BadRequestException("Chỉ có thể đánh giá ca tập đã hoàn thành (COMPLETED)");
        }

        if (reviewRepository.existsByBookingId(booking.getId())) {
            throw new BadRequestException("Ca tập này đã được đánh giá trước đó. Mỗi ca tập chỉ được đánh giá 1 lần duy nhất!");
        }

        Review review = Review.builder()
                .booking(booking)
                .student(student)
                .pt(booking.getPt())
                .rating(request.getRating())
                .comment(request.getComment() != null ? request.getComment().trim() : null)
                .build();

        // Lưu bản ghi Review vào CSDL
        // CHÚ Ý: Không tính toán average_rating hay total_reviews trong mã Java!
        // MySQL Trigger trg_reviews_after_insert sẽ tự động cập nhật hai trường này trong pt_profiles.
        review = reviewRepository.save(review);

        log.info("Học viên {} đã gửi đánh giá {} sao cho PT Profile ID #{}, Booking ID #{}",
                studentEmail, request.getRating(), booking.getPt().getId(), booking.getId());

        return ReviewResponse.fromEntity(review);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getReviewsByPtId(Long ptId) {
        if (!ptProfileRepository.existsById(ptId)) {
            throw new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + ptId);
        }
        return reviewRepository.findByPtIdOrderByCreatedAtDesc(ptId).stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getMyReviews(String studentEmail) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        return reviewRepository.findByStudentIdOrderByCreatedAtDesc(student.getId()).stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public ReviewResponse getReviewByBookingId(Long bookingId) {
        Review review = reviewRepository.findByBookingId(bookingId).orElse(null);
        return ReviewResponse.fromEntity(review);
    }
}
