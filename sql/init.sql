CREATE TABLE IF NOT EXISTS events (
    id             BIGINT       AUTO_INCREMENT PRIMARY KEY,
    event_id       VARCHAR(36)  NOT NULL UNIQUE,
    event_type     VARCHAR(50)  NOT NULL,
    user_id        BIGINT       NOT NULL,
    order_id       INT,
    lecture_id     INT,
    amount         INT,
    payment_method VARCHAR(50),
    error_code     VARCHAR(50),
    error_page     VARCHAR(100),
    timestamp      DATETIME     NOT NULL,
    ingested_at    DATETIME     DEFAULT CURRENT_TIMESTAMP
);
