package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.VerificationStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;

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

    @Column(columnDefinition = "TEXT")
    private String bio;

    @Column(name = "experience_years", nullable = false)
    @Builder.Default
    private Integer experienceYears = 0;

    @Column(name = "available_locations", nullable = false, columnDefinition = "TEXT")
    private String availableLocations;

    @Column(name = "location_pricing_note", columnDefinition = "TEXT")
    private String locationPricingNote;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "certificate_urls")
    private String certificateUrls;

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