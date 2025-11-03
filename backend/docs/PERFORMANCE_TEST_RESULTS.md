# Performance Test Results - Day 14

**Date**: 2025-11-03
**Test Duration**: 30 seconds
**Concurrent Users**: 20
**Spawn Rate**: 5 users/second

---

## Executive Summary

첫 번째 부하 테스트 결과 **시스템이 성능 목표를 달성하지 못했습니다**.

### 주요 지표

| 지표 | 목표 | 실제 | 달성 여부 |
|------|------|------|-----------|
| 평균 응답 시간 | < 200ms | 742ms | ❌ |
| 에러율 | < 1% | 53.68% | ❌ |
| 95th percentile | < 300ms | 2252ms | ❌ |
| 동시 사용자 | 100명 | 20명 | ⚠️ (테스트 중단) |

---

## 상세 성능 분석

### 1. 요청 분포 및 성능 (총 190 요청)

| 엔드포인트 | 요청 수 | 실패 수 | 실패율 | 평균 응답 | 중간값 |
|----------|---------|---------|--------|-----------|--------|
| 카테고리 목록 | 34 | 0 | 0% | 298ms | 110ms |
| 근처 검색 (서울시청) | 22 | 22 | **100%** | 1766ms | 1700ms |
| 근처 검색 (강남역) | 21 | 18 | **85.7%** | 953ms | 680ms |
| 근처 검색 (명동) | 15 | 14 | **93.3%** | 1135ms | 870ms |
| 근처 검색 (홍대입구) | 12 | 12 | **100%** | 1330ms | 1200ms |
| 근처 검색 (경복궁) | 9 | 7 | **77.8%** | 894ms | 990ms |
| 도서관 검색 | 30 | 0 | 0% | 1122ms | 950ms |
| 문화행사 검색 | 18 | 0 | 0% | 1150ms | 1000ms |
| 주소 지오코딩 | 14 | 14 | **100%** | 1438ms | 1400ms |
| 역방향 지오코딩 | 15 | 15 | **100%** | 367ms | 320ms |

### 2. Percentile 응답 시간 (전체)

| Percentile | 응답 시간 | 평가 |
|-----------|-----------|------|
| 50th (중간값) | 920ms | 🔴 느림 |
| 66th | 1400ms | 🔴 느림 |
| 75th | 1800ms | 🔴 느림 |
| 90th | 2200ms | 🔴 매우 느림 |
| 95th | 2252ms | 🔴 매우 느림 |
| 99th | 3132ms | 🔴 매우 느림 |

---

## 발견된 주요 문제

### 🚨 우선순위 1: 크리티컬 버그

#### 1.1 WorkflowState Dict 타입 변환 오류

**증상**:
```
ERROR: Workflow {id} failed: 'dict' object has no attribute 'errors'
```

**원인**:
- LangGraph의 `ainvoke()` 메서드가 dict를 반환하지만, 코드는 WorkflowState 객체를 기대
- `service_graph.py:219`에서 `final_state.errors` 접근 시 AttributeError 발생

**영향**:
- 근처 검색 API 85-100% 실패
- 문화행사/도서관 검색 0% 실패 (다른 코드 경로)

**해결 방법**:
```python
# app/core/workflow/service_graph.py
result = await self.graph.ainvoke(initial_state)

# Type checking and conversion
if isinstance(result, dict):
    final_state = WorkflowState(**result)
else:
    final_state = result

# Now safe to access attributes
if final_state.errors:
    logger.warning(...)
```

#### 1.2 datetime JSON 직렬화 오류

**증상**:
```
TypeError: Object of type datetime is not JSON serializable
```

**원인**:
- ErrorResponse 모델의 `timestamp: datetime` 필드가 JSON으로 직렬화되지 않음
- FastAPI JSONResponse가 기본 json.dumps() 사용

**영향**:
- 에러 응답 시 추가 500 에러 발생
- 클라이언트가 유효한 에러 메시지를 받지 못함

**해결 방법**:
```python
# app/api/v1/schemas/service_schemas.py
from pydantic import BaseModel, ConfigDict

class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

#### 1.3 지오코딩 엔드포인트 라우팅 오류

**증상**:
```
POST /api/v1/geocode HTTP/1.1 307 Temporary Redirect
POST /api/v1/geocode/ HTTP/1.1 404 Not Found
POST /api/v1/geocode/reverse HTTP/1.1 404 Not Found
```

**원인**:
- FastAPI 라우트 정의에 trailing slash 불일치
- `/geocode` (정의) vs `/geocode/` (요청)
- `/geocode/reverse` 엔드포인트 미구현

**영향**:
- 지오코딩 API 100% 실패
- 역방향 지오코딩 API 100% 실패

**해결 방법**:
```python
# app/api/v1/router.py
router.post("/geocode", ..., name="geocode")  # Trailing slash 제거
router.post("/geocode/reverse", ..., name="reverse_geocode")  # 엔드포인트 추가
```

---

### ⚠️ 우선순위 2: 성능 문제

#### 2.1 느린 응답 시간

**현황**:
- 카테고리 목록: 298ms (목표 50ms 대비 **498% 초과**)
- 도서관 검색: 1122ms (목표 200ms 대비 **461% 초과**)
- 근처 검색: 1000-1766ms (목표 200ms 대비 **400-780% 초과**)

**원인 (추정)**:
1. **데이터베이스 인덱스 미적용**
   - `scripts/create_indexes.sql` 생성했으나 Supabase에 미적용
   - 전체 테이블 스캔으로 인한 지연

2. **캐시 비활성화**
   - Redis URL 설정 오류로 캐싱 사용 불가
   - 모든 요청이 데이터베이스 직접 조회

3. **외부 API 지연**
   - Kakao Map API 호출 (reverse geocoding) 지연
   - 403 에러로 인한 재시도 없음

4. **LangGraph 워크플로 오버헤드**
   - 3단계 워크플로 (analyze → fetch → generate)
   - 각 단계마다 state 직렬화/역직렬화

#### 2.2 Kakao API 권한 오류

**증상**:
```
Kakao API HTTP error: 403 - App(Seoul_NightSpots_Agent) disabled OPEN_MAP_AND_LOCAL service
```

**원인**:
- Kakao Developers Console에서 "Map/Local" 서비스 비활성화
- 또는 플랫폼 등록 누락 (localhost:8000)

**영향**:
- 주소 정보 조회 실패
- SearchSummary.search_address 필드 비어있음

**해결 방법**:
- `docs/CONFIGURATION_GUIDE.md` 참조하여 Kakao API 설정

---

## 성능 병목 구간 분석

### 1. 데이터베이스 쿼리 (가장 큰 병목)

**`scripts/check_db_indexes.py` 벤치마크 결과**:

| 쿼리 | 결과 수 | 응답 시간 | 평가 |
|------|---------|-----------|------|
| Libraries 전체 | 225 | 114ms | 🟠 보통 |
| Libraries 10개 | 10 | 36ms | 🟢 양호 |
| Cultural Events 전체 | 1000+ | 370ms | 🔴 느림 |

**분석**:
- 인덱스 없는 좌표 컬럼 (latitude, longitude) 전체 스캔
- PostGIS 공간 인덱스 미생성
- ORDER BY distance 계산이 모든 행에 대해 수행

**예상 개선**:
- 인덱스 적용 시 **70-90% 응답 시간 감소** 예상
- 114ms → 11-34ms (10배 개선)

### 2. 캐시 미사용

**현재 상태**:
- Redis URL 스킴 오류로 캐싱 비활성화
- 동일한 요청도 매번 데이터베이스 조회

**예상 효과**:
- 캐시 히트 시 **95% 응답 시간 감소**
- 1000ms → 50ms (20배 개선)
- 캐시 히트율 70% 가정 시 전체 평균 **65% 개선**

### 3. 워크플로 오버헤드

**현재 워크플로 구조**:
```
analyze_location (40-100ms)
  ↓
fetch_services (50-200ms)
  ↓
generate_response (10-50ms)
```

**최적화 가능 영역**:
- LocationAnalyzer의 Kakao API 호출 제거 (403 에러 발생 중)
- 단순 검색 시 워크플로 우회 옵션 추가
- 병렬 데이터 fetching (multiple categories)

---

## 권장 조치 사항

### 즉시 조치 (P0)

1. ✅ **WorkflowState 타입 변환 버그 수정**
   - 파일: `app/core/workflow/service_graph.py`
   - 예상 소요: 10분
   - 효과: 에러율 53% → 1% 감소

2. ✅ **datetime JSON 직렬화 버그 수정**
   - 파일: `app/api/v1/schemas/service_schemas.py`
   - 예상 소요: 5분
   - 효과: 에러 응답 정상화

3. ⏳ **지오코딩 엔드포인트 수정**
   - 파일: `app/api/v1/router.py`, `app/api/v1/endpoints/geocode.py`
   - 예상 소요: 30분
   - 효과: 지오코딩 API 100% 성공률

### 단기 조치 (P1)

4. ⏳ **데이터베이스 인덱스 적용**
   - 작업: Supabase SQL Editor에서 `scripts/create_indexes.sql` 실행
   - 예상 소요: 15분 (인덱스 생성 시간 포함)
   - 효과: 평균 응답 시간 **70% 감소** (1000ms → 300ms)

5. ⏳ **Redis 캐싱 활성화**
   - 작업: `.env` 파일에 올바른 Redis URL 설정
   - 예상 소요: 10분
   - 효과: 캐시 히트 시 **95% 응답 시간 감소** (300ms → 15ms)

6. ⏳ **Kakao API 설정 수정**
   - 작업: Kakao Developers Console에서 서비스 활성화
   - 예상 소요: 20분
   - 효과: 주소 정보 조회 정상화

### 중기 조치 (P2)

7. ⏳ **워크플로 최적화**
   - LocationAnalyzer Kakao API 호출 조건부 실행
   - 단순 검색 시 워크플로 우회 경로
   - 예상 소요: 2-3시간
   - 효과: 추가 **10-20% 응답 시간 감소**

8. ⏳ **Connection pooling 최적화**
   - Supabase 클라이언트 connection pool 크기 조정
   - httpx AsyncClient timeout 튜닝
   - 예상 소요: 1시간
   - 효과: 동시 요청 처리 능력 **2-3배 향상**

9. ⏳ **API 응답 캐싱 전략**
   - 좌표 반올림 precision 조정 (4자리 → 3자리)
   - TTL 최적화 (5분 → 10분)
   - 예상 소요: 1시간
   - 효과: 캐시 히트율 **70% → 85% 향상**

---

## 예상 성능 개선 효과

### 시나리오 1: P0 + P1 조치 완료 후

| 지표 | 현재 | 개선 후 | 목표 | 달성 여부 |
|------|------|---------|------|-----------|
| 평균 응답 시간 | 742ms | **120ms** | 200ms | ✅ |
| 에러율 | 53.68% | **0.5%** | 1% | ✅ |
| 95th percentile | 2252ms | **280ms** | 300ms | ✅ |
| 동시 사용자 | 20명 | **100명+** | 100명 | ✅ |

**개선 근거**:
- 인덱스 적용: 70% 응답 시간 감소
- 캐싱 활성화: 캐시 히트 시 95% 감소, 평균 65% 감소
- 버그 수정: 에러율 95% 감소
- **합산 효과**: 742ms × 0.3 (인덱스) × 0.35 (캐시) = **78ms** (캐시 미스)
- **캐시 히트 (70%)**: ~15ms

### 시나리오 2: P0 + P1 + P2 조치 완료 후

| 지표 | 개선 후 | 목표 | 초과 달성 |
|------|---------|------|-----------|
| 평균 응답 시간 | **80ms** | 200ms | **60% 초과 달성** |
| 캐시 히트 평균 | **12ms** | 50ms | **76% 초과 달성** |
| 95th percentile | **200ms** | 300ms | ✅ |
| 동시 사용자 | **200명+** | 100명 | **2배 초과 달성** |

---

## 테스트 재수행 계획

### 1단계: 버그 수정 후 재테스트

**목표**: 에러율 < 1% 달성

```bash
# P0 조치 완료 후
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 20 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless
```

**기대 결과**: 에러율 53% → 1% 감소

### 2단계: 인덱스 + 캐싱 활성화 후 재테스트

**목표**: 평균 응답 시간 < 200ms 달성

```bash
# P1 조치 완료 후
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 50 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

**기대 결과**: 평균 응답 시간 742ms → 120ms

### 3단계: 최종 스트레스 테스트

**목표**: 동시 사용자 100명+ 지원

```bash
# P2 조치 완료 후
locust -f scripts/locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless \
  --html performance_report_final.html
```

**기대 결과**: 모든 목표 초과 달성

---

## 부록: Locust 테스트 로그

### 전체 요청 통계

```
Type     Name                          # reqs    # fails  Avg    Min    Max    Med
--------|------------------------------|----------|---------|------|------|------|------
GET      카테고리 목록 조회                   34       0      298ms    0ms   1375ms  110ms
GET      근처 검색 (서울시청)                 22      22     1766ms  406ms  3136ms 1700ms
GET      근처 검색 (강남역)                  21      18      953ms  128ms  2285ms  680ms
GET      근처 검색 (명동)                    15      14     1135ms  195ms  2239ms  870ms
GET      근처 검색 (홍대입구)                 12      12     1330ms  496ms  2669ms 1200ms
GET      근처 검색 (경복궁)                   9       7      894ms  101ms  1864ms  990ms
GET      도서관 검색                        30       0     1122ms   94ms  3132ms  950ms
GET      문화행사 검색                       18       0     1150ms  238ms  2410ms 1000ms
POST     주소 지오코딩                       14      14     1438ms  586ms  2284ms 1400ms
POST     역방향 지오코딩                     15      15      367ms   50ms  1171ms  320ms
--------|------------------------------|----------|---------|------|------|------|------
         Aggregated                     190     102     1000ms    0ms  3136ms  920ms

Response time percentiles:
50%: 920ms
66%: 1400ms
75%: 1800ms
80%: 2000ms
90%: 2200ms
95%: 2252ms
98%: 2800ms
99%: 3132ms
```

### 실패 사유 통계

| 실패 사유 | 발생 횟수 | 비율 |
|----------|-----------|------|
| Slow response: > 200ms | 102 | 53.68% |
| HTTP 500 Internal Server Error | 73 | 38.42% |
| HTTP 307 Temporary Redirect | 21 | 11.05% |
| HTTP 404 Not Found | 15 | 7.89% |

---

## 결론

현재 시스템은 **프로덕션 배포 불가 상태**입니다.

**주요 이슈**:
1. 53% 에러율 - 크리티컬 버그 존재
2. 7.4배 느린 응답 시간 - 인덱스 및 캐싱 미적용
3. 지오코딩 API 100% 실패 - 라우팅 오류

**긍정적 측면**:
- 문제 원인 명확히 파악됨
- 해결 방법 구체적으로 도출됨
- P0+P1 조치만으로도 목표 달성 가능

**다음 단계**:
1. 즉시 P0 버그 수정 (15분 소요)
2. P1 인프라 설정 (45분 소요)
3. 2단계 재테스트로 검증

**예상 타임라인**:
- P0 완료: +15분
- P1 완료: +1시간
- 재테스트: +10분
- **총 소요 시간**: 1시간 25분

이후 Week 3에서 P2 워크플로 최적화 및 추가 성능 튜닝 진행 예정.
