package controller;

import dto.traffic.DetailTrafficData;
import dto.traffic.ListTrafficData;
import dto.traffic.RegisterTrafficData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;
import service.TrafficDataService;

@RestController
@RequestMapping("/traffics")
public class TrafficDataController {

    @Autowired
    TrafficDataService service;

    @PostMapping
    public ResponseEntity<DetailTrafficData> register(RegisterTrafficData registerTrafficData, UriComponentsBuilder uriComponentsBuilder){
        var detailTraffic = service.register(registerTrafficData);

        var uri = uriComponentsBuilder
                .path("/traffics/{id}")
                .buildAndExpand(detailTraffic.id())
                .toUri();

        return ResponseEntity.created(uri)
                .body(detailTraffic);
    }

    @GetMapping
    public ResponseEntity<Page<ListTrafficData>> list(Pageable pageable){
        return ResponseEntity.ok(service.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DetailTrafficData> detail(Long id){
        return ResponseEntity.ok(service.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(Long id){
        service.delete(id);
        return ResponseEntity.noContent()
                .build();
    }
}