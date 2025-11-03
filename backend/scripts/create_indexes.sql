-- Seoul Location Services - Database Indexes
-- 생성일: 2025-11-03
-- 용도: 공간 검색 및 정렬 성능 최적화

-- Cultural Events
CREATE INDEX IF NOT EXISTS idx_cultural_events_coords ON cultural_events (lat, lot);
CREATE INDEX IF NOT EXISTS idx_cultural_events_created_at ON cultural_events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cultural_events_strtdate ON cultural_events (strtdate);

-- Libraries
CREATE INDEX IF NOT EXISTS idx_libraries_coords ON libraries (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_libraries_created_at ON libraries (created_at DESC);

-- Cultural Spaces
CREATE INDEX IF NOT EXISTS idx_cultural_spaces_coords ON cultural_spaces (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_cultural_spaces_created_at ON cultural_spaces (created_at DESC);

-- Future Heritages
CREATE INDEX IF NOT EXISTS idx_future_heritages_coords ON future_heritages (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_future_heritages_created_at ON future_heritages (created_at DESC);

-- Public Reservations
CREATE INDEX IF NOT EXISTS idx_public_reservations_coords ON public_reservations (y_coord, x_coord);
CREATE INDEX IF NOT EXISTS idx_public_reservations_created_at ON public_reservations (created_at DESC);
