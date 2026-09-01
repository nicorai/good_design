SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    backend_start
FROM pg_stat_activity
ORDER BY backend_start;


SELECT
    name,
    setting
FROM pg_settings
WHERE name IN (
    'max_connections',
    'log_destination',
    'logging_collector',
    'log_directory',
    'log_filename'
);