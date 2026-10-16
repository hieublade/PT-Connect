package com.PTconnect.backend;

import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.Student;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class BackendApplicationTests {

    @Autowired UserRepository users;
    @Autowired PTProfileRepository profiles;
    @Autowired WalletRepository wallets;

    @Test
    void entitiesMatchSchema() {
        assertEquals(5, users.findAll().size());

        User u1 = users.findByEmail("student.a@ptconnect.vn").orElseThrow();
        assertInstanceOf(Student.class, u1);

        User u3 = users.findByEmail("pt.hoangc@ptconnect.vn").orElseThrow();
        assertInstanceOf(PT.class, u3);

        assertEquals(2, profiles.findVerifiedAndActivePTs(
                VerificationStatus.VERIFIED, UserStatus.ACTIVE).size());

        assertTrue(wallets.findByUserId(2L).isPresent());
    }
}