# Development Timeline - Seoul Location Services App

## 4주 개발 일정 상세

### Week 1: 데이터 수집 파이프라인 (Day 1-7)

#### Day 1 (2025-11-02): 프로젝트 초기 설정 ✅ COMPLETED
**목표**: 개발 환경 구축 및 인프라 설정

**Tasks**:
- [x] 프로젝트 계획서 작성
  - [x] PROJECT_PLAN.md (완전한 개발 계획서)
  - [x] DEVELOPMENT_TIMELINE.md (28일 상세 일정)
  - [x] README.md (프로젝트 소개)
  - [x] QUICK_START.md (5분 빠른 시작 가이드)
- [x] Git 저장소 생성 및 `.gitignore` 설정
- [x] 프로젝트 디렉토리 구조 생성
  - [x] backend/ (FastAPI 구조)
  - [x] frontend/ (React 구조)
  - [x] docs/ (문서)
- [x] Supabase 데이터베이스 스키마 준비
  - [x] init_supabase_schema.sql 작성
  - [x] PostGIS 확장 설정
  - [x] 5개 테이블 스키마 (cultural_events, libraries, cultural_spaces, public_reservations, future_heritages)
  - [x] 공간 인덱스 (GIST) 정의
  - [x] 자동 location 업데이트 트리거
  - [x] 헬퍼 함수 (calculate_distance, get_services_within_radius)
- [x] Backend 초기 파일 작성
  - [x] app/main.py (FastAPI 앱 + CORS + 에러 핸들링)
  - [x] app/core/config.py (Pydantic Settings)
  - [x] app/api/v1/router.py (API 라우터)
  - [x] requirements.txt (모든 의존성)
  - [x] .env.example (환경변수 템플릿)
  - [x] README.md (Backend 문서)
- [x] Frontend 초기 파일 작성
  - [x] package.json (의존성 정의)
  - [x] .env.example (환경변수 템플릿)
  - [x] README.md (Frontend 문서)
- [x] Git 초기 커밋
  - Commit: "Initial commit: Day 1 project setup complete"
  - 29 files changed, 3599 insertions(+)

**산출물**:
- ✅ 프로젝트 구조 완성 (backend + frontend)
- ✅ 완전한 문서화 (4개 주요 문서)
- ✅ Supabase 스키마 SQL 준비 완료 (실행 대기)
- ✅ FastAPI 기본 구조 완성
- ✅ Git 저장소 초기화
- ✅ 환경변수 템플릿 (backend + frontend)

**다음 단계 (Day 2)**:
- [ ] Supabase SQL 실행 (init_supabase_schema.sql)
- [ ] Supabase 클라이언트 구현 (app/db/supabase_client.py)
- [ ] Firebase 프로젝트 설정 (선택적)
- [ ] Upstash Redis 프로젝트 생성
- [ ] 데이터베이스 연결 테스트

---

#### Day 2 (2025-11-03): 데이터베이스 설정 완료 ✅ COMPLETED
**목표**: 데이터베이스 스키마 구현 및 테스트

**Tasks**:
- [x] Supabase 테이블 생성 SQL 스크립트 작성 (Day 1에서 완료)
  - [x] `cultural_events` 테이블
  - [x] `libraries` 테이블
  - [x] `cultural_spaces` 테이블
  - [x] `public_reservations` 테이블
  - [x] `future_heritages` 테이블
  - [x] `collection_logs` 테이블
- [x] PostGIS 공간 인덱스 생성
  - [x] `GIST(location)` 인덱스 (5개 테이블)
  - [x] 자동 location 업데이트 트리거 구현
  - [x] 헬퍼 함수 (calculate_distance, get_services_within_radius)
- [x] Supabase 프로젝트 생성 및 설정
  - [x] 프로젝트 생성 (xptueenuumxhmhkantdl.supabase.co)
  - [x] API 키 발급 (anon, service_role)
  - [x] Database URL 확인
- [x] 환경변수 설정 (backend/.env)
  - [x] SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY
  - [x] SUPABASE_DATABASE_URL (URL 인코딩 처리)
- [x] Python 가상환경 설정
  - [x] venv 생성
  - [x] 의존성 설치 (supabase, psycopg2-binary, python-dotenv)
- [x] Supabase Python 클라이언트 테스트
  - [x] test_supabase_simple.py 작성
  - [x] 모든 테이블 접근 확인 (6개 테이블)
  - [x] CRUD 작업 테스트 (Insert, Select, Update, Delete)
  - [x] Trigger 동작 확인 (location 필드 자동 생성)
- [x] 데이터베이스 연결 테스트
  - [x] Supabase Client 연결 성공
  - [x] 테이블 스키마 확인 완료
  - [x] PostGIS 기능 동작 확인

**산출물**:
- ✅ 완전한 데이터베이스 스키마 (init_supabase_schema.sql)
- ✅ 연결 테스트 스크립트 (test_supabase_simple.py)
- ✅ 연결 테스트 통과 (모든 기능 정상 동작)
- ✅ Python 가상환경 및 의존성 설치 완료

**Note**:
- Row Level Security (RLS)는 프로덕션 배포 시 설정 (Week 4)
- Firebase Admin SDK는 선택사항으로 보류
- PostgreSQL 직접 연결은 Python Client로 대체

---

#### Day 3 (2025-11-02): Seoul API Client 구현 ✅ COMPLETED
**목표**: 서울시 공공 API 통신 모듈 구현

**Tasks**:
- [x] `collectors/seoul_api_client.py` 구현 (470+ lines)
  - [x] httpx 기반 비동기 HTTP 클라이언트
  - [x] API 키 인증 (URL 경로에 포함)
  - [x] Retry 로직 (tenacity: 3회, exponential backoff)
  - [x] Timeout 설정 (30초)
  - [x] 에러 핸들링 (429, 500, 503 HTTP 상태 + Seoul API 에러 코드)
- [x] XML/JSON 파싱 로직 (xmltodict 사용)
- [x] 페이지네이션 자동 처리 (1,000개/페이지)
- [x] 좌표 변환 유틸리티 구현 (`app/utils/coordinate_transform.py`, 350+ lines)
  - [x] TM 중부원점 ↔ WGS84 변환 (pyproj EPSG:2097 ↔ EPSG:4326)
  - [x] Haversine 거리 계산 (미터 단위)
  - [x] 서울시 범위 검증 (37.0-38.0, 126.0-128.0)
  - [x] Smart Convert (좌표계 자동 감지)
- [x] API 응답 샘플 데이터 수집 (9개 엔드포인트)
  - [x] `scripts/collect_sample_data.py` 작성
  - [x] 전체 4,824 레코드 수집 완료
  - [x] 좌표 분석 (범위, 유효성, 서울시 포함 여부)
- [x] 단위 테스트 작성 (52개 테스트, 100% 통과)
  - [x] `tests/test_seoul_api_client.py` (26개 테스트)
  - [x] `tests/test_coordinate_transform.py` (26개 테스트)
  - [x] Mock 기반 단위 테스트
  - [x] 실제 API 통합 테스트 (pytest -m integration)

**산출물**:
- ✅ Seoul API Client 완성 (`collectors/seoul_api_client.py`)
  - 9개 엔드포인트 정의
  - 비동기 컨텍스트 매니저 지원
  - 자동 페이지네이션
  - 에러 복구 로직
- ✅ 좌표 변환 모듈 (`app/utils/coordinate_transform.py`)
  - TM ↔ WGS84 양방향 변환
  - 거리 계산 (Haversine 공식)
  - 좌표 검증 및 포맷팅
- ✅ 샘플 데이터 (`backend/data/samples/`)
  - 9개 JSON 파일 (엔드포인트별)
  - collection_summary.json (메타데이터)
- ✅ 단위 테스트 (52/52 통과, 100% success rate)

**Note**:
- 일부 예약 API (reservation_*)는 lat/lon이 반대로 저장되어 있음 (API 데이터 이슈)
- cultural_spaces와 future_heritage는 좌표 데이터 없음 (주소만 제공)
- pytest 설치 완료 (pytest-asyncio 포함)

---

#### Day 4 (2025-11-02): Data Collectors 구현 (Part 1) ✅ COMPLETED
**목표**: 개별 API별 데이터 수집기 구현 (5개)

**Tasks**:
- [x] `collectors/base_collector.py` 구현 (360+ 줄)
  - [x] 추상 베이스 클래스 정의 (ABC 상속)
  - [x] Supabase 연결 관리
  - [x] Seoul API Client 통합
  - [x] 좌표 변환 지원 (CoordinateTransformer 통합)
  - [x] 공통 로깅 로직
  - [x] 데이터 검증 메서드 (validate_record)
  - [x] 좌표 변환 메서드 (transform_coordinates, swap 지원)
  - [x] 날짜 파싱 메서드 (parse_date)
  - [x] 문자열 정규화 메서드 (normalize_string)
  - [x] 수집 로그 기록 (_log_collection)
  - [x] UPSERT 기능 (중복 시 업데이트)
- [x] `collectors/cultural_events_collector.py` (180+ 줄)
  - [x] `/culturalEventInfo` API 호출
  - [x] 날짜 파싱 (YYYY-MM-DD 형식 지원)
  - [x] 이미지 URL 정규화
  - [x] 유무료 구분 boolean 변환
  - [x] API ID 생성 (MD5 해시)
- [x] `collectors/libraries_collector.py` (240+ 줄)
  - [x] `/SeoulPublicLibraryInfo` API 호출
  - [x] `/SeoulDisableLibraryInfo` API 호출
  - [x] 두 API 결과 통합 (library_type 필드)
  - [x] 좌표 필드 통합 (LAT/LNG, XCNTS/YDNTS)
- [x] `collectors/cultural_spaces_collector.py` (130+ 줄)
  - [x] `/culturalSpaceInfo` API 호출
  - [x] 주제 코드 매핑 (SUBJCODE, CODENAME)
  - [x] 좌표 없음 처리 (주소만 제공)
  - [x] 입장료 무료 여부 boolean 변환
- [x] `collectors/future_heritages_collector.py` (130+ 줄)
  - [x] `/futureHeritageInfo` API 호출
  - [x] 카테고리 정규화
  - [x] 관리번호를 API ID로 사용
  - [x] 좌표 없음 처리
- [x] `collectors/public_reservations_collector.py` (300+ 줄)
  - [x] `/ListPublicReservationMedical` API 호출
  - [x] `/ListPublicReservationEducation` API 호출
  - [x] `/ListPublicReservationCulture` API 호출
  - [x] 3개 API 결과 통합 (category 필드)
  - [x] 좌표 스왑 이슈 수정 (X=경도, Y=위도)
  - [x] 예약 날짜 파싱
  - [x] 인원 수 변환 (max_capacity, min_capacity)
- [x] `scripts/collect_all_data.py` (150+ 줄)
  - [x] 전체 Collector 통합 실행
  - [x] 진행상황 표시
  - [x] 테스트 모드 (--test 플래그)
  - [x] 통계 출력
- [x] `collectors/__init__.py` 패키지 초기화

**산출물**:
- ✅ Base Collector 추상 클래스 (360+ 줄)
- ✅ 5개 Collector 클래스 완성 (980+ 줄)
- ✅ 통합 수집 스크립트 (150+ 줄)
- ✅ 총 코드 라인 수: 1,490+ 줄

**발견된 이슈** (Day 5에서 수정 예정):
- ⚠️ Collector 컬럼명과 Supabase 스키마 불일치
  - 예: `category` → `codename`, `themecode`
  - 예: `registered_at` → `rgstdate`
- ⚠️ 날짜 파싱 포맷 불일치
  - API 응답: `YYYY-MM-DD HH:MM:SS.0`
  - 파싱 시도: `%Y%m%d` (YYYYMMDD 형식)
  - 해결 필요: split()[0]로 날짜 부분만 추출 후 파싱

---

#### Day 5 (2025-11-06): Data Collectors 구현 (Part 2)
**목표**: 공공예약 API 통합 및 데이터 프로세서 구현

**Tasks**:
- [ ] `collectors/reservations_collector.py`
  - [ ] `/ListPublicReservationMedical` API 호출
  - [ ] `/ListPublicReservationEducation` API 호출
  - [ ] `/ListPublicReservationCulture` API 호출
  - [ ] `/tvYeyakCOllect` API 호출
  - [ ] 4개 API 결과 통합 및 중복 제거
  - [ ] 예약 상태 필드 정규화
- [ ] `collectors/data_processor.py` 구현
  - [ ] 데이터 정규화 (공백 제거, 대소문자 통일)
  - [ ] 필수 필드 검증 (위도, 경도, 이름)
  - [ ] 중복 데이터 감지 (api_id 기준)
  - [ ] 데이터 품질 점수 계산
- [ ] 통합 테스트 (9개 API 전체 수집)

**산출물**:
- 공공예약 통합 Collector
- 데이터 프로세서 완성
- 통합 테스트 통과

---

#### Day 6 (2025-11-07): 데이터 수집 스크립트 및 스케줄러
**목표**: 자동 수집 시스템 구축

**Tasks**:
- [ ] `scripts/collect_all.py` 작성
  - [ ] 9개 Collector 순차 실행
  - [ ] 진행상황 표시 (tqdm)
  - [ ] Supabase Upsert (중복 시 업데이트)
  - [ ] Firebase 백업 동기화
  - [ ] 수집 로그 저장 (`collection_logs` 테이블)
- [ ] `scripts/scheduler.py` 작성
  - [ ] APScheduler 설정
  - [ ] Cron jobs 정의:
    - 매일 03:00 - 문화행사, 공공예약
    - 매주 월요일 - 도서관, 문화공간
    - 매월 1일 - 미래유산
  - [ ] 에러 알림 (로그 기록)
- [ ] `scripts/data_quality_check.py` 작성
  - [ ] 좌표 범위 검증 (서울시 내)
  - [ ] 중복 레코드 체크
  - [ ] 누락 필드 리포트
- [ ] 초기 데이터 수집 실행 (실제 API 호출)

**산출물**:
- 자동 수집 스크립트 완성
- 스케줄러 설정 완료
- Supabase에 데이터 저장 완료

---

#### Day 7 (2025-11-08): Week 1 마무리 및 검증
**목표**: 데이터 품질 검증 및 문서화

**Tasks**:
- [ ] 전체 데이터 수집 테스트
  - [ ] 9개 API 모두 성공 확인
  - [ ] 총 레코드 수 확인 (예상: 10,000+)
- [ ] 데이터 품질 리포트 생성
  - [ ] 카테고리별 레코드 수
  - [ ] 좌표 범위 분포
  - [ ] 에러율 (<5% 목표)
- [ ] 성능 테스트
  - [ ] 전체 수집 시간 측정 (<30분 목표)
  - [ ] 메모리 사용량 확인
- [ ] Week 1 완료 리포트 작성
  - [ ] 달성 목표 체크리스트
  - [ ] 데이터 통계
  - [ ] 발견된 이슈 및 해결책
- [ ] GitHub에 코드 푸시
- [ ] 다음 주 계획 검토

**산출물**:
- Week 1 완료 리포트 (Markdown)
- 데이터 수집 완료 (Supabase)
- 자동 스케줄러 운영 시작

---

### Week 2: Backend API 개발 (Day 8-14)

#### Day 8 (2025-11-09): FastAPI 프로젝트 설정
**목표**: FastAPI 기반 REST API 기본 구조 구축

**Tasks**:
- [ ] `backend/app/main.py` 생성
  - [ ] FastAPI 앱 초기화
  - [ ] CORS 미들웨어 설정
  - [ ] 라우터 등록
  - [ ] Health check endpoint (`/health`)
- [ ] `app/core/config.py` 작성
  - [ ] pydantic-settings 기반 환경변수 관리
  - [ ] Supabase, Redis, Kakao 설정
- [ ] `app/api/v1/router.py` 생성
  - [ ] API 버전 관리 구조
- [ ] `app/db/supabase_client.py` 구현
  - [ ] Supabase 클라이언트 싱글톤
  - [ ] 연결 풀 설정
- [ ] `app/db/models.py` 작성
  - [ ] Pydantic 모델 정의 (5개 테이블)
- [ ] API 문서 설정 (Swagger UI)
- [ ] 개발 서버 실행 테스트

**산출물**:
- FastAPI 기본 구조 완성
- Swagger UI 접근 가능 ([http://localhost:8000/docs](http://localhost:8000/docs))

---

#### Day 9 (2025-11-10): Redis 캐싱 및 유틸리티
**목표**: 캐싱 레이어 구현 및 공통 유틸리티 작성

**Tasks**:
- [ ] `app/core/services/redis_service.py` 구현
  - [ ] Upstash Redis 클라이언트 연결
  - [ ] 캐시 키 생성 전략 (좌표 반올림)
  - [ ] TTL 5분 설정
  - [ ] Get/Set/Delete 메서드
- [ ] `app/core/services/distance_service.py` 구현
  - [ ] Haversine 거리 계산 함수
  - [ ] 반경 내 필터링 함수
  - [ ] 거리순 정렬 함수
- [ ] `app/utils/coordinate_transform.py` 구현
  - [ ] TM → WGS84 변환 (pyproj)
  - [ ] 좌표 검증 (범위 체크)
- [ ] `app/utils/cache.py` 구현
  - [ ] 캐시 데코레이터 (`@cache_response`)
  - [ ] 캐시 무효화 로직
- [ ] 단위 테스트 작성

**산출물**:
- Redis 캐싱 서비스 완성
- 거리 계산 모듈 완성
- 유틸리티 함수 테스트 통과

---

#### Day 10 (2025-11-11): LangGraph Agent - LocationAnalyzer
**목표**: 위치 분석 에이전트 구현

**Tasks**:
- [ ] LangGraph 프로젝트 구조 설계
- [ ] `app/core/agents/location_analyzer.py` 구현
  - [ ] 입력: 사용자 위치 (위도/경도 또는 주소)
  - [ ] Kakao Map API 주소→좌표 변환 연동
  - [ ] 좌표 정규화 (소수점 6자리)
  - [ ] 반경 설정 (default: 2000m)
  - [ ] 카테고리 우선순위 설정
  - [ ] 출력: `AnalyzedLocation` 상태
- [ ] Kakao Map Geocoding API 클라이언트 구현
- [ ] 에이전트 단위 테스트
  - [ ] 위도/경도 입력 테스트
  - [ ] 주소 입력 테스트
  - [ ] 잘못된 입력 에러 핸들링

**산출물**:
- LocationAnalyzer 에이전트 완성
- Kakao Geocoding 연동 완료

---

#### Day 11 (2025-11-12): LangGraph Agent - ServiceFetcher & ResponseGenerator
**목표**: 서비스 조회 및 응답 생성 에이전트 구현

**Tasks**:
- [ ] `app/core/agents/service_fetcher.py` 구현
  - [ ] 입력: `AnalyzedLocation` 상태
  - [ ] PostGIS 공간 쿼리 (`ST_DWithin`)
  - [ ] Redis 캐시 조회 (히트 시 바로 반환)
  - [ ] Supabase 쿼리 (캐시 미스 시)
  - [ ] Haversine 거리 계산 및 정렬
  - [ ] Redis 캐시 저장 (TTL 5분)
  - [ ] 출력: `FetchedServices` 상태
- [ ] `app/core/agents/response_generator.py` 구현
  - [ ] 입력: `FetchedServices` 상태
  - [ ] 카테고리별 그룹화
  - [ ] Kakao Map 마커 데이터 생성
  - [ ] (선택적) Ollama LLM 추천 텍스트 생성
  - [ ] 출력: JSON 응답
- [ ] 에이전트 통합 테스트
  - [ ] 캐시 히트/미스 시나리오
  - [ ] 거리 계산 정확도 검증

**산출물**:
- ServiceFetcher 에이전트 완성
- ResponseGenerator 에이전트 완성
- Redis 캐싱 동작 확인

---

#### Day 12 (2025-11-13): LangGraph Workflow 및 API 엔드포인트 (Part 1)
**목표**: 3-에이전트 워크플로우 구축 및 주요 API 구현

**Tasks**:
- [ ] `app/core/workflow/service_graph.py` 구현
  - [ ] LangGraph StateGraph 정의
  - [ ] 3개 에이전트 연결 (LocationAnalyzer → ServiceFetcher → ResponseGenerator)
  - [ ] 상태 전달 로직
  - [ ] 에러 핸들링 (각 노드별)
- [ ] `app/api/v1/endpoints/services.py` 구현
  - [ ] `GET /api/v1/services/nearby`
    - Query params: lat, lon, radius, categories, limit
    - LangGraph 워크플로우 호출
    - Redis 캐싱 적용
  - [ ] `GET /api/v1/services/{category}`
    - 카테고리별 필터링
    - 정렬 옵션 (distance, name, date)
- [ ] API 응답 스키마 정의 (Pydantic)
- [ ] 통합 테스트 (워크플로우 전체 실행)

**산출물**:
- LangGraph 워크플로우 완성
- 2개 API 엔드포인트 구현

---

#### Day 13 (2025-11-14): API 엔드포인트 (Part 2)
**목표**: 나머지 API 엔드포인트 구현

**Tasks**:
- [ ] `app/api/v1/endpoints/services.py` 추가 구현
  - [ ] `GET /api/v1/services/{category}/{id}`
    - 서비스 상세 정보 조회
    - 주변 서비스 추천 (반경 500m)
- [ ] `app/api/v1/endpoints/geocode.py` 구현
  - [ ] `POST /api/v1/geocode`
    - 주소 → 좌표 변환 (Kakao API)
    - 역방향 지오코딩 (좌표 → 주소)
- [ ] `app/api/v1/endpoints/recommendations.py` 구현
  - [ ] `POST /api/v1/recommendations`
    - 사용자 선호도 파싱
    - Ollama LLM 기반 추천
    - Fallback 로직 (LLM 실패 시 거리 기반)
- [ ] API 의존성 주입 (`app/api/dependencies.py`)
  - [ ] Supabase 클라이언트 주입
  - [ ] Redis 클라이언트 주입
- [ ] 전체 API 테스트 (Pytest)

**산출물**:
- 6개 API 엔드포인트 완성
- Pytest 테스트 커버리지 >70%

---

#### Day 14 (2025-11-15): Week 2 마무리 - 성능 최적화
**목표**: API 성능 최적화 및 문서화

**Tasks**:
- [ ] 데이터베이스 쿼리 최적화
  - [ ] EXPLAIN ANALYZE 실행
  - [ ] 느린 쿼리 튜닝
  - [ ] 인덱스 추가 검토
- [ ] API 응답 속도 벤치마크
  - [ ] 캐시 히트: <50ms 목표
  - [ ] 캐시 미스: <200ms 목표
- [ ] 동시 요청 부하 테스트 (locust)
  - [ ] 100 RPS 처리 확인
- [ ] Vercel Serverless 최적화
  - [ ] Cold start 시간 측정
  - [ ] 번들 사이즈 최소화
- [ ] API 문서 작성
  - [ ] Swagger 설명 추가
  - [ ] 예제 요청/응답
- [ ] Week 2 완료 리포트 작성
  - [ ] API 성능 지표
  - [ ] 테스트 결과
  - [ ] 다음 주 계획

**산출물**:
- API 응답 속도 <200ms 달성
- Swagger 문서 완성
- Week 2 완료 리포트

---

### Week 3: Frontend 개발 (Day 15-21)

#### Day 15 (2025-11-16): React 프로젝트 설정
**목표**: React + Vite 프로젝트 구축 및 기본 설정

**Tasks**:
- [ ] Vite React TypeScript 프로젝트 생성
- [ ] Tailwind CSS 설정
  - [ ] `tailwind.config.js` 작성
  - [ ] 커스텀 색상 팔레트 정의
- [ ] shadcn/ui 설정
  - [ ] `components.json` 생성
  - [ ] 필요한 컴포넌트 설치 (Button, Card, Dialog, etc.)
- [ ] React Query 설정
  - [ ] `QueryClientProvider` 설정
  - [ ] devtools 활성화
- [ ] Zustand 스토어 설정
  - [ ] `stores/locationStore.ts` 생성
  - [ ] 위치 상태 관리
- [ ] 프로젝트 구조 생성
  - [ ] `components/`, `hooks/`, `services/`, `stores/`, `types/`
- [ ] Kakao Map SDK 스크립트 로드 (`index.html`)
- [ ] 개발 서버 실행 확인

**산출물**:
- React 프로젝트 기본 구조 완성
- Tailwind + shadcn/ui 설정 완료

---

#### Day 16 (2025-11-17): API 클라이언트 및 훅 구현
**목표**: Backend API 통신 레이어 구축

**Tasks**:
- [ ] `services/api.ts` 구현
  - [ ] axios 인스턴스 생성
  - [ ] baseURL 설정 (환경변수)
  - [ ] 요청/응답 인터셉터
  - [ ] 에러 핸들링
- [ ] API 함수 작성
  - [ ] `getNearbyServices(lat, lon, radius, categories)`
  - [ ] `getServicesByCategory(category, lat, lon)`
  - [ ] `getServiceDetail(category, id)`
  - [ ] `geocodeAddress(address)`
- [ ] `types/services.ts` 타입 정의
  - [ ] Service 인터페이스
  - [ ] Category 열거형
  - [ ] API 응답 타입
- [ ] `hooks/useServices.ts` 구현
  - [ ] React Query 기반 데이터 페칭
  - [ ] 자동 캐싱 (5분)
  - [ ] 로딩/에러 상태 관리
- [ ] `hooks/useLocation.ts` 구현
  - [ ] Geolocation API 래퍼
  - [ ] 위치 권한 요청
  - [ ] 위치 업데이트 감지
- [ ] 단위 테스트 (Vitest)

**산출물**:
- API 클라이언트 완성
- 커스텀 훅 구현
- 타입 정의 완료

---

#### Day 17 (2025-11-18): Kakao Map 컴포넌트 개발
**목표**: Kakao Map 기본 기능 구현

**Tasks**:
- [ ] `services/kakao.ts` 구현
  - [ ] Kakao SDK 타입 정의
  - [ ] 지도 초기화 함수
  - [ ] 마커 생성/제거 함수
- [ ] `hooks/useKakaoMap.ts` 구현
  - [ ] 지도 인스턴스 관리
  - [ ] 마커 상태 관리
  - [ ] 지도 이벤트 리스너
- [ ] `components/map/KakaoMap.tsx` 구현
  - [ ] 지도 컨테이너 렌더링
  - [ ] 초기 중심 좌표 설정 (서울시청)
  - [ ] 줌 레벨 제어
  - [ ] 현재 위치 마커 표시
  - [ ] 지도 이동 이벤트 핸들러
- [ ] 반응형 디자인 (전체 화면)
- [ ] 테스트 (지도 로딩 확인)

**산출물**:
- Kakao Map 컴포넌트 완성
- 지도 초기화 동작 확인

---

#### Day 18 (2025-11-19): 마커 및 오버레이 컴포넌트
**목표**: 서비스 마커 표시 및 클러스터링 구현

**Tasks**:
- [ ] `components/map/MarkerCluster.tsx` 구현
  - [ ] 카테고리별 마커 색상 정의
    - 문화행사: 빨강, 도서관: 파랑, 문화공간: 초록, 공공예약: 주황, 미래유산: 보라
  - [ ] 마커 클러스터링 로직 (1km 기준)
  - [ ] 클러스터 클릭 시 확대
  - [ ] 마커 클릭 이벤트 핸들러
- [ ] `components/map/CustomOverlay.tsx` 구현
  - [ ] 마커 클릭 시 미리보기 카드 표시
  - [ ] 서비스 이름, 카테고리, 거리 표시
  - [ ] "상세보기" 버튼
  - [ ] 닫기 버튼
- [ ] 마커 아이콘 디자인 (SVG)
- [ ] 오버레이 스타일링 (Tailwind)
- [ ] 성능 최적화 (가상화, 메모이제이션)

**산출물**:
- 카테고리별 마커 표시
- 클러스터링 동작 확인
- 마커 클릭 시 오버레이 표시

---

#### Day 19 (2025-11-20): 서비스 목록 UI (Part 1)
**목표**: 좌측 패널 서비스 목록 구현

**Tasks**:
- [ ] `components/location/LocationInput.tsx` 구현
  - [ ] 주소 검색 입력창 (Kakao Postcode API)
  - [ ] 자동완성 기능
  - [ ] 검색 버튼
- [ ] `components/location/CurrentLocation.tsx` 구현
  - [ ] GPS 위치 버튼
  - [ ] 위치 권한 요청 프롬프트
  - [ ] 로딩 스피너
- [ ] `components/services/ServiceList.tsx` 구현
  - [ ] 카테고리 필터 (체크박스)
  - [ ] 정렬 옵션 (거리순, 이름순, 날짜순)
  - [ ] 무한 스크롤 (React Query Infinite Query)
  - [ ] 로딩/에러/빈 상태 UI
- [ ] 반응형 레이아웃
  - [ ] 모바일: 하단 시트
  - [ ] 데스크톱: 좌측 사이드바
- [ ] 애니메이션 (Framer Motion)

**산출물**:
- 위치 입력 컴포넌트 완성
- 서비스 목록 패널 완성

---

#### Day 20 (2025-11-21): 서비스 목록 UI (Part 2)
**목표**: 서비스 카드 및 상세 정보 모달 구현

**Tasks**:
- [ ] `components/services/ServiceCard.tsx` 구현
  - [ ] 썸네일 이미지 (lazy loading)
  - [ ] 서비스 이름, 카테고리 배지
  - [ ] 거리 표시 (예: "1.2km")
  - [ ] 주소 (1줄 요약)
  - [ ] 즐겨찾기 버튼 (로컬 스토리지)
  - [ ] 호버 효과
- [ ] `components/services/ServiceDetail.tsx` 구현
  - [ ] shadcn/ui Dialog 사용
  - [ ] 상세 정보 표시
    - 이미지 슬라이더
    - 운영 시간, 휴관일
    - 전화번호, 홈페이지 링크
    - 예약 링크 (공공예약 서비스)
  - [ ] 공유 기능 (Web Share API)
  - [ ] 길찾기 버튼 (Kakao Map 앱 연동)
  - [ ] 주변 서비스 추천 (API 호출)
- [ ] 접근성 개선 (ARIA labels, 키보드 네비게이션)

**산출물**:
- 서비스 카드 컴포넌트 완성
- 상세 정보 모달 완성

---

#### Day 21 (2025-11-22): Week 3 마무리 - UX 개선
**목표**: 반응형 디자인 및 사용자 경험 최적화

**Tasks**:
- [ ] 모바일 최적화 (375px ~ 768px)
  - [ ] 터치 제스처 지원 (지도 핀치 줌)
  - [ ] 하단 시트 드래그 기능
  - [ ] 작은 화면 레이아웃 조정
- [ ] 로딩/에러 상태 UI 개선
  - [ ] Skeleton UI (지도, 서비스 카드)
  - [ ] 에러 바운더리 (React Error Boundary)
  - [ ] Retry 버튼
- [ ] 다크모드 지원 (선택적)
  - [ ] 색상 팔레트 정의
  - [ ] 시스템 설정 감지
  - [ ] 토글 버튼
- [ ] 성능 최적화
  - [ ] 이미지 최적화 (WebP, lazy loading)
  - [ ] 컴포넌트 메모이제이션 (React.memo)
  - [ ] 번들 사이즈 분석 (vite-bundle-visualizer)
- [ ] 접근성 검증 (axe DevTools)
- [ ] 크로스 브라우저 테스트 (Chrome, Safari, Samsung Internet)
- [ ] Week 3 완료 리포트 작성
  - [ ] UI/UX 스크린샷
  - [ ] 성능 지표 (Lighthouse)
  - [ ] 발견된 이슈

**산출물**:
- 반응형 UI 완성
- Lighthouse 성능 점수 >90
- Week 3 완료 리포트

---

### Week 4: 통합 및 배포 (Day 22-28)

#### Day 22 (2025-11-23): Vercel 배포 설정
**목표**: Frontend 및 Backend Vercel 배포

**Tasks**:
- [ ] Frontend Vercel 배포
  - [ ] `frontend/vercel.json` 작성
  - [ ] Vercel 프로젝트 생성
  - [ ] 환경변수 설정 (Kakao API Key)
  - [ ] Git 연동 (자동 배포)
  - [ ] 프로덕션 도메인 확인
- [ ] Backend Vercel Serverless 배포
  - [ ] `backend/vercel.json` 작성 (Serverless Functions)
  - [ ] Python 런타임 설정 (3.11)
  - [ ] 환경변수 설정 (Supabase, Redis, Seoul API)
  - [ ] Cold start 최적화 (경량 패키지)
- [ ] CORS 설정 업데이트 (프로덕션 도메인)
- [ ] API Base URL 업데이트 (Frontend .env)
- [ ] 배포 테스트 (프로덕션 환경)

**산출물**:
- Frontend 배포 완료 (예: seoul-services.vercel.app)
- Backend 배포 완료 (예: seoul-services-api.vercel.app)

---

#### Day 23 (2025-11-24): CI/CD 파이프라인 구축
**목표**: GitHub Actions 자동 배포 설정

**Tasks**:
- [ ] `.github/workflows/frontend-deploy.yml` 작성
  - [ ] Node.js 18 설치
  - [ ] 의존성 설치 (`npm ci`)
  - [ ] 빌드 (`npm run build`)
  - [ ] 테스트 (`npm test`)
  - [ ] Vercel 배포
- [ ] `.github/workflows/backend-deploy.yml` 작성
  - [ ] Python 3.11 설치
  - [ ] 의존성 설치 (`pip install -r requirements.txt`)
  - [ ] Pytest 실행
  - [ ] Vercel 배포
- [ ] `.github/workflows/data-collection.yml` 작성
  - [ ] 매일 03:00 KST 실행 (GitHub Actions Cron)
  - [ ] 데이터 수집 스크립트 실행
- [ ] GitHub Secrets 설정
  - [ ] Vercel Token
  - [ ] API Keys
- [ ] 배포 테스트 (Push to main)

**산출물**:
- CI/CD 파이프라인 완성
- 자동 배포 동작 확인

---

#### Day 24 (2025-11-25): E2E 테스트
**목표**: Playwright 기반 통합 테스트 작성

**Tasks**:
- [ ] Playwright 설정
  - [ ] `npm install -D @playwright/test`
  - [ ] `playwright.config.ts` 작성
- [ ] E2E 테스트 시나리오 작성
  - [ ] **시나리오 1**: 현재 위치 조회
    - GPS 위치 허용
    - 지도 중심 이동 확인
    - 주변 서비스 마커 표시 확인
  - [ ] **시나리오 2**: 주소 검색
    - 주소 입력 ("서울시청")
    - 검색 결과 선택
    - 지도 이동 및 마커 표시
  - [ ] **시나리오 3**: 카테고리 필터링
    - "도서관" 카테고리 선택
    - 도서관 마커만 표시 확인
  - [ ] **시나리오 4**: 서비스 상세보기
    - 마커 클릭
    - 오버레이 표시 확인
    - "상세보기" 클릭
    - 모달 열림 확인
- [ ] 테스트 실행 및 디버깅

**산출물**:
- E2E 테스트 스위트 완성
- 테스트 커버리지 >80%

---

#### Day 25 (2025-11-26): 성능 및 보안 테스트
**목표**: Lighthouse, 부하 테스트, 보안 점검

**Tasks**:
- [ ] Lighthouse 성능 테스트
  - [ ] Performance >90 목표
  - [ ] Accessibility >95 목표
  - [ ] Best Practices >90 목표
  - [ ] SEO >90 목표
  - [ ] 개선 사항 적용
- [ ] 부하 테스트 (locust)
  - [ ] 동시 사용자 100명 시뮬레이션
  - [ ] API 응답 시간 P95 <500ms 확인
  - [ ] 에러율 <1% 확인
- [ ] 보안 점검
  - [ ] API 키 노출 확인 (프론트엔드 소스)
  - [ ] CORS 설정 검증
  - [ ] SQL Injection 테스트
  - [ ] XSS 방어 확인
  - [ ] HTTPS 강제 확인
- [ ] 크로스 브라우저 테스트
  - [ ] Chrome, Safari, Firefox
  - [ ] iOS Safari, Samsung Internet
- [ ] 모바일 디바이스 테스트
  - [ ] iPhone (iOS 16+)
  - [ ] Android (Chrome)

**산출물**:
- Lighthouse 점수 >90 달성
- 보안 취약점 0건
- 크로스 브라우저 호환성 확인

---

#### Day 26 (2025-11-27): 모니터링 및 분석 설정
**목표**: 운영 모니터링 도구 설정

**Tasks**:
- [ ] Vercel Analytics 설정
  - [ ] Web Vitals 추적
  - [ ] 페이지 뷰 추적
- [ ] Sentry 에러 추적 설정
  - [ ] Sentry 프로젝트 생성 (무료 티어)
  - [ ] Frontend SDK 설치
  - [ ] Backend SDK 설치
  - [ ] Source Maps 업로드
- [ ] Supabase 모니터링
  - [ ] 데이터베이스 사용량 대시보드
  - [ ] 느린 쿼리 확인
- [ ] Upstash Redis 모니터링
  - [ ] 캐시 히트율 확인
  - [ ] 사용량 대시보드
- [ ] 사용자 피드백 폼 생성
  - [ ] Google Forms 연동
  - [ ] 앱 내 "피드백 보내기" 버튼

**산출물**:
- 모니터링 대시보드 완성
- 에러 추적 시스템 동작

---

#### Day 27 (2025-11-28): 문서화 및 최적화
**목표**: 최종 문서 작성 및 비용 최적화

**Tasks**:
- [ ] `README.md` 최종 업데이트
  - [ ] 프로젝트 소개
  - [ ] 기능 설명 (GIF/스크린샷)
  - [ ] 기술 스택
  - [ ] 배포 URL
  - [ ] 로컬 개발 가이드
- [ ] API 문서 공개
  - [ ] Swagger UI 접근 URL
  - [ ] 예제 코드 (cURL, JavaScript)
- [ ] 사용자 가이드 작성
  - [ ] "처음 사용자" 튜토리얼
  - [ ] 주요 기능 설명
  - [ ] FAQ
- [ ] 개발자 문서 작성
  - [ ] 프로젝트 구조 설명
  - [ ] 기여 가이드 (CONTRIBUTING.md)
  - [ ] 코드 스타일 가이드
- [ ] 비용 최적화 체크리스트
  - [ ] Vercel 대역폭 사용량 확인 (<100GB)
  - [ ] Supabase DB 사이즈 확인 (<500MB)
  - [ ] Upstash 명령 수 확인 (<10,000/일)
  - [ ] 이미지 최적화 (WebP)
  - [ ] 번들 사이즈 최소화 (<500KB)
- [ ] 라이선스 파일 추가 (MIT)

**산출물**:
- 완전한 문서화
- 비용 최적화 완료 ($0/월 유지)

---

#### Day 28 (2025-11-29): 런칭 및 프로젝트 완료
**목표**: 공식 런칭 및 피드백 수집

**Tasks**:
- [ ] 프로덕션 배포 최종 확인
  - [ ] 모든 기능 동작 확인
  - [ ] API 응답 확인
  - [ ] 지도 로딩 확인
  - [ ] 에러 로그 확인 (Sentry)
- [ ] 런칭 공지
  - [ ] GitHub 저장소 공개
  - [ ] README 배지 추가 (Vercel 배포 상태)
  - [ ] 소셜 미디어 공유 (선택적)
- [ ] 초기 사용자 피드백 수집
  - [ ] 테스트 사용자 초대 (10명)
  - [ ] 피드백 폼 응답 수집
- [ ] 버그 리포트 대응
  - [ ] GitHub Issues 모니터링
  - [ ] 긴급 버그 수정
- [ ] Week 4 완료 리포트 작성
  - [ ] 최종 성과 지표
    - MAU 목표: 1,000+
    - API 응답 속도: <200ms
    - Lighthouse 점수: >90
    - 월 비용: $0
  - [ ] 배포 URL 및 문서 링크
  - [ ] 다음 단계 계획 (Phase 2)
- [ ] **프로젝트 완료 축하!** 🎉

**산출물**:
- 공식 런칭 완료
- 초기 사용자 피드백 수집
- 최종 프로젝트 리포트

---

## 마일스톤 요약

| 주차 | 기간 | 목표 | 완료 기준 |
|------|------|------|-----------|
| **Week 1** | Day 1-7 | 데이터 수집 파이프라인 | ✅ Supabase에 10,000+ 레코드 저장 |
| **Week 2** | Day 8-14 | Backend API 개발 | ✅ 6개 API 엔드포인트, 응답 <200ms |
| **Week 3** | Day 15-21 | Frontend 개발 | ✅ Kakao Map 통합, Lighthouse >90 |
| **Week 4** | Day 22-28 | 배포 및 운영 | ✅ Vercel 배포, E2E 테스트 >80% |

## 위험 관리

### 일정 지연 대응책
- **Week 1 지연**: Week 2에서 API 엔드포인트 수 축소 (필수 3개만)
- **Week 2 지연**: Week 3에서 고급 UI 기능 제외 (다크모드, 무한 스크롤)
- **Week 3 지연**: Week 4에서 E2E 테스트 범위 축소
- **Week 4 지연**: 런칭 연기, 버그 수정 우선

### 기술적 문제 대응책
- **Seoul API 장애**: Firebase 백업 데이터 사용
- **Vercel 무료 티어 한도**: Cloudflare Pages 대체 고려
- **Kakao Map API 이슈**: Naver Map API로 전환 (2일 소요)
- **LangGraph 복잡도**: 단순 함수 체이닝으로 대체

---

**마지막 업데이트**: 2025-11-02
**다음 리뷰**: Week 1 종료 후 (Day 7)
