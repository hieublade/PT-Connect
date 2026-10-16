package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.WorkoutPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface WorkoutPlanRepository extends JpaRepository<WorkoutPlan, Long> {

    List<WorkoutPlan> findByEnrollmentIdOrderByCreatedAtDesc(Long enrollmentId);

    List<WorkoutPlan> findByPtIdOrderByCreatedAtDesc(Long ptId);
}
