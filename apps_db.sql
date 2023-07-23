CREATE TABLE IF NOT EXISTS Applications (
    app_id SERIAL PRIMARY KEY,
    app_name VARCHAR(255),
    app_version VARCHAR(255),
    app_min_version VARCHAR(255),
    app_size VARCHAR(255)
);

WITH new_values (app_name, app_version, app_min_version, app_size) AS (
    VALUES (%s, %s, %s, %s)
),
upsert AS (
    UPDATE Applications AS a
    SET app_version = nv.app_version,
        app_min_version = nv.app_min_version,
        app_size = nv.app_size
    FROM new_values AS nv
    WHERE a.app_name = nv.app_name
    RETURNING a.*
)
INSERT INTO Applications (app_name, app_version, app_min_version, app_size)
SELECT app_name, app_version, app_min_version, app_size
FROM new_values
WHERE NOT EXISTS (
    SELECT 1
    FROM upsert AS u
    WHERE new_values.app_name = u.app_name
);