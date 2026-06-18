package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.traffic.DetailRoute;
import com.trafficData.Aracaju.dto.traffic.ListRoute;
import com.trafficData.Aracaju.dto.traffic.RegisterRoute;
import com.trafficData.Aracaju.dto.traffic.UpdateRoute;
import com.trafficData.Aracaju.entity.Route;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.LocationRepository;
import com.trafficData.Aracaju.repository.RouteRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
        validateIds(dto.originId(), dto.destinationId());

        var origin = locationRepository.findById(dto.originId())
                .orElseThrow(() -> new NotFound("Origin not found"));

        var destination = locationRepository.findById(dto.destinationId())
                .orElseThrow(() -> new NotFound("Destination not found"));

        validateDifferentLocations(origin.getId(), destination.getId());

        if (repository.existsByOriginAndDestination(origin, destination)) {
            throw new IllegalArgumentException("Route already exists");
        }

        var route = new Route();
        route.setOrigin(origin);
        route.setDestination(destination);
        route.setName(buildRouteName(origin.getName(), destination.getName()));
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
        validateIds(dto.originId(), dto.destinationId());

        var route = repository.findById(id)
                .orElseThrow(() -> new NotFound("Route not found"));

        var origin = locationRepository.findById(dto.originId())
                .orElseThrow(() -> new NotFound("Origin not found"));

        var destination = locationRepository.findById(dto.destinationId())
                .orElseThrow(() -> new NotFound("Destination not found"));

        validateDifferentLocations(origin.getId(), destination.getId());

        boolean routeChanged =
                !route.getOrigin().getId().equals(origin.getId()) ||
                        !route.getDestination().getId().equals(destination.getId());

        if (routeChanged && repository.existsByOriginAndDestination(origin, destination)) {
            throw new IllegalArgumentException("Route already exists");
        }

        route.updateRoute(
                origin,
                destination,
                buildRouteName(origin.getName(), destination.getName())
        );

        return new DetailRoute(route);
    }

    @Transactional
    public void delete(Long id) {
        var route = repository.findById(id)
                .orElseThrow(() -> new NotFound("Route not found"));

        repository.delete(route);
    }

    private void validateIds(Long originId, Long destinationId) {
        if (originId == null) {
            throw new IllegalArgumentException("Origin ID is required");
        }

        if (destinationId == null) {
            throw new IllegalArgumentException("Destination ID is required");
        }
    }

    private void validateDifferentLocations(Long originId, Long destinationId) {
        if (originId.equals(destinationId)) {
            throw new IllegalArgumentException("Origin and destination cannot be the same");
        }
    }

    private String buildRouteName(String originName, String destinationName) {
        return originName + " -> " + destinationName;
    }
}