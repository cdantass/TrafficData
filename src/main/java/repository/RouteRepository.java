package repository;

import entity.Location;
import entity.Route;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RouteRepository extends JpaRepository<Route, Long> {
    boolean existsByOriginAndDestination(Location origin, Location destination);
}
