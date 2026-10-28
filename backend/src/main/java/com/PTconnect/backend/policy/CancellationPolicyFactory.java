package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.enums.Role;
import org.springframework.stereotype.Component;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Factory điều phối các hiện thực CancellationPolicy theo Role (Milestone 7).
 * Minh chứng mẫu thiết kế Strategy và Nguyên tắc Open-Closed (SOLID).
 */
@Component
public class CancellationPolicyFactory {

    private final Map<Role, CancellationPolicy> policyMap;

    public CancellationPolicyFactory(List<CancellationPolicy> policies) {
        this.policyMap = new EnumMap<>(Role.class);
        for (CancellationPolicy policy : policies) {
            this.policyMap.put(policy.getSupportedRole(), policy);
        }
    }

    public CancellationPolicy getPolicy(Role role) {
        if (role == null) {
            throw new IllegalArgumentException("Role không được để trống khi chọn chính sách hủy");
        }
        return Optional.ofNullable(policyMap.get(role))
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy chính sách hủy phù hợp cho role: " + role));
    }

    public CancellationPolicy getPolicy(String roleStr) {
        if (roleStr == null) {
            throw new IllegalArgumentException("Role không được để trống khi chọn chính sách hủy");
        }
        try {
            Role role = Role.valueOf(roleStr.trim().toUpperCase());
            return getPolicy(role);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Không tìm thấy chính sách hủy phù hợp cho role: " + roleStr);
        }
    }
}
