package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.trafficPred.PredictRequest;
import com.trafficData.Aracaju.dto.trafficPred.PredictResponse;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class PredictionService {

    private final RestTemplate restTemplate;

    public PredictionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public PredictResponse predict(PredictRequest request) {
        String url = "http://localhost:8000/predict";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setAccept(java.util.Collections.singletonList(MediaType.APPLICATION_JSON));

        HttpEntity<PredictRequest> entity = new HttpEntity<>(request, headers);

        ResponseEntity<PredictResponse> response =
                restTemplate.postForEntity(url, entity, PredictResponse.class);

        return response.getBody();
    }
}