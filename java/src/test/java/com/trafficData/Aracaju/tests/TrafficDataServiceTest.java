package com.trafficData.Aracaju.tests;

import com.trafficData.Aracaju.dto.traffic.RegisterTrafficData;
import com.trafficData.Aracaju.entity.Route;
import com.trafficData.Aracaju.entity.TrafficData;
import com.trafficData.Aracaju.entity.TrafficLevel;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.RouteRepository;
import com.trafficData.Aracaju.repository.TrafficDataRepository;
import com.trafficData.Aracaju.service.TrafficDataService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("TrafficDataService")
class TrafficDataServiceTest {

    @Mock private TrafficDataRepository trafficDataRepository;
    @Mock private RouteRepository routeRepository;

    @InjectMocks
    private TrafficDataService trafficDataService;

    private Route activeRoute;
    private Route inactiveRoute;

    @BeforeEach
    void setUp() throws Exception {
        activeRoute = new Route();
        activeRoute.setActive(true);
        setId(activeRoute, 1L);

        inactiveRoute = new Route();
        inactiveRoute.setActive(false);
        setId(inactiveRoute, 2L);
    }

    // calculateTrafficLevel
    @Test
    @DisplayName("calculateTrafficLevel: ratio < 1.2 → LOW")
    void calculateLevel_low() {
        assertThat(trafficDataService.calculateTrafficLevel(600.0, 700.0))
                .isEqualTo(TrafficLevel.LOW);
    }

    @Test
    @DisplayName("calculateTrafficLevel: ratio entre 1.2 e 1.5 → MEDIUM")
    void calculateLevel_medium() {
        assertThat(trafficDataService.calculateTrafficLevel(600.0, 800.0))
                .isEqualTo(TrafficLevel.MEDIUM);
    }

    @Test
    @DisplayName("calculateTrafficLevel: ratio >= 1.5 → HIGH")
    void calculateLevel_high() {
        assertThat(trafficDataService.calculateTrafficLevel(600.0, 950.0))
                .isEqualTo(TrafficLevel.HIGH);
    }

    // register
    @Test
    @DisplayName("register: deve salvar e retornar DetailTrafficData")
    void register_success() {
        var dto = new RegisterTrafficData(1L, 600.0, 800.0, 40.0);
        when(routeRepository.findById(1L)).thenReturn(Optional.of(activeRoute));
        when(trafficDataRepository.save(any(TrafficData.class))).thenAnswer(inv -> inv.getArgument(0));

        var result = trafficDataService.register(dto);

        assertThat(result).isNotNull();
        assertThat(result.trafficLevel()).isEqualTo(TrafficLevel.MEDIUM);
        verify(trafficDataRepository).save(any(TrafficData.class));
    }

    @Test
    @DisplayName("register: deve lançar NotFound para rota inexistente")
    void register_routeNotFound() {
        when(routeRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> trafficDataService.register(
                new RegisterTrafficData(99L, 600.0, 800.0, 40.0)))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Route not found");
    }

    @Test
    @DisplayName("register: deve lançar exceção para rota inativa")
    void register_inactiveRoute() {
        when(routeRepository.findById(2L)).thenReturn(Optional.of(inactiveRoute));

        assertThatThrownBy(() -> trafficDataService.register(
                new RegisterTrafficData(2L, 600.0, 800.0, 40.0)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("inactive route");
    }

    @Test
    @DisplayName("register: deve lançar exceção quando durationInTraffic < duration")
    void register_invalidDuration() {
        assertThatThrownBy(() -> trafficDataService.register(
                new RegisterTrafficData(1L, 800.0, 600.0, 40.0)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Duration in traffic cannot be less than duration");
    }

    @Test
    @DisplayName("register: deve lançar exceção quando duration é zero")
    void register_zeroDuration() {
        assertThatThrownBy(() -> trafficDataService.register(
                new RegisterTrafficData(1L, 0.0, 600.0, 40.0)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Duration must be greater than zero");
    }

    @Test
    @DisplayName("register: deve lançar exceção quando speed é zero")
    void register_zeroSpeed() {
        assertThatThrownBy(() -> trafficDataService.register(
                new RegisterTrafficData(1L, 600.0, 800.0, 0.0)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Average speed must be greater than zero");
    }

    // detail
    @Test
    @DisplayName("detail: deve lançar NotFound para ID inexistente")
    void detail_notFound() {
        when(trafficDataRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> trafficDataService.detail(99L))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Traffic not found");
    }

    // delete
    @Test
    @DisplayName("delete: deve remover dado de tráfego existente")
    void delete_success() {
        var td = new TrafficData();
        when(trafficDataRepository.findById(1L)).thenReturn(Optional.of(td));

        trafficDataService.delete(1L);

        verify(trafficDataRepository).delete(td);
    }

    // helpers
    private void setId(Object obj, Long id) throws Exception {
        var field = obj.getClass().getDeclaredField("id");
        field.setAccessible(true);
        field.set(obj, id);
    }
}