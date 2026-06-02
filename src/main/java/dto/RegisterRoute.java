package dto;

import entity.Location;

public record RegisterRoute(Long originId, Long destinationId, String name) {
}
