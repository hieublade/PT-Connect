package com.ptconnect.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PTProfileResponse {
    private Long id;
    private Long userId;
    private String fullName;
    private String email;
    private String phone;
    private String avatarUrl;
    private String bio;
    private Integer experienceYears;
    private String availableLocations;
    private String locationPricingNote;
    private BigDecimal averageRating;
    private Integer totalReviews;
    private String verificationStatus;
    private List<String> specializations;
}