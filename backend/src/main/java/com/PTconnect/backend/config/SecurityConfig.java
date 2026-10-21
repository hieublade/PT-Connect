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
        configuration.setAllowedOriginPatterns(List.of("*"));
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
                        // 1. Cac endpoint cong khai (Auth, Public Health, va User API Milestone 2)
                        .requestMatchers(
                                "/auth/register",
                                "/auth/login",
                                "/api/v1/auth/register",
                                "/api/v1/auth/login",
                                "/api/public/**",
                                "/api/v1/public/**",
                                "/api/v1/users/**",
                                "/error"
                        ).permitAll()

                        // 2. Endpoint thong tin ca nhan (can dang nhap bat ky role nao)
                        .requestMatchers("/auth/me", "/api/v1/auth/me").authenticated()

                        // 3. Phan quyen theo Role
                        .requestMatchers("/api/student/**", "/api/v1/student/**").hasRole("STUDENT")
                        .requestMatchers("/api/pt/**", "/api/v1/pt/**").hasRole("PT")
                        .requestMatchers("/api/admin/**", "/api/v1/admin/**").hasRole("ADMIN")

                        // Milestone 5: Chuc nang Student, Wallet va Enrollment
                        .requestMatchers("/api/v1/wallet/topup", "/api/wallet/topup").hasRole("STUDENT")
                        .requestMatchers(org.springframework.http.HttpMethod.POST, "/api/v1/enrollments", "/api/enrollments").hasRole("STUDENT")
                        .requestMatchers("/api/v1/enrollments/my", "/api/enrollments/my").hasRole("STUDENT")
                        .requestMatchers("/api/v1/wallet/**", "/api/wallet/**").authenticated()
                        .requestMatchers("/api/v1/enrollments/**", "/api/enrollments/**").authenticated()
                        .requestMatchers("/api/v1/pt-profiles/**", "/api/pt-profiles/**").authenticated()

                        // 4. Endpoint quan ly User danh rieng cho nguoi dung da xac thuc
                        .requestMatchers("/api/v1/users/**").authenticated()

                        // 5. Tat ca cac request con lai bat buoc phai dang nhap
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

            response.sendError(HttpServletResponse.SC_FORBIDDEN, "Access Denied");
        }
    }
}
