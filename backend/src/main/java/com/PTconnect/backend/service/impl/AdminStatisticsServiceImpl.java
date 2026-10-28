package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.response.AdminBookingAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminPaymentAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminStatisticsResponse;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.Cancellation;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import com.PTconnect.backend.entity.enums.PaymentType;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.PaymentRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IAdminStatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AdminStatisticsServiceImpl implements IAdminStatisticsService {

    private final UserRepository userRepository;
    private final BookingRepository bookingRepository;
    private final PaymentRepository paymentRepository;

    @Override
    public AdminStatisticsResponse getStatistics() {
        long totalStudents = userRepository.countByRole(Role.STUDENT);
        long totalPts = userRepository.countByRole(Role.PT);
        long totalBookings = bookingRepository.count();

        BigDecimal totalRevenue = paymentRepository.sumAmountByPaymentTypeAndStatus(
                PaymentType.PURCHASE_PACKAGE,
                PaymentStatus.SUCCESS
        );
        if (totalRevenue == null) {
            totalRevenue = BigDecimal.ZERO;
        }

        return AdminStatisticsResponse.builder()
                .totalStudents(totalStudents)
                .totalPts(totalPts)
                .totalBookings(totalBookings)
                .totalRevenue(totalRevenue)
                .build();
    }

    @Override
    public List<AdminBookingAnalyticsResponse> getBookingAnalytics() {
        List<Object[]> rows = bookingRepository.findBookingsWithCancellation();
        return rows.stream()
                .map(this::mapRowToBookingAnalytics)
                .collect(Collectors.toList());
    }

    @Override
    public Page<AdminBookingAnalyticsResponse> getBookingAnalytics(Pageable pageable) {
        Page<Object[]> page = bookingRepository.findBookingsWithCancellation(pageable);
        return page.map(this::mapRowToBookingAnalytics);
    }

    @Override
    public List<AdminPaymentAnalyticsResponse> getPaymentAnalytics() {
        return paymentRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(AdminPaymentAnalyticsResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    public Page<AdminPaymentAnalyticsResponse> getPaymentAnalytics(Pageable pageable) {
        return paymentRepository.findAllByOrderByCreatedAtDesc(pageable)
                .map(AdminPaymentAnalyticsResponse::fromEntity);
    }

    private AdminBookingAnalyticsResponse mapRowToBookingAnalytics(Object[] row) {
        Booking b = (Booking) row[0];
        Cancellation cancel = (Cancellation) row[1];
        String cancelledBy = null;
        String reason = null;
        if (cancel != null) {
            cancelledBy = cancel.getCancelledByRole() != null ? cancel.getCancelledByRole() : "STUDENT";
            reason = cancel.getReason();
        } else if (b.getStatus() == BookingStatus.CANCELLED) {
            cancelledBy = "STUDENT";
        }
        return AdminBookingAnalyticsResponse.fromEntity(b, cancelledBy, reason);
    }
}

