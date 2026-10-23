package com.PTconnect.backend.policy;

import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Factory điều phối các hiện thực CancellationPolicy theo Role (Milestone 7).
 * Minh chứng mẫu thiết kế Strategy và Nguyên tắc Open-Closed (SOLID).
 */
@Component
public class CancellationPolicyFactory {

    private final Map<String, CancellationPolicy> policyMap;

    public CancellationPolicyFactory(List<CancellationPolicy> policies) {
        this.policyMap = policies.stream()
                .collect(Collectors.toMap(
                        policy -> policy.getSupportedRole().toUpperCase(),
                        Function.identity()
                ));
    }

    public CancellationPolicy getPolicy(String role) {
        if (role == null) {
            throw new IllegalArgumentException("Role không được để trống khi chọn chính sách hủy");
        }
        return Optional.ofNullable(policyMap.get(role.toUpperCase()))
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy chính sách hủy phù hợp cho role: " + role));
    }
}
