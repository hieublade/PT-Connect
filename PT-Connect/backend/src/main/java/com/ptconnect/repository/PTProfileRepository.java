package com.ptconnect.repository;

import com.ptconnect.entity.PTProfile;
import com.ptconnect.entity.enums.UserStatus;
import com.ptconnect.entity.enums.VerificationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

public interface PTProfileRepository extends JpaRepository<PTProfile, Long> {

    // Danh sách cho Student: phải VERIFIED và users.status = ACTIVE (AC 3.6)
    @Query("""
           SELECT p FROM PTProfile p
           WHERE p.verificationStatus = :vStatus AND p.pt.status = :uStatus
           """)
    List<PTProfile> findVerifiedAndActivePTs(@Param("vStatus") VerificationStatus vStatus,
                                             @Param("uStatus") UserStatus uStatus);

    // Tìm theo tên (truyền name = "" để lấy tất cả)
    @Query("""
           SELECT p FROM PTProfile p
           WHERE p.verificationStatus = :vStatus AND p.pt.status = :uStatus
             AND LOWER(p.pt.fullName) LIKE LOWER(CONCAT('%', :name, '%'))
           """)
    List<PTProfile> searchVerifiedPTs(@Param("name") String name,
                                      @Param("vStatus") VerificationStatus vStatus,
                                      @Param("uStatus") UserStatus uStatus);

    List<PTProfile> findByVerificationStatus(VerificationStatus status);

    Optional<PTProfile> findByPtId(Long userId);
}