package service;

import dto.traffic.*;
import entity.TrafficData;
import entity.TrafficLevel;
import exception.NotFound;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import repository.RouteRepository;
import repository.TrafficDataRepository;

import java.time.LocalDateTime;

@Service
public class TrafficDataService {

    private TrafficDataRepository trafficDataRepository;
    private RouteRepository routeRepository;

    @Transactional
    public DetailTrafficData register(RegisterTrafficData registerTrafficData){
        var route = routeRepository.findById(registerTrafficData.routeId())
                .orElseThrow(()-> new NotFound("Traffic not found"));

        var trafficData = new TrafficData();

        trafficData.setRoute(route);
        trafficData.setTimestamp(LocalDateTime.now());
        trafficData.setDuration(registerTrafficData.duration());
        trafficData.setDurationInTraffic(registerTrafficData.durationInTraffic());
        trafficData.setAverageSpeed(registerTrafficData.averageSpeed());

        trafficData.setTrafficLevel(calculateTrafficLevel(registerTrafficData.duration(),
                registerTrafficData.durationInTraffic()));
        trafficDataRepository.save(trafficData);

        return new DetailTrafficData(trafficData);
    }

    public TrafficLevel calculateTrafficLevel(Double duration, Double durationInTraffic) {
        double ratio = durationInTraffic / duration;

        if (ratio < 1.2){
            return TrafficLevel.LOW;
        }

        if (ratio < 1.5){
            return TrafficLevel.MEDIUM;
        }

        return TrafficLevel.HIGH;
    }

    public Page<ListTrafficData> list(Pageable pageable){
        return trafficDataRepository.findAll(pageable)
                .map(ListTrafficData::new);
    }

    public DetailTrafficData detail(Long id){
        var traffic = trafficDataRepository.findById(id)
                .orElseThrow(()-> new NotFound("Route not found"));
        return new DetailTrafficData(traffic);
    }
    @Transactional
    public void delete(Long id){
        if (!trafficDataRepository.existsById(id)){
            throw new NotFound("Traffic not found");
        }
        trafficDataRepository.deleteById(id);
    }
}