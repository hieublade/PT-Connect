package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Workout;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface WorkoutRepository extends JpaRepository<Workout, Long> {

    List<Workout> findByPlanId(Long planId);
}
