package com.trafficData.Aracaju.dto.location;

import com.trafficData.Aracaju.entity.Location;

public record LocationDetail(Long id, String name, Double latitude, Double longitude) {
    public LocationDetail(Location location){
        this(location.getId(), location.getName(), location.getLatitude(), location.getLongitude());
    }
}
