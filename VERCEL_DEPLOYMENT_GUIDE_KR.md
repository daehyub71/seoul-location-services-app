# Vercel 배포 가이드

Seoul Location Services를 Vercel에 배포하기 위한 완전한 단계별 가이드입니다.

## 목차

1. [사전 준비사항](#사전-준비사항)
2. [프로젝트 구조](#프로젝트-구조)
3. [Backend 배포](#backend-배포)
4. [Frontend 배포](#frontend-배포)
5. [배포 후 설정](#배포-후-설정)
6. [검증](#검증)
7. [CI/CD 설정](#cicd-설정)
8. [문제 해결](#문제-해결)

---

## 사전 준비사항

### 필수 계정

1. **Vercel 계정**: https://vercel.com 에서 회원가입
2. **Supabase 계정**: https://supabase.com 에서 회원가입
3. **Upstash 계정**: https://upstash.com 에서 회원가입
4. **Kakao Developers 계정**: https://developers.kakao.com 에서 회원가입
5. **서울 열린데이터광장 계정**: https://data.seoul.go.kr 에서 회원가입

### 필수 도구

```bash
# Node.js 설치 (v18 이상)
node --version  # 버전 확인

# Vercel CLI 설치
npm install -g vercel

# 설치 확인
vercel --version
```

### GitHub 저장소

코드가 GitHub에 푸시되어 있는지 확인:
```bash
git remote -v
git push origin main
```

---

## 프로젝트 구조

```
seoul-location-services-app/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── vercel.json          ✅ 생성 완료
│   └── .env.example
├── backend/
│   ├── app/
│   ├── api/
│   │   └── index.py         ✅ 생성 완료 (Vercel handler)
│   ├── requirements.txt
│   ├── vercel.json          ✅ 생성 완료
│   └── .env.example
├── VERCEL_ENV_VARIABLES_KR.md   ✅ 생성 완료
└── VERCEL_DEPLOYMENT_GUIDE_KR.md ✅ 이 문서
```

---

## Backend 배포

### 단계 1: Backend 준비

```bash
# backend 디렉토리로 이동
cd backend

# vercel.json 파일 확인
cat vercel.json

# api/index.py 파일 확인
cat api/index.py
```

### 단계 2: Vercel 로그인

```bash
# Vercel에 로그인
vercel login

# 인증 방법 선택:
# - GitHub
# - GitLab
# - Bitbucket
# - Email
```

### 단계 3: Backend 첫 배포

```bash
# Vercel 프로젝트 초기화
vercel

# 프롬프트를 따라가세요:
```

**프롬프트와 답변:**

```
? Set up and deploy "~/seoul-location-services-app/backend"? [Y/n]
→ Y

? Which scope do you want to deploy to?
→ (Vercel 계정 선택)

? Link to existing project? [y/N]
→ N

? What's your project's name?
→ seoul-location-services-backend

? In which directory is your code located?
→ ./

? Want to override the settings? [y/N]
→ N
```

**예상 출력:**

```
🔗  Linked to your-account/seoul-location-services-backend
🔍  Inspect: https://vercel.com/your-account/seoul-location-services-backend/[deployment-id]
✅  Preview: https://seoul-location-services-backend-[hash].vercel.app
```

### 단계 4: Backend 환경 변수 설정

1. Vercel 대시보드로 이동: https://vercel.com/dashboard
2. 프로젝트 선택: **seoul-location-services-backend**
3. **Settings** → **Environment Variables** 로 이동
4. [VERCEL_ENV_VARIABLES_KR.md](./VERCEL_ENV_VARIABLES_KR.md)에서 모든 필수 변수 추가

**필수 변수** (반드시 설정):

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres.xxx:password@...

# Redis
UPSTASH_URL=https://xxx.upstash.io
UPSTASH_TOKEN=AbCdEfGhIjKlMnOpQrStUvWxYz...
REDIS_URL=https://xxx.upstash.io

# APIs
SEOUL_API_KEY=your_seoul_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key

# 설정
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_ENABLED=true
COLLECTION_SCHEDULE_ENABLED=false  # ⚠️ Serverless에서는 비활성화
```

**중요**: **Production**, **Preview**, **Development** 모두에 환경 변수 설정

### 단계 5: 프로덕션 배포

```bash
# 프로덕션 배포
vercel --prod

# 예상 출력:
✅  Production: https://seoul-location-services-backend.vercel.app
```

### 단계 6: Backend 배포 검증

```bash
# 헬스 엔드포인트 테스트
curl https://your-backend.vercel.app/health

# 예상 응답:
{
  "status": "healthy",
  "version": "v1",
  "environment": "production",
  "cache_enabled": true
}

# API 문서 확인
open https://your-backend.vercel.app/docs
```

---

## Frontend 배포

### 단계 1: Frontend 준비

```bash
# frontend 디렉토리로 이동
cd ../frontend

# vercel.json 파일 확인
cat vercel.json

# 빌드 테스트 (선택사항)
npm install
npm run build
```

### 단계 2: Frontend 첫 배포

```bash
# Vercel 프로젝트 초기화
vercel

# 프롬프트를 따라가세요:
```

**프롬프트와 답변:**

```
? Set up and deploy "~/seoul-location-services-app/frontend"? [Y/n]
→ Y

? Which scope do you want to deploy to?
→ (Vercel 계정 선택)

? Link to existing project? [y/N]
→ N

? What's your project's name?
→ seoul-location-services-frontend

? In which directory is your code located?
→ ./

? Want to override the settings? [y/N]
→ N
```

### 단계 3: Frontend 환경 변수 설정

1. Vercel 대시보드로 이동: https://vercel.com/dashboard
2. 프로젝트 선택: **seoul-location-services-frontend**
3. **Settings** → **Environment Variables** 로 이동
4. 필수 변수 추가:

**필수 변수**:

```bash
# Backend API URL (backend 배포에서 확인)
VITE_API_BASE_URL=https://seoul-location-services-backend.vercel.app

# Kakao JavaScript Key (REST API Key 아님!)
VITE_KAKAO_MAP_API_KEY=your_kakao_javascript_key

# 앱 설정 (선택사항)
VITE_APP_NAME=Seoul Location Services
VITE_APP_VERSION=1.0.0
VITE_DEFAULT_LAT=37.5665
VITE_DEFAULT_LON=126.9780
VITE_DEFAULT_ZOOM=5
VITE_ENABLE_DARK_MODE=false
VITE_ENABLE_LLM_RECOMMENDATIONS=false
VITE_ENABLE_ANALYTICS=false
```

### 단계 4: Kakao JavaScript Key 설정

1. [Kakao Developers 콘솔](https://developers.kakao.com/console/app) 로 이동
2. 애플리케이션 선택
3. **앱 설정** → **플랫폼** → **Web** 으로 이동
4. **플랫폼 추가** 클릭 → **Web** 선택
5. 도메인 추가:
   - `https://seoul-location-services-frontend.vercel.app`
   - `https://*.vercel.app` (프리뷰 배포용)
   - `http://localhost:5173` (로컬 개발용)
6. **저장** 클릭
7. **JavaScript 키** 복사 (요약 페이지에서 확인)
8. DNS 전파를 위해 5-10분 대기

### 단계 5: 프로덕션 배포

```bash
# 프로덕션 배포
vercel --prod

# 예상 출력:
✅  Production: https://seoul-location-services-frontend.vercel.app
```

### 단계 6: Frontend 배포 검증

1. 브라우저에서 열기: https://your-frontend.vercel.app
2. 확인 사항:
   - ✅ Kakao Map이 정상적으로 로드됨
   - ✅ 지도에 위치 서비스가 표시됨
   - ✅ 서비스 목록에 데이터가 표시됨
   - ✅ 마커 클릭 시 모든 데이터가 포함된 InfoWindow가 표시됨
   - ✅ 브라우저 콘솔에 CORS 에러가 없음

---

## 배포 후 설정

### 1. Backend CORS 업데이트 (필요시)

커스텀 도메인 사용 시 backend 환경 변수에 추가:

```bash
# Vercel 대시보드 → Backend 프로젝트 → Settings → Environment Variables
CORS_ORIGINS_EXTRA=https://myapp.com,https://www.myapp.com
```

### 2. 커스텀 도메인 설정 (선택사항)

**Frontend:**
1. Frontend 프로젝트 → **Settings** → **Domains** 로 이동
2. **Add Domain** 클릭
3. 도메인 입력: `myapp.com`
4. DNS 설정 안내를 따라 진행
5. Vercel이 자동으로 SSL 인증서 발급

**Backend:**
1. Backend 프로젝트 → **Settings** → **Domains** 로 이동
2. **Add Domain** 클릭
3. 도메인 입력: `api.myapp.com`
4. DNS 설정 안내를 따라 진행

**Frontend 환경 변수 업데이트:**
```bash
VITE_API_BASE_URL=https://api.myapp.com
```

### 3. Vercel Analytics 활성화 (선택사항)

1. Frontend 프로젝트 → **Analytics** 로 이동
2. **Enable Analytics** 클릭
3. 실시간 트래픽 및 Web Vitals 확인

### 4. 프리뷰 배포 비밀번호 보호 (선택사항)

1. 프로젝트 → **Settings** → **General** 로 이동
2. **Deployment Protection** 으로 스크롤
3. **Password Protection** 활성화
4. 프리뷰 배포용 비밀번호 설정

---

## CI/CD 설정

### Git 통합으로 자동 배포

Vercel은 GitHub에 푸시할 때 자동으로 배포합니다:

**프로덕션 배포:**
```bash
git push origin main  # 프로덕션 배포
```

**프리뷰 배포:**
```bash
git push origin feature-branch  # 프리뷰 배포 생성
```

### Git 통합 설정

1. 프로젝트 → **Settings** → **Git** 로 이동
2. GitHub 저장소 연결
3. 설정:
   - **Production Branch**: `main`
   - **Preview Branches**: 모든 브랜치
   - **Auto-deploy**: 활성화

### 환경별 브랜치

다른 환경 설정:

1. **Settings** → **Environment Variables** 로 이동
2. 다른 값 설정:
   - **Production**: Main 브랜치
   - **Preview**: Feature 브랜치
   - **Development**: 로컬 개발

---

## 검증 체크리스트

### Backend 헬스 체크

- [ ] Health 엔드포인트 응답: `/health`
- [ ] API 문서 접근 가능: `/docs`
- [ ] 샘플 API 호출 작동: `/api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000`
- [ ] Redis 캐시 작동 (응답 시간 확인)
- [ ] 데이터베이스 연결 성공
- [ ] Function 로그에 에러 없음

### Frontend 헬스 체크

- [ ] 홈페이지 로딩 성공
- [ ] Kakao Map 정상 표시
- [ ] 마커가 지도에 표시됨
- [ ] InfoWindow에 모든 데이터 표시
- [ ] 서비스 목록 데이터 로딩
- [ ] 서비스 항목 클릭 시 InfoWindow 표시
- [ ] 콘솔에 CORS 에러 없음
- [ ] 콘솔에 JavaScript 에러 없음

### 통합 테스트

```bash
# 주변 서비스 API 테스트
curl "https://your-backend.vercel.app/api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000"

# 예상: 서비스 배열이 포함된 JSON 응답

# Frontend-Backend 통합 테스트
open https://your-frontend.vercel.app
# 지도 클릭 → 마커 로드 확인
# 마커 클릭 → InfoWindow 표시 확인
# 서비스 목록 항목 클릭 → InfoWindow 표시 확인
```

---

## 문제 해결

### 일반적인 Backend 문제

#### 문제: FUNCTION_INVOCATION_FAILED (Function Crash)

**증상:**
- "This Serverless Function has crashed" 에러
- "FUNCTION_INVOCATION_FAILED" 메시지
- "Python process exited with exit status: 1"

**원인:**
- 잘못된 handler 형식 사용 (예: AWS Lambda 형식)
- Vercel은 ASGI/WSGI `app` 변수 또는 `BaseHTTPRequestHandler` 클래스 필요

**해결책:**
```python
# ❌ 잘못된 방식 (AWS Lambda 형식)
def handler(event, context):
    return {'statusCode': 200, 'body': '...'}

# ❌ 잘못된 방식 (Mangum 사용)
from mangum import Mangum
handler = Mangum(app)

# ✅ 올바른 방식 (FastAPI의 경우)
from fastapi import FastAPI

app = FastAPI()  # Vercel이 자동으로 인식

@app.get("/")
def root():
    return {"message": "Hello"}
```

**핵심:**
- Vercel은 ASGI 앱을 **자동 감지**하므로 Mangum 불필요
- `app` 변수를 export하기만 하면 됨
- requirements.txt에서 mangum 제거

#### 문제: 500 Internal Server Error

**증상:**
- Backend가 500 에러 반환
- Function 로그에 환경 변수 누락 표시

**해결책:**
```bash
# Vercel 대시보드에서 환경 변수 확인
# 모든 필수 변수가 설정되었는지 확인
# 재배포: vercel --prod
```

#### 문제: Database Connection Timeout

**증상:**
- Function 로그에 타임아웃 에러
- "could not connect to server" 에러

**해결책:**
```bash
# 1. SUPABASE_DATABASE_URL이 Session 모드(port 6543)를 사용하는지 확인
# 올바름: postgresql://postgres.xxx:password@...pooler.supabase.com:6543/postgres
# 틀림:   postgresql://postgres.xxx:password@...pooler.supabase.com:5432/postgres

# 2. Supabase 대시보드에서 연결 문자열 확인
# Settings → Database → Connection string → Session mode

# 3. Vercel function 로그에서 연결 테스트
```

#### 문제: Redis Connection Failed

**증상:**
- 캐시가 작동하지 않음
- "UPSTASH_URL not set" 에러

**해결책:**
```bash
# 1. UPSTASH_URL이 HTTPS REST 엔드포인트인지 확인
# 올바름: https://xxx-xxx.upstash.io
# 틀림:   redis://xxx-xxx.upstash.io:6379

# 2. UPSTASH_TOKEN이 올바른지 확인
# Upstash Console → Database → REST API → Token에서 확인

# 3. REDIS_URL = UPSTASH_URL 인지 확인
```

#### 문제: CORS Errors

**증상:**
- 브라우저 콘솔에 CORS policy 에러
- Frontend에서 Backend API 호출 불가

**해결책:**
```bash
# 1. Backend CORS 설정에 Frontend 도메인이 포함되었는지 확인
# Backend 코드에 이미 포함됨: https://*.vercel.app

# 2. 커스텀 도메인의 경우 backend 환경 변수에 추가:
CORS_ORIGINS_EXTRA=https://myapp.com

# 3. Backend 재배포: vercel --prod

# 4. 브라우저 캐시 지우고 다시 테스트
```

### 일반적인 Frontend 문제

#### 문제: Map Not Loading

**증상:**
- 빈 지도 영역
- 콘솔 에러: "kakao is not defined"

**해결책:**
```bash
# 1. VITE_KAKAO_MAP_API_KEY가 설정되었는지 확인
# 2. JavaScript Key인지 확인 (REST API Key 아님)
# 3. Kakao Developer Console에 도메인이 등록되었는지 확인:
#    - Settings → Platform → Web → Vercel 도메인 추가
# 4. 도메인 추가 후 5-10분 대기
# 5. 브라우저 캐시 지우고 새로고침
```

#### 문제: Backend API Not Responding

**증상:**
- 서비스가 로드되지 않음
- 콘솔 에러: "Failed to fetch"

**해결책:**
```bash
# 1. VITE_API_BASE_URL이 올바른지 확인
# 올바름: https://your-backend.vercel.app (끝에 슬래시 없음)

# 2. Backend가 배포되고 정상인지 확인:
curl https://your-backend.vercel.app/health

# 3. Backend CORS에 Frontend 도메인이 허용되었는지 확인
# 4. 환경 변수 변경 후 Frontend 재배포
```

#### 문제: InfoWindow Not Showing Data

**증상:**
- InfoWindow가 표시되지만 데이터가 불완전함
- 콘솔에 undefined properties 에러

**해결책:**
```bash
# 1. 브라우저 콘솔에서 구체적인 에러 확인
# 2. Backend API 응답에 모든 필드가 포함되었는지 확인
# 3. kakao.ts의 createServiceInfoWindowContent() 함수 확인
# 4. 브라우저 캐시 지우고 다시 테스트
```

### Vercel 플랫폼 문제

#### 문제: Build Failed

**증상:**
- 빌드 에러로 배포 실패
- 배포 목록에 빨간 X 표시

**해결책:**
```bash
# 1. Vercel 대시보드에서 빌드 로그 확인
#    Deployments → 실패한 배포 선택 → View logs

# 2. 일반적인 원인:
#    - package.json에 의존성 누락
#    - TypeScript 에러
#    - 빌드용 환경 변수 미설정

# 3. 로컬에서 빌드 테스트:
npm run build

# 4. 에러 수정 후 재배포
```

#### 문제: Function Timeout

**증상:**
- 504 Gateway Timeout 에러
- 로그에 "FUNCTION_INVOCATION_TIMEOUT"

**해결책:**
```bash
# 1. 데이터베이스 쿼리 최적화
# 2. Redis 캐싱 추가
# 3. Vercel 플랜 업그레이드 (Hobby: 10s, Pro: 60s timeout)
# 4. vercel.json의 maxDuration 설정 확인
```

---

## 모니터링 및 유지보수

### Function 로그 보기

```bash
# Vercel 대시보드에서:
1. Deployments로 이동
2. 배포 클릭
3. **View Function Logs** 클릭
4. 실시간 로그 모니터링
```

### 성능 모니터링

```bash
# Vercel 대시보드에서:
1. Analytics로 이동
2. 메트릭 확인:
   - 응답 시간
   - 에러율
   - 초당 요청 수
   - Web Vitals (LCP, FID, CLS)
```

### 배포 업데이트

```bash
# 방법 1: Git push (권장)
git add .
git commit -m "feat: 기능 업데이트"
git push origin main

# 방법 2: 수동 배포
cd frontend  # 또는 backend
vercel --prod
```

### 배포 롤백

```bash
# Vercel 대시보드에서:
1. Deployments로 이동
2. 이전 정상 배포 찾기
3. **⋯** → **Promote to Production** 클릭
```

---

## 성능 최적화

### Backend 최적화

1. **Redis 캐싱 활성화**
   ```bash
   CACHE_ENABLED=true
   REDIS_CACHE_TTL=300  # 5분
   ```

2. **데이터베이스 쿼리 최적화**
   - 자주 조회하는 컬럼에 인덱스 추가
   - Supabase 쿼리 최적화 사용

3. **Function Cold Start 줄이기**
   - requirements.txt의 의존성 최소화
   - Lambda 크기 < 50MB 유지

### Frontend 최적화

1. **Vite 빌드 최적화 활성화**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     build: {
       minify: 'terser',
       sourcemap: false,
       rollupOptions: {
         output: {
           manualChunks: {
             'react-vendor': ['react', 'react-dom'],
             'map-vendor': ['@/services/kakao'],
           }
         }
       }
     }
   })
   ```

2. **Vercel Image Optimization 활성화**
   - next/image의 `<Image>` 컴포넌트 사용
   - 배포 전 이미지 최적화

3. **캐싱 헤더 활성화**
   - vercel.json에 이미 설정됨
   - 에셋 1년 캐싱

---

## 비용 최적화

### Vercel 무료 티어 한도

- **Function 실행**: 100 GB-시간/월
- **대역폭**: 100 GB/월
- **빌드**: 무제한
- **배포**: 무제한

### 무료 티어 유지 팁

1. **Redis 캐싱 활성화**로 function 호출 줄이기
2. **이미지 최적화**로 대역폭 줄이기
3. **스마트 캐싱**으로 API 호출 최소화
4. **Supabase 무료 티어 사용** (500 MB 저장소)
5. **Upstash 무료 티어 사용** (일 10,000 명령)

### 업그레이드 고려사항

다음의 경우 Pro($20/월)로 업그레이드:
- 10초 이상의 function timeout 필요
- 대역폭 한도 초과
- 비밀번호 보호 필요
- 고급 분석 필요
- 팀 협업 필요

---

## 보안 Best Practices

1. **환경 변수**
   - `.env` 파일 절대 커밋하지 않기
   - Vercel의 암호화된 저장소 사용
   - 정기적으로 키 로테이션

2. **API Keys**
   - service_role 키 비밀 유지
   - CORS로 도메인 제한
   - API 사용량 모니터링

3. **데이터베이스 보안**
   - Supabase Row Level Security (RLS) 활성화
   - Prepared statements 사용
   - 접근 로그 감사

4. **Frontend 보안**
   - CSP 헤더 (Content Security Policy) 활성화
   - 모든 사용자 입력 검증
   - 표시 데이터 새니타이제이션

5. **모니터링**
   - Sentry로 에러 추적 설정
   - Function 로그 모니터링
   - 이상 징후 알림 설정

---

## 다음 단계

성공적인 배포 후:

1. ✅ 커스텀 도메인 설정
2. ✅ Vercel Analytics 활성화
3. ✅ Sentry 에러 추적 설정
4. ✅ 모니터링 알림 설정
5. ✅ 팀용 배포 문서 작성
6. ✅ CI/CD 파이프라인 설정
7. ✅ 스테이징 환경 설정
8. ✅ 백업 전략 수립
9. ✅ 스케일링 전략 계획
10. ✅ 유지보수 일정 수립

---

## 지원 리소스

- **Vercel 문서**: https://vercel.com/docs
- **Vercel 지원**: https://vercel.com/support
- **Supabase 문서**: https://supabase.com/docs
- **Kakao Developers**: https://developers.kakao.com/docs
- **커뮤니티**: Vercel Discord, Supabase Discord

---

## 배포 체크리스트

### 배포 전

- [ ] 모든 코드 Git에 커밋
- [ ] 로컬에서 테스트 통과
- [ ] 로컬에서 빌드 성공
- [ ] 환경 변수 문서화
- [ ] API 키 발급
- [ ] 데이터베이스 스키마 마이그레이션

### 배포

- [ ] Backend Vercel 배포
- [ ] Backend 환경 변수 설정
- [ ] Backend 헬스 체크 통과
- [ ] Frontend Vercel 배포
- [ ] Frontend 환경 변수 설정
- [ ] Frontend 로딩 성공

### 배포 후

- [ ] 통합 테스트 통과
- [ ] Function 로그에 에러 없음
- [ ] 브라우저 콘솔에 에러 없음
- [ ] 성능 양호
- [ ] Analytics 활성화
- [ ] 모니터링 설정
- [ ] 문서 업데이트
- [ ] 팀 공지

---

**마지막 업데이트**: 2025-11-05
**버전**: 1.0.0
**관리**: Seoul Location Services 팀

---

## 빠른 참조 명령어

```bash
# 로그인
vercel login

# 프리뷰 배포
vercel

# 프로덕션 배포
vercel --prod

# 로그 보기
vercel logs

# 배포 목록
vercel ls

# 배포 삭제
vercel rm [deployment-url]

# 프로젝트 연결
vercel link

# 환경 변수 가져오기
vercel env pull

# 프로젝트 정보 보기
vercel inspect
```
