package com.PTconnect.backend.modules.auth.repository;

import com.PTconnect.backend.modules.auth.entity.PTProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PTProfileRepository extends JpaRepository<PTProfile, Long> {
    Optional<PTProfile> findByTrainerId(Long trainerId);
}