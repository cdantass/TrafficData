package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import com.trafficData.Aracaju.service.RouteService;
import com.trafficData.Aracaju.service.TrafficAIService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/analysis")
@SecurityRequirement(name = "bearer-key")
@Tag(name = "Traffic Analysis", description = "Previsões de tráfego com IA")
public class TrafficAnalysisController {

    @Autowired
    private TrafficAIService trafficAIService;

    @Autowired
    private RouteService routeService;

    @GetMapping("/predict")
    @Operation(summary = "Previsão de tráfego para uma rota em dia e hora específicos")
    public ResponseEntity<PredictResponse> predict(
            @RequestParam Long routeId,
            @RequestParam int dayOfWeek,
            @RequestParam int hour) {

        routeService.detail(routeId);

        return ResponseEntity.ok(trafficAIService.predict(routeId, dayOfWeek, hour));
    }

    @GetMapping("/best-hour")
    @Operation(summary = "Melhor horário do dia para uma rota")
    public ResponseEntity<PredictResponse> bestHour(
            @RequestParam Long routeId,
            @RequestParam int dayOfWeek) {

        routeService.detail(routeId);

        return ResponseEntity.ok(trafficAIService.predictBestHour(routeId, dayOfWeek));
    }
}