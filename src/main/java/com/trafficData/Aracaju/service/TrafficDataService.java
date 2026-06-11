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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class TrafficDataService {

    @Autowired
    private TrafficDataRepository trafficDataRepository;

    @Autowired
    private RouteRepository routeRepository;

    @Transactional
    public DetailTrafficData register(RegisterTrafficData registerTrafficData) {
        var route = routeRepository.findById(registerTrafficData.routeId())
                .orElseThrow(() -> new NotFound("Route not found"));

        var trafficData = new TrafficData();
        trafficData.setRoute(route);
        trafficData.setTimestamp(LocalDateTime.now());
        trafficData.setDuration(registerTrafficData.duration());
        trafficData.setDurationInTraffic(registerTrafficData.durationInTraffic());
        trafficData.setAverageSpeed(registerTrafficData.averageSpeed());
        trafficData.setTrafficLevel(
                calculateTrafficLevel(
                        registerTrafficData.duration(),
                        registerTrafficData.durationInTraffic()
                )
        );

        trafficDataRepository.save(trafficData);
        return new DetailTrafficData(trafficData);
    }

    @Transactional
    public DetailTrafficData update(Long id, UpdateTrafficData updateTrafficData) {
        var trafficData = trafficDataRepository.findById(id)
                .orElseThrow(() -> new NotFound("Traffic not found"));

        var route = routeRepository.findById(updateTrafficData.routeId())
                .orElseThrow(() -> new NotFound("Route not found"));

        trafficData.setRoute(route);
        trafficData.setTimestamp(LocalDateTime.now());

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
        if (!trafficDataRepository.existsById(id)) {
            throw new NotFound("Traffic not found");
        }

        trafficDataRepository.deleteById(id);
    }
}