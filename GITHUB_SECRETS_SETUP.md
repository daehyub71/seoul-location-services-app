# GitHub Secrets 설정 가이드

GitHub Actions CI/CD 파이프라인을 실행하기 위해 필요한 모든 Secrets 설정 방법을 안내합니다.

## 📋 목차

- [Secrets 설정 방법](#secrets-설정-방법)
- [필수 Secrets 목록](#필수-secrets-목록)
- [Vercel Secrets](#vercel-secrets)
- [Supabase Secrets](#supabase-secrets)
- [API Keys](#api-keys)
- [검증 방법](#검증-방법)

---

## Secrets 설정 방법

### 1. GitHub Repository 접속
```
https://github.com/daehyub71/seoul-location-services-app
```

### 2. Settings → Secrets and variables → Actions 이동

### 3. "New repository secret" 클릭

### 4. 아래 Secrets를 하나씩 추가

---

## 필수 Secrets 목록

총 **12개**의 Secrets이 필요합니다.

| Secret Name | 설명 | 사용처 |
|-------------|------|--------|
| `VERCEL_TOKEN` | Vercel 배포 토큰 | Frontend/Backend 배포 |
| `VERCEL_ORG_ID` | Vercel Organization ID | Frontend/Backend 배포 |
| `VERCEL_PROJECT_ID_FRONTEND` | Frontend 프로젝트 ID | Frontend 배포 |
| `VERCEL_PROJECT_ID_BACKEND` | Backend 프로젝트 ID | Backend 배포 |
| `SUPABASE_URL` | Supabase 프로젝트 URL | Backend, 데이터 수집 |
| `SUPABASE_KEY` | Supabase Anon Key | Backend, 데이터 수집 |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | 데이터 수집 |
| `UPSTASH_URL` | Upstash Redis URL | Backend, 캐시 무효화 |
| `UPSTASH_TOKEN` | Upstash Redis Token | Backend, 캐시 무효화 |
| `SEOUL_API_KEY` | 서울시 Open API 키 | 데이터 수집 |
| `VITE_KAKAO_MAP_API_KEY` | Kakao Map JavaScript Key | Frontend 빌드 |
| `VITE_API_BASE_URL` | Backend API URL | Frontend 빌드 (선택적) |

---

## Vercel Secrets

### 1. VERCEL_TOKEN

**발급 방법**:
1. [Vercel Dashboard](https://vercel.com/account/tokens) 접속
2. "Create Token" 클릭
3. Token 이름 입력 (예: `github-actions`)
4. Scope: Full Account 선택
5. Expiration: No Expiration 권장
6. 생성된 토큰 복사

**값 예시**:
```
vercel_1a2b3c4d5e6f7g8h9i0j
```

---

### 2. VERCEL_ORG_ID

**확인 방법**:
1. Vercel 프로젝트 Settings 접속
2. "General" 탭에서 확인

또는 로컬에서 확인:
```bash
cd frontend  # 또는 backend
cat .vercel/project.json
```

**값 예시**:
```
team_abc123xyz
```

---

### 3. VERCEL_PROJECT_ID_FRONTEND

**확인 방법**:
```bash
cd frontend
cat .vercel/project.json
```

JSON에서 `projectId` 값 복사

**값 예시**:
```
prj_abc123xyz456def789
```

---

### 4. VERCEL_PROJECT_ID_BACKEND

**확인 방법**:
```bash
cd backend
cat .vercel/project.json
```

JSON에서 `projectId` 값 복사

**값 예시**:
```
prj_xyz789def456abc123
```

---

## Supabase Secrets

### 1. SUPABASE_URL

**확인 방법**:
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택
3. Settings → API → Project URL 복사

**값 예시**:
```
https://abcdefghijklmnop.supabase.co
```

---

### 2. SUPABASE_KEY (Anon Key)

**확인 방법**:
1. Supabase Dashboard → Settings → API
2. "anon public" 키 복사

**값 예시**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. SUPABASE_SERVICE_ROLE_KEY

**확인 방법**:
1. Supabase Dashboard → Settings → API
2. "service_role" 키 복사
3. ⚠️ **중요**: 절대 클라이언트에 노출하지 말 것!

**값 예시**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Upstash Redis Secrets

### 1. UPSTASH_URL

**확인 방법**:
1. [Upstash Console](https://console.upstash.com/) 접속
2. Redis 데이터베이스 선택
3. "REST API" 섹션에서 `UPSTASH_REDIS_REST_URL` 복사

**값 예시**:
```
https://abc-def-12345.upstash.io
```

---

### 2. UPSTASH_TOKEN

**확인 방법**:
1. Upstash Console → Redis 데이터베이스 선택
2. "REST API" 섹션에서 `UPSTASH_REDIS_REST_TOKEN` 복사

**값 예시**:
```
AaBbCcDdEeFfGgHhIiJjKkLlMmNn12345678==
```

---

## API Keys

### 1. SEOUL_API_KEY

**발급 방법**:
1. [서울 열린데이터 광장](https://data.seoul.go.kr/) 접속
2. 회원가입 및 로그인
3. 마이페이지 → 인증키 신청
4. 발급된 인증키 복사

**값 예시**:
```
6b4d5a7c8e9f1a2b3c4d5e6f7g8h9i0j
```

---

### 2. VITE_KAKAO_MAP_API_KEY

**발급 방법**:
1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 내 애플리케이션 → 앱 선택
3. "앱 키" 섹션에서 **JavaScript 키** 복사 (REST API 키 아님!)
4. 플랫폼 설정에서 도메인 등록:
   - `http://localhost:5173` (개발)
   - `https://seoul-location-services-frontend-*.vercel.app` (프로덕션)

**값 예시**:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

### 3. VITE_API_BASE_URL (선택적)

**설정 값**:
```
https://seoul-location-services-backend-1um0gnhuv-daehyub71s-projects.vercel.app
```

> **참고**: 하드코딩되어 있어 Secret 설정 불필요. 변경 시에만 설정.

---

## 검증 방법

### 1. Secrets 확인

GitHub Repository → Settings → Secrets and variables → Actions

총 12개 Secret이 등록되어 있는지 확인:

- ✅ VERCEL_TOKEN
- ✅ VERCEL_ORG_ID
- ✅ VERCEL_PROJECT_ID_FRONTEND
- ✅ VERCEL_PROJECT_ID_BACKEND
- ✅ SUPABASE_URL
- ✅ SUPABASE_KEY
- ✅ SUPABASE_SERVICE_ROLE_KEY
- ✅ UPSTASH_URL
- ✅ UPSTASH_TOKEN
- ✅ SEOUL_API_KEY
- ✅ VITE_KAKAO_MAP_API_KEY
- ✅ VITE_API_BASE_URL (선택적)

---

### 2. 워크플로우 테스트

#### Frontend 배포 테스트
```bash
# 변경사항 커밋
git add frontend/
git commit -m "test: trigger frontend CI/CD"
git push origin main
```

GitHub Actions 탭에서 "Frontend CI/CD" 워크플로우 확인

---

#### Backend 배포 테스트
```bash
# 변경사항 커밋
git add backend/
git commit -m "test: trigger backend CI/CD"
git push origin main
```

GitHub Actions 탭에서 "Backend CI/CD" 워크플로우 확인

---

#### 데이터 수집 수동 실행
1. GitHub → Actions 탭
2. "Daily Data Collection" 선택
3. "Run workflow" 클릭
4. 실행 결과 확인

---

## 문제 해결

### 배포 실패 시

#### 1. "Invalid Vercel Token"
- VERCEL_TOKEN이 만료되었거나 잘못됨
- 새로운 토큰 발급 후 재설정

#### 2. "Project not found"
- VERCEL_PROJECT_ID가 잘못됨
- `.vercel/project.json`에서 올바른 ID 확인

#### 3. "Supabase connection failed"
- SUPABASE_URL 또는 SUPABASE_KEY가 잘못됨
- Supabase Dashboard에서 재확인

#### 4. "API rate limit exceeded"
- SEOUL_API_KEY 할당량 초과
- 다음 날까지 대기 또는 새 키 발급

---

### 데이터 수집 실패 시

자동으로 GitHub Issue가 생성됩니다. Issue에서 다음 확인:

- [ ] 서울 API 키 유효성
- [ ] Supabase 연결 상태
- [ ] API 엔드포인트 변경
- [ ] 데이터 스키마 변경

---

## 보안 권장사항

### ✅ DO
- Secrets는 GitHub Repository Settings에만 저장
- Service Role Key는 서버 사이드에서만 사용
- 주기적으로 토큰 갱신 (최소 6개월)
- 의심스러운 활동 발견 시 즉시 키 재발급

### ❌ DON'T
- Secrets를 코드에 하드코딩 금지
- `.env` 파일을 git에 커밋 금지
- Public 저장소에 Secrets 노출 금지
- Service Role Key를 클라이언트에 노출 금지

---

## 추가 자료

- [GitHub Actions Secrets 공식 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Vercel CLI 문서](https://vercel.com/docs/cli)
- [Supabase API Keys 가이드](https://supabase.com/docs/guides/api/api-keys)
- [Upstash Redis 문서](https://docs.upstash.com/redis)

---

**작성일**: 2025-11-05
**업데이트**: CI/CD 파이프라인 구축 완료 (Day 23)
