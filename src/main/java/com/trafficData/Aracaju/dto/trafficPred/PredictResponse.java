package com.trafficData.Aracaju.dto.trafficPred;

public record PredictResponse(
        String predictedLevel,
        Double predictedDuration,
        Double confidence,
        String recommendation
) {}
