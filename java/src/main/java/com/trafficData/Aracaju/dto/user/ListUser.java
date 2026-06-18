package com.trafficData.Aracaju.dto.user;

import com.trafficData.Aracaju.entity.User;
import com.trafficData.Aracaju.entity.UserRole;

public record ListUser(Long id, String name, String email, UserRole userRole) {
    public ListUser(User user){
        this(user.getId(), user.getName(), user.getEmail(), user.getRole());
    }
}
