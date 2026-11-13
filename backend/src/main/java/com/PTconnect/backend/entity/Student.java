package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.Role;
import jakarta.persistence.DiscriminatorValue;
import jakarta.persistence.Entity;
import lombok.*;
import lombok.experimental.SuperBuilder;

@Entity
@DiscriminatorValue("STUDENT")
@Getter
@Setter
@NoArgsConstructor
@SuperBuilder
public class Student extends User {

    @Override
    public Role getRole() { return Role.STUDENT; }

    @Override
    public String getHomePage() { return "STUDENT_HOME"; }

    @Override
    public String getDisplayRole() { return "Học viên"; }
}
