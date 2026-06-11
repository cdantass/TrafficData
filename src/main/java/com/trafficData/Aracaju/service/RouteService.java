package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.traffic.DetailRoute;
import com.trafficData.Aracaju.dto.traffic.ListRoute;
import com.trafficData.Aracaju.dto.traffic.RegisterRoute;
import com.trafficData.Aracaju.dto.traffic.UpdateRoute;
import com.trafficData.Aracaju.entity.Route;
import com.trafficData.Aracaju.infra.exception.NotFound;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.trafficData.Aracaju.repository.LocationRepository;
import com.trafficData.Aracaju.repository.RouteRepository;

@Service
public class RouteService {

    private final RouteRepository repository;
    private final LocationRepository locationRepository;

    public RouteService(RouteRepository repository,
                        LocationRepository locationRepository) {
        this.repository = repository;
        this.locationRepository = locationRepository;
    }

    @Transactional
    public DetailRoute register(RegisterRoute dto) {

        var origin = locationRepository.findById(dto.originId())
                .orElseThrow(() -> new NotFound("Origin not found"));

        var destination = locationRepository.findById(dto.destinationId())
                .orElseThrow(() -> new NotFound("Destination not found"));

        if (origin.getId().equals(destination.getId())) {
            throw new IllegalArgumentException(
                    "Origin and destination cannot be the same"
            );
        }

        if (repository.existsByOriginAndDestination(origin, destination)) {
            throw new RuntimeException("Route already exists");
        }

        var route = new Route();

        route.setOrigin(origin);
        route.setDestination(destination);
        route.setName(origin.getName() + " -> " + destination.getName());
        route.setActive(true);

        repository.save(route);

        return new DetailRoute(route);
    }

    public Page<ListRoute> list(Pageable pageable) {
        return repository.findAll(pageable)
                .map(ListRoute::new);
    }

    public DetailRoute detail(Long id) {
        var route = repository.findById(id)
                .orElseThrow(() -> new NotFound("Route not found"));

        return new DetailRoute(route);
    }

    @Transactional
    public DetailRoute update(Long id, UpdateRoute dto) {

        var route = repository.findById(dto.id())
                .orElseThrow(() -> new NotFound("Route not found"));

        var origin = locationRepository.findById(dto.originId())
                .orElseThrow(() -> new NotFound("Origin not found"));

        var destination = locationRepository.findById(dto.destinationId())
                .orElseThrow(() -> new NotFound("Destination not found"));

        if (origin.getId().equals(destination.getId())) {
            throw new IllegalArgumentException(
                    "Origin and destination cannot be the same"
            );
        }

        route.updateRoute(
                origin,
                destination,
                origin.getName() + " -> " + destination.getName()
        );

        return new DetailRoute(route);
    }

    @Transactional
    public void delete(Long id) {

        var route = repository.findById(id)
                .orElseThrow(() -> new NotFound("Route not found"));

        repository.delete(route);
    }
}