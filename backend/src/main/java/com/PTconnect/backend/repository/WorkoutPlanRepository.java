package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.WorkoutPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface WorkoutPlanRepository extends JpaRepository<WorkoutPlan, Long> {

    List<WorkoutPlan> findByEnrollmentIdOrderByCreatedAtDesc(Long enrollmentId);

    @Query("SELECT w FROM WorkoutPlan w WHERE w.enrollment.course.pt.id = :ptId ORDER BY w.createdAt DESC")
    List<WorkoutPlan> findByPtIdOrderByCreatedAtDesc(@Param("ptId") Long ptId);
}
