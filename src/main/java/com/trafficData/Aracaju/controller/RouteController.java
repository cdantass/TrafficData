package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.traffic.RegisterRoute;
import com.trafficData.Aracaju.dto.traffic.DetailRoute;
import com.trafficData.Aracaju.dto.traffic.ListRoute;
import com.trafficData.Aracaju.dto.traffic.UpdateRoute;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;
import com.trafficData.Aracaju.service.RouteService;

@RestController
@RequestMapping("/routes")
public class RouteController {

    @Autowired
    RouteService routeService;

    @PostMapping
    public ResponseEntity<DetailRoute> register(@RequestBody @Valid RegisterRoute registerRoute, UriComponentsBuilder uriComponentsBuilder){
        var detailRoute = routeService.register(registerRoute);

        var uri = uriComponentsBuilder
                .path("/routes/{id}")
                .buildAndExpand(detailRoute.id())
                .toUri();
        return ResponseEntity.created(uri)
                .body(detailRoute);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DetailRoute> update(@PathVariable Long id, @RequestBody @Valid UpdateRoute updateRoute){
        return ResponseEntity.ok(routeService.update(id, updateRoute));
    }

    @GetMapping
    public ResponseEntity<Page<ListRoute>> list(Pageable pageable){
        return ResponseEntity.ok(routeService.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DetailRoute> detail( @PathVariable Long id){
        return ResponseEntity.ok(routeService.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete( @PathVariable Long id){
        routeService.delete(id);
        return ResponseEntity.noContent().build();
    }
}