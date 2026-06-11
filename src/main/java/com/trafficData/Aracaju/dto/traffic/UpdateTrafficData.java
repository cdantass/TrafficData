package com.trafficData.Aracaju.dto.traffic;

import jakarta.validation.constraints.NotNull;

public record UpdateTrafficData(@NotNull Long routeId) {
}
