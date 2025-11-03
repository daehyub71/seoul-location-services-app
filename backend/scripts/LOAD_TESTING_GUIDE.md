# Load Testing Guide - Seoul Location Services API

## Overview

이 가이드는 서울 위치 서비스 API의 동시 요청 부하 테스트를 수행하는 방법을 설명합니다.

## 성능 목표

### 응답 시간
- **카테고리 목록 조회**: < 50ms (캐시 히트 기대)
- **근처 서비스 검색**: < 200ms (캐시 미스), < 50ms (캐시 히트)
- **카테고리별 검색**: < 200ms
- **지오코딩**: < 200ms

### 안정성
- **에러율**: < 1%
- **95th percentile 응답 시간**: < 300ms
- **동시 사용자**: 100명 이상 지원

## Prerequisites

### 1. Locust 설치

```bash
cd /Users/sunchulkim/src/seoul-location-services-app/backend
source venv/bin/activate
pip install locust
```

### 2. API 서버 실행

**터미널 1: Backend API**
```bash
cd /Users/sunchulkim/src/seoul-location-services-app/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버 확인:
```bash
curl http://localhost:8000/health
```

## 부하 테스트 실행

### 방법 1: Web UI (권장)

**터미널 2: Locust 실행**
```bash
cd /Users/sunchulkim/src/seoul-location-services-app/backend
source venv/bin/activate
locust -f scripts/locustfile.py --host http://localhost:8000
```

**웹 브라우저 접속**:
- URL: http://localhost:8089
- Number of users: 100 (동시 사용자 수)
- Spawn rate: 10 (초당 증가 사용자 수)
- Host: http://localhost:8000 (이미 설정됨)

**Start 버튼 클릭** → 실시간 통계 확인

**실시간 모니터링**:
- Statistics: 각 엔드포인트별 응답 시간, RPS, 실패율
- Charts: 시간대별 응답 시간 그래프
- Failures: 에러 로그
- Exceptions: 예외 발생 내역
- Current ratio: 요청 분포

### 방법 2: Headless (CLI)

**단일 시나리오 테스트 (2분)**:
```bash
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless
```

**점진적 부하 증가 테스트 (5분)**:
```bash
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

**스트레스 테스트 (고부하, 10분)**:
```bash
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 200 \
  --spawn-rate 20 \
  --run-time 10m \
  --headless
```

## 테스트 시나리오

### 1. 요청 분포 (가중치 기반)

| 엔드포인트 | 가중치 | 설명 |
|----------|--------|------|
| 카테고리 목록 | 5 | 가장 빈번한 요청 (캐시 효과) |
| 근처 검색 | 10 | 가장 중요한 기능 |
| 문화행사 검색 | 3 | 카테고리별 검색 |
| 도서관 검색 | 3 | 카테고리별 검색 |
| 주소 지오코딩 | 2 | 주소 변환 |
| 역방향 지오코딩 | 1 | 좌표 변환 |

**총 가중치**: 24
- 근처 검색이 전체 요청의 ~42% 차지

### 2. 테스트 데이터

**좌표 (5개 지역 순환)**:
- 서울시청: 37.5665, 126.9780
- 강남역: 37.5172, 127.0473
- 명동: 37.5510, 126.9882
- 홍대입구: 37.5660, 126.9014
- 경복궁: 37.5797, 126.9770

**카테고리 (5개 순환)**:
- cultural_events
- libraries
- cultural_spaces
- future_heritages
- public_reservations

### 3. 대기 시간

각 사용자는 요청 사이에 **1~3초 대기** (실제 사용자 패턴 시뮬레이션)

## 결과 해석

### Web UI 지표

**Statistics 탭**:
```
Name                    # reqs  # fails  Avg    Min    Max  Median  req/s
카테고리 목록 조회        500      0      15     10     50    14     8.3
근처 검색 (서울시청)     1000     5      120    80     300   110    16.7
문화행사 검색            300      2      150    100    400   140    5.0
...
```

**목표 달성 기준**:
- ✅ Avg < 200ms (근처 검색, 카테고리별 검색)
- ✅ Avg < 50ms (카테고리 목록)
- ✅ Failures < 1%
- ✅ 95th percentile < 300ms (Charts 탭에서 확인)

### Headless 출력

테스트 종료 시 자동으로 요약 출력:

```
================================================================================
부하 테스트 결과 요약
================================================================================
총 요청 수: 5000
성공: 4985
실패: 15
에러율: 0.30%

평균 응답 시간: 125.50ms
중간값 응답 시간: 110.00ms
95th percentile: 280.00ms
99th percentile: 450.00ms

목표 달성:
  ✅ 평균 응답 < 200ms
  ✅ 95th percentile < 300ms
  ✅ 에러율 < 1%
================================================================================
```

## 문제 해결

### 1. 높은 응답 시간

**증상**: 평균 응답 시간 > 200ms

**원인 및 해결**:
- **캐시 미활성화**: Redis 설정 확인
  ```bash
  curl http://localhost:8000/api/v1/cache/stats
  ```
- **데이터베이스 인덱스 누락**: 인덱스 적용
  ```bash
  # Supabase SQL Editor에서 실행
  cat scripts/create_indexes.sql
  ```
- **외부 API 지연**: Kakao API 응답 시간 확인

### 2. 높은 에러율

**증상**: Failures > 1%

**원인 및 해결**:
- **API 서버 과부하**: 동시 사용자 수 감소
  ```bash
  locust ... --users 50 --spawn-rate 5
  ```
- **타임아웃**: FastAPI worker 수 증가
  ```bash
  uvicorn app.main:app --workers 4
  ```
- **Kakao API 실패**: API 키 및 권한 확인
  ```bash
  grep KAKAO_MAP .env
  ```

### 3. Connection Refused

**증상**: 연결 실패 에러

**해결**:
- API 서버 실행 확인
  ```bash
  curl http://localhost:8000/health
  ```
- 포트 충돌 확인
  ```bash
  lsof -i :8000
  ```

## 성능 최적화 체크리스트

### Backend

- [ ] Redis 캐싱 활성화 (CACHE_ENABLED=true)
- [ ] 데이터베이스 인덱스 적용 (create_indexes.sql)
- [ ] FastAPI worker 수 증가 (--workers 4)
- [ ] Connection pooling 설정 확인
- [ ] 불필요한 로깅 제거 (LOG_LEVEL=WARNING)

### Database

- [ ] Supabase 인덱스 생성
- [ ] PostGIS 공간 인덱스 확인
- [ ] 테이블 통계 업데이트 (ANALYZE)

### Caching

- [ ] Redis TTL 설정 (REDIS_CACHE_TTL=300)
- [ ] 캐시 히트율 모니터링 (목표: > 70%)
- [ ] 캐시 키 전략 검토 (좌표 반올림 precision=4)

### External APIs

- [ ] Kakao API 응답 시간 모니터링
- [ ] 타임아웃 설정 (timeout=5s)
- [ ] Retry 로직 구현
- [ ] Fallback 전략 (캐시된 결과 반환)

## 고급 테스트 시나리오

### 1. 캐시 웜업 테스트

**목적**: 캐시 효과 측정

```bash
# Step 1: 캐시 초기화
curl -X POST http://localhost:8000/api/v1/cache/flush

# Step 2: 첫 번째 실행 (캐시 미스)
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 1m \
  --headless

# Step 3: 두 번째 실행 (캐시 히트)
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 1m \
  --headless
```

**기대 결과**: 두 번째 실행의 평균 응답 시간이 50% 이상 감소

### 2. 점진적 부하 증가 (Spike Test)

**목적**: 급격한 트래픽 증가 대응 능력 측정

```bash
# 50명 → 200명으로 급증
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 200 \
  --spawn-rate 50 \
  --run-time 5m \
  --headless
```

### 3. 지속 부하 테스트 (Soak Test)

**목적**: 장시간 안정성 검증

```bash
# 30분 동안 100명 유지
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 30m \
  --headless
```

**모니터링**:
- 메모리 누수 확인
- 캐시 히트율 추이
- 에러율 변화

## 보고서 생성

### CSV Export (Web UI)

Web UI에서:
1. Statistics 탭 → "Download Data" → CSV 다운로드
2. Excel로 열어서 차트 생성

### HTML Report (Headless)

```bash
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html report.html
```

생성된 `report.html` 파일을 브라우저로 열어서 확인

## 참고 자료

- **Locust 공식 문서**: https://docs.locust.io/
- **FastAPI 성능 최적화**: https://fastapi.tiangolo.com/deployment/
- **Redis 캐싱 전략**: https://redis.io/docs/manual/patterns/
- **PostgreSQL 인덱싱**: https://www.postgresql.org/docs/current/indexes.html

## 문의

부하 테스트 관련 문의사항은 프로젝트 이슈 트래커에 등록해주세요.
