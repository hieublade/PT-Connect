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

    // Khóa bi quan phục vụ trừ/hoàn buổi tập an toàn đa luồng (Milestone 6)
    @org.springframework.data.jpa.repository.Lock(jakarta.persistence.LockModeType.PESSIMISTIC_WRITE)
    @org.springframework.data.jpa.repository.Query("SELECT e FROM Enrollment e WHERE e.id = :id")
    Optional<Enrollment> findByIdWithLock(@org.springframework.data.repository.query.Param("id") Long id);
}
