package com.PTconnect.backend.modules.auth.repository;

import com.PTconnect.backend.modules.auth.entity.Admin;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AdminRepository extends JpaRepository<Admin, Long> {
}