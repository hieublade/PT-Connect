package com.PTconnect.backend.config;

import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.Optional;

@Component
public class JwtFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(JwtFilter.class);

    private final JwtUtil jwtUtil;
    private final ObjectProvider<UserRepository> userRepositoryProvider;

    public JwtFilter(JwtUtil jwtUtil, ObjectProvider<UserRepository> userRepositoryProvider) {
        this.jwtUtil = jwtUtil;
        this.userRepositoryProvider = userRepositoryProvider;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        final String jwt = authHeader.substring(7);

        try {
            final String userEmail = jwtUtil.extractEmail(jwt);

            if (userEmail != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                if (!jwtUtil.isTokenExpired(jwt)) {
                    String roleName = jwtUtil.extractRole(jwt);
                    Object principal = userEmail;

                    UserRepository userRepository = userRepositoryProvider.getIfAvailable();
                    if (userRepository != null) {
                        Optional<User> userOptional = userRepository.findByEmail(userEmail);
                        if (userOptional.isPresent()) {
                            User user = userOptional.get();
                            principal = user;
                            if (user.getRole() != null) {
                                roleName = user.getRole().name();
                            }
                        }
                    }

                    if (roleName == null || roleName.isBlank()) {
                        roleName = "STUDENT";
                    }

                    SimpleGrantedAuthority authority = new SimpleGrantedAuthority("ROLE_" + roleName.toUpperCase());
                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                            principal,
                            null,
                            Collections.singletonList(authority)
                    );
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (Exception e) {
            log.warn("JWT validation failed: {}", e.getMessage());
        }

        filterChain.doFilter(request, response);
    }
}
