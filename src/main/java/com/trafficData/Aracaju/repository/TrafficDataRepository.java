package com.trafficData.Aracaju.repository;

import com.trafficData.Aracaju.entity.TrafficData;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.time.LocalDateTime;
import java.util.List;

public interface TrafficDataRepository extends JpaRepository<TrafficData, Long> {
    Page<TrafficData> findByRouteId(Long routeId, Pageable pageable);

    @Query("""
    SELECT t FROM TrafficData t
    WHERE t.route.id = :routeId
    AND t.timestamp >= :from
    ORDER BY t.timestamp DESC
""")
    List<TrafficData> findHistoryByRoute(Long routeId, LocalDateTime from);
}
