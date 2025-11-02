# Seoul Location Services App - Development Plan

## 프로젝트 개요

### 목적
서울시 공공 API 데이터를 수집하여 사용자의 현재 위치 기반으로 문화시설, 도서관, 공공예약 서비스 등을 카카오 맵에 표시하는 모바일 웹 애플리케이션

### 핵심 가치
- **실시간 위치 기반 추천**: 사용자의 현재 위치를 중심으로 주변 공공 서비스 정보 제공
- **통합 공공 서비스**: 9개 서울시 공공 API를 하나의 플랫폼에서 제공
- **제로 비용 운영**: 무료 티어만 사용하여 월 $0 운영비 달성

## 기술 스택

### Frontend
- **Framework**: React + TypeScript (Vercel 배포)
- **Map**: Kakao Map JavaScript SDK
- **State Management**: React Query (서버 상태) + Zustand (클라이언트 상태)
- **UI**: Tailwind CSS + shadcn/ui
- **Build Tool**: Vite

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Architecture**: LangGraph 기반 Multi-Agent Workflow
- **Database**: Supabase PostgreSQL
- **Cache**: Upstash Redis (API 응답 캐싱)
- **LLM**: Ollama (llama3.1:8b) - 선택적 사용
- **Deployment**: Vercel Serverless Functions

### Data Collection
- **Scheduler**: APScheduler (매일 1회 자동 수집)
- **Backup Storage**: Firebase Realtime Database (데이터 이중화)
- **API Client**: httpx (비동기 HTTP 클라이언트)

### Infrastructure
| 서비스 | 무료 티어 한도 | 용도 |
|--------|----------------|------|
| Vercel | 100GB 대역폭/월, 6,000 서버리스 실행시간/월 | 프론트엔드 + API 배포 |
| Supabase | 500MB DB, 2GB 대역폭/월 | PostgreSQL 데이터베이스 |
| Upstash Redis | 10,000 명령/일 | API 응답 캐싱 (5분 TTL) |
| Firebase | 1GB 저장공간, 10GB 다운로드/월 | 데이터 백업 및 실시간 동기화 |
| Ollama | 무제한 (로컬) | LLM 기반 추천 (선택적) |

## 서울시 공공 API 목록

### 수집 대상 (위도/경도 포함 API)

| API명 | 엔드포인트 | 주요 필드 | 수집 주기 |
|-------|-----------|----------|----------|
| 문화행사 정보 | `/culturalEventInfo` | LAT, LOT, CODENAME, TITLE, DATE | 매일 |
| 공공도서관 현황 | `/SeoulPublicLibraryInfo` | XCNTS, YCNTS, LBRRY_NAME, ADRES | 주 1회 |
| 문화공간 정보 | `/culturalSpaceInfo` | LAT, LOT, FAC_NAME, ADDR | 주 1회 |
| 장애인 도서관 | `/SeoulDisableLibraryInfo` | XCNTS, YCNTS, LBRRY_NAME | 주 1회 |
| 진료 공공예약 | `/ListPublicReservationMedical` | X, Y, SVCNM, PLACENM | 매일 |
| 교육 공공예약 | `/ListPublicReservationEducation` | X, Y, SVCNM, PLACENM | 매일 |
| 문화행사 공공예약 | `/ListPublicReservationCulture` | X, Y, SVCNM, PLACENM | 매일 |
| 공공예약 종합 | `/tvYeyakCOllect` | X, Y, SVCNM, PLACENM | 매일 |
| 서울미래유산 | `/futureHeritageInfo` | LAT, LNG, NAME, ADDR | 월 1회 |

### 좌표계 처리
- **입력 좌표계**: WGS84 (위도/경도) 또는 TM 좌표계
- **출력 좌표계**: WGS84 (Kakao Map 호환)
- **변환 로직**: TM → WGS84 변환 모듈 구현 필요

## 시스템 아키텍처

### 전체 구조
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Kakao Map    │  │ Location     │  │ Service      │       │
│  │ Component    │  │ Tracker      │  │ List         │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────────────────────────┐
│              Backend API (FastAPI + Vercel)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           LangGraph Multi-Agent Workflow              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Location │→ │ Service  │→ │ Response │           │   │
│  │  │ Analyzer │  │ Fetcher  │  │ Generator│           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Redis Cache  │  │ Supabase     │  │ Seoul API    │       │
│  │ (5min TTL)   │  │ Client       │  │ Client       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Data Collection Service                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ APScheduler  │→ │ Seoul API    │→ │ Data         │       │
│  │ (Cron Jobs)  │  │ Collector    │  │ Processor    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Supabase DB  │  │ Firebase     │                         │
│  │ (Primary)    │  │ (Backup)     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### LangGraph Multi-Agent Workflow

```python
# 3-Agent 워크플로우
StateGraph:
  1. LocationAnalyzer (위치 분석 에이전트)
     - 입력: 사용자 위치 (위도/경도) 또는 주소
     - 출력: 정규화된 좌표, 반경(default: 2km), 우선순위 카테고리
     - 사용: Kakao Map API (주소→좌표 변환)

  2. ServiceFetcher (서비스 조회 에이전트)
     - 입력: 정규화된 좌표, 반경, 카테고리
     - 출력: 거리 계산된 서비스 목록 (Haversine formula)
     - 데이터 소스: Supabase (cached) → Redis (hot cache)

  3. ResponseGenerator (응답 생성 에이전트)
     - 입력: 서비스 목록, 사용자 컨텍스트
     - 출력: 카테고리별 정렬된 JSON 응답 + Kakao Map 마커 데이터
     - 선택적: Ollama LLM을 사용한 개인화 추천 텍스트
```

## 데이터베이스 스키마

### Supabase PostgreSQL Tables

```sql
-- 1. 문화행사 정보
CREATE TABLE cultural_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    codename VARCHAR(100),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326), -- PostGIS extension for spatial queries
    place VARCHAR(300),
    org_name VARCHAR(200),
    use_trgt VARCHAR(200),
    start_date DATE,
    end_date DATE,
    is_free VARCHAR(10),
    main_img TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'culturalEventInfo'
);

-- 2. 도서관 정보 (공공 + 장애인)
CREATE TABLE libraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    library_name VARCHAR(300) NOT NULL,
    library_type VARCHAR(50), -- 'public' or 'disabled'
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    tel VARCHAR(50),
    homepage TEXT,
    closed_day VARCHAR(100),
    open_time VARCHAR(100),
    facilities TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50)
);

-- 3. 문화공간 정보
CREATE TABLE cultural_spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    fac_name VARCHAR(300) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    tel VARCHAR(50),
    subjcode VARCHAR(100),
    main_purps TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'culturalSpaceInfo'
);

-- 4. 공공예약 서비스 (통합)
CREATE TABLE public_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    service_name VARCHAR(500) NOT NULL,
    service_type VARCHAR(50), -- 'medical', 'education', 'culture', 'general'
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    place_name VARCHAR(300),
    area_name VARCHAR(100),
    use_target VARCHAR(200),
    service_status VARCHAR(50), -- '접수중', '접수종료' etc.
    start_date DATE,
    end_date DATE,
    reservation_url TEXT,
    img_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50)
);

-- 5. 서울미래유산
CREATE TABLE future_heritages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id VARCHAR(100) UNIQUE NOT NULL,
    heritage_name VARCHAR(300) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    category VARCHAR(100),
    description TEXT,
    main_img TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'futureHeritageInfo'
);

-- 6. 데이터 수집 로그
CREATE TABLE collection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_endpoint VARCHAR(100) NOT NULL,
    collection_status VARCHAR(50), -- 'success', 'partial', 'failed'
    total_records INTEGER,
    new_records INTEGER,
    updated_records INTEGER,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_cultural_events_location ON cultural_events USING GIST(location);
CREATE INDEX idx_libraries_location ON libraries USING GIST(location);
CREATE INDEX idx_cultural_spaces_location ON cultural_spaces USING GIST(location);
CREATE INDEX idx_public_reservations_location ON public_reservations USING GIST(location);
CREATE INDEX idx_future_heritages_location ON future_heritages USING GIST(location);

CREATE INDEX idx_cultural_events_dates ON cultural_events(start_date, end_date);
CREATE INDEX idx_public_reservations_status ON public_reservations(service_status, service_type);
```

## API 설계

### REST API Endpoints

```yaml
# 1. 위치 기반 서비스 조회
GET /api/v1/services/nearby
Query Parameters:
  - lat: float (required) - 위도
  - lon: float (required) - 경도
  - radius: int (optional, default=2000) - 반경(미터)
  - categories: string[] (optional) - ['events', 'libraries', 'spaces', 'reservations', 'heritages']
  - limit: int (optional, default=50) - 최대 결과 수
Response:
  {
    "status": "success",
    "data": {
      "location": {"lat": 37.5665, "lon": 126.9780},
      "radius": 2000,
      "categories": {
        "events": [...],
        "libraries": [...],
        "spaces": [...],
        "reservations": [...],
        "heritages": [...]
      },
      "total_count": 45,
      "cached": true
    }
  }

# 2. 카테고리별 서비스 조회
GET /api/v1/services/{category}
Path Parameters:
  - category: string (events|libraries|spaces|reservations|heritages)
Query Parameters:
  - lat: float (required)
  - lon: float (required)
  - radius: int (optional)
  - limit: int (optional)
  - sort_by: string (optional, default='distance') - distance|name|date

# 3. 서비스 상세 정보
GET /api/v1/services/{category}/{id}
Response:
  {
    "id": "uuid",
    "name": "...",
    "location": {"lat": ..., "lon": ...},
    "distance": 1250, // meters from user
    "details": {...},
    "nearby_services": [...]  // 주변 다른 서비스
  }

# 4. 주소 → 좌표 변환
POST /api/v1/geocode
Body:
  {
    "address": "서울시 종로구 세종대로 209"
  }
Response:
  {
    "address": "...",
    "coordinates": {"lat": 37.5665, "lon": 126.9780},
    "formatted_address": "..."
  }

# 5. LLM 기반 추천 (선택적)
POST /api/v1/recommendations
Body:
  {
    "location": {"lat": 37.5665, "lon": 126.9780},
    "preferences": {
      "interests": ["문화", "교육"],
      "time_available": "2시간",
      "mobility": "도보"
    }
  }
Response:
  {
    "recommendations": [
      {
        "service": {...},
        "reason": "현재 위치에서 도보 10분 거리에 있으며...",
        "score": 0.92
      }
    ]
  }

# 6. 데이터 수집 상태 (관리자)
GET /api/v1/admin/collection-status
Response:
  {
    "last_collection": "2025-11-02T03:00:00Z",
    "next_scheduled": "2025-11-03T03:00:00Z",
    "status": {
      "culturalEventInfo": {"total": 1234, "updated": 45, "status": "success"},
      ...
    }
  }
```

## 프로젝트 구조

```
seoul-location-services-app/
├── frontend/                      # React + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── map/
│   │   │   │   ├── KakaoMap.tsx        # 카카오맵 컴포넌트
│   │   │   │   ├── MarkerCluster.tsx   # 마커 클러스터링
│   │   │   │   └── CustomOverlay.tsx   # 커스텀 오버레이
│   │   │   ├── services/
│   │   │   │   ├── ServiceList.tsx     # 서비스 목록
│   │   │   │   ├── ServiceCard.tsx     # 서비스 카드
│   │   │   │   └── ServiceDetail.tsx   # 상세 정보
│   │   │   ├── location/
│   │   │   │   ├── LocationInput.tsx   # 위치 입력
│   │   │   │   └── CurrentLocation.tsx # 현재 위치 버튼
│   │   │   └── ui/                     # shadcn/ui components
│   │   ├── hooks/
│   │   │   ├── useLocation.ts          # 위치 추적 훅
│   │   │   ├── useServices.ts          # 서비스 조회 훅
│   │   │   └── useKakaoMap.ts          # 카카오맵 훅
│   │   ├── services/
│   │   │   ├── api.ts                  # API 클라이언트
│   │   │   └── kakao.ts                # 카카오 SDK 래퍼
│   │   ├── stores/
│   │   │   └── locationStore.ts        # Zustand 스토어
│   │   ├── types/
│   │   │   └── services.ts             # 타입 정의
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── vercel.json
│
├── backend/                       # FastAPI
│   ├── app/
│   │   ├── main.py                     # FastAPI 엔트리포인트
│   │   ├── core/
│   │   │   ├── config.py               # 환경변수 설정
│   │   │   ├── agents/                 # LangGraph 에이전트
│   │   │   │   ├── location_analyzer.py
│   │   │   │   ├── service_fetcher.py
│   │   │   │   └── response_generator.py
│   │   │   ├── workflow/
│   │   │   │   └── service_graph.py    # LangGraph 워크플로우
│   │   │   └── services/
│   │   │       ├── supabase_service.py
│   │   │       ├── redis_service.py
│   │   │       ├── ollama_service.py
│   │   │       └── distance_service.py # Haversine 거리 계산
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── services.py
│   │   │   │   │   ├── geocode.py
│   │   │   │   │   └── recommendations.py
│   │   │   │   └── router.py
│   │   │   └── dependencies.py
│   │   ├── db/
│   │   │   ├── supabase_client.py
│   │   │   └── models.py               # Pydantic 모델
│   │   └── utils/
│   │       ├── coordinate_transform.py  # 좌표 변환
│   │       └── cache.py                 # 캐싱 유틸
│   ├── collectors/                      # 데이터 수집
│   │   ├── base_collector.py
│   │   ├── seoul_api_client.py
│   │   ├── cultural_events_collector.py
│   │   ├── libraries_collector.py
│   │   ├── cultural_spaces_collector.py
│   │   ├── reservations_collector.py
│   │   └── heritages_collector.py
│   ├── scripts/
│   │   ├── init_db.py                  # DB 초기화
│   │   ├── collect_all.py              # 전체 데이터 수집
│   │   └── scheduler.py                # APScheduler 설정
│   ├── tests/
│   ├── requirements.txt
│   ├── vercel.json
│   └── .env.example
│
├── docs/
│   ├── PROJECT_PLAN.md                 # 이 문서
│   ├── API_SPECIFICATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── DEVELOPMENT_TIMELINE.md
│
├── .github/
│   └── workflows/
│       ├── frontend-deploy.yml         # Vercel 프론트엔드 배포
│       └── backend-deploy.yml          # Vercel 서버리스 배포
│
└── README.md
```

## 개발 일정 (4주 계획)

### Week 1: 기반 구축 (Day 1-7)
**목표**: 데이터 수집 파이프라인 구축 및 데이터베이스 설정

#### Day 1-2: 프로젝트 설정
- [ ] 프로젝트 구조 생성
- [ ] Supabase 프로젝트 설정 및 테이블 생성
- [ ] Firebase 프로젝트 설정
- [ ] Upstash Redis 설정
- [ ] 환경변수 설정 (.env 파일)
- [ ] Git 저장소 생성

#### Day 3-4: 데이터 수집 모듈 개발
- [ ] Seoul API Client 구현 (httpx 기반)
- [ ] BaseCollector 클래스 구현
- [ ] 각 API별 Collector 구현 (9개)
  - [ ] CulturalEventsCollector
  - [ ] LibrariesCollector (공공 + 장애인 통합)
  - [ ] CulturalSpacesCollector
  - [ ] ReservationsCollector (4개 API 통합)
  - [ ] HeritagesCollector
- [ ] 좌표 변환 로직 구현 (TM → WGS84)
- [ ] Data Processor 구현 (정규화, 검증)

#### Day 5-6: 데이터베이스 연동
- [ ] Supabase Client 구현
- [ ] Firebase Client 구현 (백업용)
- [ ] ORM 모델 정의 (SQLAlchemy)
- [ ] 초기 데이터 수집 스크립트 작성
- [ ] 데이터 수집 로그 시스템 구현

#### Day 7: 스케줄러 및 테스트
- [ ] APScheduler 설정 (cron jobs)
  - 매일 03:00 - 문화행사, 공공예약 수집
  - 매주 월요일 - 도서관, 문화공간 수집
  - 매월 1일 - 미래유산 수집
- [ ] 전체 데이터 수집 테스트
- [ ] 데이터 품질 검증 스크립트
- [ ] Week 1 완료 리포트 작성

**주요 산출물**:
- 9개 Seoul API에서 데이터 수집 완료
- Supabase에 10,000+ 레코드 저장
- 자동 수집 스케줄러 동작

---

### Week 2: Backend API 개발 (Day 8-14)
**목표**: FastAPI 기반 REST API 구축 및 LangGraph 워크플로우 구현

#### Day 8-9: FastAPI 기본 설정
- [ ] FastAPI 프로젝트 구조 생성
- [ ] API v1 라우터 설정
- [ ] CORS 설정 (Vercel 도메인)
- [ ] 환경변수 관리 (pydantic-settings)
- [ ] 의존성 주입 설정
- [ ] Health check endpoint 구현

#### Day 10-11: LangGraph 에이전트 개발
- [ ] LangGraph 워크플로우 설계
- [ ] LocationAnalyzer 에이전트 구현
  - Kakao Map API 주소→좌표 변환
  - 입력 좌표 정규화
  - 반경 설정 (default: 2km)
- [ ] ServiceFetcher 에이전트 구현
  - PostGIS 공간 쿼리 (`ST_DWithin`)
  - Haversine 거리 계산
  - Redis 캐싱 로직 (5분 TTL)
- [ ] ResponseGenerator 에이전트 구현
  - 카테고리별 정렬
  - Kakao Map 마커 데이터 생성
  - (선택적) Ollama LLM 추천 텍스트

#### Day 12-13: API 엔드포인트 구현
- [ ] `/api/v1/services/nearby` - 위치 기반 통합 조회
- [ ] `/api/v1/services/{category}` - 카테고리별 조회
- [ ] `/api/v1/services/{category}/{id}` - 상세 정보
- [ ] `/api/v1/geocode` - 주소→좌표 변환
- [ ] `/api/v1/recommendations` - LLM 기반 추천
- [ ] Redis 캐싱 적용 (모든 GET 요청)
- [ ] API 문서 작성 (OpenAPI/Swagger)

#### Day 14: 성능 최적화 및 테스트
- [ ] 데이터베이스 인덱스 최적화
- [ ] API 응답 속도 테스트 (<200ms 목표)
- [ ] 동시 요청 부하 테스트 (locust)
- [ ] Vercel Serverless 함수 최적화
- [ ] Week 2 완료 리포트 작성

**주요 산출물**:
- REST API 6개 엔드포인트 구현
- LangGraph 3-agent 워크플로우 동작
- API 응답 속도 <200ms 달성
- Swagger 문서 완성

---

### Week 3: Frontend 개발 (Day 15-21)
**목표**: React 기반 모바일 웹 UI 구축 및 Kakao Map 연동

#### Day 15-16: React 프로젝트 설정
- [ ] Vite + React + TypeScript 프로젝트 생성
- [ ] Tailwind CSS + shadcn/ui 설정
- [ ] React Query 설정 (API 통신)
- [ ] Zustand 스토어 설정 (위치 상태)
- [ ] 프로젝트 구조 생성
- [ ] Kakao Map JavaScript SDK 설정

#### Day 17-18: 지도 컴포넌트 개발
- [ ] KakaoMap 컴포넌트 구현
  - 지도 초기화
  - 현재 위치 표시
  - 지도 이동/줌 이벤트
- [ ] MarkerCluster 컴포넌트 구현
  - 카테고리별 마커 색상
  - 클러스터링 (1km 기준)
  - 마커 클릭 이벤트
- [ ] CustomOverlay 컴포넌트 구현
  - 서비스 미리보기 카드
  - 거리 표시
  - 상세보기 버튼

#### Day 19-20: 서비스 목록 UI 개발
- [ ] LocationInput 컴포넌트 (주소 검색)
- [ ] CurrentLocation 컴포넌트 (GPS 위치)
- [ ] ServiceList 컴포넌트 (좌측 패널)
  - 카테고리 필터
  - 거리순/이름순 정렬
  - 무한 스크롤
- [ ] ServiceCard 컴포넌트
  - 썸네일 이미지
  - 거리/주소 표시
  - 즐겨찾기 버튼
- [ ] ServiceDetail 모달
  - 상세 정보 표시
  - 공유 기능
  - 길찾기 버튼 (Kakao Map 연동)

#### Day 21: 반응형 디자인 및 UX 개선
- [ ] 모바일 최적화 (375px ~ 768px)
- [ ] 터치 제스처 지원
- [ ] 로딩/에러 상태 UI
- [ ] 다크모드 지원 (선택적)
- [ ] 접근성 개선 (ARIA labels)
- [ ] Week 3 완료 리포트 작성

**주요 산출물**:
- Kakao Map 기반 인터랙티브 지도
- 카테고리별 마커 표시 (5개 카테고리)
- 모바일 최적화된 반응형 UI
- 현재 위치 추적 및 주변 서비스 자동 표시

---

### Week 4: 통합 및 배포 (Day 22-28)
**목표**: 프로덕션 배포 및 모니터링 설정

#### Day 22-23: Vercel 배포
- [ ] Frontend Vercel 배포 설정
  - vercel.json 작성
  - 환경변수 설정 (Kakao API Key)
  - 도메인 설정
- [ ] Backend Vercel Serverless 배포
  - vercel.json 작성 (serverless functions)
  - 환경변수 설정 (Supabase, Redis, etc.)
  - Cold start 최적화
- [ ] CORS 설정 (프로덕션 도메인)
- [ ] GitHub Actions CI/CD 설정
  - 자동 테스트
  - 자동 배포

#### Day 24-25: 통합 테스트
- [ ] E2E 테스트 (Playwright)
  - 현재 위치 조회 시나리오
  - 주소 검색 시나리오
  - 카테고리 필터링 시나리오
- [ ] 크로스 브라우저 테스트 (Chrome, Safari, Samsung Internet)
- [ ] 모바일 디바이스 테스트 (iOS, Android)
- [ ] 성능 테스트
  - Lighthouse 점수 > 90
  - First Contentful Paint < 1.5s
  - Time to Interactive < 3.0s
- [ ] 보안 테스트
  - API 키 노출 확인
  - XSS/CSRF 방지 확인

#### Day 26: 모니터링 및 분석 설정
- [ ] Vercel Analytics 설정
- [ ] Sentry 에러 추적 설정 (무료 티어)
- [ ] Supabase 데이터베이스 모니터링
- [ ] Upstash Redis 사용량 모니터링
- [ ] 사용자 피드백 수집 폼 (Google Forms)

#### Day 27: 문서화 및 최적화
- [ ] README.md 작성
  - 프로젝트 소개
  - 기능 설명
  - 기술 스택
  - 배포 URL
- [ ] API 문서 공개 (Swagger UI)
- [ ] 사용자 가이드 작성
- [ ] 개발자 문서 작성
- [ ] 비용 최적화 체크리스트
  - Vercel 무료 티어 한도 확인
  - Supabase 무료 티어 한도 확인
  - Redis 캐싱 효율성 확인

#### Day 28: 런칭 및 피드백 수집
- [ ] 프로덕션 배포 최종 확인
- [ ] 런칭 공지 (GitHub, SNS)
- [ ] 초기 사용자 피드백 수집
- [ ] 버그 리포트 대응
- [ ] Week 4 완료 리포트 작성
- [ ] **프로젝트 완료!** 🎉

**주요 산출물**:
- 프로덕션 배포 완료 (frontend + backend)
- CI/CD 파이프라인 구축
- E2E 테스트 커버리지 > 80%
- Lighthouse 성능 점수 > 90
- 완전한 문서화

---

## 성능 목표

### 응답 속도
- API 응답 시간 (캐시 히트): <50ms
- API 응답 시간 (캐시 미스): <200ms
- 지도 초기 로딩: <2초
- 마커 렌더링 (100개): <500ms

### 확장성
- 동시 사용자: 500+ (Vercel 무료 티어)
- 데이터베이스: 100,000+ 레코드 지원
- Redis 캐시 히트율: >80%

### 사용자 경험
- Lighthouse 성능 점수: >90
- First Contentful Paint: <1.5초
- Time to Interactive: <3.0초
- 모바일 터치 반응 속도: <100ms

## 보안 고려사항

### API 보안
- API 키는 환경변수로 관리 (절대 코드에 하드코딩 금지)
- CORS 설정 (프로덕션 도메인만 허용)
- Rate Limiting (IP당 100 req/min)
- SQL Injection 방지 (Parameterized Query)

### 클라이언트 보안
- XSS 방지 (React의 기본 이스케이핑 사용)
- HTTPS 강제 (Vercel 기본 제공)
- 사용자 위치 정보는 클라이언트에만 저장 (서버 로깅 금지)

### 데이터베이스 보안
- Supabase Row Level Security (RLS) 활성화
- 읽기 전용 API 엔드포인트 (SELECT만 허용)
- 민감 정보 필터링 (개인정보 제외)

## 비용 최적화 전략

### Vercel (무료 티어: 100GB 대역폭/월)
- 이미지 최적화 (WebP, lazy loading)
- 번들 사이즈 최소화 (<500KB)
- CDN 캐싱 활용 (static assets)

### Supabase (무료 티어: 500MB DB, 2GB 대역폭/월)
- 인덱스 최적화 (공간 쿼리 속도 향상)
- 오래된 이벤트 데이터 아카이빙 (3개월 이상)
- 이미지는 외부 URL 참조 (DB 저장 안 함)

### Upstash Redis (무료 티어: 10,000 명령/일)
- TTL 5분 설정 (너무 길면 메모리 낭비)
- 좌표 기반 캐시 키 (위도/경도 반올림)
- 인기 지역 우선 캐싱

### Firebase (무료 티어: 1GB 저장, 10GB 다운로드/월)
- 백업 용도로만 사용 (매일 1회 동기화)
- 압축된 JSON 형식으로 저장

**예상 월간 비용**: **$0** (모든 무료 티어 범위 내)

## 위험 요소 및 대응책

### 기술적 위험
| 위험 | 확률 | 영향 | 대응책 |
|------|------|------|--------|
| Seoul API 응답 지연/실패 | 중 | 중 | Retry 로직 (3회), 캐싱 강화, Firebase 백업 사용 |
| Vercel 무료 티어 한도 초과 | 중 | 높음 | 트래픽 모니터링, 이미지 최적화, 필요시 유료 전환 |
| Supabase 저장공간 부족 | 낮 | 중 | 오래된 데이터 아카이빙, 이미지 URL만 저장 |
| Kakao Map API 키 노출 | 낮 | 높음 | 도메인 제한 설정, HTTP Referrer 제한 |
| Ollama 로컬 서버 다운 | 중 | 낮 | Fallback 로직 (LLM 없이도 동작) |

### 운영 위험
| 위험 | 확률 | 영향 | 대응책 |
|------|------|------|--------|
| Seoul API 스펙 변경 | 낮 | 중 | API 버전 관리, 정기 점검 |
| 데이터 품질 저하 | 중 | 중 | 데이터 검증 로직, 수동 검수 |
| 사용자 급증으로 인한 서버 부하 | 낮 | 높음 | 캐싱 강화, Rate Limiting, Auto Scaling (유료 전환) |

## 성공 지표 (KPI)

### 기술 지표
- [ ] 데이터 수집 성공률 > 95%
- [ ] API 응답 속도 < 200ms (P95)
- [ ] 시스템 가용성 > 99%
- [ ] 캐시 히트율 > 80%

### 사용자 지표
- [ ] 월간 활성 사용자(MAU) > 1,000명
- [ ] 평균 세션 시간 > 3분
- [ ] 재방문율 > 30%
- [ ] 모바일 사용 비율 > 70%

### 비즈니스 지표
- [ ] 월 운영 비용 = $0
- [ ] 프로덕션 배포 완료 (4주 내)
- [ ] 버그 리포트 응답 시간 < 24시간
- [ ] 사용자 만족도 > 4.0/5.0

## 다음 단계 (Phase 2 아이디어)

### 추가 기능 후보
1. **개인화 추천 시스템**
   - 사용자 관심사 프로필 저장
   - 방문 기록 기반 추천
   - 협업 필터링 (유사 사용자 기반)

2. **소셜 기능**
   - 서비스 리뷰/평점
   - 즐겨찾기 공유
   - 친구 위치 공유 (선택적)

3. **고급 필터링**
   - 시간대별 필터 (현재 운영 중인 곳만)
   - 접근성 필터 (장애인 편의시설)
   - 무료/유료 필터

4. **알림 시스템**
   - 관심 지역 신규 행사 알림
   - 예약 마감 임박 알림
   - 위치 기반 푸시 알림

5. **오프라인 지원**
   - Service Worker (PWA)
   - 오프라인 데이터 캐싱
   - 앱 설치 유도

### 기술 개선 후보
- GraphQL API (REST 대체)
- Next.js로 마이그레이션 (SSR/ISR)
- WebSocket 실시간 업데이트
- AI 챗봇 (Ollama 기반)

---

## 참고 자료

### 외부 API 문서
- [서울 열린데이터광장](https://data.seoul.go.kr/)
- [Kakao Map JavaScript API](https://apis.map.kakao.com/web/)
- [Supabase Docs](https://supabase.com/docs)
- [Vercel Docs](https://vercel.com/docs)

### 기술 스택 문서
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### 좌표 변환 참고
- [좌표계 변환 라이브러리 (pyproj)](https://pyproj4.github.io/pyproj/)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)

---

**작성일**: 2025-11-02
**작성자**: AI Assistant
**버전**: 1.0
**다음 리뷰**: Week 1 종료 후 (2025-11-09)
