package com.PTconnect.backend.security;

import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

/**
 * Filter đọc JWT từ header "Authorization: Bearer <token>",
 * xác thực chữ ký, rồi set SecurityContext với role tương ứng.
 *
 * <p>Nếu header vắng mặt hoặc token không hợp lệ → filter chain tiếp tục
 * mà không set context, để Spring Security tự trả 401/403.</p>
 */
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(JwtAuthFilter.class);
    private static final String BEARER_PREFIX = "Bearer ";

    private final JwtUtil jwtUtil;

    public JwtAuthFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest  request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain         filterChain
    ) throws ServletException, IOException {

        String token = extractToken(request);

        if (token != null) {
            try {
                if (jwtUtil.isTokenValid(token)) {
                    String email = jwtUtil.extractEmail(token);
                    String role  = jwtUtil.extractRole(token);   // "STUDENT" | "PT" | "ADMIN"

                    // Spring Security convention: authority phải có tiền tố "ROLE_"
                    String authority = "ROLE_" + role;
                    List<SimpleGrantedAuthority> authorities =
                            List.of(new SimpleGrantedAuthority(authority));

                    UsernamePasswordAuthenticationToken authToken =
                            new UsernamePasswordAuthenticationToken(email, null, authorities);

                    SecurityContextHolder.getContext().setAuthentication(authToken);

                    log.debug("[JWT] Authenticated user='{}' role='{}' uri='{}'",
                            email, role, request.getRequestURI());
                } else {
                    log.warn("[JWT] Token không hợp lệ hoặc đã hết hạn — uri='{}'",
                            request.getRequestURI());
                }
            } catch (JwtException ex) {
                log.warn("[JWT] Parse token thất bại: {} — uri='{}'",
                        ex.getMessage(), request.getRequestURI());
                // Không set context → Spring Security sẽ trả 401
            }
        }

        filterChain.doFilter(request, response);
    }

    /**
     * Trích token thuần từ header "Authorization: Bearer <token>".
     *
     * @return token string, hoặc null nếu header vắng mặt / sai format
     */
    private String extractToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (StringUtils.hasText(header) && header.startsWith(BEARER_PREFIX)) {
            return header.substring(BEARER_PREFIX.length());
        }
        return null;
    }
}
