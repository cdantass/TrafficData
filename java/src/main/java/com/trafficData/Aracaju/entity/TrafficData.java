package com.trafficData.Aracaju.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@Table(name = "traffic_data")
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
public class TrafficData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "route_id")
    private Route route;

    private LocalDateTime timestamp;

    private Double duration;

    private Double durationInTraffic;

    private Double averageSpeed;

    @Enumerated(EnumType.STRING)
    private TrafficLevel trafficLevel;

    public void update(
            Route route){
        this.route = route;
    }

}