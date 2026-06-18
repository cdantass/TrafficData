package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.user.DetailUser;
import com.trafficData.Aracaju.dto.user.ListUser;
import com.trafficData.Aracaju.dto.user.RegisterRequest;
import com.trafficData.Aracaju.dto.user.UpdateUser;
import com.trafficData.Aracaju.service.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;

@RestController
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping
    public ResponseEntity<DetailUser> register(@RequestBody @Valid RegisterRequest registerRequest, UriComponentsBuilder uriComponentsBuilder){
        var detailUser = userService.register(registerRequest);

        var uri = uriComponentsBuilder
                .path("/users/{id}")
                .buildAndExpand(detailUser.id())
                .toUri();
        return ResponseEntity.created(uri)
                .body(detailUser);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DetailUser> update(@PathVariable Long id, @RequestBody @Valid UpdateUser updateUser){
        return ResponseEntity.ok(userService.update(id, updateUser));
    }

    @GetMapping
    public ResponseEntity<Page<ListUser>> list(Pageable pageable){
        return ResponseEntity.ok(userService.list(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DetailUser> detail(@PathVariable Long id){
        return ResponseEntity.ok(userService.detail(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id){
        return ResponseEntity.noContent().build();
    }
}