package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.traffic.DetailTrafficData;
import com.trafficData.Aracaju.dto.traffic.ListTrafficData;
import com.trafficData.Aracaju.dto.traffic.RegisterTrafficData;
import com.trafficData.Aracaju.dto.traffic.UpdateTrafficData;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;
import com.trafficData.Aracaju.service.TrafficDataService;

@RestController
@RequestMapping("/traffics")
public class TrafficDataController {

    @Autowired
    TrafficDataService service;

    @PostMapping
    public ResponseEntity<DetailTrafficData> register(@RequestBody @Valid RegisterTrafficData registerTrafficData, UriComponentsBuilder uriComponentsBuilder){
        var detailTraffic = service.register(registerTrafficData);

        var uri = uriComponentsBuilder
                .path("/traffics/{id}")
                .buildAndExpand(detailTraffic.id())
                .toUri();

        return ResponseEntity.created(uri)
                .body(detailTraffic);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DetailTrafficData> update(
            @PathVariable("id") Long id,
            @RequestBody @Valid UpdateTrafficData updateTrafficData) {
        return ResponseEntity.ok(service.update(id, updateTrafficData));
    }

    @GetMapping
    public ResponseEntity<Page<ListTrafficData>> list(Pageable pageable){
        return ResponseEntity.ok(service.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DetailTrafficData> detail(@PathVariable Long id){
        return ResponseEntity.ok(service.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id){
        service.delete(id);
        return ResponseEntity.noContent()
                .build();
    }
}