package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.response.AdminBookingAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminPaymentAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminStatisticsResponse;
import com.PTconnect.backend.entity.Cancellation;
import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import com.PTconnect.backend.entity.enums.PaymentType;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.CancellationRepository;
import com.PTconnect.backend.repository.PaymentRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IAdminStatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AdminStatisticsServiceImpl implements IAdminStatisticsService {

    private final UserRepository userRepository;
    private final BookingRepository bookingRepository;
    private final PaymentRepository paymentRepository;
    private final CancellationRepository cancellationRepository;

    @Override
    public AdminStatisticsResponse getStatistics() {
        long totalStudents = userRepository.countByRole(Role.STUDENT);
        long totalPts = userRepository.countByRole(Role.PT);
        long totalBookings = bookingRepository.count();

        List<Payment> packagePayments = paymentRepository.findByPaymentTypeAndStatus(
                PaymentType.PURCHASE_PACKAGE,
                PaymentStatus.SUCCESS
        );

        BigDecimal totalRevenue = packagePayments.stream()
                .map(Payment::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        return AdminStatisticsResponse.builder()
                .totalStudents(totalStudents)
                .totalPts(totalPts)
                .totalBookings(totalBookings)
                .totalRevenue(totalRevenue)
                .build();
    }

    @Override
    public List<AdminBookingAnalyticsResponse> getBookingAnalytics() {
        Map<Long, Cancellation> cancelMap = cancellationRepository.findAll().stream()
                .filter(c -> c.getBooking() != null)
                .collect(Collectors.toMap(c -> c.getBooking().getId(), c -> c, (c1, c2) -> c1));

        return bookingRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(b -> {
                    Cancellation cancel = cancelMap.get(b.getId());
                    String cancelledBy = null;
                    String reason = null;
                    if (cancel != null) {
                        cancelledBy = cancel.getCancelledByRole() != null ? cancel.getCancelledByRole() : "STUDENT";
                        reason = cancel.getReason();
                    } else if (b.getStatus() == BookingStatus.CANCELLED) {
                        cancelledBy = "STUDENT";
                    }
                    return AdminBookingAnalyticsResponse.fromEntity(b, cancelledBy, reason);
                })
                .collect(Collectors.toList());
    }

    @Override
    public List<AdminPaymentAnalyticsResponse> getPaymentAnalytics() {
        return paymentRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(AdminPaymentAnalyticsResponse::fromEntity)
                .collect(Collectors.toList());
    }
}
