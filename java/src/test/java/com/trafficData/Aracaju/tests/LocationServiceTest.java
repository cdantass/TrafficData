package com.trafficData.Aracaju.tests;

import com.trafficData.Aracaju.dto.location.LocationDetail;
import com.trafficData.Aracaju.dto.location.LocationRegister;
import com.trafficData.Aracaju.entity.Location;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.LocationRepository;
import com.trafficData.Aracaju.service.LocationService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("LocationService")
class LocationServiceTest {

    @Mock
    private LocationRepository locationRepository;

    @InjectMocks
    private LocationService locationService;

    private Location location;
    private LocationRegister registerDto;

    @BeforeEach
    void setUp() {
        registerDto = new LocationRegister("RioMar Aracaju", -10.94545, -37.04805);

        location = new Location(registerDto);
        // Simula ID gerado pelo banco
        try {
            var field = Location.class.getDeclaredField("id");
            field.setAccessible(true);
            field.set(location, 1L);
        } catch (Exception ignored) {}
    }

    // register
    @Test
    @DisplayName("register: deve salvar e retornar LocationDetail")
    void register_success() {
        when(locationRepository.save(any(Location.class))).thenReturn(location);

        LocationDetail result = locationService.register(registerDto);

        assertThat(result).isNotNull();
        assertThat(result.name()).isEqualTo("RioMar Aracaju");
        assertThat(result.latitude()).isEqualTo(-10.94545);
        assertThat(result.longitude()).isEqualTo(-37.04805);
        verify(locationRepository).save(any(Location.class));
    }

    // list
    @Test
    @DisplayName("list: deve retornar página de locations")
    void list_returnsPage() {
        var pageable = PageRequest.of(0, 10);
        when(locationRepository.findAll(pageable))
                .thenReturn(new PageImpl<>(List.of(location)));

        var page = locationService.list(pageable);

        assertThat(page).isNotNull();
        assertThat(page.getTotalElements()).isEqualTo(1);
        assertThat(page.getContent().get(0).name()).isEqualTo("RioMar Aracaju");
    }

    // detail
    @Test
    @DisplayName("detail: deve retornar LocationDetail quando ID existe")
    void detail_found() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(location));

        LocationDetail result = locationService.detail(1L);

        assertThat(result).isNotNull();
        assertThat(result.id()).isEqualTo(1L);
    }

    @Test
    @DisplayName("detail: deve lançar NotFound quando ID não existe")
    void detail_notFound() {
        when(locationRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> locationService.detail(99L))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("Location not found");
    }

    // delete
    @Test
    @DisplayName("delete: deve desativar location (soft delete)")
    void delete_success() {
        when(locationRepository.findById(1L)).thenReturn(Optional.of(location));

        locationService.delete(1L);

        assertThat(location.getActive()).isFalse();
    }

    @Test
    @DisplayName("delete: deve lançar NotFound para ID inexistente")
    void delete_notFound() {
        when(locationRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> locationService.delete(99L))
                .isInstanceOf(NotFound.class);
    }
}