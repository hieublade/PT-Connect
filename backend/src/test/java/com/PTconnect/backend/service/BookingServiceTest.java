package com.PTconnect.backend.service;

import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.service.impl.BookingServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingServiceTest {

    @Mock
    private AvailabilitySlotRepository slotRepository;

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private EnrollmentRepository enrollmentRepository;

    @InjectMocks
    private BookingServiceImpl bookingService;

    private PTProfile ptProfile;
    private User student;
    private AvailabilitySlot futureAvailableSlot;
    private Enrollment activeEnrollment;

    @BeforeEach
    void setUp() {
        ptProfile = PTProfile.builder().id(1L).build();
        student = Student.builder().id(2L).fullName("Nguyen Student").build();

        futureAvailableSlot = AvailabilitySlot.builder()
                .id(100L)
                .pt(ptProfile)
                .startTime(LocalDateTime.now().plusDays(1))
                .endTime(LocalDateTime.now().plusDays(1).plusHours(1))
                .status(SlotStatus.AVAILABLE)
                .build();

        activeEnrollment = Enrollment.builder()
                .id(200L)
                .student(student)
                .pt(ptProfile)
                .remainingSessions(10)
                .totalSessions(12)
                .startDate(LocalDate.now().minusDays(5))
                .endDate(LocalDate.now().plusDays(30))
                .status(EnrollmentStatus.ACTIVE)
                .build();
    }

    @Test
    @DisplayName("Validation thành công khi slot AVAILABLE trong tương lai và hợp đồng hợp lệ")
    void validateBookingRequest_Success() {
        when(slotRepository.findById(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findById(200L)).thenReturn(Optional.of(activeEnrollment));

        assertDoesNotThrow(() ->
                bookingService.validateBookingRequest(100L, 2L, 200L)
        );
    }

    @Test
    @DisplayName("Ngoại lệ khi slot không ở trạng thái AVAILABLE")
    void validateBookingRequest_SlotNotAvailable() {
        futureAvailableSlot.setStatus(SlotStatus.BOOKED);
        when(slotRepository.findById(100L)).thenReturn(Optional.of(futureAvailableSlot));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.validateBookingRequest(100L, 2L, 200L)
        );
        assertTrue(ex.getMessage().contains("không còn khả dụng"));
    }

    @Test
    @DisplayName("Ngoại lệ khi slot có thời gian trong quá khứ")
    void validateBookingRequest_SlotInPast() {
        futureAvailableSlot.setStartTime(LocalDateTime.now().minusHours(2));
        when(slotRepository.findById(100L)).thenReturn(Optional.of(futureAvailableSlot));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.validateBookingRequest(100L, 2L, 200L)
        );
        assertTrue(ex.getMessage().contains("quá khứ"));
    }

    @Test
    @DisplayName("Ngoại lệ khi hợp đồng đã hết số buổi tập (remainingSessions <= 0)")
    void validateBookingRequest_NoRemainingSessions() {
        activeEnrollment.setRemainingSessions(0);
        when(slotRepository.findById(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findById(200L)).thenReturn(Optional.of(activeEnrollment));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.validateBookingRequest(100L, 2L, 200L)
        );
        assertTrue(ex.getMessage().contains("hết số buổi tập"));
    }

    @Test
    @DisplayName("Ngoại lệ khi hợp đồng không thuộc về học viên hiện tại")
    void validateBookingRequest_WrongStudent() {
        when(slotRepository.findById(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findById(200L)).thenReturn(Optional.of(activeEnrollment));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.validateBookingRequest(100L, 999L, 200L)
        );
        assertTrue(ex.getMessage().contains("không thuộc về bạn"));
    }
}
