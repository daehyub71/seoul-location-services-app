"""
Unit tests for LocationAnalyzer Agent
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.core.agents.location_analyzer import (
    LocationAnalyzer,
    analyze_location,
    create_location_query
)
from app.core.workflow.state import LocationQuery, AnalyzedLocation


class TestLocationAnalyzer:
    """LocationAnalyzer 에이전트 테스트"""

    @pytest.fixture
    def analyzer(self):
        """LocationAnalyzer 인스턴스"""
        return LocationAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_coordinates_valid(self, analyzer):
        """유효한 좌표 입력 테스트"""
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=1000
        )

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = "서울특별시 중구 세종대로 110"

            result = await analyzer.analyze(query)

            assert result is not None
            assert result.latitude == 37.5665
            assert result.longitude == 126.9780
            assert result.radius == 1000
            assert result.source == "coordinates"
            assert result.confidence == 1.0
            assert result.address == "서울특별시 중구 세종대로 110"

    @pytest.mark.asyncio
    async def test_analyze_coordinates_normalization(self, analyzer):
        """좌표 정규화 테스트 (소수점 6자리)"""
        query = LocationQuery(
            latitude=37.56656789,
            longitude=126.97801234,
            radius=2000
        )

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = None

            result = await analyzer.analyze(query)

            assert result is not None
            assert result.latitude == 37.566568  # 6자리로 반올림
            assert result.longitude == 126.978012  # 6자리로 반올림

    @pytest.mark.asyncio
    async def test_analyze_address_success(self, analyzer):
        """주소 입력 성공 테스트"""
        query = LocationQuery(
            address="서울시청",
            radius=1500
        )

        with patch.object(analyzer.kakao_service, 'address_to_coordinates', new_callable=AsyncMock) as mock_geo:
            mock_geo.return_value = (37.5665, 126.9780)

            result = await analyzer.analyze(query)

            assert result is not None
            assert result.latitude == 37.5665
            assert result.longitude == 126.9780
            assert result.address == "서울시청"
            assert result.radius == 1500
            assert result.source == "address"
            assert result.confidence == 0.9  # 주소 변환은 낮은 신뢰도

    @pytest.mark.asyncio
    async def test_analyze_address_keyword_fallback(self, analyzer):
        """주소 검색 실패 시 키워드 검색 폴백"""
        query = LocationQuery(
            address="강남역",
            radius=2000
        )

        with patch.object(analyzer.kakao_service, 'address_to_coordinates', new_callable=AsyncMock) as mock_addr, \
             patch.object(analyzer.kakao_service, 'keyword_search', new_callable=AsyncMock) as mock_keyword:

            # 주소 검색 실패
            mock_addr.return_value = None
            # 키워드 검색 성공
            mock_keyword.return_value = (37.4979, 127.0276)

            result = await analyzer.analyze(query)

            assert result is not None
            assert result.latitude == 37.4979
            assert result.longitude == 127.0276
            assert result.address == "강남역"

    @pytest.mark.asyncio
    async def test_analyze_address_geocoding_failure(self, analyzer):
        """Geocoding 실패 테스트"""
        query = LocationQuery(
            address="존재하지않는주소",
            radius=1000
        )

        with patch.object(analyzer.kakao_service, 'address_to_coordinates', new_callable=AsyncMock) as mock_addr, \
             patch.object(analyzer.kakao_service, 'keyword_search', new_callable=AsyncMock) as mock_keyword:

            mock_addr.return_value = None
            mock_keyword.return_value = None

            result = await analyzer.analyze(query)

            assert result is None

    @pytest.mark.asyncio
    async def test_analyze_no_input(self, analyzer):
        """입력 없음 에러 테스트"""
        query = LocationQuery(radius=1000)

        result = await analyzer.analyze(query)

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_with_category(self, analyzer):
        """카테고리 지정 테스트"""
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=1000,
            category="libraries"
        )

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = None

            result = await analyzer.analyze(query)

            assert result is not None
            assert result.category == "libraries"

    def test_validate_location_valid(self, analyzer):
        """유효한 위치 검증"""
        location = AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            source="coordinates"
        )

        assert analyzer.validate_location(location) is True

    def test_validate_location_invalid_latitude(self, analyzer):
        """유효하지 않은 위도"""
        location = AnalyzedLocation(
            latitude=91.0,  # > 90
            longitude=126.9780,
            radius=2000,
            source="coordinates"
        )

        assert analyzer.validate_location(location) is False

    def test_validate_location_invalid_longitude(self, analyzer):
        """유효하지 않은 경도"""
        location = AnalyzedLocation(
            latitude=37.5665,
            longitude=-181.0,  # < -180
            radius=2000,
            source="coordinates"
        )

        assert analyzer.validate_location(location) is False

    def test_validate_location_radius_warning(self, analyzer):
        """반경 범위 경고 (차단하지 않음)"""
        location = AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            radius=50,  # < 100 (경고)
            source="coordinates"
        )

        # 경고만 발생, 유효성은 True
        assert analyzer.validate_location(location) is True

    @pytest.mark.asyncio
    async def test_analyze_batch(self, analyzer):
        """배치 분석 테스트"""
        queries = [
            LocationQuery(latitude=37.5665, longitude=126.9780, radius=1000),
            LocationQuery(latitude=37.4979, longitude=127.0276, radius=2000)
        ]

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = None

            results = await analyzer.analyze_batch(queries)

            assert len(results) == 2
            assert results[0] is not None
            assert results[1] is not None
            assert results[0].latitude == 37.5665
            assert results[1].latitude == 37.4979


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    @pytest.mark.asyncio
    async def test_analyze_location_coordinates(self):
        """analyze_location() 좌표 입력"""
        with patch('app.core.agents.location_analyzer.LocationAnalyzer.analyze', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                source="coordinates"
            )

            result = await analyze_location(latitude=37.5665, longitude=126.9780)

            assert result is not None
            assert result.latitude == 37.5665

    @pytest.mark.asyncio
    async def test_analyze_location_address(self):
        """analyze_location() 주소 입력"""
        with patch('app.core.agents.location_analyzer.LocationAnalyzer.analyze', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                address="서울시청",
                radius=2000,
                source="address"
            )

            result = await analyze_location(address="서울시청")

            assert result is not None
            assert result.address == "서울시청"

    def test_create_location_query(self):
        """create_location_query() 테스트"""
        query = create_location_query(
            latitude=37.5665,
            longitude=126.9780,
            radius=1500,
            category="libraries"
        )

        assert isinstance(query, LocationQuery)
        assert query.latitude == 37.5665
        assert query.longitude == 126.9780
        assert query.radius == 1500
        assert query.category == "libraries"

    def test_create_location_query_with_priority(self):
        """카테고리 우선순위 포함"""
        query = create_location_query(
            address="강남역",
            category_priority=["libraries", "cultural_spaces"]
        )

        assert query.address == "강남역"
        assert query.category_priority == ["libraries", "cultural_spaces"]


class TestSeoulBoundsValidation:
    """서울 경계 검증 테스트"""

    @pytest.fixture
    def analyzer(self):
        return LocationAnalyzer()

    @pytest.mark.asyncio
    async def test_coordinates_inside_seoul(self, analyzer):
        """서울 내부 좌표"""
        query = LocationQuery(
            latitude=37.5665,  # 서울시청
            longitude=126.9780,
            radius=1000
        )

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = "서울특별시"

            result = await analyzer.analyze(query)

            assert result is not None
            # 서울 내부이므로 정상 처리

    @pytest.mark.asyncio
    async def test_coordinates_outside_seoul(self, analyzer):
        """서울 외부 좌표 (경고만 발생)"""
        query = LocationQuery(
            latitude=35.1796,  # 부산
            longitude=129.0756,
            radius=1000
        )

        with patch.object(analyzer.kakao_service, 'reverse_geocode', new_callable=AsyncMock) as mock_reverse:
            mock_reverse.return_value = "부산광역시"

            result = await analyzer.analyze(query)

            # 서울 외부이지만 결과는 반환 (경고만)
            assert result is not None
            assert result.latitude == 35.1796


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
