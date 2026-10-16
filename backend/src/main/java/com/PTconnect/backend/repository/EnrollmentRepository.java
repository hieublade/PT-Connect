package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {
    List<Enrollment> findByStudentId(Long studentId);
    List<Enrollment> findByCourseId(Long courseId);
    List<Enrollment> findByPtId(Long ptId);
    List<Enrollment> findByStatus(EnrollmentStatus status);
    Optional<Enrollment> findByStudentIdAndCourseId(Long studentId, Long courseId);
}
