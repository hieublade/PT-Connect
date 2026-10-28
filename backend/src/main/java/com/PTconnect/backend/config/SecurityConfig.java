package com.PTconnect.backend.config;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.io.IOException;
import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtFilter jwtFilter;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of(
                "http://localhost:8501",
                "http://127.0.0.1:8501",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080"
        ));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        // 1. Endpoint cap nhat avatar va thong tin me bat buoc phai dang nhap (first-match)
                        .requestMatchers("/api/v1/users/avatar", "/api/v1/auth/me").authenticated()

                        // 2. Cac endpoint cong khai (Auth, Public Health)
                        .requestMatchers(
                                "/api/v1/auth/register",
                                "/api/v1/auth/login",
                                "/api/v1/public/**",
                                "/error"
                        ).permitAll()

                        // 3. Ho so HLV va danh sach khoa hoc cong khai cho khach vang lai xem
                        .requestMatchers(org.springframework.http.HttpMethod.GET, "/api/v1/pt-profiles/**").permitAll()

                        // 4. Milestone 6: Booking endpoints
                        .requestMatchers(org.springframework.http.HttpMethod.POST, "/api/v1/bookings").hasRole("STUDENT")
                        .requestMatchers("/api/v1/bookings/my").hasRole("STUDENT")
                        .requestMatchers("/api/v1/pt/bookings/**").hasRole("PT")
                        .requestMatchers("/api/v1/bookings/**").authenticated()

                        // 5. Phan quyen theo Role co san
                        .requestMatchers("/api/v1/student/**").hasRole("STUDENT")
                        .requestMatchers("/api/v1/pt/**").hasRole("PT")
                        .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")

                        // 6. Milestone 5: Chuc nang Student, Wallet va Enrollment
                        .requestMatchers("/api/v1/wallet/topup").hasRole("STUDENT")
                        .requestMatchers(org.springframework.http.HttpMethod.POST, "/api/v1/enrollments").hasRole("STUDENT")
                        .requestMatchers("/api/v1/enrollments/my").hasRole("STUDENT")
                        .requestMatchers("/api/v1/wallet/**").authenticated()
                        .requestMatchers("/api/v1/enrollments/**").authenticated()
                        .requestMatchers("/api/v1/users/**").authenticated()

                        // 7. Milestone 7: Chuc nang Diem danh, Huy lich va Danh gia (Review)
                        .requestMatchers(org.springframework.http.HttpMethod.POST, "/api/v1/reviews").hasRole("STUDENT")
                        .requestMatchers("/api/v1/reviews/**").permitAll()
                        .requestMatchers("/api/v1/attendance/**").authenticated()

                        // 8. Tat ca cac request con lai bat buoc phai dang nhap
                        .anyRequest().authenticated()
                )
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint((request, response, authException) ->
                                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized"))
                        .accessDeniedHandler(loggingAccessDeniedHandler())
                )
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public AccessDeniedHandler loggingAccessDeniedHandler() {
        return new LoggingAccessDeniedHandler();
    }

    public static class LoggingAccessDeniedHandler implements AccessDeniedHandler {

        private static final Logger secLog = LoggerFactory.getLogger("com.PTconnect.security.denial");

        @Override
        public void handle(
                HttpServletRequest request,
                HttpServletResponse response,
                AccessDeniedException accessDeniedException
        ) throws IOException {

            String principal = (request.getUserPrincipal() != null)
                    ? request.getUserPrincipal().getName()
                    : "anonymous";

            String uri = request.getRequestURI();

            secLog.warn(
                    "[ACCESS DENIED] user='{}' endpoint='{}' reason='{}' — 403 Forbidden",
                    principal, uri, accessDeniedException.getMessage()
            );

            response.setContentType("application/json;charset=UTF-8");
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            response.getWriter().write("""
                    {
                        "status": 403,
                        "message": "Bạn không có quyền truy cập tài nguyên này",
                        "data": null
                    }
                    """);
        }
    }
}
