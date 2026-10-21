package com.PTconnect.backend;

import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.entity.enums.WalletStatus;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
@Transactional
class BackendApplicationTests {

    @Autowired
    private UserRepository users;

    @Autowired
    private PTProfileRepository profiles;

    @Autowired
    private WalletRepository wallets;

    @BeforeEach
    void seedDataIfEmpty() {
        if (users.count() == 0) {
            Student s1 = Student.builder()
                    .fullName("Nguyen Van A")
                    .email("student.a@ptconnect.vn")
                    .phone("0900000001")
                    .passwordHash("hash")
                    .role(Role.STUDENT)
                    .status(UserStatus.ACTIVE)
                    .build();

            Student s2 = Student.builder()
                    .fullName("Tran Thi B")
                    .email("student.b@ptconnect.vn")
                    .phone("0900000002")
                    .passwordHash("hash")
                    .role(Role.STUDENT)
                    .status(UserStatus.ACTIVE)
                    .build();

            PT pt1 = PT.builder()
                    .fullName("Le Hoang C")
                    .email("pt.hoangc@ptconnect.vn")
                    .phone("0900000003")
                    .passwordHash("hash")
                    .role(Role.PT)
                    .status(UserStatus.ACTIVE)
                    .build();

            PT pt2 = PT.builder()
                    .fullName("Pham Minh D")
                    .email("pt.minhd@ptconnect.vn")
                    .phone("0900000004")
                    .passwordHash("hash")
                    .role(Role.PT)
                    .status(UserStatus.ACTIVE)
                    .build();

            Admin a1 = Admin.builder()
                    .fullName("Admin System")
                    .email("admin@ptconnect.vn")
                    .phone("0900000005")
                    .passwordHash("hash")
                    .role(Role.ADMIN)
                    .status(UserStatus.ACTIVE)
                    .build();

            users.saveAll(List.of(s1, s2, pt1, pt2, a1));

            PTProfile p1 = PTProfile.builder()
                    .pt(pt1)
                    .experienceYears(5)
                    .availableLocations("Cali")
                    .verificationStatus(VerificationStatus.VERIFIED)
                    .build();

            PTProfile p2 = PTProfile.builder()
                    .pt(pt2)
                    .experienceYears(3)
                    .availableLocations("Studio")
                    .verificationStatus(VerificationStatus.VERIFIED)
                    .build();

            profiles.saveAll(List.of(p1, p2));

            Wallet w = Wallet.builder()
                    .user(s2)
                    .balance(new BigDecimal("4200000.00"))
                    .currency("VND")
                    .status(WalletStatus.ACTIVE)
                    .build();

            wallets.save(w);
        }
    }

    @Test
    void entitiesMatchSchema() {
        assertEquals(5, users.findAll().size());

        User u1 = users.findByEmail("student.a@ptconnect.vn").orElseThrow();
        assertInstanceOf(Student.class, u1);

        User u3 = users.findByEmail("pt.hoangc@ptconnect.vn").orElseThrow();
        assertInstanceOf(PT.class, u3);

        assertEquals(2, profiles.findVerifiedAndActivePTs(
                VerificationStatus.VERIFIED, UserStatus.ACTIVE).size());

        User u2 = users.findByEmail("student.b@ptconnect.vn").orElseThrow();
        assertTrue(wallets.findByUserId(u2.getId()).isPresent());
    }
}