package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.trafficPred.PredictRequest;
import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import com.trafficData.Aracaju.infra.exception.AiServiceException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class TrafficAIService {

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private final RestClient restClient = RestClient.create();

    public PredictResponse predict(Long routeId, int dayOfWeek, int hour) {
        try {
            return restClient.post()
                    .uri(aiServiceUrl + "/predict")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(new PredictRequest(routeId, dayOfWeek, hour))
                    .retrieve()
                    .body(PredictResponse.class);
        } catch (Exception e) {
            throw new AiServiceException("Serviço de IA indisponível: " + e.getMessage());
        }
    }

    public Object bestHours(Long routeId, int dayOfWeek) {
        try {
            return restClient.get()
                    .uri(aiServiceUrl + "/best-hours/{routeId}?day_of_week={day}",
                            routeId, dayOfWeek)
                    .retrieve()
                    .body(Object.class);
        } catch (Exception e) {
            throw new AiServiceException("Serviço de IA indisponível: " + e.getMessage());
        }
    }

    public Object insights(Long routeId) {
        try {
            return restClient.get()
                    .uri(aiServiceUrl + "/insights/{routeId}", routeId)
                    .retrieve()
                    .body(Object.class);
        } catch (Exception e) {
            throw new AiServiceException("Serviço de IA indisponível: " + e.getMessage());
        }
    }

    public Object health() {
        try {
            return restClient.get()
                    .uri(aiServiceUrl + "/health")
                    .retrieve()
                    .body(Object.class);
        } catch (Exception e) {
            throw new AiServiceException("Serviço de IA offline");
        }
    }
}
