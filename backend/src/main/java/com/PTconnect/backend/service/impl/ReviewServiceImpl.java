package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.request.ReviewAppealRequest;
import com.PTconnect.backend.dto.request.ReviewStudentEvidenceRequest;
import com.PTconnect.backend.dto.request.ReviewVerdictRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.PTProfile;
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

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Triển khai nghiệp vụ Đánh giá nhận xét Huấn luyện viên và quy trình phản biện/kiểm duyệt (Milestone 7).
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

        int rating = request.getRating();
        String status = "PUBLISHED";
        String comment = request.getComment() != null ? request.getComment().trim() : null;

        // Quy tắc nghiệp vụ: Đánh giá 1 - 3 sao là đánh giá tiêu cực / có vấn đề
        // Bắt buộc học viên phải nêu rõ lý do góp ý hoặc bằng chứng để Admin & PT có căn cứ phân xử
        if (rating <= 3) {
            if (comment == null || comment.isBlank()) {
                throw new BadRequestException("Khi đánh giá từ 1 đến 3 sao, bạn vui lòng nhập lý do cụ thể để Huấn luyện viên và Quản trị viên hỗ trợ giải quyết thỏa đáng.");
            }
            status = "FLAGGED";
        }

        Review review = Review.builder()
                .booking(booking)
                .rating(rating)
                .comment(comment)
                .status(status)
                .studentEvidence(request.getStudentEvidence() != null ? request.getStudentEvidence().trim() : null)
                .createdAt(LocalDateTime.now())
                .build();

        review = reviewRepository.save(review);

        // Nếu đánh giá tốt 4-5 sao (PUBLISHED), cập nhật ngay số sao và lượt đánh giá cho PT
        if ("PUBLISHED".equals(status)) {
            updatePtRating(booking.getPt().getId());
        }

        log.info("Học viên {} đã gửi đánh giá {} sao cho PT Profile ID #{}, Booking ID #{}. Trạng thái: {}",
                studentEmail, rating, booking.getPt().getId(), booking.getId(), status);

        return ReviewResponse.fromEntity(review);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getReviewsByPtId(Long ptId) {
        if (!ptProfileRepository.existsById(ptId)) {
            throw new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên với ID: " + ptId);
        }
        // Chỉ lấy những đánh giá hợp lệ (PUBLISHED), các đánh giá tranh chấp 1-3 sao chưa kiểm duyệt hoặc bị xóa sẽ không hiển thị công khai
        return reviewRepository.findPublishedByPtIdOrderByCreatedAtDesc(ptId).stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getMyPtReviews(String ptEmail) {
        User ptUser = userRepository.findByEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy tài khoản với email: " + ptEmail));

        PTProfile ptProfile = ptProfileRepository.findByPtId(ptUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Tài khoản chưa khởi tạo hồ sơ Huấn luyện viên (PT Profile)"));

        // Lấy toàn bộ đánh giá của PT (bao gồm FLAGGED, APPEALED, EVIDENCE_REQUESTED, PUBLISHED, REMOVED)
        return reviewRepository.findAllByPtIdOrderByCreatedAtDesc(ptProfile.getId()).stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getMyReviews(String studentEmail) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        return reviewRepository.findByBookingStudentIdOrderByCreatedAtDesc(student.getId()).stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public ReviewResponse getReviewByBookingId(Long bookingId) {
        Review review = reviewRepository.findByBookingId(bookingId).orElse(null);
        return ReviewResponse.fromEntity(review);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ReviewResponse appealReview(String ptEmail, Long reviewId, ReviewAppealRequest request) {
        User ptUser = userRepository.findByEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy HLV với email: " + ptEmail));

        PTProfile ptProfile = ptProfileRepository.findByPtId(ptUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Bạn chưa tạo hồ sơ Huấn luyện viên"));

        Review review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đánh giá với ID: " + reviewId));

        if (!review.getBooking().getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền phản biện đánh giá không thuộc về mình");
        }

        if ("REMOVED".equals(review.getStatus())) {
            throw new BadRequestException("Đánh giá này đã được Quản trị viên gỡ bỏ, bạn không cần phản biện nữa.");
        }

        review.setPtAppeal(request.getPtAppeal().trim());
        if (request.getPtEvidence() != null && !request.getPtEvidence().isBlank()) {
            review.setPtEvidence(request.getPtEvidence().trim());
        }
        review.setPtAppealedAt(LocalDateTime.now());
        review.setStatus("APPEALED");

        review = reviewRepository.save(review);
        log.info("HLV {} đã gửi phản biện cho Review ID #{}", ptEmail, reviewId);

        return ReviewResponse.fromEntity(review);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ReviewResponse submitStudentEvidence(String studentEmail, Long reviewId, ReviewStudentEvidenceRequest request) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        Review review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đánh giá với ID: " + reviewId));

        if (!review.getBooking().getStudent().getId().equals(student.getId())) {
            throw new BadRequestException("Bạn không thể cập nhật chứng cứ cho đánh giá của học viên khác");
        }

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("HH:mm dd/MM/yyyy");
        String newEvidence = "[" + LocalDateTime.now().format(fmt) + "]: " + request.getStudentEvidence().trim();
        if (review.getStudentEvidence() != null && !review.getStudentEvidence().isBlank()) {
            review.setStudentEvidence(review.getStudentEvidence() + "\n" + newEvidence);
        } else {
            review.setStudentEvidence(newEvidence);
        }

        // Nếu trạng thái đang là EVIDENCE_REQUESTED, chuyển sang APPEALED để Admin nhận biết đã có bổ sung
        if ("EVIDENCE_REQUESTED".equals(review.getStatus())) {
            review.setStatus("APPEALED");
        }

        review = reviewRepository.save(review);
        log.info("Học viên {} đã bổ sung bằng chứng cho Review ID #{}", studentEmail, reviewId);

        return ReviewResponse.fromEntity(review);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewResponse> getModerationReviews() {
        return reviewRepository.findAllRequiringModeration().stream()
                .map(ReviewResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ReviewResponse adminVerdict(Long reviewId, ReviewVerdictRequest request) {
        Review review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đánh giá với ID: " + reviewId));

        String decision = request.getDecision().trim().toUpperCase();
        Long ptId = review.getBooking().getPt().getId();

        switch (decision) {
            case "REMOVE" -> {
                // Admin phán quyết: Xóa bỏ đánh giá xấu (do học viên vu khống, vi phạm quy tắc,...)
                review.setStatus("REMOVED");
                review.setAdminDecision("REMOVED");
                review.setAdminNote(request.getAdminNote().trim());
                review.setResolvedAt(LocalDateTime.now());
                review = reviewRepository.save(review);
                // Cập nhật lại điểm đánh giá của PT (loại bỏ review này)
                updatePtRating(ptId);
                log.info("Admin đã XÓA BỎ đánh giá xấu Review ID #{}", reviewId);
            }
            case "KEEP" -> {
                // Admin phán quyết: Giữ lại đánh giá xấu (phản ánh đúng thực tế, dịch vụ chưa tốt)
                review.setStatus("PUBLISHED");
                review.setAdminDecision("KEPT");
                review.setAdminNote(request.getAdminNote().trim());
                review.setResolvedAt(LocalDateTime.now());
                review = reviewRepository.save(review);
                // Cập nhật lại điểm đánh giá của PT (tính cả review này vào điểm số công khai)
                updatePtRating(ptId);
                log.info("Admin đã GIỮ LẠI đánh giá Review ID #{}", reviewId);
            }
            case "REQUEST_EVIDENCE" -> {
                // Admin yêu cầu 2 bên bổ sung thêm bằng chứng (ảnh, đoạn chat, biên bản...)
                review.setStatus("EVIDENCE_REQUESTED");
                review.setAdminDecision("REQUEST_EVIDENCE");
                review.setAdminNote(request.getAdminNote().trim());
                review = reviewRepository.save(review);
                log.info("Admin YÊU CẦU BỔ SUNG BẰNG CHỨNG cho Review ID #{}", reviewId);
            }
            default -> throw new BadRequestException("Quyết định không hợp lệ. Chỉ chấp nhận REMOVE, KEEP hoặc REQUEST_EVIDENCE.");
        }

        return ReviewResponse.fromEntity(review);
    }

    /**
     * Cập nhật lại averageRating và totalReviews cho PTProfile dựa trên các đánh giá hợp lệ (PUBLISHED).
     */
    private void updatePtRating(Long ptId) {
        PTProfile ptProfile = ptProfileRepository.findById(ptId).orElse(null);
        if (ptProfile != null) {
            Double avg = reviewRepository.calculateAverageRatingForPt(ptId);
            Long count = reviewRepository.countPublishedReviewsForPt(ptId);
            BigDecimal rating = BigDecimal.valueOf(avg != null ? avg : 5.0).setScale(2, RoundingMode.HALF_UP);
            ptProfile.setAverageRating(rating);
            ptProfile.setTotalReviews(count != null ? count.intValue() : 0);
            ptProfileRepository.save(ptProfile);
            log.info("Đã cập nhật lại rating cho PT Profile ID #{}: average={}, total={}",
                    ptId, ptProfile.getAverageRating(), ptProfile.getTotalReviews());
        }
    }
}
