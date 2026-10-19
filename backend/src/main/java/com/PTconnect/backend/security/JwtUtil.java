package com.PTconnect.backend.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * Utility tạo và xác thực JWT token.
 * Secret key cứng — chỉ dùng cho dev/test, KHÔNG dùng cho production.
 */
@Component
public class JwtUtil {

    // Minimum 256-bit secret cho HMAC-SHA256
    private static final String SECRET =
            "test-secret-key-for-unit-tests-only-min-256-bits-xxxx";

    // Token hết hạn sau 1 giờ (milliseconds)
    private static final long EXPIRATION_MS = 3_600_000L;

    private static final String CLAIM_ROLE = "role";

    private SecretKey signingKey() {
        byte[] keyBytes = SECRET.getBytes(StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    /**
     * Tạo JWT token chứa email (subject) và role (claim).
     *
     * @param email email người dùng — dùng làm subject
     * @param role  giá trị role thuần: "STUDENT", "PT", hoặc "ADMIN"
     * @return chuỗi JWT compact
     */
    public String generateToken(String email, String role) {
        Date now    = new Date();
        Date expiry = new Date(now.getTime() + EXPIRATION_MS);

        return Jwts.builder()
                .subject(email)
                .claim(CLAIM_ROLE, role)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(signingKey())
                .compact();
    }

    /**
     * Trích xuất email (subject) từ token.
     *
     * @param token JWT compact string
     * @return email, hoặc ném JwtException nếu token không hợp lệ
     */
    public String extractEmail(String token) {
        return parseClaims(token).getSubject();
    }

    /**
     * Trích xuất role claim từ token.
     *
     * @param token JWT compact string
     * @return giá trị role: "STUDENT", "PT", hoặc "ADMIN"
     */
    public String extractRole(String token) {
        return parseClaims(token).get(CLAIM_ROLE, String.class);
    }

    /**
     * Kiểm tra token còn hiệu lực (chữ ký hợp lệ và chưa hết hạn).
     *
     * @param token JWT compact string
     * @return true nếu hợp lệ; false nếu hết hạn hoặc chữ ký sai
     */
    public boolean isTokenValid(String token) {
        try {
            Claims claims = parseClaims(token);
            return !claims.getExpiration().before(new Date());
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    // ── Private helper ────────────────────────────────────────────────────────

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(signingKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
