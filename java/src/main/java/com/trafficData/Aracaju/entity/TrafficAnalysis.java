package com.trafficData.Aracaju.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@Table(name = "traffic_analysis")
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
public class TrafficAnalysis {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    private Route route;

    private Integer hour;

    private String dayOfWeek;

    private Double avgDuration;

    private String predictedTraffic;
}
