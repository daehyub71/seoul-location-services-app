# Quick Start Guide

## 빠른 시작 (5분 안에 시작하기)

### 1. 환경 준비

**필수 도구**:
```bash
# Node.js 18+ 확인
node --version  # v18.0.0 이상

# Python 3.11+ 확인
python --version  # 3.11.0 이상

# Git 확인
git --version
```

**계정 생성** (무료):
- [Supabase](https://supabase.com/) - 데이터베이스
- [Upstash](https://upstash.com/) - Redis 캐싱
- [Kakao Developers](https://developers.kakao.com/) - 지도 API
- [서울 열린데이터광장](https://data.seoul.go.kr/) - 공공 API 키

---

### 2. 프로젝트 클론

```bash
cd /Users/sunchulkim/src
git clone https://github.com/your-username/seoul-location-services-app.git
cd seoul-location-services-app
```

---

### 3. Backend 설정 (5분)

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 아래 값들을 입력하세요:
# - SUPABASE_URL, SUPABASE_KEY (Supabase 대시보드에서 복사)
# - UPSTASH_URL, UPSTASH_TOKEN (Upstash 대시보드에서 복사)
# - SEOUL_API_KEY (서울 열린데이터광장에서 발급)

# 데이터베이스 초기화
python scripts/init_db.py

# 초기 데이터 수집 (10-20분 소요)
python scripts/collect_all.py

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

**확인**: [http://localhost:8000/docs](http://localhost:8000/docs) 접속 → Swagger UI 확인

---

### 4. Frontend 설정 (3분)

**새 터미널 창에서**:

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 아래 값들을 입력하세요:
# - VITE_KAKAO_MAP_API_KEY (Kakao Developers JavaScript 키)
# - VITE_API_BASE_URL=http://localhost:8000

# 개발 서버 실행
npm run dev
```

**확인**: [http://localhost:5173](http://localhost:5173) 접속 → 지도 화면 확인

---

### 5. 기능 테스트 (2분)

1. **현재 위치 조회**:
   - 브라우저에서 위치 권한 허용
   - "현재 위치" 버튼 클릭
   - 지도가 현재 위치로 이동하고 주변 서비스 마커가 표시됨

2. **주소 검색**:
   - 검색창에 "서울시청" 입력
   - 검색 결과 선택
   - 지도가 해당 위치로 이동

3. **서비스 상세보기**:
   - 지도에서 마커 클릭
   - 미리보기 카드에서 "상세보기" 클릭
   - 모달에서 전체 정보 확인

---

## 주요 명령어 요약

### Backend
```bash
# 개발 서버 실행
uvicorn app.main:app --reload --port 8000

# 데이터 수집 (수동)
python scripts/collect_all.py

# 데이터 품질 검사
python scripts/data_quality_check.py

# 테스트 실행
pytest tests/ -v

# 스케줄러 실행 (자동 수집)
python scripts/scheduler.py
```

### Frontend
```bash
# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프리뷰 (빌드 결과 확인)
npm run preview

# 테스트
npm test

# E2E 테스트
npx playwright test
```

---

## API 키 발급 가이드

### 1. Supabase
1. [supabase.com](https://supabase.com/) 접속 → 회원가입
2. "New Project" 클릭
3. 프로젝트 이름 입력 (예: seoul-services)
4. Database Password 설정
5. Region: Northeast Asia (Seoul) 선택
6. Project Settings → API → "anon public" 키 복사 → `SUPABASE_KEY`
7. Project Settings → API → "service_role" 키 복사 → `SUPABASE_SERVICE_ROLE_KEY`
8. Project Settings → Database → Connection String 복사 → `SUPABASE_DATABASE_URL`

### 2. Upstash Redis
1. [upstash.com](https://upstash.com/) 접속 → 회원가입
2. "Create Database" 클릭
3. Name 입력 (예: seoul-cache)
4. Type: Regional 선택
5. Region: AWS ap-northeast-2 (Seoul) 선택
6. REST API → "UPSTASH_REDIS_REST_URL" 복사 → `UPSTASH_URL`
7. REST API → "UPSTASH_REDIS_REST_TOKEN" 복사 → `UPSTASH_TOKEN`

### 3. Kakao Map API
1. [developers.kakao.com](https://developers.kakao.com/) 접속 → 카카오 계정으로 로그인
2. "내 애플리케이션" → "애플리케이션 추가하기"
3. 앱 이름 입력 (예: 서울 위치 서비스)
4. 앱 키 → "JavaScript 키" 복사 → `VITE_KAKAO_MAP_API_KEY`
5. 플랫폼 → "Web 플랫폼 추가"
6. 사이트 도메인 등록: `http://localhost:5173` (개발용)

### 4. Seoul Open API
1. [data.seoul.go.kr](https://data.seoul.go.kr/) 접속 → 회원가입
2. 마이페이지 → "인증키 신청"
3. 신청 사유 입력 (예: 개인 프로젝트)
4. 발급된 인증키 복사 → `SEOUL_API_KEY`

---

## 트러블슈팅

### 문제: "Module not found" 에러 (Backend)
**해결**:
```bash
# 가상환경이 활성화되어 있는지 확인
which python  # /path/to/venv/bin/python 이어야 함

# 의존성 재설치
pip install -r requirements.txt
```

### 문제: "CORS error" (Frontend → Backend)
**해결**:
- `backend/app/main.py`에서 CORS 설정 확인
- `allow_origins`에 `http://localhost:5173` 포함되어 있는지 확인

### 문제: Kakao Map이 로딩되지 않음
**해결**:
1. 브라우저 콘솔에서 에러 확인
2. Kakao API 키가 올바른지 확인 (`.env` 파일)
3. Kakao Developers에서 도메인 등록 확인 (`http://localhost:5173`)

### 문제: 데이터베이스 연결 실패
**해결**:
1. Supabase 프로젝트가 "Active" 상태인지 확인
2. `SUPABASE_DATABASE_URL`의 비밀번호에 특수문자가 있으면 URL 인코딩
3. PostGIS 확장이 활성화되어 있는지 확인 (Supabase 대시보드 → Database → Extensions)

---

## 다음 단계

### Week 1 체크리스트
- [ ] 프로젝트 클론 및 환경 설정 완료
- [ ] Backend 서버 실행 확인
- [ ] Frontend 개발 서버 실행 확인
- [ ] Supabase에 데이터 수집 완료 (10,000+ 레코드)
- [ ] API 엔드포인트 테스트 (Swagger UI)
- [ ] 지도에 마커 표시 확인

### 유용한 링크
- **프로젝트 계획서**: [PROJECT_PLAN.md](./PROJECT_PLAN.md)
- **개발 일정**: [DEVELOPMENT_TIMELINE.md](./DEVELOPMENT_TIMELINE.md)
- **API 문서**: http://localhost:8000/docs (서버 실행 후)
- **Supabase 대시보드**: https://app.supabase.com/
- **Vercel 배포 가이드**: https://vercel.com/docs

---

**도움이 필요하신가요?**
- GitHub Issues: https://github.com/your-username/seoul-location-services-app/issues
- 이메일: your-email@example.com

**Happy Coding! 🚀**
