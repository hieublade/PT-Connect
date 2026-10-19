package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.enums.CourseStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CourseRepository extends JpaRepository<Course, Long> {
    List<Course> findByPtId(Long ptId);
    List<Course> findByStatus(CourseStatus status);
    List<Course> findByPtIdAndStatus(Long ptId, CourseStatus status);
}
