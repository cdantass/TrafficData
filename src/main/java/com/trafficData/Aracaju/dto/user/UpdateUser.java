package com.trafficData.Aracaju.dto.user;

import com.trafficData.Aracaju.entity.UserRole;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record UpdateUser(@NotNull Long id,
                         @NotBlank String name,
                         @NotBlank String email,
                         String password,
                         UserRole role) {
}
