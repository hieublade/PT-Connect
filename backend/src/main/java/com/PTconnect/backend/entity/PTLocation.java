package com.PTconnect.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "pt_locations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTLocation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "pt_id", nullable = false)
    private PTProfile ptProfile;

    @Column(name = "location_name", nullable = false, length = 255)
    private String locationName;
}

