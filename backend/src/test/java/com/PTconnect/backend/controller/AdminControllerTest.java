package com.PTconnect.backend.controller;

import com.PTconnect.backend.config.JwtFilter;
import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.config.SecurityConfig;
import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.Admin;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.GlobalExceptionHandler;
import com.PTconnect.backend.service.IAdminPTService;
import com.PTconnect.backend.service.IUserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;
import com.PTconnect.backend.service.IAdminStatisticsService;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = AdminController.class)
@Import({SecurityConfig.class, JwtUtil.class, JwtFilter.class, GlobalExceptionHandler.class})
@ActiveProfiles("test")
@DisplayName("Kiểm thử các API quản trị duyệt PT (Admin Milestone 4)")
class AdminControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    @MockitoBean
    private IUserService userService;

    @MockitoBean
    private IAdminPTService adminPTService;

    @MockitoBean
    private IAdminStatisticsService adminStatisticsService;

    private String adminToken;

    @BeforeEach
    void setUp() {
        Admin admin = Admin.builder()
                .id(5L)
                .email("admin@ptconnect.vn")
                .fullName("Admin System")
                .role(Role.ADMIN)
                .status(UserStatus.ACTIVE)
                .build();
        adminToken = jwtUtil.generateToken(admin);
    }

    @Test
    @DisplayName("Admin lấy danh sách PT chờ duyệt PENDING (200 OK)")
    void testGetPendingPTsSuccess() throws Exception {
        PendingPTResponse pending = PendingPTResponse.builder()
                .id(10L)
                .userId(15L)
                .fullName("Nguyen Van PT")
                .email("newpt@ptconnect.vn")
                .phone("0988776655")
                .experienceYears(2)
                .availableLocations("Hà Nội")
                .verificationStatus(VerificationStatus.PENDING)
                .userStatus(UserStatus.PENDING)
                .build();

        when(adminPTService.getPendingPTs()).thenReturn(List.of(pending));

        mockMvc.perform(get("/api/v1/admin/pt/pending")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data[0].fullName").value("Nguyen Van PT"))
                .andExpect(jsonPath("$.data[0].verificationStatus").value("PENDING"));
    }

    @Test
    @DisplayName("Admin phê duyệt PT thành công (200 OK, VERIFIED & ACTIVE)")
    void testApprovePTSuccess() throws Exception {
        PTProfileResponse approved = PTProfileResponse.builder()
                .id(10L)
                .userId(15L)
                .fullName("Nguyen Van PT")
                .verificationStatus(VerificationStatus.VERIFIED)
                .userStatus(UserStatus.ACTIVE)
                .build();

        when(adminPTService.approvePT(10L)).thenReturn(approved);

        mockMvc.perform(put("/api/v1/admin/pt/10/approve")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.verificationStatus").value("VERIFIED"))
                .andExpect(jsonPath("$.data.userStatus").value("ACTIVE"));
    }

    @Test
    @DisplayName("Admin từ chối PT thành công (200 OK, REJECTED & PENDING)")
    void testRejectPTSuccess() throws Exception {
        PTProfileResponse rejected = PTProfileResponse.builder()
                .id(10L)
                .userId(15L)
                .fullName("Nguyen Van PT")
                .verificationStatus(VerificationStatus.REJECTED)
                .userStatus(UserStatus.PENDING)
                .build();

        when(adminPTService.rejectPT(10L)).thenReturn(rejected);

        mockMvc.perform(put("/api/v1/admin/pt/10/reject")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.verificationStatus").value("REJECTED"))
                .andExpect(jsonPath("$.data.userStatus").value("PENDING"));
    }
}
