package com.PTconnect.backend.controller;

import com.PTconnect.backend.config.JwtFilter;
import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.config.SecurityConfig;
import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.GlobalExceptionHandler;
import com.PTconnect.backend.service.IPTService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = PTController.class)
@Import({SecurityConfig.class, JwtUtil.class, JwtFilter.class, GlobalExceptionHandler.class})
@ActiveProfiles("test")
@DisplayName("Kiểm thử các API chức năng của PT (Milestone 4)")
class PTControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @MockitoBean
    private IPTService ptService;

    private String ptToken;

    @BeforeEach
    void setUp() {
        PT pt = PT.builder()
                .id(3L)
                .email("pt.hoangc@ptconnect.vn")
                .fullName("Le Hoang C")
                .role(Role.PT)
                .status(UserStatus.ACTIVE)
                .build();
        ptToken = jwtUtil.generateToken(pt);
    }

    @Test
    @DisplayName("Lấy thông tin hồ sơ cá nhân của PT (200 OK)")
    void testGetProfileSuccess() throws Exception {
        PTProfileResponse profileResponse = PTProfileResponse.builder()
                .id(1L)
                .userId(3L)
                .fullName("Le Hoang C")
                .email("pt.hoangc@ptconnect.vn")
                .experienceYears(5)
                .availableLocations("Phòng Cali Cầu Giấy")
                .verificationStatus(VerificationStatus.VERIFIED)
                .build();

        when(ptService.getProfile(eq("pt.hoangc@ptconnect.vn"))).thenReturn(profileResponse);

        mockMvc.perform(get("/api/v1/pt/profile")
                        .header("Authorization", "Bearer " + ptToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.fullName").value("Le Hoang C"))
                .andExpect(jsonPath("$.data.experienceYears").value(5));
    }

    @Test
    @DisplayName("Cập nhật thông tin hồ sơ PT thành công (200 OK)")
    void testUpdateProfileSuccess() throws Exception {
        UpdatePTProfileRequest request = UpdatePTProfileRequest.builder()
                .bio("HLV thể hình chuyên nghiệp")
                .experienceYears(6)
                .availableLocations("Cầu Giấy, Hà Nội")
                .locationPricingNote("Phụ thu 10% tại nhà")
                .certificateUrls("[\"https://cdn.ptconnect.vn/cert1.pdf\"]")
                .build();

        PTProfileResponse updated = PTProfileResponse.builder()
                .id(1L)
                .fullName("Le Hoang C")
                .experienceYears(6)
                .availableLocations("Cầu Giấy, Hà Nội")
                .build();

        when(ptService.updateProfile(eq("pt.hoangc@ptconnect.vn"), any(UpdatePTProfileRequest.class)))
                .thenReturn(updated);

        mockMvc.perform(put("/api/v1/pt/profile")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data.experienceYears").value(6));
    }

    @Test
    @DisplayName("Cập nhật hồ sơ PT thất bại khi địa điểm để trống (400 Bad Request)")
    void testUpdateProfileEmptyLocationReturns400() throws Exception {
        UpdatePTProfileRequest request = UpdatePTProfileRequest.builder()
                .bio("HLV")
                .experienceYears(3)
                .availableLocations("")
                .build();

        mockMvc.perform(put("/api/v1/pt/profile")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    @DisplayName("Tạo khóa học mới thành công (201 Created)")
    void testCreateCourseSuccess() throws Exception {
        CreateCourseRequest request = CreateCourseRequest.builder()
                .title("Gói Giảm Mỡ Cấp Tốc 12 Buổi")
                .description("Giáo trình HIIT và Dinh dưỡng chuẩn khoa học")
                .totalSessions(12)
                .validityDays(30)
                .basePrice(new BigDecimal("3600000.00"))
                .build();

        CourseResponse courseResponse = CourseResponse.builder()
                .id(10L)
                .ptId(1L)
                .ptName("Le Hoang C")
                .title("Gói Giảm Mỡ Cấp Tốc 12 Buổi")
                .totalSessions(12)
                .validityDays(30)
                .basePrice(new BigDecimal("3600000.00"))
                .status(CourseStatus.ACTIVE)
                .createdAt(LocalDateTime.now())
                .build();

        when(ptService.createCourse(eq("pt.hoangc@ptconnect.vn"), any(CreateCourseRequest.class)))
                .thenReturn(courseResponse);

        mockMvc.perform(post("/api/v1/pt/courses")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value(201))
                .andExpect(jsonPath("$.data.title").value("Gói Giảm Mỡ Cấp Tốc 12 Buổi"));
    }

    @Test
    @DisplayName("Tạo khóa học thất bại khi tổng số buổi <= 0 (400 Bad Request)")
    void testCreateCourseInvalidSessionsReturns400() throws Exception {
        CreateCourseRequest request = CreateCourseRequest.builder()
                .title("Khóa học lỗi")
                .totalSessions(0)
                .validityDays(30)
                .basePrice(new BigDecimal("1000000.00"))
                .build();

        mockMvc.perform(post("/api/v1/pt/courses")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    @DisplayName("Lấy danh sách khóa học của PT (200 OK)")
    void testGetCoursesSuccess() throws Exception {
        CourseResponse c = CourseResponse.builder()
                .id(1L)
                .title("Khóa Tập Cơ Bản")
                .totalSessions(24)
                .basePrice(new BigDecimal("5000000.00"))
                .status(CourseStatus.ACTIVE)
                .build();

        when(ptService.getCourses(eq("pt.hoangc@ptconnect.vn"))).thenReturn(List.of(c));

        mockMvc.perform(get("/api/v1/pt/courses")
                        .header("Authorization", "Bearer " + ptToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200))
                .andExpect(jsonPath("$.data[0].title").value("Khóa Tập Cơ Bản"));
    }

    @Test
    @DisplayName("Tạo khung giờ rảnh (Slot) thành công (201 Created)")
    void testCreateSlotSuccess() throws Exception {
        LocalDateTime start = LocalDateTime.now().plusDays(1).withHour(9).withMinute(0);
        LocalDateTime end = start.plusHours(1);

        SlotResponse slotResponse = SlotResponse.builder()
                .id(100L)
                .ptId(1L)
                .startTime(start)
                .endTime(end)
                .status(SlotStatus.AVAILABLE)
                .build();

        when(ptService.createSlot(eq("pt.hoangc@ptconnect.vn"), any(CreateSlotRequest.class)))
                .thenReturn(slotResponse);

        String json = "{\"startTime\":\"2026-10-25T09:00:00\",\"endTime\":\"2026-10-25T10:00:00\"}";

        mockMvc.perform(post("/api/v1/pt/slots")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value(201))
                .andExpect(jsonPath("$.data.status").value("AVAILABLE"));
    }

    @Test
    @DisplayName("Tạo slot lỗi khi giờ bắt đầu trong quá khứ (400 Bad Request)")
    void testCreateSlotPastReturns400() throws Exception {
        when(ptService.createSlot(eq("pt.hoangc@ptconnect.vn"), any(CreateSlotRequest.class)))
                .thenThrow(new IllegalArgumentException("Thời gian bắt đầu slot không được ở trong quá khứ"));

        String json = "{\"startTime\":\"2020-01-01T09:00:00\",\"endTime\":\"2020-01-01T10:00:00\"}";

        mockMvc.perform(post("/api/v1/pt/slots")
                        .header("Authorization", "Bearer " + ptToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.message").value("Thời gian bắt đầu slot không được ở trong quá khứ"));
    }

    @Test
    @DisplayName("Xóa slot AVAILABLE thành công (200 OK)")
    void testDeleteSlotSuccess() throws Exception {
        doNothing().when(ptService).deleteSlot(eq("pt.hoangc@ptconnect.vn"), eq(5L));

        mockMvc.perform(delete("/api/v1/pt/slots/5")
                        .header("Authorization", "Bearer " + ptToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value(200));
    }
}
