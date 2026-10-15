package com.PTconnect.backend.modules.course.repository;

import com.PTconnect.backend.modules.course.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CourseRepository extends JpaRepository<Course, Long> {
}
