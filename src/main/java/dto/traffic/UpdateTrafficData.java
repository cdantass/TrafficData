package dto.traffic;

import jakarta.validation.constraints.NotNull;

public record UpdateTrafficData(@NotNull Long id, @NotNull Long routeId) {
}
