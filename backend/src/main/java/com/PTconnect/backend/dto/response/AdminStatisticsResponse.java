package com.PTconnect.backend.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AdminStatisticsResponse {

    private long totalStudents;

    @JsonProperty("totalPts")
    private long totalPts;

    private long totalBookings;
    private BigDecimal totalRevenue;
}
