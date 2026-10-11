package com.PTconnect.backend.modules.auth.repository;

import com.PTconnect.backend.modules.auth.entity.Student;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {
}