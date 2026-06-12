package com.trafficData.Aracaju.dto.traffic;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record UpdateTrafficData(
        @NotNull(message = "Route ID is required")
        Long routeId,

        @NotNull(message = "Duration is required")
        @Positive(message = "Duration must be greater than zero")
        Double duration,

        @NotNull(message = "Duration in traffic is required")
        @Positive(message = "Duration in traffic must be greater than zero")
        Double durationInTraffic,

        @NotNull(message = "Average speed is required")
        @Positive(message = "Average speed must be greater than zero")
        Double averageSpeed
) {
}