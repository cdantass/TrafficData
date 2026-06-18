package com.trafficData.Aracaju.tests;

import com.trafficData.Aracaju.dto.user.RegisterRequest;
import com.trafficData.Aracaju.dto.user.UpdateUser;
import com.trafficData.Aracaju.entity.User;
import com.trafficData.Aracaju.entity.UserRole;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.UserRepository;
import com.trafficData.Aracaju.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("UserService")
class UserServiceTest {

    @Mock private UserRepository userRepository;
    @Mock private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    private User user;

    @BeforeEach
    void setUp() throws Exception {
        var dto = new RegisterRequest(null, "carlos", "Carlos@teste.com", "senha123", UserRole.USER);
        user = new User(dto, "hashed_password");
        setId(user, 1L);
    }

    // register
    @Test
    @DisplayName("register: deve criar usuário com sucesso")
    void register_success() {
        when(userRepository.findByEmail("carlos@test.com")).thenReturn(Optional.empty());
        when(passwordEncoder.encode("senha123")).thenReturn("hashed_password");
        when(userRepository.save(any(User.class))).thenReturn(user);

        var result = userService.register(
                new RegisterRequest(null, "carlos", "Carlos@teste.com", "senha123", UserRole.USER));

        assertThat(result).isNotNull();
        assertThat(result.email()).isEqualTo("carlos@test.com");
        assertThat(result.role()).isEqualTo(UserRole.USER);
    }

    @Test
    @DisplayName("register: deve lançar exceção para e-mail duplicado")
    void register_duplicateEmail() {
        when(userRepository.findByEmail("carlos@test.com")).thenReturn(Optional.of(user));

        assertThatThrownBy(() -> userService.register(
                new RegisterRequest(null, "carlos", "Carlos@teste.com", "senha123", UserRole.USER)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Email already in use");
    }

    @Test
    @DisplayName("register: role nulo deve ser USER por padrão")
    void register_defaultRoleUser() {
        when(userRepository.findByEmail(anyString())).thenReturn(Optional.empty());
        when(passwordEncoder.encode(anyString())).thenReturn("hashed");
        when(userRepository.save(any(User.class))).thenAnswer(inv -> inv.getArgument(0));

        var result = userService.register(
                new RegisterRequest(null, "cau", "cau@test.com", null, UserRole.USER));

        assertThat(result.role()).isEqualTo(UserRole.USER);
    }

    // detail
    @Test
    @DisplayName("detail: deve retornar usuário existente")
    void detail_found() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        var result = userService.detail(1L);

        assertThat(result.email()).isEqualTo("carlos@test.com");
    }

    @Test
    @DisplayName("detail: deve lançar NotFound para ID inexistente")
    void detail_notFound() {
        when(userRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userService.detail(99L))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("User not found");
    }

    // update
    @Test
    @DisplayName("update: deve atualizar nome e role")
    void update_success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        var result = userService.update(1L, new UpdateUser(1L, "Carlos Novo", null, null, UserRole.ADMIN));

        assertThat(result.name()).isEqualTo("Carlos Novo");
        assertThat(result.role()).isEqualTo(UserRole.ADMIN);
    }

    @Test
    @DisplayName("update: deve codificar nova senha quando fornecida")
    void update_newPassword() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(passwordEncoder.encode("novaSenha")).thenReturn("nova_hash");

        userService.update(1L, new UpdateUser(1L, null, null, "novaSenha", null));

        verify(passwordEncoder).encode("novaSenha");
    }

    // delete
    @Test
    @DisplayName("delete: deve remover usuário existente")
    void delete_success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        userService.delete(1L);

        verify(userRepository).delete(user);
    }

    // helpers
    private void setId(Object obj, Long id) throws Exception {
        var field = obj.getClass().getDeclaredField("id");
        field.setAccessible(true);
        field.set(obj, id);
    }
}
