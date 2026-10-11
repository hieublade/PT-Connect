package com.PTconnect.backend.modules.auth.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "trainers")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Trainer extends User {

    @OneToOne(mappedBy = "trainer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private PTProfile ptProfile;

    @Column(length = 200)
    private String expertise;

    @Column(length = 200)
    private String workingHours;

    @Column(nullable = false)
    private Integer totalClients = 0;
}