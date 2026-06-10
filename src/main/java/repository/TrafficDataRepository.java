package repository;

import entity.TrafficData;
import org.springframework.data.domain.Page;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TrafficDataRepository extends JpaRepository<TrafficData, Long> {
    Page<TrafficData> findByRouteId(Long routeId);
}
