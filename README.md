# Seoul Location Services App

> 서울시 공공 서비스를 한눈에! 위치 기반 문화·교육·의료 정보 통합 플랫폼

## 프로젝트 소개

현재 위치 또는 원하는 지역을 기준으로 서울시의 다양한 공공 서비스 정보를 카카오 맵에서 확인할 수 있는 모바일 웹 애플리케이션입니다.

### 주요 기능

- **실시간 위치 추적**: GPS를 통한 현재 위치 자동 감지
- **9개 서울시 공공 API 통합**:
  - 문화행사 정보
  - 공공도서관 (일반 + 장애인)
  - 문화공간
  - 공공예약 서비스 (진료/교육/문화행사)
  - 서울미래유산
- **카카오 맵 시각화**: 카테고리별 마커 표시 및 클러스터링
- **거리 기반 정렬**: 가까운 곳부터 자동 정렬
- **상세 정보 제공**: 운영시간, 예약 링크, 길찾기 등

## 기술 스택

### Frontend
- React 18 + TypeScript
- Vite (빌드 도구)
- Tailwind CSS + shadcn/ui
- React Query (서버 상태 관리)
- Zustand (클라이언트 상태 관리)
- Kakao Map JavaScript SDK

### Backend
- FastAPI (Python 3.11+)
- LangGraph (Multi-Agent Workflow)
- Supabase PostgreSQL (데이터베이스)
- Upstash Redis (캐싱)
- Ollama (선택적 LLM 추천)

### Infrastructure
- Vercel (프론트엔드 + 서버리스 API)
- Supabase (데이터베이스)
- Upstash Redis (캐싱 레이어)
- Firebase Realtime Database (백업)

## 아키텍처

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  React Frontend         │
│  (Kakao Map)            │
└──────┬──────────────────┘
       │ REST API
       ▼
┌─────────────────────────┐
│  FastAPI Backend        │
│  ┌──────────────────┐   │
│  │  LangGraph       │   │
│  │  3-Agent System  │   │
│  └──────────────────┘   │
└──┬────────┬────────┬────┘
   │        │        │
   ▼        ▼        ▼
┌─────┐ ┌───────┐ ┌──────┐
│Redis│ │Supabase│Seoul│
│Cache│ │PostgreSQL│API│
└─────┘ └────────┘ └─────┘
```

## 시작하기

### 사전 요구사항

- Node.js 18+
- Python 3.11+
- Supabase 계정
- Upstash Redis 계정
- Kakao Developers 계정
- Seoul API 키

### 환경 변수 설정

#### Backend `.env`
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_DATABASE_URL=your_postgres_connection_string

# Upstash Redis
UPSTASH_URL=your_upstash_url
UPSTASH_TOKEN=your_upstash_token

# Seoul API
SEOUL_API_KEY=your_seoul_api_key

# Ollama (선택적)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=bge-m3
```

#### Frontend `.env`
```bash
VITE_KAKAO_MAP_API_KEY=your_kakao_javascript_key
VITE_API_BASE_URL=http://localhost:8000
```

### 설치 및 실행

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 데이터베이스 초기화
python scripts/init_db.py

# 초기 데이터 수집
python scripts/collect_all.py

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 개발 일정

- **Week 1** (Day 1-7): 데이터 수집 파이프라인 구축
- **Week 2** (Day 8-14): Backend API 개발 (LangGraph)
- **Week 3** (Day 15-21): Frontend 개발 (React + Kakao Map)
- **Week 4** (Day 22-28): 통합 테스트 및 배포

자세한 일정은 [PROJECT_PLAN.md](./PROJECT_PLAN.md)를 참고하세요.

## API 문서

서버 실행 후 [http://localhost:8000/docs](http://localhost:8000/docs)에서 Swagger UI를 통해 API 문서를 확인할 수 있습니다.

### 주요 엔드포인트

```bash
# 주변 서비스 조회
GET /api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000

# 카테고리별 조회
GET /api/v1/services/events?lat=37.5665&lon=126.9780

# 주소 → 좌표 변환
POST /api/v1/geocode
{
  "address": "서울시 종로구 세종대로 209"
}

# LLM 기반 추천 (선택적)
POST /api/v1/recommendations
{
  "location": {"lat": 37.5665, "lon": 126.9780},
  "preferences": {"interests": ["문화", "교육"]}
}
```

## 프로젝트 구조

```
seoul-location-services-app/
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── hooks/         # 커스텀 훅
│   │   ├── services/      # API 클라이언트
│   │   └── stores/        # 상태 관리
│   └── package.json
│
├── backend/               # FastAPI 백엔드
│   ├── app/
│   │   ├── core/          # LangGraph 에이전트
│   │   ├── api/           # REST 엔드포인트
│   │   └── db/            # 데이터베이스 모델
│   ├── collectors/        # 데이터 수집
│   └── scripts/           # 유틸리티 스크립트
│
├── docs/                  # 문서
└── README.md
```

## 비용 구조

| 서비스 | 무료 티어 | 월 비용 |
|--------|-----------|---------|
| Vercel | 100GB 대역폭 | $0 |
| Supabase | 500MB DB | $0 |
| Upstash Redis | 10,000 명령/일 | $0 |
| Firebase | 1GB 저장 | $0 |
| Ollama | 로컬 실행 | $0 |
| **총계** | | **$0/월** ✨ |

## 성능 목표

- API 응답 속도: <200ms
- 지도 초기 로딩: <2초
- Lighthouse 성능 점수: >90
- 동시 사용자: 500+

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이선스

MIT License

## 문의

프로젝트 관련 문의는 GitHub Issues를 이용해주세요.

---

**Made with ❤️ for Seoul Citizens**
