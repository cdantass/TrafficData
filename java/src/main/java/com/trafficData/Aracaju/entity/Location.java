package com.trafficData.Aracaju.entity;

import com.trafficData.Aracaju.dto.location.LocationRegister;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@AllArgsConstructor
@Table(name = "location")
@NoArgsConstructor
@EqualsAndHashCode(of = "id")
public class Location {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    private Double latitude;
    private Double longitude;

    private Boolean active;


    public Location(LocationRegister locationRegister) {
        this.name = locationRegister.name();
        this.latitude = locationRegister.latitude();
        this.longitude = locationRegister.longitude();
        this.active = true;
    }

    public void delete(){
        this.active = false;
    }
}
