package com.trafficData.Aracaju.dto.trafficPred;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public record PredictResponse(
        @JsonProperty("route_id")               Long routeId,
        @JsonProperty("day_of_week")            int dayOfWeek,
        @JsonProperty("day_of_week_name")       String dayOfWeekName,
        int hour,
        @JsonProperty("predicted_level")        String predictedLevel,
        @JsonProperty("predicted_duration")     Double predictedDuration,
        Double confidence,
        @JsonProperty("is_peak_hour")           Boolean isPeakHour,
        String recommendation,
        @JsonProperty("probability_distribution") Map<String, Double> probabilityDistribution,
        @JsonProperty("model_version")          String modelVersion
) {}