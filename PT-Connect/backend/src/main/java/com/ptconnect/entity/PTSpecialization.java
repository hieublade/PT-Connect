package com.ptconnect.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "pt_specializations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTSpecialization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pt_id", nullable = false)
    private PTProfile ptProfile;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "specialization_id", nullable = false)
    private Specialization specialization;
}