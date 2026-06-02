package service;

import dto.location.LocationDetail;
import dto.location.LocationList;
import dto.location.LocationRegister;
import entity.Location;
import exception.NotFound;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import repository.LocationRepository;

@Service
public class LocationService {

    @Autowired
    private LocationRepository locationRepository;

    @Transactional
    public LocationDetail register(LocationRegister locationRegister){
        var location = locationRepository.save(new Location(locationRegister));
        return new LocationDetail(location);
    }

    public Page<LocationList> list(Pageable pageable){
        return locationRepository.findAll(pageable)
                .map(LocationList::new);
    }

    public LocationDetail detail(Long id){
        var location = locationRepository.findById(id)
                .orElseThrow(()-> new NotFound("Location not found"));
        return new LocationDetail(location);
    }

    @Transactional
    public void delete(Long id){
        var location = locationRepository.findById(id)
                .orElseThrow(()-> new NotFound("Location not found"));
        location.delete();
    }
}