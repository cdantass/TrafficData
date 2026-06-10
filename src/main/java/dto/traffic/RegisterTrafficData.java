package dto.traffic;

import entity.Route;
import entity.TrafficLevel;

import java.time.LocalDateTime;

public record RegisterTrafficData(
        Long routeId,
        Double duration,
        Double durationInTraffic,
        Double averageSpeed
) {
}
