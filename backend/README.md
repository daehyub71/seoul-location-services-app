# Seoul Location Services - Backend

FastAPI 기반 서울시 공공 서비스 위치 정보 API

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py              # FastAPI 애플리케이션 엔트리포인트
│   ├── core/
│   │   ├── config.py        # 환경변수 설정
│   │   ├── agents/          # LangGraph 에이전트 (Day 10-11)
│   │   ├── workflow/        # LangGraph 워크플로우 (Day 12)
│   │   └── services/        # 비즈니스 로직 서비스 (Day 9+)
│   ├── api/
│   │   └── v1/
│   │       ├── router.py    # API 라우터 통합
│   │       └── endpoints/   # API 엔드포인트 (Day 12-13)
│   ├── db/
│   │   ├── supabase_client.py  # Supabase 클라이언트 (Day 2)
│   │   └── models.py           # Pydantic 모델 (Day 8)
│   └── utils/               # 유틸리티 함수 (Day 9)
├── collectors/              # 데이터 수집기 (Day 3-5)
├── scripts/                 # 스크립트 (Day 2, 6-7)
├── tests/                   # 테스트 (Day 14+)
├── requirements.txt         # Python 의존성
└── .env.example            # 환경변수 템플릿
```

## 설치

### 1. 가상환경 생성

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어서 실제 값으로 수정
```

필수 환경변수:
- `SUPABASE_URL` - Supabase 프로젝트 URL
- `SUPABASE_KEY` - Supabase anon/public key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `SUPABASE_DATABASE_URL` - PostgreSQL 연결 문자열
- `UPSTASH_URL` - Upstash Redis URL
- `UPSTASH_TOKEN` - Upstash Redis 토큰
- `SEOUL_API_KEY` - 서울 열린데이터광장 API 키

## 데이터베이스 초기화

### Supabase SQL 실행 (Day 1)

1. [Supabase Dashboard](https://app.supabase.com/) 접속
2. SQL Editor 열기
3. `scripts/init_supabase_schema.sql` 내용 복사
4. "Run" 클릭

이 스크립트는 다음을 생성합니다:
- PostGIS 확장 활성화
- 5개 주요 테이블 (문화행사, 도서관, 문화공간, 공공예약, 미래유산)
- 공간 인덱스 (GIST)
- 자동 location 업데이트 트리거
- 헬퍼 함수 (`calculate_distance`, `get_services_within_radius`)

## 실행

### 개발 서버

```bash
uvicorn app.main:app --reload --port 8000
```

또는:

```bash
python app/main.py
```

### API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 개발 일정

### Week 1 (Day 1-7): 데이터 수집 파이프라인
- ✅ Day 1: 프로젝트 설정 및 DB 스키마
- [ ] Day 2: Supabase 클라이언트 구현
- [ ] Day 3: Seoul API 클라이언트 구현
- [ ] Day 4: 데이터 수집기 구현 (Part 1)
- [ ] Day 5: 데이터 수집기 구현 (Part 2)
- [ ] Day 6: 스케줄러 및 자동화
- [ ] Day 7: 데이터 품질 검증

### Week 2 (Day 8-14): API 개발
- [ ] Day 8-9: FastAPI 기본 구조 및 Redis 캐싱
- [ ] Day 10-11: LangGraph 에이전트 구현
- [ ] Day 12-13: API 엔드포인트 구현
- [ ] Day 14: 성능 최적화

## 테스트

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html

# 특정 테스트만
pytest tests/test_services.py -v
```

## API 엔드포인트 (Week 2 이후)

### 서비스 조회
```
GET /api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000
GET /api/v1/services/{category}?lat=37.5665&lon=126.9780
GET /api/v1/services/{category}/{id}
```

### 지오코딩
```
POST /api/v1/geocode
{
  "address": "서울시 종로구 세종대로 209"
}
```

### LLM 추천 (선택적)
```
POST /api/v1/recommendations
{
  "location": {"lat": 37.5665, "lon": 126.9780},
  "preferences": {"interests": ["문화", "교육"]}
}
```

## 기술 스택

- **Framework**: FastAPI 0.109+
- **Database**: Supabase (PostgreSQL + PostGIS)
- **Cache**: Upstash Redis
- **AI**: LangGraph, Ollama (선택적)
- **HTTP Client**: httpx
- **Testing**: pytest
- **Geospatial**: pyproj, shapely

## 라이선스

MIT
