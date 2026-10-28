package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import com.PTconnect.backend.entity.enums.Role;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Kiểm thử đơn vị (JUnit 5) cho từng dòng trong Bảng chính sách hủy lịch mục 3.11.
 * Minh chứng tính ĐA HÌNH (Polymorphism) và mẫu thiết kế Strategy (Milestone 7 - Hưng).
 */
class CancellationPolicyTest {

    private StudentCancellationPolicy studentPolicy;
    private PtCancellationPolicy ptPolicy;
    private AdminCancellationPolicy adminPolicy;
    private CancellationPolicyFactory factory;

    private static final BigDecimal SESSION_FEE = BigDecimal.valueOf(300000.00); // 300.000 đ

    @BeforeEach
    void setUp() {
        studentPolicy = new StudentCancellationPolicy();
        ptPolicy = new PtCancellationPolicy();
        adminPolicy = new AdminCancellationPolicy();
        factory = new CancellationPolicyFactory(List.of(studentPolicy, ptPolicy, adminPolicy));
    }

    private Booking createBooking(BookingType type, BookingStatus status, LocalDateTime slotStartTime) {
        AvailabilitySlot slot = AvailabilitySlot.builder()
                .startTime(slotStartTime)
                .endTime(slotStartTime.plusHours(1))
                .build();

        return Booking.builder()
                .id(100L)
                .bookingType(type)
                .status(status)
                .sessionFee(SESSION_FEE)
                .slot(slot)
                .build();
    }

    @Test
    @DisplayName("Dòng 1: Học viên hủy khi PENDING -> Hoàn 1 buổi, không đền bù, không phạt")
    void testStudentCancelPending() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(48);
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.PENDING, slotTime);

        CancellationCalculationResult result = studentPolicy.calculate(booking, now, "Bận việc đột xuất", null);

        assertTrue(result.isRestoreSession(), "Phải hoàn trả 1 buổi tập");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()), "Số tiền hoàn lại bằng session_fee");
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()), "Tiền đền bù phải bằng 0");
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()), "Tiền phạt phải bằng 0");
    }

    @Test
    @DisplayName("Dòng 2: Học viên hủy CONFIRMED cách giờ tập >= 24 giờ -> Hoàn 1 buổi, không đền bù, không phạt")
    void testStudentCancelConfirmedAdvanceNotice() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(25); // Cách 25 giờ (>= 24h)
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = studentPolicy.calculate(booking, now, "Có kế hoạch khác", null);

        assertTrue(result.isRestoreSession(), "Phải hoàn trả 1 buổi tập");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()));
        assertTrue(result.getHoursBeforeSession().doubleValue() >= 24.0);
    }

    @Test
    @DisplayName("Dòng 3: Học viên hủy CONFIRMED cách giờ tập < 24 giờ -> Mất buổi, đền bù 50% cho PT, không phạt")
    void testStudentCancelConfirmedLate() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(5); // Cách 5 giờ (< 24h)
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = studentPolicy.calculate(booking, now, "Bận đột xuất", null);

        assertFalse(result.isRestoreSession(), "Học viên bị mất buổi, không được hoàn lại");
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getRefundAmount()));

        BigDecimal expectedComp = SESSION_FEE.multiply(BigDecimal.valueOf(0.50)); // 150.000 đ
        assertEquals(0, expectedComp.compareTo(result.getCompensationAmount()), "Đền bù 50% session_fee vào ví PT");
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()), "Không phạt thêm học viên");
    }

    @Test
    @DisplayName("Dòng 4: Học viên hủy lịch TRIAL -> Không có buổi hoàn, không đền bù, không phạt")
    void testStudentCancelTrial() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(10);
        Booking booking = createBooking(BookingType.TRIAL, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = studentPolicy.calculate(booking, now, "Không tiện tham gia", null);

        assertFalse(result.isRestoreSession(), "Buổi học thử không có số buổi tập để hoàn");
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getRefundAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()));
    }

    @Test
    @DisplayName("Dòng 5: Huấn luyện viên từ chối khi PENDING -> Hoàn 1 buổi cho học viên, không phạt")
    void testPtRejectPending() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(30);
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.PENDING, slotTime);

        CancellationCalculationResult result = ptPolicy.calculate(booking, now, "HLV trùng lịch đột xuất", null);

        assertTrue(result.isRestoreSession(), "Phải hoàn trả buổi tập cho học viên");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()));
    }

    @Test
    @DisplayName("Dòng 6: Huấn luyện viên hủy CONFIRMED cách giờ tập >= 24 giờ -> Hoàn 1 buổi, không đền bù, không phạt")
    void testPtCancelConfirmedAdvanceNotice() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(48); // Cách 48 giờ
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = ptPolicy.calculate(booking, now, "HLV đi công tác", null);

        assertTrue(result.isRestoreSession(), "Phải hoàn trả 1 buổi tập cho học viên");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()));
    }

    @Test
    @DisplayName("Dòng 7: Huấn luyện viên hủy CONFIRMED cách giờ tập < 24 giờ -> Hoàn 1 buổi, đền bù 20% cho học viên, phạt 20% trừ ví PT")
    void testPtCancelConfirmedLate() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(4); // Cách 4 giờ (< 24h)
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = ptPolicy.calculate(booking, now, "HLV ốm đột xuất", null);

        assertTrue(result.isRestoreSession(), "Vẫn hoàn lại 1 buổi cho học viên");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()));

        BigDecimal expectedCompAndPenalty = SESSION_FEE.multiply(BigDecimal.valueOf(0.20)); // 60.000 đ
        assertEquals(0, expectedCompAndPenalty.compareTo(result.getCompensationAmount()), "Đền bù 20% vào ví học viên");
        assertEquals(0, expectedCompAndPenalty.compareTo(result.getPenaltyAmount()), "Phạt 20% trừ từ ví Huấn luyện viên");
    }

    @Test
    @DisplayName("Dòng 8: Quản trị viên hủy do bất khả kháng (có evidence_url) -> Hoàn 1 buổi, không đền bù, không phạt")
    void testAdminCancelForceMajeure() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(2);
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        CancellationCalculationResult result = adminPolicy.calculate(
                booking, now, "Phòng tập bảo trì khẩn cấp do mất điện", "https://cdn.ptconnect.vn/evidence/power_outage.jpg"
        );

        assertTrue(result.isRestoreSession(), "Hoàn lại 1 buổi cho học viên");
        assertEquals(0, SESSION_FEE.compareTo(result.getRefundAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(result.getPenaltyAmount()));
        assertTrue(result.getExplanation().contains("power_outage.jpg"));
    }

    @Test
    @DisplayName("Minh chứng tính Đa hình (Polymorphism): Sử dụng cùng một interface CancellationPolicy cho 3 role khác nhau")
    void testPolymorphismViaInterface() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime slotTime = now.plusHours(5); // < 24h
        Booking booking = createBooking(BookingType.PACKAGE, BookingStatus.CONFIRMED, slotTime);

        // 1. Phía Student hủy sát giờ: không hoàn buổi, đền bù 50%
        CancellationPolicy studentPol = factory.getPolicy("STUDENT");
        CancellationCalculationResult rStudent = studentPol.calculate(booking, now, "Học viên hủy", null);
        assertFalse(rStudent.isRestoreSession());
        assertEquals(0, SESSION_FEE.multiply(BigDecimal.valueOf(0.50)).compareTo(rStudent.getCompensationAmount()));

        // 2. Phía PT hủy sát giờ: hoàn buổi, đền bù 20%, phạt 20%
        CancellationPolicy ptPol = factory.getPolicy("PT");
        CancellationCalculationResult rPt = ptPol.calculate(booking, now, "PT hủy", null);
        assertTrue(rPt.isRestoreSession());
        assertEquals(0, SESSION_FEE.multiply(BigDecimal.valueOf(0.20)).compareTo(rPt.getCompensationAmount()));
        assertEquals(0, SESSION_FEE.multiply(BigDecimal.valueOf(0.20)).compareTo(rPt.getPenaltyAmount()));

        // 3. Phía Admin hủy: hoàn buổi, không phạt
        CancellationPolicy admPol = factory.getPolicy("ADMIN");
        CancellationCalculationResult rAdmin = admPol.calculate(booking, now, "Admin hủy", null);
        assertTrue(rAdmin.isRestoreSession());
        assertEquals(0, BigDecimal.ZERO.compareTo(rAdmin.getCompensationAmount()));
        assertEquals(0, BigDecimal.ZERO.compareTo(rAdmin.getPenaltyAmount()));
    }

    @Test
    @DisplayName("Lấy chính sách thông qua Enum Role Type-Safe")
    void testPolymorphismViaRoleEnum() {
        assertSame(studentPolicy, factory.getPolicy(Role.STUDENT));
        assertSame(ptPolicy, factory.getPolicy(Role.PT));
        assertSame(adminPolicy, factory.getPolicy(Role.ADMIN));
    }
}
