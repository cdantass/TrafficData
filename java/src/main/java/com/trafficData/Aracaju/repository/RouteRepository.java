package com.trafficData.Aracaju.repository;

import com.trafficData.Aracaju.entity.Location;
import com.trafficData.Aracaju.entity.Route;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RouteRepository extends JpaRepository<Route, Long> {
    boolean existsByOriginAndDestination(Location origin, Location destination);
}
