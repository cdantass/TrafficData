package entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Getter
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
@Setter
public class TrafficData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
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