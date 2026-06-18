package com.trafficData.Aracaju.dto.traffic;

import jakarta.validation.constraints.NotNull;

public record UpdateRoute(

        @NotNull
        Long id,

        @NotNull
        Long originId,

        @NotNull
        Long destinationId

) {
}