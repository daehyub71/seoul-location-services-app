-- Seoul Location Services App - Supabase Database Schema
-- This script creates all necessary tables, indexes, and extensions

-- ============================================================================
-- 1. Enable PostGIS Extension (for geospatial queries)
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- 2. Cultural Events Table (문화행사 정보)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cultural_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    codename VARCHAR(100),
    guname VARCHAR(50),
    place VARCHAR(300),
    org_name VARCHAR(200),
    use_trgt VARCHAR(200),
    use_fee VARCHAR(100),
    player VARCHAR(300),
    program VARCHAR(1000),
    etc_desc TEXT,
    org_link TEXT,
    main_img TEXT,
    rgstdate DATE,
    ticket VARCHAR(200),
    strtdate DATE,
    end_date DATE,
    themecode VARCHAR(100),
    lot DECIMAL(11, 8),  -- Longitude (경도)
    lat DECIMAL(10, 8),  -- Latitude (위도)
    is_free VARCHAR(10),
    hmpg_addr TEXT,

    -- PostGIS geometry column for spatial queries
    location GEOGRAPHY(POINT, 4326),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'culturalEventInfo',

    -- Constraints
    CONSTRAINT check_coordinates_events CHECK (
        lat BETWEEN 37.0 AND 38.0 AND
        lot BETWEEN 126.0 AND 128.0
    )
);

-- Create spatial index for fast proximity queries
CREATE INDEX IF NOT EXISTS idx_cultural_events_location
ON cultural_events USING GIST(location);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_cultural_events_dates
ON cultural_events(strtdate, end_date);

CREATE INDEX IF NOT EXISTS idx_cultural_events_guname
ON cultural_events(guname);

CREATE INDEX IF NOT EXISTS idx_cultural_events_updated
ON cultural_events(updated_at);

-- Trigger to auto-update location from lat/lot
CREATE OR REPLACE FUNCTION update_cultural_events_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lat IS NOT NULL AND NEW.lot IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.lot, NEW.lat), 4326)::geography;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cultural_events_location
BEFORE INSERT OR UPDATE ON cultural_events
FOR EACH ROW EXECUTE FUNCTION update_cultural_events_location();

-- ============================================================================
-- 3. Libraries Table (도서관 정보: 공공 + 장애인)
-- ============================================================================
CREATE TABLE IF NOT EXISTS libraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    library_name VARCHAR(300) NOT NULL,
    library_type VARCHAR(50) NOT NULL,  -- 'public' or 'disabled'
    guname VARCHAR(50),
    address VARCHAR(500),
    tel VARCHAR(50),
    homepage TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    opertime VARCHAR(200),
    closing_day VARCHAR(100),
    book_count INTEGER,
    seat_count INTEGER,
    facilities TEXT,

    -- PostGIS geometry column
    location GEOGRAPHY(POINT, 4326),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50),

    CONSTRAINT check_coordinates_libraries CHECK (
        latitude BETWEEN 37.0 AND 38.0 AND
        longitude BETWEEN 126.0 AND 128.0
    )
);

CREATE INDEX IF NOT EXISTS idx_libraries_location
ON libraries USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_libraries_type
ON libraries(library_type);

CREATE INDEX IF NOT EXISTS idx_libraries_guname
ON libraries(guname);

-- Trigger to auto-update location
CREATE OR REPLACE FUNCTION update_libraries_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_libraries_location
BEFORE INSERT OR UPDATE ON libraries
FOR EACH ROW EXECUTE FUNCTION update_libraries_location();

-- ============================================================================
-- 4. Cultural Spaces Table (문화공간 정보)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cultural_spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    fac_name VARCHAR(300) NOT NULL,
    guname VARCHAR(50),
    subjcode VARCHAR(100),
    fac_code VARCHAR(50),
    codename VARCHAR(100),
    addr VARCHAR(500),
    zipcode VARCHAR(20),
    telno VARCHAR(50),
    homepage TEXT,
    restroomyn VARCHAR(10),
    parking_info VARCHAR(200),
    main_purps TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- PostGIS geometry column
    location GEOGRAPHY(POINT, 4326),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'culturalSpaceInfo',

    CONSTRAINT check_coordinates_spaces CHECK (
        latitude BETWEEN 37.0 AND 38.0 AND
        longitude BETWEEN 126.0 AND 128.0
    )
);

CREATE INDEX IF NOT EXISTS idx_cultural_spaces_location
ON cultural_spaces USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_cultural_spaces_subjcode
ON cultural_spaces(subjcode);

CREATE INDEX IF NOT EXISTS idx_cultural_spaces_guname
ON cultural_spaces(guname);

-- Trigger to auto-update location
CREATE OR REPLACE FUNCTION update_cultural_spaces_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cultural_spaces_location
BEFORE INSERT OR UPDATE ON cultural_spaces
FOR EACH ROW EXECUTE FUNCTION update_cultural_spaces_location();

-- ============================================================================
-- 5. Public Reservations Table (공공예약 서비스 통합)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    service_type VARCHAR(50) NOT NULL,  -- 'medical', 'education', 'culture', 'general'
    svcid VARCHAR(50),
    maxclassnm VARCHAR(100),
    minclassnm VARCHAR(100),
    svcstatnm VARCHAR(50),
    svcnm VARCHAR(500) NOT NULL,
    payatnm VARCHAR(50),
    placenm VARCHAR(300),
    usetgtinfo VARCHAR(200),
    svcurl TEXT,
    x_coord DECIMAL(11, 8),  -- X (Longitude)
    y_coord DECIMAL(10, 8),  -- Y (Latitude)
    svcopnbgndt DATE,
    svcopnenddt DATE,
    rcptbgndt TIMESTAMPTZ,
    rcptenddt TIMESTAMPTZ,
    areanm VARCHAR(100),
    imgurl TEXT,
    dtlcont TEXT,
    telno VARCHAR(50),
    v_max INTEGER,
    v_min INTEGER,
    revstddaynm VARCHAR(100),
    revstdday INTEGER,

    -- PostGIS geometry column
    location GEOGRAPHY(POINT, 4326),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50),

    CONSTRAINT check_coordinates_reservations CHECK (
        y_coord BETWEEN 37.0 AND 38.0 AND
        x_coord BETWEEN 126.0 AND 128.0
    )
);

CREATE INDEX IF NOT EXISTS idx_public_reservations_location
ON public_reservations USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_public_reservations_type
ON public_reservations(service_type);

CREATE INDEX IF NOT EXISTS idx_public_reservations_status
ON public_reservations(svcstatnm);

CREATE INDEX IF NOT EXISTS idx_public_reservations_dates
ON public_reservations(svcopnbgndt, svcopnenddt);

CREATE INDEX IF NOT EXISTS idx_public_reservations_area
ON public_reservations(areanm);

-- Trigger to auto-update location
CREATE OR REPLACE FUNCTION update_public_reservations_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.y_coord IS NOT NULL AND NEW.x_coord IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.x_coord, NEW.y_coord), 4326)::geography;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_public_reservations_location
BEFORE INSERT OR UPDATE ON public_reservations
FOR EACH ROW EXECUTE FUNCTION update_public_reservations_location();

-- ============================================================================
-- 6. Future Heritages Table (서울미래유산)
-- ============================================================================
CREATE TABLE IF NOT EXISTS future_heritages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    no INTEGER,
    main_category VARCHAR(100),
    sub_category VARCHAR(100),
    name VARCHAR(300) NOT NULL,
    year_designated INTEGER,
    gu_name VARCHAR(50),
    dong_name VARCHAR(100),
    address VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    description TEXT,
    reason TEXT,
    main_img TEXT,

    -- PostGIS geometry column
    location GEOGRAPHY(POINT, 4326),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'futureHeritageInfo',

    CONSTRAINT check_coordinates_heritages CHECK (
        latitude BETWEEN 37.0 AND 38.0 AND
        longitude BETWEEN 126.0 AND 128.0
    )
);

CREATE INDEX IF NOT EXISTS idx_future_heritages_location
ON future_heritages USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_future_heritages_category
ON future_heritages(main_category, sub_category);

CREATE INDEX IF NOT EXISTS idx_future_heritages_gu
ON future_heritages(gu_name);

-- Trigger to auto-update location
CREATE OR REPLACE FUNCTION update_future_heritages_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_future_heritages_location
BEFORE INSERT OR UPDATE ON future_heritages
FOR EACH ROW EXECUTE FUNCTION update_future_heritages_location();

-- ============================================================================
-- 7. Collection Logs Table (데이터 수집 로그)
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_endpoint VARCHAR(100) NOT NULL,
    collection_status VARCHAR(50) NOT NULL,  -- 'success', 'partial', 'failed'
    total_records INTEGER DEFAULT 0,
    new_records INTEGER DEFAULT 0,
    updated_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_collection_logs_endpoint
ON collection_logs(api_endpoint);

CREATE INDEX IF NOT EXISTS idx_collection_logs_status
ON collection_logs(collection_status);

CREATE INDEX IF NOT EXISTS idx_collection_logs_created
ON collection_logs(created_at DESC);

-- ============================================================================
-- 8. Helper Functions
-- ============================================================================

-- Function to calculate distance between two points (in meters)
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DECIMAL,
    lon1 DECIMAL,
    lat2 DECIMAL,
    lon2 DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_SetSRID(ST_MakePoint(lon1, lat1), 4326)::geography,
        ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)::geography
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get services within radius (meters)
CREATE OR REPLACE FUNCTION get_services_within_radius(
    center_lat DECIMAL,
    center_lon DECIMAL,
    radius_meters INTEGER DEFAULT 2000
)
RETURNS TABLE (
    category VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    distance_meters DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'events'::VARCHAR, id, title,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography)
    FROM cultural_events
    WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography, radius_meters)

    UNION ALL

    SELECT 'libraries'::VARCHAR, id, library_name,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography)
    FROM libraries
    WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography, radius_meters)

    UNION ALL

    SELECT 'spaces'::VARCHAR, id, fac_name,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography)
    FROM cultural_spaces
    WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography, radius_meters)

    UNION ALL

    SELECT 'reservations'::VARCHAR, id, svcnm,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography)
    FROM public_reservations
    WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography, radius_meters)

    UNION ALL

    SELECT 'heritages'::VARCHAR, id, name,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography)
    FROM future_heritages
    WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography, radius_meters)

    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. Row Level Security (RLS) - Optional for production
-- ============================================================================

-- Enable RLS on all tables (uncomment for production)
-- ALTER TABLE cultural_events ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE libraries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cultural_spaces ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public_reservations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE future_heritages ENABLE ROW LEVEL SECURITY;

-- Create policies (read-only for anon users)
-- CREATE POLICY "Allow public read access on cultural_events"
-- ON cultural_events FOR SELECT
-- USING (true);

-- (Repeat for other tables as needed)

-- ============================================================================
-- 10. Sample Queries for Testing
-- ============================================================================

-- Example 1: Find all services within 2km of Seoul City Hall (37.5665, 126.9780)
-- SELECT * FROM get_services_within_radius(37.5665, 126.9780, 2000);

-- Example 2: Count services by category
-- SELECT
--     'events' as category, COUNT(*) FROM cultural_events
-- UNION ALL
-- SELECT 'libraries', COUNT(*) FROM libraries
-- UNION ALL
-- SELECT 'spaces', COUNT(*) FROM cultural_spaces
-- UNION ALL
-- SELECT 'reservations', COUNT(*) FROM public_reservations
-- UNION ALL
-- SELECT 'heritages', COUNT(*) FROM future_heritages;

-- Example 3: Find libraries within 1km and sort by distance
-- SELECT
--     library_name,
--     address,
--     ST_Distance(
--         location,
--         ST_SetSRID(ST_MakePoint(126.9780, 37.5665), 4326)::geography
--     ) as distance_meters
-- FROM libraries
-- WHERE ST_DWithin(
--     location,
--     ST_SetSRID(ST_MakePoint(126.9780, 37.5665), 4326)::geography,
--     1000
-- )
-- ORDER BY distance_meters;

-- ============================================================================
-- End of Schema
-- ============================================================================
