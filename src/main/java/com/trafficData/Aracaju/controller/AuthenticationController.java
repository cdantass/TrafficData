package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.auth.AuthenticationRequest;
import com.trafficData.Aracaju.dto.auth.DadosTokenJWT;
import com.trafficData.Aracaju.entity.User;
import com.trafficData.Aracaju.infra.security.TokenService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/login")
public class AuthenticationController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private TokenService tokenService;

    @PostMapping
    public ResponseEntity<?> effectLogin(@RequestBody @Valid AuthenticationRequest dados) {
        try {
            var authenticationToken = new UsernamePasswordAuthenticationToken(
                    dados.email(),
                    dados.password()
            );

            var authentication = authenticationManager.authenticate(authenticationToken);

            var jwt = tokenService.generateToken((User) authentication.getPrincipal());

            return ResponseEntity.ok(new DadosTokenJWT(jwt));

        } catch (BadCredentialsException e) {
            return ResponseEntity.status(401).body("Login or Password invalid");
        }
    }

    @GetMapping("/me")
    public ResponseEntity<UserDetails> me(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(user);
    }
}