package com.PTconnect.backend.modules.auth.repository;

import com.PTconnect.backend.modules.auth.entity.Trainer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TrainerRepository extends JpaRepository<Trainer, Long> {
}