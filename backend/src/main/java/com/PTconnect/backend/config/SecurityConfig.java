package com.PTconnect.backend.config;

import com.PTconnect.backend.security.JwtAuthFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import java.io.IOException;

/**
 * Cấu hình Spring Security cho PT-Connect backend.
 *
 * <p>Ma trận phân quyền URL:</p>
 * <pre>
 *   /api/public/**   → permitAll()
 *   /api/auth/**     → permitAll()
 *   /api/student/**  → ROLE_STUDENT only
 *   /api/pt/**       → ROLE_PT only
 *   /api/admin/**    → ROLE_ADMIN only
 *   (mọi request còn lại) → authenticated()
 * </pre>
 *
 * <p>CSRF tắt (stateless REST). Session policy = STATELESS.</p>
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private static final Logger log = LoggerFactory.getLogger(SecurityConfig.class);

    private final JwtAuthFilter jwtAuthFilter;

    public SecurityConfig(JwtAuthFilter jwtAuthFilter) {
        this.jwtAuthFilter = jwtAuthFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // 1. Tắt CSRF — API REST stateless không cần
            .csrf(AbstractHttpConfigurer::disable)

            // 2. Session stateless — không tạo HttpSession
            .sessionManagement(session ->
                    session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

            // 3. Phân quyền theo URL
            .authorizeHttpRequests(auth -> auth
                    .requestMatchers("/api/public/**").permitAll()
                    .requestMatchers("/api/auth/**").permitAll()
                    .requestMatchers("/api/student/**").hasRole("STUDENT")
                    .requestMatchers("/api/pt/**").hasRole("PT")
                    .requestMatchers("/api/admin/**").hasRole("ADMIN")
                    .anyRequest().authenticated()
            )

            // 4. Exception handling: 401 khi chưa xác thực (anonymous), 403 khi sai quyền (access denied)
            .exceptionHandling(ex -> ex
                    .authenticationEntryPoint((request, response, authException) ->
                            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized"))
                    .accessDeniedHandler(loggingAccessDeniedHandler())
            )

            // 5. Đặt JwtAuthFilter TRƯỚC UsernamePasswordAuthenticationFilter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    /**
     * AccessDeniedHandler tùy chỉnh: log chi tiết who/what/why rồi trả 403.
     * Log này là nguồn để SecurityDenialLogTest capture và assert.
     */
    @Bean
    public AccessDeniedHandler loggingAccessDeniedHandler() {
        return new LoggingAccessDeniedHandler();
    }

    /**
     * Handler nội bộ — viết thành static class để dễ test độc lập.
     */
    public static class LoggingAccessDeniedHandler implements AccessDeniedHandler {

        private static final Logger secLog =
                LoggerFactory.getLogger("com.PTconnect.security.denial");

        @Override
        public void handle(
                HttpServletRequest       request,
                HttpServletResponse      response,
                AccessDeniedException    accessDeniedException
        ) throws IOException {

            String principal = (request.getUserPrincipal() != null)
                    ? request.getUserPrincipal().getName()
                    : "anonymous";

            String uri = request.getRequestURI();

            secLog.warn(
                    "[ACCESS DENIED] user='{}' endpoint='{}' reason='{}' — 403 Forbidden",
                    principal, uri, accessDeniedException.getMessage()
            );

            response.sendError(HttpServletResponse.SC_FORBIDDEN, "Access Denied");
        }
    }
}
