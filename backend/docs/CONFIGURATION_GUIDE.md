# 환경 설정 가이드

## 1. Kakao Map API 설정

### 문제
```
Kakao API HTTP error: 403 - App(Seoul_NightSpots_Agent) disabled OPEN_MAP_AND_LOCAL service.
```

### 해결 방법

1. **Kakao Developers 콘솔 접속**
   - URL: https://developers.kakao.com/console/app
   - 로그인 후 앱 선택

2. **플랫폼 설정**
   - "플랫폼" 탭 클릭
   - "Web 플랫폼 등록" 클릭
   - 사이트 도메인 추가:
     ```
     http://localhost:8000
     http://localhost:8501
     http://127.0.0.1:8000
     http://127.0.0.1:8501
     ```

3. **서비스 활성화**
   - "제품 설정" > "Kakao 로그인" 클릭
   - "활성화 설정" ON
   - "OpenID Connect 활성화" (선택사항)

4. **Local API 활성화**
   - "제품 설정" > "지도/로컬" 클릭
   - "활성화 설정" ON
   - 사용할 API 체크:
     - ✅ 주소 검색
     - ✅ 좌표계 변환
     - ✅ 키워드로 장소 검색
     - ✅ 좌표로 주소 변환하기

5. **API 키 확인**
   - "앱 설정" > "앱 키" 클릭
   - **REST API 키** 복사
   - `.env` 파일에 추가:
     ```bash
     KAKAO_REST_API_KEY=your_rest_api_key_here
     ```

### 테스트

```bash
# API 키 테스트
curl -X GET "https://dapi.kakao.com/v2/local/search/keyword.json?query=카카오" \
  -H "Authorization: KakaoAK YOUR_API_KEY"
```

성공 시 200 OK 응답과 JSON 데이터 반환

---

## 2. Redis (Upstash) URL 설정

### 문제
```
Redis connection failed: Redis URL must specify one of the following schemes (redis://, rediss://, unix://).
```

### 원인
Upstash Redis URL이 HTTP/HTTPS 형식(`https://...`)인데, Redis 클라이언트는 `redis://` 또는 `rediss://` 스킴을 요구합니다.

### 해결 방법

#### 옵션 1: Upstash REST API 사용 (권장)

`.env` 파일 수정:
```bash
# Upstash에서 제공하는 REST API URL 사용
UPSTASH_URL=https://your-upstash-url.upstash.io
UPSTASH_TOKEN=your_upstash_token

# Redis URL을 REST API URL로 설정
REDIS_URL=https://your-upstash-url.upstash.io
```

`app/core/services/redis_service.py` 수정 필요 (HTTP 클라이언트 사용):
```python
import httpx

class RedisService:
    def __init__(self):
        self.base_url = settings.UPSTASH_URL
        self.token = settings.UPSTASH_TOKEN

    async def get(self, key: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/get/{key}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.json().get("result")
```

#### 옵션 2: Upstash Redis 호환 URL 사용

Upstash Console에서 Redis 호환 URL 확인:
```bash
# Upstash Dashboard > Database > Details
# "Redis Compatible Endpoint" 섹션 확인

REDIS_URL=rediss://default:YOUR_PASSWORD@your-endpoint.upstash.io:6379
```

`.env` 파일 예시:
```bash
# Option 1: REST API (권장)
UPSTASH_URL=https://charming-dane-12345.upstash.io
UPSTASH_TOKEN=AYN...xyz
REDIS_URL=https://charming-dane-12345.upstash.io

# Option 2: Redis Protocol
REDIS_URL=rediss://default:AYN...xyz@charming-dane-12345.upstash.io:6379
```

### 테스트

```bash
# Redis 연결 테스트
source venv/bin/activate
python -c "
from app.core.services.redis_service import get_redis_service
redis = get_redis_service()
if redis.enabled:
    print('✅ Redis 연결 성공!')
else:
    print('❌ Redis 비활성화')
"
```

---

## 3. 전체 .env 파일 예시

```bash
# ==========================================
# Application
# ==========================================
ENVIRONMENT=development
API_VERSION=v1
LOG_LEVEL=INFO

# ==========================================
# Supabase Configuration
# ==========================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres

# ==========================================
# Upstash Redis Configuration
# ==========================================
UPSTASH_URL=https://charming-dane-12345.upstash.io
UPSTASH_TOKEN=AYN...xyz
REDIS_URL=https://charming-dane-12345.upstash.io

# ==========================================
# Seoul Open API Configuration
# ==========================================
SEOUL_API_KEY=your_seoul_api_key_here
SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088

# ==========================================
# Kakao API Configuration
# ==========================================
KAKAO_REST_API_KEY=your_kakao_rest_api_key_here

# ==========================================
# Ollama Configuration (Optional)
# ==========================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=bge-m3

# ==========================================
# Cache Configuration
# ==========================================
REDIS_CACHE_TTL=300
CACHE_ENABLED=true

# ==========================================
# API Rate Limiting
# ==========================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

---

## 4. 설정 확인 체크리스트

### Supabase
- [ ] `SUPABASE_URL` 설정됨
- [ ] `SUPABASE_KEY` (anon key) 설정됨
- [ ] `SUPABASE_SERVICE_ROLE_KEY` 설정됨
- [ ] 5개 테이블 생성 완료 (libraries, cultural_events, 등)
- [ ] PostGIS 확장 설치됨
- [ ] 데이터 수집 완료

### Redis (Upstash)
- [ ] `UPSTASH_URL` 설정됨
- [ ] `UPSTASH_TOKEN` 설정됨
- [ ] `REDIS_URL` 올바른 스킴으로 설정됨
- [ ] 연결 테스트 성공

### Kakao Map API
- [ ] `KAKAO_REST_API_KEY` 설정됨
- [ ] Web 플랫폼 등록됨 (localhost:8000, localhost:8501)
- [ ] "지도/로컬" 서비스 활성화됨
- [ ] API 테스트 성공 (curl 테스트)

### Seoul Open API
- [ ] `SEOUL_API_KEY` 설정됨
- [ ] API 키 활성화 상태 확인
- [ ] 데이터 수집 테스트 성공

---

## 5. 문제 해결 (Troubleshooting)

### Kakao API 403 에러
**증상**: `App disabled OPEN_MAP_AND_LOCAL service`
**해결**:
1. Kakao Developers 콘솔 확인
2. "제품 설정" > "지도/로컬" 활성화
3. Web 플랫폼에 localhost 도메인 추가
4. API 키 재발급 (필요시)

### Redis 연결 실패
**증상**: `Redis URL must specify one of the following schemes`
**해결**:
1. `.env`에서 `REDIS_URL` 확인
2. `redis://` 또는 `rediss://` 스킴 사용
3. 또는 Upstash REST API URL 사용 (HTTPS)
4. 서버 재시작

### Supabase 연결 실패
**증상**: `Connection refused` 또는 `Invalid API key`
**해결**:
1. Supabase Project 대시보드 확인
2. API Settings에서 키 재확인
3. 네트워크 방화벽 확인
4. URL 형식 확인 (https:// 포함)

### Seoul API 한도 초과
**증상**: `429 Too Many Requests`
**해결**:
1. 캐싱 활성화 확인 (`CACHE_ENABLED=true`)
2. TTL 증가 (`REDIS_CACHE_TTL=600`)
3. API 호출 빈도 감소
4. 새 API 키 발급 고려

---

**작성일**: 2025-11-15
**프로젝트**: Seoul Location Services App - Backend
