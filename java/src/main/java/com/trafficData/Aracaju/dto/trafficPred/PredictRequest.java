package com.trafficData.Aracaju.dto.trafficPred;

import com.fasterxml.jackson.annotation.JsonProperty;

public record PredictRequest(
        @JsonProperty("route_id")    Long routeId,
        @JsonProperty("day_of_week") int dayOfWeek,
        int hour
) {}