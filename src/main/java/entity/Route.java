package entity;

import dto.traffic.RegisterRoute;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
public class Route {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    private Location origin;

    @ManyToOne
    private Location destination;

    private String name;

    private Boolean active;

    public Route(Location origin, Location destination, String name) {
        this.origin = origin;
        this.destination = destination;
        this.name = name;
        this.active = true;
    }

    public void updateRoute(
            Location origin,
            Location destination,
            String name
    ) {
        this.origin = origin;
        this.destination = destination;
        this.name = name;
    }

    public void delete() {
        this.active = false;
    }
}