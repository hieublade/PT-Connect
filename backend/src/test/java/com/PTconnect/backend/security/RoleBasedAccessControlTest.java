package com.PTconnect.backend.security;

import com.PTconnect.backend.config.JwtFilter;
import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.config.SecurityConfig;
import com.PTconnect.backend.controller.AdminController;
import com.PTconnect.backend.controller.PTController;
import com.PTconnect.backend.controller.PublicController;
import com.PTconnect.backend.controller.StudentController;
import com.PTconnect.backend.service.IAdminPTService;
import com.PTconnect.backend.service.IPTService;
import com.PTconnect.backend.service.IUserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Ma trận phân quyền Role × API (Milestone 3 - Huy).
 *
 * <p>Ma trận kiểm tra:</p>
 * <pre>
 *   Role        | /api/public/health | /api/student/dashboard | /api/pt/courses | /api/admin/users
 *   ------------+--------------------+------------------------+-----------------+------------------
 *   Anonymous   |      200 OK        |    401 Unauthorized    | 401 Unauth      | 401 Unauth
 *   STUDENT     |      200 OK        |        200 OK          | 403 Forbidden   | 403 Forbidden
 *   PT          |      200 OK        |     403 Forbidden      |     200 OK      | 403 Forbidden
 *   ADMIN       |      200 OK        |     403 Forbidden      | 403 Forbidden   |     200 OK
 * </pre>
 */
@WebMvcTest(controllers = {
        PublicController.class,
        StudentController.class,
        PTController.class,
        AdminController.class
})
@Import({SecurityConfig.class, JwtUtil.class, JwtFilter.class})
@ActiveProfiles("test")
@DisplayName("Ma trận phân quyền Role × API")
class RoleBasedAccessControlTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    @MockitoBean
    private IUserService userService;

    @MockitoBean
    private IPTService ptService;

    @MockitoBean
    private IAdminPTService adminPTService;

    private String studentToken;
    private String ptToken;
    private String adminToken;

    @BeforeEach
    void setUp() {
        studentToken = jwtUtil.generateToken("student.a@ptconnect.vn", "STUDENT");
        ptToken      = jwtUtil.generateToken("pt.hoangc@ptconnect.vn",  "PT");
        adminToken   = jwtUtil.generateToken("admin@ptconnect.vn",       "ADMIN");
    }

    // ══════════════════════════════════════════════════════════════════════════
    // ROW 1: Anonymous (không có token)
    // ══════════════════════════════════════════════════════════════════════════

    @Nested
    @DisplayName("Anonymous (không token)")
    class AnonymousTests {

        @Test
        @DisplayName("GET /api/public/health → 200 OK")
        void givenAnonymous_whenGetPublicHealth_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/public/health"))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/student/dashboard → 401 Unauthorized")
        void givenAnonymous_whenGetStudentDashboard_thenReturn401() throws Exception {
            mockMvc.perform(get("/api/student/dashboard"))
                    .andExpect(status().isUnauthorized());
        }

        @Test
        @DisplayName("GET /api/pt/courses → 401 Unauthorized")
        void givenAnonymous_whenGetPtCourses_thenReturn401() throws Exception {
            mockMvc.perform(get("/api/pt/courses"))
                    .andExpect(status().isUnauthorized());
        }

        @Test
        @DisplayName("GET /api/admin/users → 401 Unauthorized")
        void givenAnonymous_whenGetAdminUsers_thenReturn401() throws Exception {
            mockMvc.perform(get("/api/admin/users"))
                    .andExpect(status().isUnauthorized());
        }
    }

    // ══════════════════════════════════════════════════════════════════════════
    // ROW 2: STUDENT token
    // ══════════════════════════════════════════════════════════════════════════

    @Nested
    @DisplayName("STUDENT token")
    class StudentTokenTests {

        @Test
        @DisplayName("GET /api/public/health → 200 OK")
        void givenStudentToken_whenGetPublicHealth_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/public/health")
                            .header("Authorization", "Bearer " + studentToken))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/student/dashboard → 200 OK")
        void givenStudentToken_whenGetStudentDashboard_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/student/dashboard")
                            .header("Authorization", "Bearer " + studentToken))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/pt/courses → 403 Forbidden")
        void givenStudentToken_whenGetPtCourses_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/pt/courses")
                            .header("Authorization", "Bearer " + studentToken))
                    .andExpect(status().isForbidden());
        }

        @Test
        @DisplayName("GET /api/admin/users → 403 Forbidden")
        void givenStudentToken_whenGetAdminUsers_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/admin/users")
                            .header("Authorization", "Bearer " + studentToken))
                    .andExpect(status().isForbidden());
        }
    }

    // ══════════════════════════════════════════════════════════════════════════
    // ROW 3: PT token
    // ══════════════════════════════════════════════════════════════════════════

    @Nested
    @DisplayName("PT token")
    class PtTokenTests {

        @Test
        @DisplayName("GET /api/public/health → 200 OK")
        void givenPtToken_whenGetPublicHealth_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/public/health")
                            .header("Authorization", "Bearer " + ptToken))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/student/dashboard → 403 Forbidden")
        void givenPtToken_whenGetStudentDashboard_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/student/dashboard")
                            .header("Authorization", "Bearer " + ptToken))
                    .andExpect(status().isForbidden());
        }

        @Test
        @DisplayName("GET /api/pt/courses → 200 OK")
        void givenPtToken_whenGetPtCourses_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/pt/courses")
                            .header("Authorization", "Bearer " + ptToken))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/admin/users → 403 Forbidden")
        void givenPtToken_whenGetAdminUsers_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/admin/users")
                            .header("Authorization", "Bearer " + ptToken))
                    .andExpect(status().isForbidden());
        }
    }

    // ══════════════════════════════════════════════════════════════════════════
    // ROW 4: ADMIN token
    // ══════════════════════════════════════════════════════════════════════════

    @Nested
    @DisplayName("ADMIN token")
    class AdminTokenTests {

        @Test
        @DisplayName("GET /api/public/health → 200 OK")
        void givenAdminToken_whenGetPublicHealth_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/public/health")
                            .header("Authorization", "Bearer " + adminToken))
                    .andExpect(status().isOk());
        }

        @Test
        @DisplayName("GET /api/student/dashboard → 403 Forbidden")
        void givenAdminToken_whenGetStudentDashboard_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/student/dashboard")
                            .header("Authorization", "Bearer " + adminToken))
                    .andExpect(status().isForbidden());
        }

        @Test
        @DisplayName("GET /api/pt/courses → 403 Forbidden")
        void givenAdminToken_whenGetPtCourses_thenReturn403() throws Exception {
            mockMvc.perform(get("/api/pt/courses")
                            .header("Authorization", "Bearer " + adminToken))
                    .andExpect(status().isForbidden());
        }

        @Test
        @DisplayName("GET /api/admin/users → 200 OK")
        void givenAdminToken_whenGetAdminUsers_thenReturn200() throws Exception {
            mockMvc.perform(get("/api/admin/users")
                            .header("Authorization", "Bearer " + adminToken))
                    .andExpect(status().isOk());
        }
    }
}
