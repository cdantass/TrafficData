package com.trafficData.Aracaju.controller;


import com.trafficData.Aracaju.dto.trafficPred.PredictRequest;
import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import com.trafficData.Aracaju.service.PredictionService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/predictions")
public class PredictionController {

    private final PredictionService predictionService;

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @PostMapping
    public PredictResponse predict(@RequestBody PredictRequest request) {
        return predictionService.predict(request);
    }
}
