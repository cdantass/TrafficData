package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.traffic.DetailTrafficData;
import com.trafficData.Aracaju.dto.traffic.ListTrafficData;
import com.trafficData.Aracaju.dto.traffic.RegisterTrafficData;
import com.trafficData.Aracaju.dto.traffic.UpdateTrafficData;
import com.trafficData.Aracaju.entity.TrafficData;
import com.trafficData.Aracaju.entity.TrafficLevel;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.RouteRepository;
import com.trafficData.Aracaju.repository.TrafficDataRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class TrafficDataService {

    private final TrafficDataRepository trafficDataRepository;
    private final RouteRepository routeRepository;

    public TrafficDataService(TrafficDataRepository trafficDataRepository,
                              RouteRepository routeRepository) {
        this.trafficDataRepository = trafficDataRepository;
        this.routeRepository = routeRepository;
    }

    @Transactional
    public DetailTrafficData register(RegisterTrafficData dto) {
        validateTrafficData(dto.routeId(), dto.duration(), dto.durationInTraffic(), dto.averageSpeed());

        var route = routeRepository.findById(dto.routeId())
                .orElseThrow(() -> new NotFound("Route not found"));

        if (Boolean.FALSE.equals(route.getActive())) {
            throw new IllegalArgumentException("Cannot register traffic data for an inactive route");
        }

        var trafficData = new TrafficData();
        trafficData.setRoute(route);
        trafficData.setTimestamp(LocalDateTime.now());
        trafficData.setDuration(dto.duration());
        trafficData.setDurationInTraffic(dto.durationInTraffic());
        trafficData.setAverageSpeed(dto.averageSpeed());
        trafficData.setTrafficLevel(
                calculateTrafficLevel(dto.duration(), dto.durationInTraffic())
        );

        trafficDataRepository.save(trafficData);

        return new DetailTrafficData(trafficData);
    }

    @Transactional
    public DetailTrafficData update(Long id, UpdateTrafficData dto) {
        validateTrafficData(dto.routeId(), dto.duration(), dto.durationInTraffic(), dto.averageSpeed());

        var trafficData = trafficDataRepository.findById(id)
                .orElseThrow(() -> new NotFound("Traffic not found"));

        var route = routeRepository.findById(dto.routeId())
                .orElseThrow(() -> new NotFound("Route not found"));

        if (Boolean.FALSE.equals(route.getActive())) {
            throw new IllegalArgumentException("Cannot update traffic data with an inactive route");
        }

        trafficData.setRoute(route);
        trafficData.setTimestamp(LocalDateTime.now());
        trafficData.setDuration(dto.duration());
        trafficData.setDurationInTraffic(dto.durationInTraffic());
        trafficData.setAverageSpeed(dto.averageSpeed());
        trafficData.setTrafficLevel(
                calculateTrafficLevel(dto.duration(), dto.durationInTraffic())
        );

        return new DetailTrafficData(trafficData);
    }

    public TrafficLevel calculateTrafficLevel(Double duration, Double durationInTraffic) {
        double ratio = durationInTraffic / duration;

        if (ratio < 1.2) {
            return TrafficLevel.LOW;
        }

        if (ratio < 1.5) {
            return TrafficLevel.MEDIUM;
        }

        return TrafficLevel.HIGH;
    }

    public Page<ListTrafficData> list(Pageable pageable) {
        return trafficDataRepository.findAll(pageable)
                .map(ListTrafficData::new);
    }

    public DetailTrafficData detail(Long id) {
        var traffic = trafficDataRepository.findById(id)
                .orElseThrow(() -> new NotFound("Traffic not found"));

        return new DetailTrafficData(traffic);
    }

    @Transactional
    public void delete(Long id) {
        var traffic = trafficDataRepository.findById(id)
                .orElseThrow(() -> new NotFound("Traffic not found"));

        trafficDataRepository.delete(traffic);
    }

    private void validateTrafficData(Long routeId,
                                     Double duration,
                                     Double durationInTraffic,
                                     Double averageSpeed) {

        if (routeId == null) {
            throw new IllegalArgumentException("Route ID is required");
        }

        if (duration == null || duration <= 0) {
            throw new IllegalArgumentException("Duration must be greater than zero");
        }

        if (durationInTraffic == null || durationInTraffic <= 0) {
            throw new IllegalArgumentException("Duration in traffic must be greater than zero");
        }

        if (durationInTraffic < duration) {
            throw new IllegalArgumentException("Duration in traffic cannot be less than duration");
        }

        if (averageSpeed == null || averageSpeed <= 0) {
            throw new IllegalArgumentException("Average speed must be greater than zero");
        }
    }
}