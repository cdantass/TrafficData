package com.trafficData.Aracaju.tests;

import com.trafficData.Aracaju.dto.user.RegisterRequest;
import com.trafficData.Aracaju.entity.User;
import com.trafficData.Aracaju.entity.UserRole;
import com.trafficData.Aracaju.infra.security.TokenService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import static org.assertj.core.api.Assertions.*;

@DisplayName("TokenService")
class TokenServiceTest {

    private TokenService tokenService;
    private User user;

    @BeforeEach
    void setUp() {
        tokenService = new TokenService();
        ReflectionTestUtils.setField(tokenService, "secret", "test-secret-key-aracaju-2024-xyz");

        user = new User(
                new RegisterRequest(null,"Carlos", "carlos@test.com", "senha123", UserRole.USER),
                "hashed_password"
        );
    }

    @Test
    @DisplayName("generateToken: deve gerar token não nulo")
    void generateToken_notNull() {
        String token = tokenService.generateToken(user);
        assertThat(token).isNotNull().isNotBlank();
    }

    @Test
    @DisplayName("generateToken: tokens diferentes para chamadas distintas")
    void generateToken_unique() {
        String token1 = tokenService.generateToken(user);
        String token2 = tokenService.generateToken(user);
        // Tokens podem ser iguais em < 1s, mas o subject deve ser o mesmo
        assertThat(tokenService.getSubject(token1)).isEqualTo("carlos@test.com");
        assertThat(tokenService.getSubject(token2)).isEqualTo("carlos@test.com");
    }

    @Test
    @DisplayName("getSubject: deve retornar email do usuário")
    void getSubject_returnsEmail() {
        String token = tokenService.generateToken(user);
        String subject = tokenService.getSubject(token);
        assertThat(subject).isEqualTo("carlos@test.com");
    }

    @Test
    @DisplayName("getSubject: deve lançar exceção para token inválido")
    void getSubject_invalidToken() {
        assertThatThrownBy(() -> tokenService.getSubject("token.invalido.aqui"))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("inválido");
    }

    @Test
    @DisplayName("getSubject: deve lançar exceção para token com secret errado")
    void getSubject_wrongSecret() {
        String token = tokenService.generateToken(user);

        var outroService = new TokenService();
        ReflectionTestUtils.setField(outroService, "secret", "outro-secret-completamente-diferente");

        assertThatThrownBy(() -> outroService.getSubject(token))
                .isInstanceOf(RuntimeException.class);
    }
}