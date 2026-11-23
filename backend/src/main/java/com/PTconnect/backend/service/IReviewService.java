package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.request.ReviewAppealRequest;
import com.PTconnect.backend.dto.request.ReviewStudentEvidenceRequest;
import com.PTconnect.backend.dto.request.ReviewVerdictRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;

import java.util.List;

public interface IReviewService {

    ReviewResponse createReview(String studentEmail, CreateReviewRequest request);

    List<ReviewResponse> getReviewsByPtId(Long ptId);

    List<ReviewResponse> getMyPtReviews(String ptEmail);

    List<ReviewResponse> getMyReviews(String studentEmail);

    ReviewResponse getReviewByBookingId(Long bookingId);

    ReviewResponse appealReview(String ptEmail, Long reviewId, ReviewAppealRequest request);

    ReviewResponse submitStudentEvidence(String studentEmail, Long reviewId, ReviewStudentEvidenceRequest request);

    List<ReviewResponse> getModerationReviews();

    ReviewResponse adminVerdict(Long reviewId, ReviewVerdictRequest request);
}

