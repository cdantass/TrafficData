package com.trafficData.Aracaju.controller;

import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import com.trafficData.Aracaju.service.RouteService;
import com.trafficData.Aracaju.service.TrafficAIService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
    @Operation(
            summary = "Previsão de tráfego",
            description = "Retorna nível de tráfego, duração estimada e recomendação para um dia e hora específicos."
    )
    public ResponseEntity<PredictResponse> predict(
            @Parameter(description = "ID da rota", example = "1") @RequestParam Long routeId,
            @Parameter(description = "Dia da semana (0=Segunda ... 6=Domingo)", example = "1") @RequestParam int dayOfWeek,
            @Parameter(description = "Hora do dia (0-23)", example = "8") @RequestParam int hour) {

        routeService.detail(routeId);
        return ResponseEntity.ok(trafficAIService.predict(routeId, dayOfWeek, hour));
    }

    @GetMapping("/best-hours")
    @Operation(
            summary = "Ranking de melhores horários",
            description = "Retorna todos os horários do dia ordenados do menor para o maior tráfego."
    )
    public ResponseEntity<Object> bestHours(
            @Parameter(description = "ID da rota", example = "1") @RequestParam Long routeId,
            @Parameter(description = "Dia da semana (0=Segunda ... 6=Domingo)", example = "1") @RequestParam int dayOfWeek) {

        routeService.detail(routeId);
        return ResponseEntity.ok(trafficAIService.bestHours(routeId, dayOfWeek));
    }

    @GetMapping("/insights/{routeId}")
    @Operation(
            summary = "Análise completa da rota",
            description = "Retorna os melhores e piores horários para cada dia da semana."
    )
    public ResponseEntity<Object> insights(
            @Parameter(description = "ID da rota", example = "1") @PathVariable Long routeId) {

        routeService.detail(routeId);
        return ResponseEntity.ok(trafficAIService.insights(routeId));
    }

    @GetMapping("/health")
    @Operation(
            summary = "Status da IA",
            description = "Verifica se o serviço Python está online e se o modelo já foi treinado."
    )
    public ResponseEntity<Object> health() {
        return ResponseEntity.ok(trafficAIService.health());
    }
}