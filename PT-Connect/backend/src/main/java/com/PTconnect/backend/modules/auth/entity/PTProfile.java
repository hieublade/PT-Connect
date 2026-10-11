package com.PTconnect.backend.modules.auth.entity;

import com.PTconnect.backend.common.enums.VerificationStatus;
import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

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
    @JoinColumn(name = "trainer_id", nullable = false, unique = true)
    private Trainer trainer;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String biography;

    @Size(max = 255)
    @Column(length = 255)
    private String specialization;

    @Size(max = 255)
    @Column(length = 255)
    private String certificates;

    @Size(max = 500)
    @Column(length = 500)
    private String availability;

    @Column(length = 255)
    private String location;

    @DecimalMin(value = "0.0", inclusive = true)
    @Column(nullable = false)
    @Builder.Default
    private Double hourlyRate = 0.0;

    @Builder.Default
    @Column(nullable = false)
    private Double averageRating = 0.0;

    @Builder.Default
    @Column(nullable = false)
    private Integer totalReviews = 0;

    @Builder.Default
    @Column(nullable = false)
    private Double contractCompletionRate = 100.0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    @Builder.Default
    private VerificationStatus verificationStatus = VerificationStatus.PENDING;

    @Builder.Default
    @Column(nullable = false)
    private Boolean isVerified = false;

    @Builder.Default
    @Column(nullable = false)
    private Boolean isFeatured = false;

    @Builder.Default
    @Column(nullable = false)
    private Integer totalStudents = 0;

    @NotNull(message = "Trainer không được null")
    public Trainer getTrainer() {
        return trainer;
    }
}