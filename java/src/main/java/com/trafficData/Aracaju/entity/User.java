package com.trafficData.Aracaju.entity;

import com.trafficData.Aracaju.dto.user.RegisterRequest;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

@Entity
@Getter
@Setter
@Table(name = "users")
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Column(unique = true)
    private String email;

    private String password;

    @Enumerated(EnumType.STRING)
    private UserRole role;

    private Boolean active = true;

    public User(RegisterRequest dto, String hashedPassword) {
        this.name = dto.name();
        this.email = dto.email();
        this.password = hashedPassword;
        this.role = dto.role() != null ? dto.role() : UserRole.USER;
        this.active = true;
    }

    public void update(String name, String email, String password, UserRole role) {
        if (name != null && !name.isBlank()) {
            this.name = name;
        }
        if (email != null && !email.isBlank()) {
            this.email = email;
        }
        if (password != null && !password.isBlank()) {
            this.password = password;
        }
        if (role != null) {
            this.role = role;
        }
    }

    public void delete() {
        this.active = false;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        if (this.role == UserRole.ADMIN) {
            return List.of(
                    new SimpleGrantedAuthority("ROLE_ADMIN"),
                    new SimpleGrantedAuthority("ROLE_USER")
            );
        }
        return List.of(new SimpleGrantedAuthority("ROLE_USER"));
    }

    @Override
    public String getUsername() {
        return this.email;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return this.active;
    }
}