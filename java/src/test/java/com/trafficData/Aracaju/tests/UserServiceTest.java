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

import java.lang.reflect.Field;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("UserService")
class UserServiceTest {

    private static final String EXISTING_NAME = "carlos";
    private static final String EXISTING_EMAIL = "Carlos@test.com";
    private static final String EXISTING_PASSWORD = "senha123";
    private static final String EXISTING_HASH = "hashed_password";

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    private User user;

    @BeforeEach
    void setUp() throws Exception {
        var dto = new RegisterRequest(null, EXISTING_NAME, EXISTING_EMAIL, EXISTING_PASSWORD, UserRole.USER);
        user = new User(dto, EXISTING_HASH);
        setId(user, 1L);
    }

    @Test
    @DisplayName("register: deve criar usuário com sucesso")
    void register_success() throws Exception {
        String email = "novo@test.com";
        String password = "senha123";

        var request = new RegisterRequest(null, "novo", email, password, UserRole.USER);

        when(userRepository.findByEmail(email)).thenReturn(Optional.empty());
        when(passwordEncoder.encode(password)).thenReturn("hashed_new");
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User saved = invocation.getArgument(0);
            setId(saved, 2L);
            return saved;
        });

        var result = userService.register(request);

        assertThat(result).isNotNull();
        assertThat(result.email()).isEqualTo(email);
        assertThat(result.role()).isEqualTo(UserRole.USER);
    }

    @Test
    @DisplayName("register: deve lançar exceção para e-mail duplicado")
    void register_duplicateEmail() {
        var request = new RegisterRequest(null, "carlos", EXISTING_EMAIL, EXISTING_PASSWORD, UserRole.USER);

        when(userRepository.findByEmail(EXISTING_EMAIL)).thenReturn(Optional.of(user));

        assertThatThrownBy(() -> userService.register(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Email already in use");
    }

    @Test
    @DisplayName("register: role nulo deve ser USER por padrão")
    void register_defaultRoleUser() throws Exception {
        String email = "cau@test.com";
        String password = "senha123";

        var request = new RegisterRequest(null, "cau", email, password, null);

        when(userRepository.findByEmail(email)).thenReturn(Optional.empty());
        when(passwordEncoder.encode(password)).thenReturn("hashed_default");
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User saved = invocation.getArgument(0);
            setId(saved, 3L);
            return saved;
        });

        var result = userService.register(request);

        assertThat(result).isNotNull();
        assertThat(result.email()).isEqualTo(email);
        assertThat(result.role()).isEqualTo(UserRole.USER);
    }

    @Test
    @DisplayName("detail: deve retornar usuário existente")
    void detail_found() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        var result = userService.detail(1L);

        assertThat(result).isNotNull();
        assertThat(result.email()).isEqualTo(EXISTING_EMAIL);
    }

    @Test
    @DisplayName("detail: deve lançar NotFound para ID inexistente")
    void detail_notFound() {
        when(userRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userService.detail(99L))
                .isInstanceOf(NotFound.class)
                .hasMessageContaining("User not found");
    }

    @Test
    @DisplayName("update: deve atualizar nome e role")
    void update_success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        var result = userService.update(1L, new UpdateUser(1L, "Carlos Novo", null, null, UserRole.ADMIN));

        assertThat(result).isNotNull();
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

    @Test
    @DisplayName("delete: deve remover usuário existente")
    void delete_success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        userService.delete(1L);

        verify(userRepository).delete(user);
    }

    private void setId(Object obj, Long id) throws Exception {
        Field field = obj.getClass().getDeclaredField("id");
        field.setAccessible(true);
        field.set(obj, id);
    }
}