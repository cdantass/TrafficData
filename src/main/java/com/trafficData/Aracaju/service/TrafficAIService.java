package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.trafficPred.PredictRequest;
import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class TrafficAIService {

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private final RestClient restClient = RestClient.create();

    public PredictResponse predict(Long routeId, int dayOfWeek, int hour, double averageSpeed) {
        return restClient.post()
                .uri(aiServiceUrl + "/predict")
                .body(new PredictRequest(routeId, dayOfWeek, hour, averageSpeed))
                .retrieve()
                .body(PredictResponse.class);
    }
}
