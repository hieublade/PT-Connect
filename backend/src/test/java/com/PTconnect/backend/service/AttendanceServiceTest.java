package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.StudentCheckInRequest;
import com.PTconnect.backend.dto.response.AttendanceResponse;
import com.PTconnect.backend.dto.response.StartAttendanceResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.*;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.impl.AttendanceServiceImpl;
import com.PTconnect.backend.util.OtpUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AttendanceServiceTest {

    @Mock
    private AttendanceRepository attendanceRepository;

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private EnrollmentRepository enrollmentRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PTProfileRepository ptProfileRepository;

    @Mock
    private OtpUtil otpUtil;

    @InjectMocks
    private AttendanceServiceImpl attendanceService;

    private PT ptUser;
    private PTProfile ptProfile;
    private User student;
    private Booking booking;
    private AvailabilitySlot slot;

    @BeforeEach
    void setUp() {
        ptUser = PT.builder().id(1L).email("pt@test.com").fullName("HLV Minh").build();
        ptProfile = PTProfile.builder().id(10L).pt(ptUser).build();
        student = Student.builder().id(2L).email("student@test.com").fullName("Học viên An").build();

        slot = AvailabilitySlot.builder()
                .id(100L)
                .startTime(LocalDateTime.now().minusMinutes(5))
                .endTime(LocalDateTime.now().plusMinutes(55))
                .build();

        booking = Booking.builder()
                .id(50L)
                .pt(ptProfile)
                .student(student)
                .slot(slot)
                .status(BookingStatus.CONFIRMED)
                .build();
    }

    @Test
    @DisplayName("PT mở phiên điểm danh thành công -> Sinh OTP và ghi nhận check-in ban đầu")
    void testStartAttendance_Success() {
        when(ptProfileRepository.findByPtEmail("pt@test.com")).thenReturn(Optional.of(ptProfile));
        when(bookingRepository.findByIdWithLock(50L)).thenReturn(Optional.of(booking));
        when(otpUtil.generateOtp(eq(50L), anyInt())).thenReturn("123456");
        when(attendanceRepository.findByBookingId(50L)).thenReturn(Optional.empty());
        when(attendanceRepository.save(any(Attendance.class))).thenAnswer(inv -> inv.getArgument(0));

        StartAttendanceResponse response = attendanceService.startAttendance("pt@test.com", 50L);

        assertNotNull(response);
        assertEquals("123456", response.getOtpCode());
        assertEquals(AttendanceStatus.PRESENT, response.getStatus());
        verify(attendanceRepository).save(any(Attendance.class));
    }

    @Test
    @DisplayName("Học viên nhập đúng OTP -> studentConfirmed = true")
    void testStudentCheckIn_Success() {
        when(userRepository.findByEmail("student@test.com")).thenReturn(Optional.of(student));
        when(bookingRepository.findByIdWithLock(50L)).thenReturn(Optional.of(booking));

        Attendance attendance = Attendance.builder()
                .id(1L)
                .booking(booking)
                .checkInTime(LocalDateTime.now())
                .studentConfirmed(false)
                .ptConfirmed(false)
                .status(AttendanceStatus.PRESENT)
                .build();

        when(attendanceRepository.findByBookingId(50L)).thenReturn(Optional.of(attendance));
        when(otpUtil.validateOtp(50L, "123456")).thenReturn(true);
        when(attendanceRepository.save(any(Attendance.class))).thenAnswer(inv -> inv.getArgument(0));

        StudentCheckInRequest request = StudentCheckInRequest.builder().otpCode("123456").build();
        AttendanceResponse response = attendanceService.studentCheckIn("student@test.com", 50L, request);

        assertNotNull(response);
        assertTrue(response.getStudentConfirmed());
    }

    @Test
    @DisplayName("Học viên nhập sai OTP -> Báo lỗi BadRequestException")
    void testStudentCheckIn_WrongOtp() {
        when(userRepository.findByEmail("student@test.com")).thenReturn(Optional.of(student));
        when(bookingRepository.findByIdWithLock(50L)).thenReturn(Optional.of(booking));

        Attendance attendance = Attendance.builder()
                .id(1L)
                .booking(booking)
                .studentConfirmed(false)
                .build();

        when(attendanceRepository.findByBookingId(50L)).thenReturn(Optional.of(attendance));
        when(otpUtil.validateOtp(50L, "999999")).thenReturn(false);

        StudentCheckInRequest request = StudentCheckInRequest.builder().otpCode("999999").build();
        assertThrows(BadRequestException.class, () -> attendanceService.studentCheckIn("student@test.com", 50L, request));
    }

    @Test
    @DisplayName("Điểm danh hai phía thành công -> Booking chuyển sang COMPLETED")
    void testTwoSidedAttendance_CompletesBooking() {
        when(ptProfileRepository.findByPtEmail("pt@test.com")).thenReturn(Optional.of(ptProfile));
        when(bookingRepository.findByIdWithLock(50L)).thenReturn(Optional.of(booking));

        // Học viên đã confirm trước đó
        Attendance attendance = Attendance.builder()
                .id(1L)
                .booking(booking)
                .checkInTime(LocalDateTime.now())
                .studentConfirmed(true)
                .ptConfirmed(false)
                .status(AttendanceStatus.PRESENT)
                .build();

        when(attendanceRepository.findByBookingId(50L)).thenReturn(Optional.of(attendance));
        when(attendanceRepository.save(any(Attendance.class))).thenAnswer(inv -> inv.getArgument(0));

        AttendanceResponse response = attendanceService.ptConfirmAttendance("pt@test.com", 50L);

        assertTrue(response.isFullyConfirmed());
        assertEquals(BookingStatus.COMPLETED, booking.getStatus());
        verify(bookingRepository).save(booking);
        verify(otpUtil).clearOtp(50L);
    }
}
