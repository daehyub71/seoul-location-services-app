# Vercel 환경 변수 설정 가이드

Seoul Location Services 애플리케이션을 Vercel에 배포하는 데 필요한 모든 환경 변수를 정리한 문서입니다.

## Frontend 환경 변수

Vercel Frontend 프로젝트 설정에서 구성하세요 (Settings → Environment Variables):

### 필수 변수

| 변수명 | 설명 | 예시 값 | 발급 위치 |
|-------|-----|--------|----------|
| `VITE_KAKAO_MAP_API_KEY` | 지도 시각화를 위한 Kakao JavaScript API Key | `your_kakao_javascript_key` | [Kakao Developers Console](https://developers.kakao.com/console/app) |
| `VITE_API_BASE_URL` | Backend API 기본 URL | `https://your-backend.vercel.app` | Vercel Backend 배포 URL |

### 선택 변수

| 변수명 | 설명 | 기본값 |
|-------|-----|--------|
| `VITE_APP_NAME` | 애플리케이션 이름 | `Seoul Location Services` |
| `VITE_APP_VERSION` | 애플리케이션 버전 | `1.0.0` |
| `VITE_DEFAULT_LAT` | 기본 지도 중심 위도 (서울시청) | `37.5665` |
| `VITE_DEFAULT_LON` | 기본 지도 중심 경도 | `126.9780` |
| `VITE_DEFAULT_ZOOM` | 기본 지도 줌 레벨 | `5` |
| `VITE_ENABLE_DARK_MODE` | 다크모드 기능 활성화 | `false` |
| `VITE_ENABLE_LLM_RECOMMENDATIONS` | LLM 기반 추천 기능 활성화 | `false` |
| `VITE_ENABLE_ANALYTICS` | 분석 추적 활성화 | `false` |
| `VITE_SENTRY_DSN` | Sentry 에러 추적 DSN | (비어있음) |
| `VITE_GA_TRACKING_ID` | Google Analytics 추적 ID | (비어있음) |

### Kakao JavaScript API Key 설정

1. [Kakao Developers Console](https://developers.kakao.com/console/app) 로 이동
2. 새 애플리케이션 생성 또는 기존 애플리케이션 선택
3. **앱 설정** → **플랫폼** → **Web** 으로 이동
4. Vercel 도메인 추가: `https://your-app.vercel.app`
5. 로컬 개발 도메인 추가: `http://localhost:5173`
6. **JavaScript 키** 복사 (REST API Key 아님!)
7. 저장 후 변경사항 적용을 위해 5-10분 대기

---

## Backend 환경 변수

Vercel Backend 프로젝트 설정에서 구성하세요 (Settings → Environment Variables):

### 필수 변수 - 데이터베이스

| 변수명 | 설명 | 예시 값 | 발급 위치 |
|-------|-----|--------|----------|
| `SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxx.supabase.co` | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase Dashboard → Settings → API → anon/public |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (관리자) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase Dashboard → Settings → API → service_role (⚠️ 비밀 유지!) |
| `SUPABASE_DATABASE_URL` | PostgreSQL 연결 문자열 | `postgresql://postgres.xxx:password@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres` | Supabase Dashboard → Settings → Database → Connection string (Session mode) |

### 필수 변수 - 캐시

| 변수명 | 설명 | 예시 값 | 발급 위치 |
|-------|-----|--------|----------|
| `UPSTASH_URL` | Upstash Redis REST URL | `https://xxx.upstash.io` | [Upstash Console](https://console.upstash.com/) → Database → REST API |
| `UPSTASH_TOKEN` | Upstash Redis REST token | `AbCdEfGhIjKlMnOpQrStUvWxYz...` | Upstash Console → Database → REST API |
| `REDIS_URL` | Redis URL (UPSTASH_URL과 동일) | `https://xxx.upstash.io` | UPSTASH_URL과 동일 |

### 필수 변수 - 외부 API

| 변수명 | 설명 | 예시 값 | 발급 위치 |
|-------|-----|--------|----------|
| `SEOUL_API_KEY` | 서울 Open API 인증키 | `your_seoul_api_key` | [서울 열린데이터광장](https://data.seoul.go.kr/) → 회원가입 → 인증키 신청 |
| `KAKAO_REST_API_KEY` | 지오코딩용 Kakao REST API key | `your_kakao_rest_api_key` | [Kakao Developers Console](https://developers.kakao.com/console/app) → 앱 설정 → REST API Key |

### 선택 변수 - 설정

| 변수명 | 설명 | 기본값 |
|-------|-----|--------|
| `ENVIRONMENT` | 배포 환경 | `production` |
| `LOG_LEVEL` | 로깅 레벨 | `INFO` |
| `API_VERSION` | API 버전 접두사 | `v1` |
| `REDIS_CACHE_TTL` | 캐시 TTL (초) | `300` (5분) |
| `CACHE_ENABLED` | Redis 캐싱 활성화 | `true` |
| `COLLECTION_SCHEDULE_ENABLED` | 예약된 데이터 수집 활성화 | `false` (서버리스에서는 비활성화) |
| `COLLECTION_RETRY_COUNT` | API 실패 시 재시도 횟수 | `3` |
| `COLLECTION_TIMEOUT` | API 요청 타임아웃 (초) | `30` |
| `RATE_LIMIT_ENABLED` | API 요청 제한 활성화 | `true` |
| `RATE_LIMIT_PER_MINUTE` | 분당 요청 제한 | `100` |
| `CORS_ORIGINS_EXTRA` | 추가 CORS origin (쉼표로 구분) | (비어있음) |

### 선택 변수 - 고급 기능

| 변수명 | 설명 | 예시 값 |
|-------|-----|--------|
| `FIREBASE_DATABASE_URL` | Firebase Realtime Database URL | `https://xxx.firebaseio.com` |
| `FIREBASE_ADMIN_SDK_PATH` | Firebase Admin SDK JSON 경로 | `./firebase-admin-sdk.json` |
| `OLLAMA_BASE_URL` | Ollama API 기본 URL (서버리스에서는 비권장) | `http://localhost:11434` |
| `OLLAMA_LLM_MODEL` | Ollama LLM 모델명 | `llama3.1:8b` |
| `OLLAMA_EMBED_MODEL` | Ollama 임베딩 모델명 | `bge-m3` |

---

## 설정 방법

### 1. Frontend 배포

```bash
# frontend 디렉토리로 이동
cd frontend

# Vercel CLI 설치 (설치되지 않은 경우)
npm install -g vercel

# Vercel 로그인
vercel login

# Vercel에 배포 (첫 배포)
vercel

# 프롬프트 따라가기:
# - Set up and deploy? Yes
# - Which scope? (계정 선택)
# - Link to existing project? No
# - Project name? seoul-location-services-frontend
# - Directory? ./
# - Override settings? No

# Vercel 대시보드에서 환경 변수 설정
# 이동: https://vercel.com/dashboard
# → 프로젝트 선택 → Settings → Environment Variables
# → 모든 필수 frontend 변수 추가

# 프로덕션 배포
vercel --prod
```

### 2. Backend 배포

```bash
# backend 디렉토리로 이동
cd backend

# Vercel에 배포 (첫 배포)
vercel

# 프롬프트 따라가기:
# - Set up and deploy? Yes
# - Which scope? (계정 선택)
# - Link to existing project? No
# - Project name? seoul-location-services-backend
# - Directory? ./
# - Override settings? No

# Vercel 대시보드에서 환경 변수 설정
# 이동: https://vercel.com/dashboard
# → 프로젝트 선택 → Settings → Environment Variables
# → 모든 필수 backend 변수 추가

# 프로덕션 배포
vercel --prod
```

### 3. Frontend API URL 업데이트

Backend 배포 후:

1. Backend Vercel URL 확인 (예: `https://seoul-location-services-backend.vercel.app`)
2. Vercel 대시보드에서 Frontend 프로젝트로 이동
3. Settings → Environment Variables
4. `VITE_API_BASE_URL`을 backend URL로 업데이트
5. Frontend 재배포: `vercel --prod`

### 4. Backend CORS 업데이트

Backend는 이미 다음을 허용하도록 설정되어 있습니다:
- `https://seoul-location-services.vercel.app`
- `https://*.vercel.app` (모든 Vercel 프리뷰 배포)

커스텀 도메인 사용 시:
1. Vercel 대시보드에서 Backend 프로젝트로 이동
2. Settings → Environment Variables
3. 커스텀 도메인으로 `CORS_ORIGINS_EXTRA` 추가 (쉼표로 구분)
4. 예시: `https://myapp.com,https://www.myapp.com`

---

## 검증

### Frontend 헬스 체크

접속: `https://your-frontend.vercel.app`

예상 결과: Kakao Map 시각화와 함께 지도가 로드되어야 함

### Backend 헬스 체크

접속: `https://your-backend.vercel.app/health`

예상 JSON 응답:
```json
{
  "status": "healthy",
  "version": "v1",
  "environment": "production",
  "cache_enabled": true
}
```

### API 문서

접속: `https://your-backend.vercel.app/docs`

예상 결과: 인터랙티브 FastAPI/Swagger 문서

---

## 문제 해결

### Frontend 문제

**문제**: 지도가 로드되지 않음
- **해결**: `VITE_KAKAO_MAP_API_KEY`가 올바른 JavaScript key인지 확인 (REST API key 아님)
- **해결**: Kakao Developer Console에 도메인이 등록되었는지 확인

**문제**: Backend에 연결할 수 없음
- **해결**: `VITE_API_BASE_URL`이 올바른 backend URL을 가리키는지 확인
- **해결**: Backend CORS가 frontend 도메인을 허용하는지 확인

### Backend 문제

**문제**: 500 Internal Server Error
- **해결**: 모든 필수 환경 변수가 설정되었는지 확인
- **해결**: Supabase와 Redis 자격 증명이 올바른지 확인
- **해결**: Vercel Dashboard → Deployments → View Function Logs에서 로그 확인

**문제**: 데이터베이스 연결 타임아웃
- **해결**: `SUPABASE_DATABASE_URL`이 Session 모드를 사용하는지 확인 (Transaction 모드 아님)
- **해결**: 연결 문자열에 올바른 비밀번호가 포함되었는지 확인

**문제**: Redis 연결 실패
- **해결**: `UPSTASH_URL`과 `UPSTASH_TOKEN`이 올바른지 확인
- **해결**: REST API 엔드포인트(https) 사용, Redis 프로토콜(redis://) 아님

**문제**: CORS 에러
- **해결**: `CORS_ORIGINS_EXTRA` 환경 변수에 frontend 도메인 추가
- **해결**: 도메인에 프로토콜(https://)이 포함되고 끝에 슬래시가 없는지 확인

---

## 보안 Best Practices

1. **`.env` 파일을 절대 커밋하지 마세요** git에
2. **민감한 데이터는 Vercel의 비밀 환경 변수 사용**
3. **API 키 정기적으로 로테이션** (특히 service_role 키)
4. **프리뷰 배포에 Vercel의 비밀번호 보호 활성화**
5. **API 사용량 모니터링**으로 비정상적인 활동 감지
6. **Supabase Row Level Security (RLS) 사용**으로 데이터 보호
7. **모니터링을 위해 Vercel의 Web Analytics 활성화**

---

## 모니터링 및 유지보수

### Vercel 대시보드

- **Deployments**: 배포 히스토리 및 로그 확인
- **Analytics**: 트래픽 및 성능 모니터링
- **Functions**: 서버리스 함수 메트릭 확인
- **Logs**: 실시간 함수 로그

### Supabase 대시보드

- **Table Editor**: 데이터 확인 및 관리
- **SQL Editor**: 커스텀 쿼리 실행
- **API**: API 사용량 모니터링
- **Logs**: 데이터베이스 및 API 로그

### Upstash 대시보드

- **Database**: Redis 데이터 확인
- **Analytics**: 캐시 히트율 모니터링
- **Metrics**: 메모리 사용량 및 작업

---

## 비용 예측

### Vercel (Hobby 플랜 - 무료)
- ✅ 무제한 배포
- ✅ 월 100 GB 대역폭
- ✅ 서버리스 함수 실행 포함
- ⚠️ 함수 타임아웃: 10초 (60초로 업그레이드 가능)

### Supabase (무료 티어)
- ✅ 500 MB 데이터베이스 저장소
- ✅ 2 GB 파일 저장소
- ✅ 월 50,000 활성 사용자
- ✅ 무제한 API 요청

### Upstash Redis (무료 티어)
- ✅ 일 10,000 명령
- ✅ 256 MB 저장소
- ✅ 1개 데이터베이스

### 서울 Open API
- ✅ API 키로 무료
- ⚠️ 속도 제한 적용 (엔드포인트마다 다름)

### Kakao API
- ✅ 지도 및 지오코딩 무료
- ⚠️ 속도 제한: 일 300,000 요청

---

## 다음 단계

1. ✅ Supabase 프로젝트 및 테이블 설정
2. ✅ Upstash Redis 인스턴스 설정
3. ✅ 서울 Open API 키 등록
4. ✅ Kakao Developer 계정 등록
5. ✅ 모든 환경 변수 설정
6. ✅ Vercel에 backend 배포
7. ✅ Vercel에 frontend 배포
8. ✅ 헬스 체크로 배포 검증
9. 🔄 커스텀 도메인 설정 (선택사항)
10. 🔄 모니터링 및 분석 활성화
11. 🔄 GitHub 통합으로 CI/CD 설정

---

## 지원

문제나 질문이 있으면:
- **Vercel 문서**: https://vercel.com/docs
- **Supabase 문서**: https://supabase.com/docs
- **Kakao Developers**: https://developers.kakao.com/docs
- **서울 열린데이터광장**: https://data.seoul.go.kr/

---

**마지막 업데이트**: 2025-11-05
**버전**: 1.0.0
