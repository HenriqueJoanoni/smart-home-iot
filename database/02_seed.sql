-- ====================================================================
-- SMART HOME IOT - DATABASE SEED SCRIPT
-- ====================================================================
-- Description: Populates database with initial data for development
--              and testing purposes
-- Author: Henrique Joanoni
-- ====================================================================

-- ====================================================================
-- SEED:  device_states
-- Purpose: Initialise all controllable devices
-- ====================================================================

INSERT INTO device_states (device_name, device_type, state, value, updated_by) VALUES
    ('led_red', 'led', 'off', '{"brightness": 0, "colour": "red"}', 'system'),
    ('led_green', 'led', 'off', '{"brightness": 0, "colour": "green"}', 'system'),
    ('led_blue', 'led', 'off', '{"brightness": 0, "colour": "blue"}', 'system'),
    ('buzzer_main', 'buzzer', 'off', '{"frequency": 0, "duration": 0}', 'system')
ON CONFLICT (device_name) DO NOTHING;

-- ====================================================================
-- SEED: sensor_readings (Sample data for last 24 hours)
-- Purpose: Provide initial data for testing charts and aggregates
-- ====================================================================

-- Temperature readings (DHT22) - Realistic pattern with day/night variation
INSERT INTO sensor_readings (timestamp, sensor_type, value, unit, location, device_id)
SELECT
    timestamp,
    'temperature',
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 6 AND 18 THEN
            22.0 + (RANDOM() * 6.0) + (EXTRACT(HOUR FROM timestamp) - 12) * 0.3
        ELSE
            18.0 + (RANDOM() * 4.0)
    END,
    '°C',
    'living_room',
    'raspberry_pi_main'
FROM generate_series(
    NOW() - INTERVAL '24 hours',
    NOW(),
    INTERVAL '5 minutes'
) AS timestamp;

-- Humidity readings (DHT22) - Inverse correlation with temperature
INSERT INTO sensor_readings (timestamp, sensor_type, value, unit, location, device_id)
SELECT
    timestamp,
    'humidity',
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 6 AND 18 THEN
            45.0 + (RANDOM() * 15.0)
        ELSE
            55.0 + (RANDOM() * 15.0)
    END,
    '%',
    'living_room',
    'raspberry_pi_main'
FROM generate_series(
    NOW() - INTERVAL '24 hours',
    NOW(),
    INTERVAL '5 minutes'
) AS timestamp;

-- Light intensity readings (LDR) - Clear day/night pattern
INSERT INTO sensor_readings (timestamp, sensor_type, value, unit, location, device_id)
SELECT
    timestamp,
    'light',
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 7 AND 19 THEN
            300.0 + (RANDOM() * 500.0) + 
            SIN(RADIANS((EXTRACT(HOUR FROM timestamp) - 7) * 15)) * 200
        ELSE
            5. 0 + (RANDOM() * 15.0)
    END,
    'lux',
    'living_room',
    'raspberry_pi_main'
FROM generate_series(
    NOW() - INTERVAL '24 hours',
    NOW(),
    INTERVAL '5 minutes'
) AS timestamp;

-- Motion detection readings (PIR) - Random events, more during day
INSERT INTO sensor_readings (timestamp, sensor_type, value, unit, location, device_id)
SELECT
    timestamp,
    'motion',
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 7 AND 23 THEN
            CASE WHEN RANDOM() < 0.15 THEN 1 ELSE 0 END
        ELSE
            CASE WHEN RANDOM() < 0.03 THEN 1 ELSE 0 END
    END,
    'boolean',
    'living_room',
    'raspberry_pi_main'
FROM generate_series(
    NOW() - INTERVAL '24 hours',
    NOW(),
    INTERVAL '30 seconds'
) AS timestamp;

-- ====================================================================
-- SEED: alerts (Sample alerts)
-- Purpose: Demonstrate alert functionality
-- ====================================================================

INSERT INTO alerts (
    timestamp,
    alert_type,
    severity,
    title,
    message,
    sensor_type,
    sensor_value,
    threshold_value,
    resolved,
    resolved_at,
    resolved_by
) VALUES
    (
        NOW() - INTERVAL '2 hours',
        'high_temperature',
        'warning',
        'High Temperature Detected',
        'Living room temperature exceeded warning threshold',
        'temperature',
        31.5,
        30. 0,
        TRUE,
        NOW() - INTERVAL '1 hour 45 minutes',
        'system'
    ),
    (
        NOW() - INTERVAL '30 minutes',
        'low_light',
        'info',
        'Low Light Level',
        'Light intensity below optimal level',
        'light',
        85.0,
        100.0,
        FALSE,
        NULL,
        NULL
    ),
    (
        NOW() - INTERVAL '5 minutes',
        'motion_detected',
        'info',
        'Motion Detected',
        'Movement detected in living room',
        'motion',
        1.0,
        0.5,
        FALSE,
        NULL,
        NULL
    );

-- ====================================================================
-- SEED: system_logs (Sample logs)
-- Purpose: Demonstrate logging functionality
-- ====================================================================

INSERT INTO system_logs (timestamp, log_level, source, message, metadata) VALUES
    (NOW() - INTERVAL '1 hour', 'INFO', 'backend. app', 'Flask application started', '{"version": "1.0.0", "environment": "development"}'),
    (NOW() - INTERVAL '55 minutes', 'INFO', 'backend.pubnub', 'PubNub connection established', '{"channel": "smart-home-sensors"}'),
    (NOW() - INTERVAL '50 minutes', 'INFO', 'raspberry_pi.sensors', 'DHT22 sensor initialised', '{"gpio_pin": 4}'),
    (NOW() - INTERVAL '45 minutes', 'INFO', 'raspberry_pi. sensors', 'LDR sensor initialised', '{"gpio_pin": 17}'),
    (NOW() - INTERVAL '40 minutes', 'INFO', 'raspberry_pi.sensors', 'PIR sensor initialised', '{"gpio_pin": 27}'),
    (NOW() - INTERVAL '35 minutes', 'WARNING', 'backend.alerts', 'Temperature threshold exceeded', '{"sensor":  "temperature", "value": 31.5, "threshold": 30.0}'),
    (NOW() - INTERVAL '10 minutes', 'INFO', 'frontend.dashboard', 'User accessed dashboard', '{"ip": "192.168.1.100"}');

-- ====================================================================
-- REFRESH CONTINUOUS AGGREGATES
-- ====================================================================

-- Manually refresh aggregates to include seeded data
CALL refresh_continuous_aggregate('sensor_readings_5min', NOW() - INTERVAL '25 hours', NOW());
CALL refresh_continuous_aggregate('sensor_readings_hourly', NOW() - INTERVAL '25 hours', NOW());
CALL refresh_continuous_aggregate('sensor_readings_daily', NOW() - INTERVAL '2 days', NOW());

-- ====================================================================
-- VERIFICATION QUERIES
-- ====================================================================

DO $$
DECLARE
    sensor_count BIGINT;
    alert_count BIGINT;
    device_count BIGINT;
    log_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO sensor_count FROM sensor_readings;
    SELECT COUNT(*) INTO alert_count FROM alerts;
    SELECT COUNT(*) INTO device_count FROM device_states;
    SELECT COUNT(*) INTO log_count FROM system_logs;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database Seeding Completed';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sensor readings inserted: %', sensor_count;
    RAISE NOTICE 'Alerts inserted: %', alert_count;
    RAISE NOTICE 'Devices initialised: %', device_count;
    RAISE NOTICE 'System logs inserted: %', log_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sample Queries:';
    RAISE NOTICE '  SELECT * FROM latest_sensor_readings;';
    RAISE NOTICE '  SELECT * FROM current_system_status;';
    RAISE NOTICE '  SELECT * FROM alert_summary;';
    RAISE NOTICE '========================================';
END $$;