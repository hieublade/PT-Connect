package com.PTconnect.backend.controller;

import com.PTconnect.backend.config.JwtFilter;
import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.config.SecurityConfig;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.service.IUserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = UserController.class)
@Import({SecurityConfig.class, JwtUtil.class, JwtFilter.class})
@ActiveProfiles("test")
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    @MockitoBean
    private IUserService userService;

    private String userToken;
    private String adminToken;

    @BeforeEach
    void setUp() {
        userToken = jwtUtil.generateToken("student.a@ptconnect.vn", "STUDENT");
        adminToken = jwtUtil.generateToken("admin@ptconnect.vn", "ADMIN");

        UserDTO student = UserDTO.builder()
                .id(1L)
                .fullName("Nguyen Van A")
                .email("student.a@ptconnect.vn")
                .phone("0900000001")
                .role(Role.STUDENT)
                .status(UserStatus.ACTIVE)
                .displayRole("Học viên")
                .homePage("/student/home")
                .createdAt(LocalDateTime.now())
                .build();

        UserDTO pt = UserDTO.builder()
                .id(2L)
                .fullName("Le Hoang C")
                .email("pt.hoangc@ptconnect.vn")
                .phone("0900000003")
                .role(Role.PT)
                .status(UserStatus.ACTIVE)
                .displayRole("Huấn luyện viên")
                .homePage("/pt/dashboard")
                .createdAt(LocalDateTime.now())
                .build();

        when(userService.getUserById(1L)).thenReturn(student);
    }

    @Test
    void testAnonymousGetUserByIdReturns401() throws Exception {
        mockMvc.perform(get("/api/v1/users/1"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testAuthenticatedGetUserByIdReturns200() throws Exception {
        mockMvc.perform(get("/api/v1/users/1")
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.id").value(1))
                .andExpect(jsonPath("$.data.email").value("student.a@ptconnect.vn"))
                .andExpect(jsonPath("$.data.passwordHash").doesNotExist());
    }

    @Test
    void testAdminGetUserByIdReturns200() throws Exception {
        mockMvc.perform(get("/api/v1/users/1")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.id").value(1));
    }
}
