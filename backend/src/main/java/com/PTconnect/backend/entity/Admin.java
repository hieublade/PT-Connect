package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.Role;
import jakarta.persistence.DiscriminatorValue;
import jakarta.persistence.Entity;
import lombok.*;
import lombok.experimental.SuperBuilder;

@Entity
@DiscriminatorValue("ADMIN")
@Getter
@Setter
@NoArgsConstructor
@SuperBuilder
public class Admin extends User {

    @Override
    public Role getRole() { return Role.ADMIN; }

    @Override
    public String getHomePage() { return "ADMIN_DASHBOARD"; }

    @Override
    public String getDisplayRole() { return "Quản trị viên"; }
}
