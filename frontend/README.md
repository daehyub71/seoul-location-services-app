# Seoul Location Services - Frontend

React + TypeScript + Vite 기반 위치 기반 서비스 프론트엔드

## 기술 스택

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**:
  - React Query (서버 상태)
  - Zustand (클라이언트 상태)
- **Map**: Kakao Map JavaScript SDK
- **Animation**: Framer Motion

## 설치

```bash
cd frontend
npm install
```

## 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어서 실제 값으로 수정
```

필수 환경변수:
- `VITE_KAKAO_MAP_API_KEY` - Kakao Developers JavaScript 키
- `VITE_API_BASE_URL` - Backend API URL (개발: http://localhost:8000)

## 실행

```bash
# 개발 서버 (http://localhost:5173)
npm run dev

# 빌드
npm run build

# 빌드 미리보기
npm run preview
```

## 프로젝트 구조

```
frontend/
├── src/
│   ├── components/
│   │   ├── map/           # 지도 관련 컴포넌트
│   │   ├── services/      # 서비스 목록/카드
│   │   ├── location/      # 위치 입력
│   │   └── ui/            # shadcn/ui 컴포넌트
│   ├── hooks/             # 커스텀 훅
│   ├── services/          # API 클라이언트
│   ├── stores/            # Zustand 스토어
│   ├── types/             # TypeScript 타입
│   ├── App.tsx
│   └── main.tsx
├── public/                # 정적 파일
├── package.json
└── vite.config.ts
```

## 개발 일정

### Week 3 (Day 15-21): Frontend 개발
- [ ] Day 15: React 프로젝트 설정 (현재)
- [ ] Day 16: API 클라이언트 및 훅
- [ ] Day 17: Kakao Map 컴포넌트
- [ ] Day 18: 마커 및 오버레이
- [ ] Day 19: 서비스 목록 UI (Part 1)
- [ ] Day 20: 서비스 목록 UI (Part 2)
- [ ] Day 21: UX 개선 및 최적화

## Kakao Map 설정

### 1. API 키 발급
1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 애플리케이션 생성
3. JavaScript 키 복사
4. Web 플랫폼 추가 → `http://localhost:5173` 등록

### 2. 스크립트 로드
`index.html`에 Kakao Map SDK 추가:

```html
<script
  type="text/javascript"
  src="//dapi.kakao.com/v2/maps/sdk.js?appkey=YOUR_APP_KEY&libraries=services,clusterer"
></script>
```

## 테스트

```bash
# 단위 테스트
npm test

# UI 테스트
npm run test:ui

# E2E 테스트
npm run e2e
```

## 빌드 및 배포

```bash
# 프로덕션 빌드
npm run build

# Vercel 배포 (자동)
git push origin main
```

## 주요 기능 (Week 3 이후)

- ✅ Kakao Map 통합
- ✅ 현재 위치 추적
- ✅ 주소 검색
- ✅ 카테고리별 마커 표시
- ✅ 마커 클러스터링
- ✅ 서비스 상세보기
- ✅ 거리순 정렬
- ✅ 반응형 디자인

## 라이선스

MIT
