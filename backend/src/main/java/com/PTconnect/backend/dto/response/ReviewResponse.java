package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Review;
import lombok.*;

import java.time.LocalDateTime;

/**
 * DTO phản hồi thông tin đánh giá nhận xét của học viên (Milestone 7).
 */
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
    private String studentAvatarUrl;
    private Long ptId;
    private Integer rating;
    private String comment;
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
                .createdAt(review.getCreatedAt());

        if (review.getStudent() != null) {
            builder.studentId(review.getStudent().getId())
                    .studentName(review.getStudent().getFullName())
                    .studentAvatarUrl(review.getStudent().getAvatarUrl());
        }

        if (review.getPt() != null) {
            builder.ptId(review.getPt().getId());
        }

        return builder.build();
    }
}
