package controller;

import dto.location.LocationDetail;
import dto.location.LocationList;
import dto.location.LocationRegister;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;
import service.LocationService;

@RestController
@RequestMapping("/locations")
public class LocationController {

    @Autowired
    private LocationService locationService;

    @PostMapping
    public ResponseEntity<LocationDetail> register(@RequestBody @Valid LocationRegister locationRegister, UriComponentsBuilder uriComponentsBuilder){
        var detailLoc = locationService.register(locationRegister);

        var uri = uriComponentsBuilder
                .path("/locations/{id}")
                .buildAndExpand(detailLoc.id())
                .toUri();
        return ResponseEntity.created(uri).body(detailLoc);
    }

    @GetMapping
    public ResponseEntity<Page<LocationList>> list(Pageable pageable){
        return ResponseEntity.ok(locationService.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<LocationDetail> detail(@PathVariable Long id){
        return ResponseEntity.ok(locationService.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id){
        locationService.delete(id);
        return ResponseEntity.noContent().build();
    }
}