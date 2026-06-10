package dto.traffic;

import entity.TrafficData;
import entity.TrafficLevel;

import java.time.LocalDateTime;

public record ListTrafficData(
        Long id,
        Long routeId,
        LocalDateTime timestamp,
        Double duration,
        Double durationInTraffic,
        Double averageSpeed,
        TrafficLevel trafficLevel
) {

    public ListTrafficData(TrafficData trafficData) {
        this(
                trafficData.getId(),
                trafficData.getRoute().getId(),
                trafficData.getTimestamp(),
                trafficData.getDuration(),
                trafficData.getDurationInTraffic(),
                trafficData.getAverageSpeed(),
                trafficData.getTrafficLevel()
        );
    }
}