package entity;

import dto.RegisterRoute;
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

    public Route(RegisterRoute registerRoute) {
        this.origin = registerRoute.origin();
        this.destination = registerRoute.destination();
        this.name = registerRoute.name();
        this.active = true;
    }

    public void delete(){
        this.active = false;
    }
}
