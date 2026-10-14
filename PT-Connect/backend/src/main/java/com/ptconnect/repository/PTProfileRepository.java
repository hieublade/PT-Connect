package com.ptconnect.repository;

import com.ptconnect.entity.PTProfile;
import com.ptconnect.enums.VerificationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PTProfileRepository extends JpaRepository<PTProfile, Long> {
    Optional<PTProfile> findByUserId(Long userId);
    List<PTProfile> findByVerificationStatus(VerificationStatus status);

    @Query("SELECT p FROM PTProfile p WHERE p.verificationStatus = 'VERIFIED' " +
           "AND (:name IS NULL OR LOWER(p.user.fullName) LIKE LOWER(CONCAT('%', :name, '%')))")
    List<PTProfile> searchVerifiedPTs(@Param("name") String name);
}