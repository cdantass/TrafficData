package com.trafficData.Aracaju.service;

import com.trafficData.Aracaju.dto.user.DetailUser;
import com.trafficData.Aracaju.dto.user.ListUser;
import com.trafficData.Aracaju.dto.user.RegisterRequest;
import com.trafficData.Aracaju.dto.user.UpdateUser;
import com.trafficData.Aracaju.entity.User;
import com.trafficData.Aracaju.entity.UserRole;
import com.trafficData.Aracaju.infra.exception.NotFound;
import com.trafficData.Aracaju.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Transactional
    public DetailUser register(RegisterRequest request) {

        if (userRepository.findByEmail(request.email()).isPresent()) {
            throw new IllegalArgumentException("Email already in use");
        }

        var user = new User(request, passwordEncoder.encode(request.password()));

        userRepository.save(user);

        return new DetailUser(user);
    }

    public Page<ListUser> list(Pageable pageable) {
        return userRepository.findAll(pageable)
                .map(ListUser::new);
    }

    public DetailUser detail(Long id) {
        var user = userRepository.findById(id)
                .orElseThrow(() -> new NotFound("User not found"));
        return new DetailUser(user);
    }

    @Transactional
    public DetailUser update(Long id, UpdateUser updateUser) {
        var user = userRepository.findById(updateUser.id())
                .orElseThrow(() -> new NotFound("User not found"));

        String encodedPassword = user.getPassword();

        if (updateUser.password() != null && !updateUser.password().isBlank()) {
            encodedPassword = passwordEncoder.encode(updateUser.password());
        }

        user.update(updateUser.name(), updateUser.email(), encodedPassword, updateUser.role());

        return new DetailUser(user);
    }

    @Transactional
    public void delete(Long id) {
        var user = userRepository.findById(id)
                .orElseThrow(() -> new NotFound("User not found"));
        userRepository.delete(user);
    }
}