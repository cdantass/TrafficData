package controller;

import dto.traffic.RegisterRoute;
import dto.traffic.DetailRoute;
import dto.traffic.ListRoute;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;
import service.RouteService;

@RestController
@RequestMapping("/routes")
public class RouteController {

    @Autowired
    RouteService routeService;

    @PostMapping
    public ResponseEntity<DetailRoute> register(RegisterRoute registerRoute, UriComponentsBuilder uriComponentsBuilder){
        var detailRoute = routeService.register(registerRoute);

        var uri = uriComponentsBuilder
                .path("/routes/{id}")
                .buildAndExpand(detailRoute.id())
                .toUri();
        return ResponseEntity.created(uri)
                .body(detailRoute);
    }

    @GetMapping
    public ResponseEntity<Page<ListRoute>> list(Pageable pageable){
        return ResponseEntity.ok(routeService.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DetailRoute> detail(Long id){
        return ResponseEntity.ok(routeService.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(Long id){
        routeService.delete(id);
        return ResponseEntity.noContent().build();
    }
}