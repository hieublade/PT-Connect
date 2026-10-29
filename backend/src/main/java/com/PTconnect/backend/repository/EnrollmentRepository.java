package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {
    List<Enrollment> findByStudentId(Long studentId);
    List<Enrollment> findByCourseId(Long courseId);
    List<Enrollment> findByPtId(Long ptId);
    List<Enrollment> findByStudentIdAndCourseIdAndStatus(Long studentId, Long courseId, EnrollmentStatus status);

    @Query("SELECT e FROM Enrollment e " +
           "LEFT JOIN FETCH e.student " +
           "LEFT JOIN FETCH e.course " +
           "LEFT JOIN FETCH e.pt p " +
           "LEFT JOIN FETCH p.pt " +
           "WHERE e.pt.id = :ptId")
    List<Enrollment> findByPtIdWithDetails(@Param("ptId") Long ptId);

    @Query("SELECT e FROM Enrollment e " +
           "LEFT JOIN FETCH e.student " +
           "LEFT JOIN FETCH e.course " +
           "LEFT JOIN FETCH e.pt p " +
           "LEFT JOIN FETCH p.pt " +
           "WHERE e.student.id = :studentId")
    List<Enrollment> findByStudentIdWithDetails(@Param("studentId") Long studentId);

    // Khóa bi quan phục vụ trừ/hoàn buổi tập an toàn đa luồng (Milestone 6)
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT e FROM Enrollment e WHERE e.id = :id")
    Optional<Enrollment> findByIdWithLock(@Param("id") Long id);
}
