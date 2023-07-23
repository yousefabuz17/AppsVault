CREATE TABLE IF NOT EXISTS Applications (
    app_id SERIAL PRIMARY KEY,
    app_name VARCHAR(255),
    app_version VARCHAR(255),
    app_min_version VARCHAR(255)
    app_size VARCHAR(255)
);