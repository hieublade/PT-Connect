package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.AdminBookingAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminPaymentAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminStatisticsResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface IAdminStatisticsService {

    AdminStatisticsResponse getStatistics();

    List<AdminBookingAnalyticsResponse> getBookingAnalytics();

    Page<AdminBookingAnalyticsResponse> getBookingAnalytics(Pageable pageable);

    List<AdminPaymentAnalyticsResponse> getPaymentAnalytics();

    Page<AdminPaymentAnalyticsResponse> getPaymentAnalytics(Pageable pageable);
}

