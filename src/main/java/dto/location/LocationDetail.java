package dto.location;

import entity.Location;

public record LocationDetail(Long id, String name, Double latitude, Double longetude) {
    public LocationDetail(Location location){
        this(location.getId(), location.getName(), location.getLatitude(), location.getLongitude());
    }
}
