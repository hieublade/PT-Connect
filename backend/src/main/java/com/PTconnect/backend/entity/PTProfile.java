package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.VerificationStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Entity
@Table(name = "pt_profiles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private PT pt;

    public User getUser() {
        return this.pt;
    }

    @Column(columnDefinition = "TEXT")
    private String bio;

    @Column(name = "experience_years", nullable = false)
    @Builder.Default
    private Integer experienceYears = 0;

    @OneToMany(mappedBy = "ptProfile", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<PTLocation> locations = new ArrayList<>();

    @Transient
    private String availableLocations;

    public String getAvailableLocations() {
        if (this.locations != null && !this.locations.isEmpty()) {
            return this.locations.stream()
                    .map(PTLocation::getLocationName)
                    .collect(Collectors.joining("; "));
        }
        return this.availableLocations != null ? this.availableLocations : "";
    }

    public void setAvailableLocations(String locationsStr) {
        this.availableLocations = locationsStr;
        if (this.locations == null) {
            this.locations = new ArrayList<>();
        } else {
            this.locations.clear();
        }

        if (locationsStr != null && !locationsStr.isBlank()) {
            Arrays.stream(locationsStr.split(";"))
                    .map(String::trim)
                    .filter(s -> !s.isEmpty())
                    .forEach(this::addLocation);
        }
    }

    public void addLocation(String locationName) {
        if (this.locations == null) {
            this.locations = new ArrayList<>();
        }
        if (locationName != null && !locationName.trim().isEmpty()) {
            PTLocation loc = PTLocation.builder()
                    .ptProfile(this)
                    .locationName(locationName.trim())
                    .build();
            this.locations.add(loc);
        }
    }

    public void clearLocations() {
        if (this.locations != null) {
            this.locations.clear();
        }
    }

    @Column(name = "location_pricing_note", columnDefinition = "TEXT")
    private String locationPricingNote;

    @Column(name = "certificate_url", length = 500)
    private String certificateUrl;

    public String getCertificateUrls() {
        return this.certificateUrl;
    }

    public void setCertificateUrls(String certificateUrls) {
        this.certificateUrl = certificateUrls;
    }

    @Column(name = "average_rating", insertable = false, updatable = false)
    private BigDecimal averageRating;

    @Column(name = "total_reviews", insertable = false, updatable = false)
    private Integer totalReviews;

    @Enumerated(EnumType.STRING)
    @Column(name = "verification_status", nullable = false)
    @Builder.Default
    private VerificationStatus verificationStatus = VerificationStatus.PENDING;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", insertable = false, updatable = false)
    private LocalDateTime updatedAt;

    // Phương thức nghiệp vụ quản lý quy trình xét duyệt (Encapsulation / Rich Domain Model)
    public void approve() {
        this.verificationStatus = VerificationStatus.VERIFIED;
        if (this.pt != null) {
            this.pt.activate();
        }
    }

    public void reject() {
        this.verificationStatus = VerificationStatus.REJECTED;
        if (this.pt != null) {
            this.pt.pending();
        }
    }
}