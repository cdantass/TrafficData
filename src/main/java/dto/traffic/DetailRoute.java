package dto.traffic;

import entity.Location;
import entity.Route;

public record DetailRoute(Long id, Long originId, Long destinationId, String name) {
    public DetailRoute(Route route){
        this(route.getId(), route.getOrigin().getId(), route.getDestination().getId(), route.getName());
    }
}