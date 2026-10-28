package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CancelBookingRequest;
import com.PTconnect.backend.dto.request.CreateBookingRequest;
import com.PTconnect.backend.dto.request.RejectBookingRequest;
import com.PTconnect.backend.dto.response.BookingResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.BookingConflictException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.impl.BookingServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingServiceTest {

    @Mock
    private AvailabilitySlotRepository slotRepository;

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private EnrollmentRepository enrollmentRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PTProfileRepository ptProfileRepository;

    @Mock
    private CancellationRepository cancellationRepository;

    @Mock
    private com.PTconnect.backend.policy.CancellationPolicyFactory cancellationPolicyFactory;

    @Mock
    private IWalletService walletService;

    @InjectMocks
    private BookingServiceImpl bookingService;

    private PT ptUser;
    private PTProfile ptProfile;
    private User student;
    private AvailabilitySlot futureAvailableSlot;
    private Enrollment activeEnrollment;

    @BeforeEach
    void setUp() {
        ptUser = PT.builder().id(10L).fullName("Le Hoang C").email("pt.hoangc@ptconnect.vn").build();
        ptProfile = PTProfile.builder().id(1L).pt(ptUser).build();
        student = Student.builder().id(2L).fullName("Nguyen Student").email("student.a@ptconnect.vn").build();

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
                .finalPrice(BigDecimal.valueOf(1200000))
                .remainingSessions(10)
                .totalSessions(12)
                .startDate(LocalDate.now().minusDays(5))
                .endDate(LocalDate.now().plusDays(30))
                .status(EnrollmentStatus.ACTIVE)
                .build();
    }

    @Test
    @DisplayName("Ngoại lệ khi slot có thời gian trong quá khứ")
    void createBooking_SlotInPast_ThrowsBadRequestException() {
        futureAvailableSlot.setStartTime(LocalDateTime.now().minusHours(2));
        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.PACKAGE)
                .enrollmentId(200L)
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.createBooking(student.getEmail(), req)
        );
        assertTrue(ex.getMessage().contains("quá khứ"));
    }

    @Test
    @DisplayName("Ngoại lệ khi hợp đồng đã hết số buổi tập (remainingSessions <= 0)")
    void createBooking_NoRemainingSessions_ThrowsBadRequestException() {
        Enrollment exhaustedEnrollment = Enrollment.builder()
                .id(200L)
                .student(student)
                .pt(ptProfile)
                .finalPrice(BigDecimal.valueOf(1200000))
                .remainingSessions(0)
                .totalSessions(12)
                .startDate(LocalDate.now().minusDays(5))
                .endDate(LocalDate.now().plusDays(30))
                .status(EnrollmentStatus.ACTIVE)
                .build();

        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.PACKAGE)
                .enrollmentId(200L)
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findByIdWithLock(200L)).thenReturn(Optional.of(exhaustedEnrollment));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.createBooking(student.getEmail(), req)
        );
        assertTrue(ex.getMessage().contains("hết số buổi tập"));
    }

    @Test
    @DisplayName("Ngoại lệ khi hợp đồng không thuộc về học viên hiện tại")
    void createBooking_WrongStudent_ThrowsBadRequestException() {
        User otherStudent = Student.builder().id(999L).email("other@ptconnect.vn").build();
        Enrollment otherEnrollment = Enrollment.builder()
                .id(200L)
                .student(otherStudent)
                .pt(ptProfile)
                .finalPrice(BigDecimal.valueOf(1200000))
                .remainingSessions(10)
                .totalSessions(12)
                .startDate(LocalDate.now().minusDays(5))
                .endDate(LocalDate.now().plusDays(30))
                .status(EnrollmentStatus.ACTIVE)
                .build();

        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.PACKAGE)
                .enrollmentId(200L)
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findByIdWithLock(200L)).thenReturn(Optional.of(otherEnrollment));

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.createBooking(student.getEmail(), req)
        );
        assertTrue(ex.getMessage().contains("không thuộc về bạn"));
    }

    @Test
    @DisplayName("Đặt lịch PACKAGE thành công: slot thành BOOKED, trừ 1 buổi tập, trạng thái PENDING")
    void createBooking_Package_Success() {
        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.PACKAGE)
                .enrollmentId(200L)
                .studentNote("Muốn tập Squat")
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(enrollmentRepository.findByIdWithLock(200L)).thenReturn(Optional.of(activeEnrollment));
        when(bookingRepository.saveAndFlush(any(Booking.class))).thenAnswer(i -> {
            Booking b = i.getArgument(0);
            b.setId(500L);
            return b;
        });

        BookingResponse response = bookingService.createBooking(student.getEmail(), req);

        assertNotNull(response);
        assertEquals(500L, response.getId());
        assertEquals(BookingStatus.PENDING, response.getStatus());
        assertEquals(SlotStatus.BOOKED, futureAvailableSlot.getStatus());
        assertEquals(9, activeEnrollment.getRemainingSessions()); // 10 - 1 = 9
    }

    @Test
    @DisplayName("Đặt lịch TRIAL thành công: fee = 0, slot thành BOOKED, trạng thái PENDING")
    void createBooking_Trial_Success() {
        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.TRIAL)
                .studentNote("Học thử buổi đầu")
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(bookingRepository.existsByStudentIdAndPtIdAndBookingType(student.getId(), ptProfile.getId(), BookingType.TRIAL))
                .thenReturn(false);
        when(bookingRepository.saveAndFlush(any(Booking.class))).thenAnswer(i -> {
            Booking b = i.getArgument(0);
            b.setId(501L);
            return b;
        });

        BookingResponse response = bookingService.createBooking(student.getEmail(), req);

        assertNotNull(response);
        assertEquals(BookingType.TRIAL, response.getBookingType());
        assertEquals(BigDecimal.ZERO, response.getSessionFee());
        assertEquals(SlotStatus.BOOKED, futureAvailableSlot.getStatus());
    }

    @Test
    @DisplayName("Ngoại lệ khi học thử lần 2 với cùng Huấn luyện viên")
    void createBooking_Trial_AlreadyBooked_ThrowsBadRequestException() {
        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.TRIAL)
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));
        when(bookingRepository.existsByStudentIdAndPtIdAndBookingType(student.getId(), ptProfile.getId(), BookingType.TRIAL))
                .thenReturn(true);

        BadRequestException ex = assertThrows(BadRequestException.class, () ->
                bookingService.createBooking(student.getEmail(), req)
        );
        assertTrue(ex.getMessage().contains("chỉ được học thử 1 lần"));
    }

    @Test
    @DisplayName("Ngoại lệ 409 Conflict khi slot đã bị người khác đặt trước")
    void createBooking_SlotNotAvailable_ThrowsBookingConflictException() {
        futureAvailableSlot.setStatus(SlotStatus.BOOKED);
        CreateBookingRequest req = CreateBookingRequest.builder()
                .slotId(100L)
                .bookingType(BookingType.PACKAGE)
                .enrollmentId(200L)
                .build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(slotRepository.findByIdWithLock(100L)).thenReturn(Optional.of(futureAvailableSlot));

        assertThrows(BookingConflictException.class, () ->
                bookingService.createBooking(student.getEmail(), req)
        );
    }

    @Test
    @DisplayName("PT xác nhận booking thành công: PENDING -> CONFIRMED")
    void confirmBooking_Success() {
        Booking booking = Booking.builder()
                .id(700L)
                .student(student)
                .pt(ptProfile)
                .slot(futureAvailableSlot)
                .status(BookingStatus.PENDING)
                .build();

        when(ptProfileRepository.findByPtEmail(ptUser.getEmail())).thenReturn(Optional.of(ptProfile));
        when(bookingRepository.findByIdWithLock(700L)).thenReturn(Optional.of(booking));
        when(bookingRepository.save(any(Booking.class))).thenAnswer(i -> i.getArgument(0));

        BookingResponse res = bookingService.confirmBooking(ptUser.getEmail(), 700L);

        assertNotNull(res);
        assertEquals(BookingStatus.CONFIRMED, res.getStatus());
    }

    @Test
    @DisplayName("PT từ chối booking thành công: CANCELLED, trả slot AVAILABLE, hoàn lại buổi tập")
    void rejectBooking_Success() {
        futureAvailableSlot.setStatus(SlotStatus.BOOKED);
        activeEnrollment.consumeSession(); // Đã bị trừ 1 buổi khả dụng từ 10 xuống 9 qua nghiệp vụ chuẩn

        Booking booking = Booking.builder()
                .id(800L)
                .student(student)
                .pt(ptProfile)
                .slot(futureAvailableSlot)
                .enrollment(activeEnrollment)
                .bookingType(BookingType.PACKAGE)
                .sessionFee(BigDecimal.valueOf(100000))
                .status(BookingStatus.PENDING)
                .build();

        RejectBookingRequest req = RejectBookingRequest.builder().reason("PT bận lịch cá nhân").build();

        when(cancellationPolicyFactory.getPolicy(Role.PT)).thenReturn(new com.PTconnect.backend.policy.PtCancellationPolicy());
        when(ptProfileRepository.findByPtEmail(ptUser.getEmail())).thenReturn(Optional.of(ptProfile));
        when(bookingRepository.findByIdWithLock(800L)).thenReturn(Optional.of(booking));
        when(cancellationRepository.save(any(Cancellation.class))).thenAnswer(i -> i.getArgument(0));
        when(bookingRepository.save(any(Booking.class))).thenAnswer(i -> i.getArgument(0));

        BookingResponse res = bookingService.rejectBooking(ptUser.getEmail(), 800L, req);

        assertNotNull(res);
        assertEquals(BookingStatus.CANCELLED, res.getStatus());
        assertEquals(SlotStatus.AVAILABLE, futureAvailableSlot.getStatus());
        assertEquals(10, activeEnrollment.getRemainingSessions()); // Đã hoàn lại 9 + 1 = 10
        verify(cancellationRepository, times(1)).save(any(Cancellation.class));
    }

    @Test
    @DisplayName("Học viên hủy ca tập thành công trước >= 24h qua cancelBookingByStudent: hoàn 1 buổi tập")
    void cancelBookingByStudent_Success() {
        AvailabilitySlot farFutureSlot = AvailabilitySlot.builder()
                .id(101L)
                .pt(ptProfile)
                .startTime(LocalDateTime.now().plusDays(3))
                .endTime(LocalDateTime.now().plusDays(3).plusHours(1))
                .status(SlotStatus.BOOKED)
                .build();

        activeEnrollment.consumeSession(); // 10 -> 9

        Booking booking = Booking.builder()
                .id(801L)
                .student(student)
                .pt(ptProfile)
                .slot(farFutureSlot)
                .enrollment(activeEnrollment)
                .bookingType(BookingType.PACKAGE)
                .sessionFee(BigDecimal.valueOf(100000))
                .status(BookingStatus.CONFIRMED)
                .build();

        CancelBookingRequest req = CancelBookingRequest.builder().reason("Học viên bận đột xuất").build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(bookingRepository.findByIdWithLock(801L)).thenReturn(Optional.of(booking));
        when(cancellationPolicyFactory.getPolicy(Role.STUDENT)).thenReturn(new com.PTconnect.backend.policy.StudentCancellationPolicy());
        when(cancellationRepository.save(any(Cancellation.class))).thenAnswer(i -> i.getArgument(0));
        when(bookingRepository.save(any(Booking.class))).thenAnswer(i -> i.getArgument(0));

        BookingResponse res = bookingService.cancelBookingByStudent(student.getEmail(), 801L, req);

        assertNotNull(res);
        assertEquals(BookingStatus.CANCELLED, res.getStatus());
        assertEquals(SlotStatus.AVAILABLE, farFutureSlot.getStatus());
        assertEquals(10, activeEnrollment.getRemainingSessions());
        verify(cancellationRepository, times(1)).save(any(Cancellation.class));
    }

    @Test
    @DisplayName("Học viên hủy sát giờ (< 24h): không hoàn buổi tập, đền bù 50% vào ví PT")
    void cancelBookingByStudent_LateCancel_DoesNotRestoreSession() {
        AvailabilitySlot nearSlot = AvailabilitySlot.builder()
                .id(103L)
                .pt(ptProfile)
                .startTime(LocalDateTime.now().plusHours(5))
                .endTime(LocalDateTime.now().plusHours(6))
                .status(SlotStatus.BOOKED)
                .build();

        activeEnrollment.consumeSession(); // 10 -> 9

        Booking booking = Booking.builder()
                .id(803L)
                .student(student)
                .pt(ptProfile)
                .slot(nearSlot)
                .enrollment(activeEnrollment)
                .bookingType(BookingType.PACKAGE)
                .sessionFee(BigDecimal.valueOf(100000))
                .status(BookingStatus.CONFIRMED)
                .build();

        CancelBookingRequest req = CancelBookingRequest.builder().reason("Học viên hủy sát giờ").build();

        when(userRepository.findByEmail(student.getEmail())).thenReturn(Optional.of(student));
        when(bookingRepository.findByIdWithLock(803L)).thenReturn(Optional.of(booking));
        when(cancellationPolicyFactory.getPolicy(Role.STUDENT)).thenReturn(new com.PTconnect.backend.policy.StudentCancellationPolicy());
        when(cancellationRepository.save(any(Cancellation.class))).thenAnswer(i -> i.getArgument(0));
        when(bookingRepository.save(any(Booking.class))).thenAnswer(i -> i.getArgument(0));

        BookingResponse res = bookingService.cancelBookingByStudent(student.getEmail(), 803L, req);

        assertNotNull(res);
        assertEquals(BookingStatus.CANCELLED, res.getStatus());
        assertEquals(SlotStatus.AVAILABLE, nearSlot.getStatus());
        assertEquals(9, activeEnrollment.getRemainingSessions()); // Không được hoàn: vẫn 9
        verify(cancellationRepository, times(1)).save(any(Cancellation.class));
        verify(walletService, times(1)).processBookingCompensation(eq(ptUser.getId()), eq(activeEnrollment), eq(BigDecimal.valueOf(50000).setScale(2)));
    }

    @Test
    @DisplayName("Huấn luyện viên hủy ca tập thành công qua cancelBookingByPT")
    void cancelBookingByPT_Success() {
        AvailabilitySlot farFutureSlot = AvailabilitySlot.builder()
                .id(102L)
                .pt(ptProfile)
                .startTime(LocalDateTime.now().plusDays(3))
                .endTime(LocalDateTime.now().plusDays(3).plusHours(1))
                .status(SlotStatus.BOOKED)
                .build();

        activeEnrollment.consumeSession(); // 10 -> 9

        Booking booking = Booking.builder()
                .id(802L)
                .student(student)
                .pt(ptProfile)
                .slot(farFutureSlot)
                .enrollment(activeEnrollment)
                .bookingType(BookingType.PACKAGE)
                .sessionFee(BigDecimal.valueOf(100000))
                .status(BookingStatus.CONFIRMED)
                .build();

        CancelBookingRequest req = CancelBookingRequest.builder().reason("PT có việc gia đình").build();

        when(ptProfileRepository.findByPtEmail(ptUser.getEmail())).thenReturn(Optional.of(ptProfile));
        when(bookingRepository.findByIdWithLock(802L)).thenReturn(Optional.of(booking));
        when(cancellationPolicyFactory.getPolicy(Role.PT)).thenReturn(new com.PTconnect.backend.policy.PtCancellationPolicy());
        when(cancellationRepository.save(any(Cancellation.class))).thenAnswer(i -> i.getArgument(0));
        when(bookingRepository.save(any(Booking.class))).thenAnswer(i -> i.getArgument(0));

        BookingResponse res = bookingService.cancelBookingByPT(ptUser.getEmail(), 802L, req);

        assertNotNull(res);
        assertEquals(BookingStatus.CANCELLED, res.getStatus());
        assertEquals(SlotStatus.AVAILABLE, farFutureSlot.getStatus());
        assertEquals(10, activeEnrollment.getRemainingSessions());
        verify(cancellationRepository, times(1)).save(any(Cancellation.class));
    }
}
