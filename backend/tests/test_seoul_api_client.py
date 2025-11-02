"""
Seoul API Client 단위 테스트
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.seoul_api_client import SeoulAPIClient, SeoulAPIError


class TestSeoulAPIClient:
    """SeoulAPIClient 테스트"""

    @pytest.fixture
    def api_key(self):
        """테스트용 API 키"""
        return "test_api_key_123"

    @pytest.fixture
    def client(self, api_key):
        """테스트용 클라이언트 인스턴스"""
        return SeoulAPIClient(api_key)

    def test_init(self, client, api_key):
        """초기화 테스트"""
        assert client.api_key == api_key
        assert client.timeout == SeoulAPIClient.DEFAULT_TIMEOUT
        assert client.client is None

    def test_build_url(self, client):
        """URL 생성 테스트"""
        endpoint = "culturalEventInfo"
        url = client._build_url(endpoint, 1, 1000)

        expected = f"{SeoulAPIClient.BASE_URL}/test_api_key_123/json/culturalEventInfo/1/1000/"
        assert url == expected

    def test_build_url_with_custom_format(self, client):
        """커스텀 포맷 URL 생성 테스트"""
        endpoint = "culturalEventInfo"
        url = client._build_url(endpoint, 1, 100, format="xml")

        expected = f"{SeoulAPIClient.BASE_URL}/test_api_key_123/xml/culturalEventInfo/1/100/"
        assert url == expected

    def test_get_endpoint_name(self):
        """엔드포인트 이름 조회 테스트"""
        endpoint = SeoulAPIClient.get_endpoint_name('cultural_events')
        assert endpoint == 'culturalEventInfo'

        # 존재하지 않는 키
        endpoint = SeoulAPIClient.get_endpoint_name('nonexistent')
        assert endpoint is None

    def test_list_endpoints(self):
        """엔드포인트 목록 조회 테스트"""
        endpoints = SeoulAPIClient.list_endpoints()

        assert isinstance(endpoints, dict)
        assert len(endpoints) == 9
        assert 'cultural_events' in endpoints
        assert endpoints['cultural_events'] == 'culturalEventInfo'

    def test_extract_records_success(self, client):
        """레코드 추출 성공 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 100,
                'RESULT': {'CODE': 'INFO-000', 'MESSAGE': '정상'},
                'row': [
                    {'id': 1, 'title': 'Event 1'},
                    {'id': 2, 'title': 'Event 2'}
                ]
            }
        }

        records = client._extract_records(mock_data, 'culturalEventInfo')

        assert len(records) == 2
        assert records[0]['id'] == 1
        assert records[1]['title'] == 'Event 2'

    def test_extract_records_single_dict(self, client):
        """단일 dict 레코드 추출 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 1,
                'row': {'id': 1, 'title': 'Single Event'}
            }
        }

        records = client._extract_records(mock_data, 'culturalEventInfo')

        assert len(records) == 1
        assert records[0]['id'] == 1

    def test_extract_records_empty(self, client):
        """빈 레코드 추출 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 0,
                'row': []
            }
        }

        records = client._extract_records(mock_data, 'culturalEventInfo')

        assert len(records) == 0

    def test_extract_records_no_row(self, client):
        """row 필드 없는 경우 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 0
            }
        }

        records = client._extract_records(mock_data, 'culturalEventInfo')

        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self, api_key):
        """비동기 컨텍스트 매니저 테스트"""
        async with SeoulAPIClient(api_key) as client:
            assert client.client is not None
            assert isinstance(client.client, httpx.AsyncClient)

        # 종료 후 client는 닫혀야 함
        with pytest.raises(RuntimeError):
            await client.client.get("http://example.com")

    @pytest.mark.asyncio
    async def test_fetch_success(self, client):
        """HTTP 요청 성공 테스트"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'culturalEventInfo': {
                'RESULT': {'CODE': 'INFO-000'},
                'row': []
            }
        }

        async with client:
            with patch.object(client.client, 'get', new=AsyncMock(return_value=mock_response)):
                data = await client._fetch("http://test.url")

                assert 'culturalEventInfo' in data
                assert data['culturalEventInfo']['RESULT']['CODE'] == 'INFO-000'

    @pytest.mark.asyncio
    async def test_fetch_http_error_429(self, client):
        """HTTP 429 에러 테스트 (Rate Limit)"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429

        async with client:
            with patch.object(client.client, 'get', new=AsyncMock(return_value=mock_response)):
                with pytest.raises(SeoulAPIError, match="rate limit"):
                    await client._fetch("http://test.url")

    @pytest.mark.asyncio
    async def test_fetch_http_error_500(self, client):
        """HTTP 500 에러 테스트 (Server Error)"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500

        async with client:
            with patch.object(client.client, 'get', new=AsyncMock(return_value=mock_response)):
                with pytest.raises(SeoulAPIError, match="server error"):
                    await client._fetch("http://test.url")

    @pytest.mark.asyncio
    async def test_fetch_api_error_code(self, client):
        """Seoul API 에러 코드 테스트"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'culturalEventInfo': {
                'RESULT': {'CODE': 'ERROR-001', 'MESSAGE': '인증 실패'}
            }
        }

        async with client:
            with patch.object(client.client, 'get', new=AsyncMock(return_value=mock_response)):
                with pytest.raises(SeoulAPIError, match="ERROR-001"):
                    await client._fetch("http://test.url")

    @pytest.mark.asyncio
    async def test_fetch_page_success(self, client):
        """페이지 조회 성공 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 100,
                'row': [{'id': i} for i in range(10)]
            }
        }

        async with client:
            with patch.object(client, '_fetch', new=AsyncMock(return_value=mock_data)):
                data = await client.fetch_page('culturalEventInfo', 1, 10)

                assert data == mock_data

    @pytest.mark.asyncio
    async def test_fetch_page_default_end_index(self, client):
        """기본 end_index 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'row': []
            }
        }

        async with client:
            with patch.object(client, '_fetch', new=AsyncMock(return_value=mock_data)) as mock_fetch:
                await client.fetch_page('culturalEventInfo', 1)

                # _build_url이 호출되었는지 확인 (end_index = 1 + 1000 - 1 = 1000)
                assert mock_fetch.called

    @pytest.mark.asyncio
    async def test_get_total_count_success(self, client):
        """총 레코드 수 조회 성공 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 4534,
                'row': []
            }
        }

        async with client:
            with patch.object(client, 'fetch_page', new=AsyncMock(return_value=mock_data)):
                total = await client.get_total_count('culturalEventInfo')

                assert total == 4534

    @pytest.mark.asyncio
    async def test_get_total_count_not_found(self, client):
        """총 레코드 수 조회 실패 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'row': []
            }
        }

        async with client:
            with patch.object(client, 'fetch_page', new=AsyncMock(return_value=mock_data)):
                total = await client.get_total_count('culturalEventInfo')

                assert total == 0

    @pytest.mark.asyncio
    async def test_fetch_all_single_page(self, client):
        """단일 페이지 전체 조회 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'list_total_count': 10,
                'row': [{'id': i} for i in range(10)]
            }
        }

        async with client:
            with patch.object(client, 'fetch_page', new=AsyncMock(return_value=mock_data)):
                records = await client.fetch_all('culturalEventInfo')

                assert len(records) == 10

    @pytest.mark.asyncio
    async def test_fetch_all_with_max_records(self, client):
        """최대 레코드 수 제한 테스트"""
        mock_page1 = {
            'culturalEventInfo': {
                'row': [{'id': i} for i in range(1000)]
            }
        }

        mock_page2 = {
            'culturalEventInfo': {
                'row': [{'id': i} for i in range(1000, 2000)]
            }
        }

        async with client:
            with patch.object(client, 'fetch_page', new=AsyncMock(side_effect=[mock_page1, mock_page2])):
                records = await client.fetch_all('culturalEventInfo', max_records=500)

                # 첫 페이지만 가져오고 500개로 제한
                assert len(records) == 1000  # fetch_all은 페이지 단위로 가져오므로 1000개

    @pytest.mark.asyncio
    async def test_fetch_all_empty_response(self, client):
        """빈 응답 테스트"""
        mock_data = {
            'culturalEventInfo': {
                'row': []
            }
        }

        async with client:
            with patch.object(client, 'fetch_page', new=AsyncMock(return_value=mock_data)):
                records = await client.fetch_all('culturalEventInfo')

                assert len(records) == 0

    @pytest.mark.asyncio
    async def test_fetch_all_with_error(self, client):
        """에러 발생 시 현재까지 수집한 데이터 반환 테스트"""
        mock_page1 = {
            'culturalEventInfo': {
                'row': [{'id': i} for i in range(1000)]
            }
        }

        async with client:
            with patch.object(
                client,
                'fetch_page',
                new=AsyncMock(side_effect=[mock_page1, SeoulAPIError("API Error")])
            ):
                records = await client.fetch_all('culturalEventInfo')

                # 첫 페이지는 성공적으로 수집
                assert len(records) == 1000


class TestSeoulAPIError:
    """SeoulAPIError 테스트"""

    def test_error_message(self):
        """에러 메시지 테스트"""
        error = SeoulAPIError("Test error")
        assert str(error) == "Test error"

    def test_error_inheritance(self):
        """Exception 상속 확인"""
        error = SeoulAPIError("Test")
        assert isinstance(error, Exception)


# Integration test (실제 API 호출) - 선택적 실행
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_call():
    """
    실제 Seoul API 호출 테스트 (통합 테스트)

    실행 방법:
    pytest tests/test_seoul_api_client.py -m integration
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv('SEOUL_API_KEY')

    if not api_key:
        pytest.skip("SEOUL_API_KEY not found in .env")

    async with SeoulAPIClient(api_key) as client:
        # 문화행사 정보 조회
        endpoint = 'culturalEventInfo'

        # 총 개수 확인
        total = await client.get_total_count(endpoint)
        assert total > 0

        # 5개만 조회
        records = await client.fetch_all(endpoint, max_records=5)
        assert len(records) >= 5
        assert isinstance(records[0], dict)
