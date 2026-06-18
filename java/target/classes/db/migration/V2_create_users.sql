CREATE TABLE users (
                       id       BIGSERIAL PRIMARY KEY,
                       name     VARCHAR(255) NOT NULL,
                       email    VARCHAR(255) NOT NULL UNIQUE,
                       password VARCHAR(255) NOT NULL,
                       role     VARCHAR(20)  NOT NULL DEFAULT 'USER',
                       active   BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);