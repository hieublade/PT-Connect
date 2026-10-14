package com.ptconnect.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.SuperBuilder;

@Entity
@DiscriminatorValue("PT")
@Getter
@Setter
@NoArgsConstructor
@SuperBuilder
public class PT extends User {

    @OneToOne(mappedBy = "pt", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private PTProfile profile;

    @Override
    public String getHomePage() { return "PT_DASHBOARD"; }

    @Override
    public String getDisplayRole() { return "Huấn luyện viên"; }
}