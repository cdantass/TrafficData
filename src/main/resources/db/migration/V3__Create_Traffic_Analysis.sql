CREATE TABLE traffic_analysis (
                                  id                 BIGSERIAL PRIMARY KEY,
                                  route_id           BIGINT NOT NULL,
                                  day_of_week        VARCHAR(20) NOT NULL,
                                  hour               INTEGER NOT NULL,
                                  avg_duration       DOUBLE PRECISION NOT NULL,
                                  predicted_traffic  VARCHAR(20) NOT NULL,
                                  CONSTRAINT fk_analysis_route FOREIGN KEY (route_id) REFERENCES route(id)
);