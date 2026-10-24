package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.AdminBookingAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminPaymentAnalyticsResponse;
import com.PTconnect.backend.dto.response.AdminStatisticsResponse;

import java.util.List;

public interface IAdminStatisticsService {

    AdminStatisticsResponse getStatistics();

    List<AdminBookingAnalyticsResponse> getBookingAnalytics();

    List<AdminPaymentAnalyticsResponse> getPaymentAnalytics();
}
