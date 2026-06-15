package com.trafficData.Aracaju.dto.trafficPred;

public record PredictRequest(
        Long routeId,
        Integer dayOfWeek,
        Integer hour,
        Double averageSpeed
) {}