package com.trafficData.Aracaju.repository;

import com.trafficData.Aracaju.entity.Location;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LocationRepository extends JpaRepository<Location, Long> {
}
