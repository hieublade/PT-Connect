package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateReviewRequest;
import com.PTconnect.backend.dto.response.ReviewResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.impl.ReviewServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ReviewServiceTest {

    @Mock
    private ReviewRepository reviewRepository;

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PTProfileRepository ptProfileRepository;

    @InjectMocks
    private ReviewServiceImpl reviewService;

    private User student;
    private PTProfile ptProfile;
    private Booking booking;

    @BeforeEach
    void setUp() {
        student = Student.builder().id(10L).email("student@test.com").fullName("Nguyen Van A").build();
        ptProfile = PTProfile.builder().id(20L).build();

        booking = Booking.builder()
                .id(100L)
                .student(student)
                .pt(ptProfile)
                .status(BookingStatus.COMPLETED)
                .build();
    }

    @Test
    @DisplayName("Tạo đánh giá thành công khi ca tập COMPLETED và đúng chủ sở hữu")
    void testCreateReview_Success() {
        when(userRepository.findByEmail("student@test.com")).thenReturn(Optional.of(student));
        when(bookingRepository.findById(100L)).thenReturn(Optional.of(booking));
        when(reviewRepository.existsByBookingId(100L)).thenReturn(false);
        when(reviewRepository.save(any(Review.class))).thenAnswer(inv -> {
            Review r = inv.getArgument(0);
            r.setId(1L);
            return r;
        });

        CreateReviewRequest request = CreateReviewRequest.builder()
                .bookingId(100L)
                .rating(5)
                .comment("HLV dạy rất tận tâm và chuyên nghiệp!")
                .build();

        ReviewResponse response = reviewService.createReview("student@test.com", request);

        assertNotNull(response);
        assertEquals(5, response.getRating());
        assertEquals("HLV dạy rất tận tâm và chuyên nghiệp!", response.getComment());
        verify(reviewRepository).save(any(Review.class));
        // Đảm bảo mã Java không tự can thiệp cập nhật average_rating hay total_reviews của pt_profiles
        verifyNoInteractions(ptProfileRepository);
    }

    @Test
    @DisplayName("Không được đánh giá khi ca tập chưa COMPLETED")
    void testCreateReview_NotCompleted() {
        booking.setStatus(BookingStatus.CONFIRMED);

        when(userRepository.findByEmail("student@test.com")).thenReturn(Optional.of(student));
        when(bookingRepository.findById(100L)).thenReturn(Optional.of(booking));

        CreateReviewRequest request = CreateReviewRequest.builder()
                .bookingId(100L)
                .rating(5)
                .build();

        assertThrows(BadRequestException.class, () -> reviewService.createReview("student@test.com", request));
    }

    @Test
    @DisplayName("Không được đánh giá 2 lần cho cùng 1 ca tập")
    void testCreateReview_AlreadyReviewed() {
        when(userRepository.findByEmail("student@test.com")).thenReturn(Optional.of(student));
        when(bookingRepository.findById(100L)).thenReturn(Optional.of(booking));
        when(reviewRepository.existsByBookingId(100L)).thenReturn(true);

        CreateReviewRequest request = CreateReviewRequest.builder()
                .bookingId(100L)
                .rating(4)
                .build();

        assertThrows(BadRequestException.class, () -> reviewService.createReview("student@test.com", request));
    }
}
