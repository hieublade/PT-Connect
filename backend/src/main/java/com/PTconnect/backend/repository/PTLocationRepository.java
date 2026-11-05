package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.PTLocation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PTLocationRepository extends JpaRepository<PTLocation, Long> {

    List<PTLocation> findByPtProfileId(Long ptProfileId);

    List<PTLocation> findByLocationNameContainingIgnoreCase(String locationKeyword);

    void deleteByPtProfileId(Long ptProfileId);
}

