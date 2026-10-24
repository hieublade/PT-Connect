package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    boolean existsByPhone(String phone);
    List<User> findByRole(Role role);
    long countByRole(Role role);
}