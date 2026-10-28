package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.PT;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PTRepository extends JpaRepository<PT, Long> {
}
