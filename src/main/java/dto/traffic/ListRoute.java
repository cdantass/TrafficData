package dto.traffic;

import entity.Location;
import entity.Route;

public record ListRoute(Long id, Long originId, Long destinationId, String name) {
    public ListRoute(Route route){
        this(route.getId(), route.getOrigin().getId(), route.getDestination().getId(), route.getName());
    }
}
