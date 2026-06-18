package com.trafficData.Aracaju.dto.traffic;

import jakarta.validation.constraints.NotNull;

public record RegisterRoute(@NotNull(message = "Origin ID is required") Long originId,
                            @NotNull(message = "Destination ID is required") Long destinationId) {
}
