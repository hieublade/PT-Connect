package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.LoginRequest;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.Wallet;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@ActiveProfiles("test")
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PTProfileRepository ptProfileRepository;

    @Autowired
    private WalletRepository walletRepository;

    @Test
    @DisplayName("Đăng ký Học viên (STUDENT) thành công và tự động tạo Ví")
    void testRegisterStudentSuccess() throws Exception {
        String uniqueEmail = "student.test." + System.currentTimeMillis() + "@ptconnect.vn";
        RegisterRequest request = RegisterRequest.builder()
                .fullName("Nguyễn Văn Student")
                .email(uniqueEmail)
                .password("123456")
                .phone("098" + (System.currentTimeMillis() % 10000000))
                .role(Role.STUDENT)
                .build();

        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.token").isNotEmpty())
                .andExpect(jsonPath("$.data.user.email").value(uniqueEmail))
                .andExpect(jsonPath("$.data.user.role").value("STUDENT"))
                .andExpect(jsonPath("$.data.user.status").value("ACTIVE"));

        // Kiểm tra database: ví tiền được tạo tự động
        User user = userRepository.findByEmail(uniqueEmail).orElseThrow();
        assertEquals(UserStatus.ACTIVE, user.getStatus());
        Optional<Wallet> walletOpt = walletRepository.findByUserId(user.getId());
        assertTrue(walletOpt.isPresent(), "Ví tiền phải được tạo tự động cùng user");
        assertEquals(0, walletOpt.get().getBalance().signum());
    }

    @Test
    @DisplayName("Đăng ký PT thành công: PT có status=PENDING, PTProfile ở trạng thái PENDING và tạo Ví trong 1 transaction")
    void testRegisterPTSuccess() throws Exception {
        String uniqueEmail = "pt.test." + System.currentTimeMillis() + "@ptconnect.vn";
        RegisterRequest request = RegisterRequest.builder()
                .fullName("Trần Văn PT")
                .email(uniqueEmail)
                .password("123456")
                .phone("097" + (System.currentTimeMillis() % 10000000))
                .role(Role.PT)
                .bio("Huấn luyện viên thể hình 5 năm kinh nghiệm")
                .experienceYears(5)
                .availableLocations("Quận 1, Quận 7, TP.HCM")
                .build();

        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.token").isNotEmpty())
                .andExpect(jsonPath("$.data.user.role").value("PT"))
                .andExpect(jsonPath("$.data.user.status").value("PENDING"));

        // Kiểm tra database: PT có trạng thái PENDING
        User user = userRepository.findByEmail(uniqueEmail).orElseThrow();
        assertEquals(UserStatus.PENDING, user.getStatus(), "PT mới đăng ký phải ở trạng thái PENDING");

        // Kiểm tra database: PTProfile có trạng thái PENDING
        Optional<PTProfile> profileOpt = ptProfileRepository.findByPtId(user.getId());
        assertTrue(profileOpt.isPresent(), "PTProfile phải được tạo cùng PT");
        assertEquals(VerificationStatus.PENDING, profileOpt.get().getVerificationStatus(), "PT mới đăng ký phải ở trạng thái PENDING");

        // Kiểm tra database: ví tiền cũng được tạo
        Optional<Wallet> walletOpt = walletRepository.findByUserId(user.getId());
        assertTrue(walletOpt.isPresent(), "Ví tiền phải được tạo tự động cùng PT");
    }

    @Test
    @DisplayName("Đăng nhập và lấy thông tin cá nhân qua GET /api/v1/auth/me")
    void testLoginAndGetMeFlow() throws Exception {
        String uniqueEmail = "login.test." + System.currentTimeMillis() + "@ptconnect.vn";
        RegisterRequest registerReq = RegisterRequest.builder()
                .fullName("Lê Đăng Nhập")
                .email(uniqueEmail)
                .password("password123")
                .phone("096" + (System.currentTimeMillis() % 10000000))
                .role(Role.STUDENT)
                .build();

        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(registerReq)))
                .andExpect(status().isCreated());

        // Đăng nhập đúng mật khẩu
        LoginRequest loginReq = LoginRequest.builder()
                .email(uniqueEmail)
                .password("password123")
                .build();

        MvcResult loginResult = mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginReq)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.token").isNotEmpty())
                .andReturn();

        String responseBody = loginResult.getResponse().getContentAsString();
        String token = objectMapper.readTree(responseBody).path("data").path("token").asText();

        // Gọi GET /api/v1/auth/me với Bearer Token
        mockMvc.perform(get("/api/v1/auth/me")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.email").value(uniqueEmail))
                .andExpect(jsonPath("$.data.fullName").value("Lê Đăng Nhập"));
    }

    @Test
    @DisplayName("Đăng nhập sai mật khẩu phải trả về lỗi 401")
    void testLoginWrongPassword() throws Exception {
        LoginRequest loginReq = LoginRequest.builder()
                .email("student.a@ptconnect.vn")
                .password("sai_mat_khau_123")
                .build();

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginReq)))
                .andExpect(status().isUnauthorized());
    }
}
