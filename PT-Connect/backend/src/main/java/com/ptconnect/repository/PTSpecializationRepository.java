package com.ptconnect.repository;

import com.ptconnect.entity.PTSpecialization;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PTSpecializationRepository extends JpaRepository<PTSpecialization, Long> {
    List<PTSpecialization> findByPtProfileId(Long ptProfileId);
    void deleteByPtProfileId(Long ptProfileId);
}