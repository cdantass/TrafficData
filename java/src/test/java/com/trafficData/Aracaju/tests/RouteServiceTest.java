package com.trafficData.Aracaju.tests;

import com.trafficData.Aracaju.dto.traffic.DetailRoute;
import com.trafficData.Aracaju.dto.traffic.RegisterRoute;
import com.trafficData.Aracaju.dto.traffic.UpdateRoute;
import com.trafficData.Aracaju.entity.Location;
import com.trafficData.Aracaju.entity.Route;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.LocationRepository;
import com.trafficData.Aracaju.repository.RouteRepository;
import com.trafficData.Aracaju.service.RouteService;
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
@DisplayName("RouteService")
class RouteServiceTest {

    @Mock
    private RouteRepository routeRepository;

    @Mock
    private LocationRepository locationRepository;

    @InjectMocks
    private RouteService routeService;

    private Location origin;
    private Location destination;
    private Route route;

    @BeforeEach
    void setUp() throws Exception {
        origin = buildLocation(1L, "RioMar Aracaju", -10.94545, -37.04805);
        destination = buildLocation(2L, "UFS Aracaju", -10.92380, -37.10610);

        route = new Route(origin, destination, "RioMar Aracaju -> UFS Aracaju");
        setId(route, 1L);
    }

    @Test
    @DisplayName("register: deve criar rota com sucesso")
    void register_success() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(origin));
        when(locationRepository.findById(2L)).thenReturn(Optional.of(destination));
        when(routeRepository.existsByOriginAndDestination(origin, destination)).thenReturn(false);
        when(routeRepository.save(any(Route.class))).thenReturn(route);

        DetailRoute result = routeService.register(new RegisterRoute(1L, 2L));

        assertThat(result).isNotNull();
        assertThat(result.name()).isEqualTo("RioMar Aracaju -> UFS Aracaju");
        verify(routeRepository).save(any(Route.class));
    }

    @Test
    @DisplayName("register: deve lançar exceção quando rota já existe")
    void register_duplicateRoute() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(origin));
        when(locationRepository.findById(2L)).thenReturn(Optional.of(destination));
        when(routeRepository.existsByOriginAndDestination(origin, destination)).thenReturn(true);

        assertThatThrownBy(() -> routeService.register(new RegisterRoute(1L, 2L)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Route already exists");
    }

    @Test
    @DisplayName("register: deve lançar exceção quando origem == destino")
    void register_sameOriginDestination() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(origin));

        assertThatThrownBy(() -> routeService.register(new RegisterRoute(1L, 1L)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Origin and destination cannot be the same");
    }

    @Test
    @DisplayName("register: deve lançar NotFound quando origem não existe")
    void register_originNotFound() {
        when(locationRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> routeService.register(new RegisterRoute(99L, 2L)))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Origin not found");
    }

    @Test
    @DisplayName("register: deve lançar NotFound quando destino não existe")
    void register_destinationNotFound() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(origin));
        when(locationRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> routeService.register(new RegisterRoute(1L, 99L)))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Destination not found");
    }

    @Test
    @DisplayName("detail: deve retornar rota existente")
    void detail_found() {
        when(routeRepository.findById(1L)).thenReturn(Optional.of(route));

        DetailRoute result = routeService.detail(1L);

        assertThat(result).isNotNull();
        assertThat(result.id()).isEqualTo(1L);
    }

    @Test
    @DisplayName("detail: deve lançar NotFound para ID inexistente")
    void detail_notFound() {
        when(routeRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> routeService.detail(99L))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Route not found");
    }

    @Test
    @DisplayName("update: deve atualizar rota com sucesso")
    void update_success() throws Exception {
        var newDest = buildLocation(4L, "HUSE Aracaju", -10.94380, -37.07150);

        when(routeRepository.findById(1L)).thenReturn(Optional.of(route));
        when(locationRepository.findById(1L)).thenReturn(Optional.of(origin));
        when(locationRepository.findById(4L)).thenReturn(Optional.of(newDest));
        when(routeRepository.existsByOriginAndDestination(origin, newDest)).thenReturn(false);

        DetailRoute result = routeService.update(1L, new UpdateRoute(1L, 1L, 4L));

        assertThat(result).isNotNull();
        assertThat(result.name()).isEqualTo("RioMar Aracaju -> HUSE Aracaju");
    }

    @Test
    @DisplayName("delete: deve remover rota existente")
    void delete_success() {
        when(routeRepository.findById(1L)).thenReturn(Optional.of(route));

        routeService.delete(1L);

        verify(routeRepository).delete(route);
    }

    @Test
    @DisplayName("delete: deve lançar NotFound para ID inexistente")
    void delete_notFound() {
        when(routeRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> routeService.delete(99L))
                .isInstanceOf(NotFound.class);
    }

    private Location buildLocation(Long id, String name, double lat, double lng) throws Exception {
        var loc = new Location(
                new com.trafficData.Aracaju.dto.location.LocationRegister(name, lat, lng)
        );
        setId(loc, id);
        return loc;
    }

    private void setId(Object obj, Long id) throws Exception {
        var field = obj.getClass().getDeclaredField("id");
        field.setAccessible(true);
        field.set(obj, id);
    }
}