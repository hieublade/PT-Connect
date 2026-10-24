package com.PTconnect.backend.security;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import com.PTconnect.backend.config.JwtFilter;
import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.config.SecurityConfig;
import com.PTconnect.backend.controller.AdminController;
import com.PTconnect.backend.controller.PTController;
import com.PTconnect.backend.controller.PublicController;
import com.PTconnect.backend.controller.StudentController;
import com.PTconnect.backend.service.IAdminPTService;
import com.PTconnect.backend.service.IAdminStatisticsService;
import com.PTconnect.backend.service.IPTService;
import com.PTconnect.backend.service.IUserService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = {
        PublicController.class,
        StudentController.class,
        PTController.class,
        AdminController.class
})
@Import({SecurityConfig.class, JwtUtil.class, JwtFilter.class})
@ActiveProfiles("test")
@DisplayName("Chụp Security Denial Log")
class SecurityDenialLogTest {

    private static final String DENIAL_LOGGER_NAME = "com.PTconnect.security.denial";

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

    @MockitoBean
    private IAdminStatisticsService adminStatisticsService;

    private ListAppender<ILoggingEvent> listAppender;
    private Logger denialLogger;

    @BeforeEach
    void attachListAppender() {
        denialLogger = (Logger) LoggerFactory.getLogger(DENIAL_LOGGER_NAME);
        denialLogger.setLevel(Level.DEBUG);

        listAppender = new ListAppender<>();
        listAppender.start();
        denialLogger.addAppender(listAppender);
    }

    @AfterEach
    void detachListAppender() {
        if (denialLogger != null && listAppender != null) {
            denialLogger.detachAppender(listAppender);
            listAppender.stop();
        }
    }

    private List<String> capturedMessages() {
        return listAppender.list.stream()
                .map(ILoggingEvent::getFormattedMessage)
                .toList();
    }

    @Test
    @DisplayName("Student gọi /api/admin/users → log chứa email + endpoint + ACCESS DENIED")
    void givenStudentToken_whenCallAdminApi_thenLogContainsUserAndEndpointAndDenial()
            throws Exception {

        String studentEmail = "student.a@ptconnect.vn";
        String token = jwtUtil.generateToken(studentEmail, "STUDENT");

        mockMvc.perform(get("/api/admin/users")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        List<String> logs = capturedMessages();

        assertThat(logs)
                .as("Phải có ít nhất 1 dòng log denial")
                .isNotEmpty();

        String denialLog = logs.get(0);

        assertThat(denialLog)
                .as("Log phải chứa email của student bị từ chối")
                .contains(studentEmail);

        assertThat(denialLog)
                .as("Log phải chứa endpoint bị chặn")
                .contains("/api/admin/users");

        assertThat(denialLog)
                .as("Log phải chứa từ khóa ACCESS DENIED")
                .containsIgnoringCase("ACCESS DENIED");
    }

    @Test
    @DisplayName("Student gọi /api/pt/courses → log chứa email student + endpoint PT")
    void givenStudentToken_whenCallPtApi_thenLogContainsStudentEmailAndPtEndpoint()
            throws Exception {

        String studentEmail = "student.b@ptconnect.vn";
        String token = jwtUtil.generateToken(studentEmail, "STUDENT");

        mockMvc.perform(get("/api/pt/courses")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        List<String> logs = capturedMessages();

        assertThat(logs).isNotEmpty();

        String denialLog = logs.get(0);
        assertThat(denialLog).contains(studentEmail);
        assertThat(denialLog).contains("/api/pt/courses");
    }

    @Test
    @DisplayName("PT gọi /api/admin/users → log chứa email PT + endpoint admin")
    void givenPtToken_whenCallAdminApi_thenLogContainsPtEmailAndAdminEndpoint()
            throws Exception {

        String ptEmail = "pt.hoangc@ptconnect.vn";
        String token = jwtUtil.generateToken(ptEmail, "PT");

        mockMvc.perform(get("/api/admin/users")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        List<String> logs = capturedMessages();

        assertThat(logs).isNotEmpty();

        String denialLog = logs.get(0);
        assertThat(denialLog).contains(ptEmail);
        assertThat(denialLog).contains("/api/admin/users");
    }

    @Test
    @DisplayName("Admin gọi /api/student/dashboard → log chứa email admin + endpoint student")
    void givenAdminToken_whenCallStudentApi_thenLogContainsAdminEmailAndStudentEndpoint()
            throws Exception {

        String adminEmail = "admin@ptconnect.vn";
        String token = jwtUtil.generateToken(adminEmail, "ADMIN");

        mockMvc.perform(get("/api/student/dashboard")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        List<String> logs = capturedMessages();

        assertThat(logs).isNotEmpty();

        String denialLog = logs.get(0);
        assertThat(denialLog).contains(adminEmail);
        assertThat(denialLog).contains("/api/student/dashboard");
    }

    @Test
    @DisplayName("Anonymous gọi /api/public/health → KHÔNG có log denial")
    void givenAnonymous_whenCallPublicApi_thenNoDenialLog() throws Exception {

        mockMvc.perform(get("/api/public/health"))
                .andExpect(status().isOk());

        List<String> logs = capturedMessages();

        assertThat(logs)
                .as("Public endpoint không nên tạo ra log denial")
                .isEmpty();
    }
}
