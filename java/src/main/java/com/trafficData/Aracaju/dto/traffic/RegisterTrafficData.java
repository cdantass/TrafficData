package com.trafficData.Aracaju.dto.traffic;

public record RegisterTrafficData(
        Long routeId,
        Double duration,
        Double durationInTraffic,
        Double averageSpeed
) {
}
