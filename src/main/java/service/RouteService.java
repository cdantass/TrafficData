package service;

import dto.RegisterRoute;
import dto.traffic.DetailRoute;
import dto.traffic.ListRoute;
import entity.Route;
import exception.NotFound;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import repository.LocationRepository;
import repository.RouteRepository;

@Service
public class RouteService {

    private final RouteRepository repository;
    private final LocationRepository locationRepository;

    public RouteService(RouteRepository repository, LocationRepository locationRepository) {
        this.repository = repository;
        this.locationRepository = locationRepository;
    }

    @Transactional
    public DetailRoute register(RegisterRoute dto){

        var origin = locationRepository.findById(dto.originId())
                .orElseThrow(() -> new NotFound("Origin not found"));

        var destination = locationRepository.findById(dto.destinationId())
                .orElseThrow(() -> new NotFound("Destination not found"));

        if(repository.existsByOriginAndDestination(origin, destination)){
            throw new RuntimeException("Route already exists");
        }

        var route = new Route();
        route.setOrigin(origin);
        route.setDestination(destination);
        route.setName(origin.getName() + " -> " + destination.getName());

        repository.save(route);

        return new DetailRoute(route);
    }

    public Page<ListRoute> list(Pageable pageable){
        return repository.findAll(pageable)
                .map(ListRoute::new);
    }

    public DetailRoute detail(Long id){
        var route = repository.findById(id)
                .orElseThrow(() -> new NotFound("Route not found"));
        return new DetailRoute(route);
    }

    @Transactional
    public void delete(Long id){
        if(!repository.existsById(id)){
            throw new NotFound("Route not found");
        }
        repository.deleteById(id);
    }
}