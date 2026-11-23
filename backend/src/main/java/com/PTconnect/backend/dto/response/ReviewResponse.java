package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Review;
import lombok.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewResponse {

    private Long id;
    private Long bookingId;
    private Long studentId;
    private String studentName;
    private String studentEmail;
    private String studentAvatarUrl;
    private Long ptId;
    private String ptName;
    private String ptEmail;
    private String courseTitle;
    private String slotTime;
    private Integer rating;
    private String comment;
    private String status;
    private String ptAppeal;
    private String ptEvidence;
    private LocalDateTime ptAppealedAt;
    private String studentEvidence;
    private String adminDecision;
    private String adminNote;
    private LocalDateTime resolvedAt;
    private LocalDateTime createdAt;

    public static ReviewResponse fromEntity(Review review) {
        if (review == null) {
            return null;
        }

        ReviewResponseBuilder builder = ReviewResponse.builder()
                .id(review.getId())
                .bookingId(review.getBooking() != null ? review.getBooking().getId() : null)
                .rating(review.getRating())
                .comment(review.getComment())
                .status(review.getStatus() != null ? review.getStatus() : "PUBLISHED")
                .ptAppeal(review.getPtAppeal())
                .ptEvidence(review.getPtEvidence())
                .ptAppealedAt(review.getPtAppealedAt())
                .studentEvidence(review.getStudentEvidence())
                .adminDecision(review.getAdminDecision())
                .adminNote(review.getAdminNote())
                .resolvedAt(review.getResolvedAt())
                .createdAt(review.getCreatedAt());

        if (review.getBooking() != null) {
            if (review.getBooking().getStudent() != null) {
                builder.studentId(review.getBooking().getStudent().getId())
                        .studentName(review.getBooking().getStudent().getFullName())
                        .studentEmail(review.getBooking().getStudent().getEmail())
                        .studentAvatarUrl(review.getBooking().getStudent().getAvatarUrl());
            }
            if (review.getBooking().getPt() != null) {
                builder.ptId(review.getBooking().getPt().getId());
                if (review.getBooking().getPt().getPt() != null) {
                    builder.ptName(review.getBooking().getPt().getPt().getFullName())
                            .ptEmail(review.getBooking().getPt().getPt().getEmail());
                }
            }
            if (review.getBooking().getEnrollment() != null && review.getBooking().getEnrollment().getCourse() != null) {
                builder.courseTitle(review.getBooking().getEnrollment().getCourse().getTitle());
            }
            if (review.getBooking().getSlot() != null && review.getBooking().getSlot().getStartTime() != null) {
                DateTimeFormatter fmt = DateTimeFormatter.ofPattern("HH:mm dd/MM/yyyy");
                builder.slotTime(review.getBooking().getSlot().getStartTime().format(fmt));
            }
        }

        return builder.build();
    }
}

