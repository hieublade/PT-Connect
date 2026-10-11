package com.PTconnect.backend.modules.auth.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "admins")
@Getter
@Setter
@NoArgsConstructor
public class Admin extends User {
    // Các thuộc tính riêng cho Admin (nếu có)
}