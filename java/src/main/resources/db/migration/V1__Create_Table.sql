CREATE TABLE location (
                          id BIGSERIAL PRIMARY KEY,
                          name VARCHAR(255) NOT NULL,
                          latitude DOUBLE PRECISION,
                          longitude DOUBLE PRECISION,
                          active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE route (
                       id BIGSERIAL PRIMARY KEY,

                       origin_id BIGINT NOT NULL,
                       destination_id BIGINT NOT NULL,

                       name VARCHAR(255) NOT NULL,

                       active BOOLEAN NOT NULL DEFAULT TRUE,

                       CONSTRAINT fk_route_origin
                           FOREIGN KEY (origin_id)
                               REFERENCES location(id),

                       CONSTRAINT fk_route_destination
                           FOREIGN KEY (destination_id)
                               REFERENCES location(id)
);

CREATE TABLE traffic_data (
                              id BIGSERIAL PRIMARY KEY,

                              route_id BIGINT NOT NULL,

                              timestamp TIMESTAMP NOT NULL,

                              duration DOUBLE PRECISION NOT NULL,

                              duration_in_traffic DOUBLE PRECISION NOT NULL,

                              average_speed DOUBLE PRECISION NOT NULL,

                              traffic_level VARCHAR(20) NOT NULL,

                              CONSTRAINT fk_traffic_route
                                  FOREIGN KEY (route_id)
                                      REFERENCES route(id)
);

CREATE INDEX idx_route_origin
    ON route(origin_id);

CREATE INDEX idx_route_destination
    ON route(destination_id);

CREATE INDEX idx_traffic_route
    ON traffic_data(route_id);

CREATE INDEX idx_traffic_timestamp
    ON traffic_data(timestamp);