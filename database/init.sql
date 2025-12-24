-- ====================================================================
-- SMART HOME IOT - DATABASE INITIALISATION SCRIPT
-- ====================================================================
-- Description: Creates tables, hypertables, indices, and functions
--              for the Smart Home IoT monitoring system
-- Database: PostgreSQL 16 + TimescaleDB 2.14+
-- Author: Henrique Joanoni
-- ====================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ====================================================================
-- TABLE: sensor_readings
-- Purpose: Stores all sensor data in time-series format
-- ====================================================================
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sensor_type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    location VARCHAR(100) DEFAULT 'living_room',
    device_id VARCHAR(100) DEFAULT 'raspberry_pi_main',
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable (TimescaleDB magic)
SELECT create_hypertable(
    'sensor_readings', 
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Create indices for optimised queries
CREATE INDEX IF NOT EXISTS idx_sensor_type_timestamp 
    ON sensor_readings (sensor_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_location_timestamp 
    ON sensor_readings (location, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_device_timestamp 
    ON sensor_readings (device_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_metadata_gin 
    ON sensor_readings USING GIN (metadata);

-- Add retention policy (optional:  keep data for 90 days)
SELECT add_retention_policy(
    'sensor_readings', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Add compression policy (compress chunks older than 7 days)
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_type,location'
);

SELECT add_compression_policy(
    'sensor_readings', 
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ====================================================================
-- TABLE: alerts
-- Purpose: Stores system alerts and warnings
-- ====================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    title VARCHAR(200) NOT NULL,
    message TEXT,
    sensor_type VARCHAR(50),
    sensor_value NUMERIC(10, 2),
    threshold_value NUMERIC(10, 2),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indices for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
    ON alerts (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_severity 
    ON alerts (severity, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_resolved 
    ON alerts (resolved, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_type 
    ON alerts (alert_type, timestamp DESC);

-- ====================================================================
-- TABLE: device_states
-- Purpose: Stores current state of actuators (LEDs, buzzer)
-- ====================================================================
CREATE TABLE IF NOT EXISTS device_states (
    id SERIAL PRIMARY KEY,
    device_name VARCHAR(50) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL,
    state VARCHAR(20) NOT NULL,
    value JSONB DEFAULT '{}',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    updated_by VARCHAR(100) DEFAULT 'system',
    metadata JSONB DEFAULT '{}'
);

-- Index for device states
CREATE INDEX IF NOT EXISTS idx_device_type 
    ON device_states (device_type);

-- ====================================================================
-- TABLE: device_history
-- Purpose: Audit trail for device state changes
-- ====================================================================
CREATE TABLE IF NOT EXISTS device_history (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_name VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    previous_state VARCHAR(20),
    new_state VARCHAR(20) NOT NULL,
    value JSONB DEFAULT '{}',
    changed_by VARCHAR(100) DEFAULT 'system',
    reason TEXT,
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable(
    'device_history', 
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '7 days'
);

-- Index for device history
CREATE INDEX IF NOT EXISTS idx_device_history_name 
    ON device_history (device_name, timestamp DESC);

-- ====================================================================
-- TABLE: system_logs
-- Purpose: Application logs and events
-- ====================================================================
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    log_level VARCHAR(20) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable(
    'system_logs', 
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Indices for system logs
CREATE INDEX IF NOT EXISTS idx_logs_level 
    ON system_logs (log_level, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_logs_source 
    ON system_logs (source, timestamp DESC);

-- Retention policy for logs (keep for 30 days)
SELECT add_retention_policy(
    'system_logs', 
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ====================================================================
-- CONTINUOUS AGGREGATES (Materialised Views)
-- Purpose: Pre-computed statistics for faster queries
-- ====================================================================

-- Aggregate:  Sensor data by 5 minutes
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', timestamp) AS bucket,
    sensor_type,
    location,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, sensor_type, location
WITH NO DATA;

-- Refresh policy for 5-minute aggregate
SELECT add_continuous_aggregate_policy(
    'sensor_readings_5min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes',
    if_not_exists => TRUE
);

-- Aggregate: Sensor data by 1 hour
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    sensor_type,
    location,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, sensor_type, location
WITH NO DATA;

-- Refresh policy for hourly aggregate
SELECT add_continuous_aggregate_policy(
    'sensor_readings_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Aggregate: Sensor data by 1 day
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_daily
WITH (timescaledb. continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    sensor_type,
    location,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, sensor_type, location
WITH NO DATA;

-- Refresh policy for daily aggregate
SELECT add_continuous_aggregate_policy(
    'sensor_readings_daily',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ====================================================================
-- FUNCTIONS
-- ====================================================================

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger:  Auto-update alerts. updated_at
CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Log device state changes to history
CREATE OR REPLACE FUNCTION log_device_state_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO device_history (
        timestamp,
        device_name,
        device_type,
        previous_state,
        new_state,
        value,
        changed_by,
        reason
    ) VALUES (
        NOW(),
        NEW.device_name,
        NEW.device_type,
        OLD.state,
        NEW. state,
        NEW.value,
        NEW.updated_by,
        'State changed'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-log device state changes
CREATE TRIGGER log_device_changes
    AFTER UPDATE ON device_states
    FOR EACH ROW
    WHEN (OLD.state IS DISTINCT FROM NEW.state)
    EXECUTE FUNCTION log_device_state_change();

-- Function: Get latest sensor reading by type
CREATE OR REPLACE FUNCTION get_latest_sensor_reading(
    p_sensor_type VARCHAR,
    p_location VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    timestamp TIMESTAMPTZ,
    sensor_type VARCHAR,
    value NUMERIC,
    unit VARCHAR,
    location VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.timestamp,
        sr.sensor_type,
        sr.value,
        sr.unit,
        sr.location
    FROM sensor_readings sr
    WHERE sr.sensor_type = p_sensor_type
        AND (p_location IS NULL OR sr. location = p_location)
    ORDER BY sr.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Get sensor statistics for time range
CREATE OR REPLACE FUNCTION get_sensor_stats(
    p_sensor_type VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ DEFAULT NOW(),
    p_location VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    sensor_type VARCHAR,
    avg_value NUMERIC,
    min_value NUMERIC,
    max_value NUMERIC,
    stddev_value NUMERIC,
    reading_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.sensor_type,
        ROUND(AVG(sr.value)::NUMERIC, 2) AS avg_value,
        ROUND(MIN(sr.value)::NUMERIC, 2) AS min_value,
        ROUND(MAX(sr.value)::NUMERIC, 2) AS max_value,
        ROUND(STDDEV(sr.value)::NUMERIC, 2) AS stddev_value,
        COUNT(*):: BIGINT AS reading_count
    FROM sensor_readings sr
    WHERE sr.sensor_type = p_sensor_type
        AND sr.timestamp >= p_start_time
        AND sr.timestamp <= p_end_time
        AND (p_location IS NULL OR sr. location = p_location)
    GROUP BY sr.sensor_type;
END;
$$ LANGUAGE plpgsql;

-- Function: Count unresolved alerts
CREATE OR REPLACE FUNCTION count_unresolved_alerts()
RETURNS TABLE (
    severity VARCHAR,
    alert_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.severity,
        COUNT(*):: BIGINT
    FROM alerts a
    WHERE a.resolved = FALSE
    GROUP BY a.severity
    ORDER BY 
        CASE a.severity
            WHEN 'critical' THEN 1
            WHEN 'warning' THEN 2
            WHEN 'info' THEN 3
        END;
END;
$$ LANGUAGE plpgsql;

-- ====================================================================
-- VIEWS
-- ====================================================================

-- View: Current device states with last reading time
CREATE OR REPLACE VIEW current_system_status AS
SELECT 
    ds. device_name,
    ds. device_type,
    ds. state,
    ds.value,
    ds.last_updated,
    (SELECT COUNT(*) FROM alerts WHERE resolved = FALSE) AS unresolved_alerts
FROM device_states ds
ORDER BY ds.device_type, ds.device_name;

-- View: Latest sensor readings (one per type)
CREATE OR REPLACE VIEW latest_sensor_readings AS
SELECT DISTINCT ON (sensor_type)
    timestamp,
    sensor_type,
    value,
    unit,
    location,
    device_id
FROM sensor_readings
ORDER BY sensor_type, timestamp DESC;

-- View: Alert summary
CREATE OR REPLACE VIEW alert_summary AS
SELECT 
    DATE_TRUNC('day', timestamp) AS alert_date,
    severity,
    alert_type,
    COUNT(*) AS alert_count,
    COUNT(*) FILTER (WHERE resolved = TRUE) AS resolved_count,
    COUNT(*) FILTER (WHERE resolved = FALSE) AS unresolved_count
FROM alerts
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', timestamp), severity, alert_type
ORDER BY alert_date DESC, severity;

-- ====================================================================
-- GRANTS (Security)
-- ====================================================================

-- Grant permissions to iot_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER};
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ${POSTGRES_USER};

-- ====================================================================
-- COMMENTS (Documentation)
-- ====================================================================

COMMENT ON TABLE sensor_readings IS 'Time-series data from all IoT sensors';
COMMENT ON TABLE alerts IS 'System alerts and warnings triggered by threshold violations';
COMMENT ON TABLE device_states IS 'Current state of all controllable devices (actuators)';
COMMENT ON TABLE device_history IS 'Audit trail of all device state changes';
COMMENT ON TABLE system_logs IS 'Application logs and system events';

COMMENT ON MATERIALIZED VIEW sensor_readings_5min IS 'Pre-aggregated sensor data in 5-minute intervals';
COMMENT ON MATERIALIZED VIEW sensor_readings_hourly IS 'Pre-aggregated sensor data in hourly intervals';
COMMENT ON MATERIALIZED VIEW sensor_readings_daily IS 'Pre-aggregated sensor data in daily intervals';

-- ====================================================================
-- COMPLETION MESSAGE
-- ====================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Smart Home IoT Database Initialised';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created:  5';
    RAISE NOTICE 'Hypertables:  3';
    RAISE NOTICE 'Continuous aggregates: 3';
    RAISE NOTICE 'Functions: 4';
    RAISE NOTICE 'Views: 3';
    RAISE NOTICE '========================================';
END $$;