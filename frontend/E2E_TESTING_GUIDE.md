# E2E 테스트 가이드

Playwright를 사용한 End-to-End 테스트 가이드입니다.

## 📦 설치

Playwright는 이미 설치되어 있습니다. 브라우저만 설치하면 됩니다:

```bash
npx playwright install chromium
```

## 🧪 테스트 시나리오

### 1. 현재 위치 조회 (01-current-location.spec.ts)
- GPS 위치 허용 및 지도 중심 이동 확인
- 주변 서비스 마커 표시 확인
- 검색 반경 변경 테스트

### 2. 주소 검색 (02-address-search.spec.ts)
- 주소 입력 및 검색
- 주소 검색 후 지도 이동 확인
- 잘못된 주소 검색 시 에러 처리
- 주소 입력 클리어 기능
- Enter 키로 검색 실행

### 3. 카테고리 필터링 (03-category-filtering.spec.ts)
- 필터 버튼 표시 및 클릭
- 도서관 카테고리만 선택
- 전체 선택/해제 버튼 동작
- 다중 카테고리 선택
- 정렬 옵션 변경

### 4. 서비스 상세보기 (04-service-detail.spec.ts)
- 서비스 리스트 항목 클릭 시 선택 표시
- 다른 서비스 항목 클릭 시 선택 변경
- 서비스 정보 표시 확인
- Map marker와 연동 확인
- 서비스 거리 정보 표시
- 서비스 카테고리 표시
- 서비스 주소 정보 표시

## 🚀 테스트 실행

### 기본 실행 (Headless 모드)
```bash
npm run e2e
```

### UI 모드로 실행 (권장)
```bash
npm run e2e:ui
```

### Headed 모드로 실행 (브라우저 보면서 실행)
```bash
npm run e2e:headed
```

### 특정 테스트만 실행
```bash
npx playwright test 01-current-location.spec.ts
```

### 디버그 모드
```bash
npx playwright test --debug
```

## 📊 테스트 리포트

테스트 실행 후 HTML 리포트 보기:

```bash
npm run e2e:report
```

## ⚙️ 설정 파일

### playwright.config.ts

주요 설정:
- **baseURL**: `http://localhost:5173`
- **testDir**: `./e2e`
- **브라우저**: Chromium (Desktop Chrome)
- **자동 재시도**: CI에서만 2회
- **비디오/스크린샷**: 실패 시에만 저장
- **웹 서버 자동 시작**: `npm run dev`

## 🧩 테스트 작성 팁

### 1. Geolocation Mock
```typescript
await context.grantPermissions(['geolocation'])
await context.setGeolocation({ latitude: 37.5665, longitude: 126.978 })
```

### 2. Wait 사용
```typescript
// DOM 요소 대기
await expect(element).toBeVisible({ timeout: 10000 })

// 타임아웃 (최소한으로 사용)
await page.waitForTimeout(1000)
```

### 3. 유연한 Selector
```typescript
// 여러 선택자 중 하나 찾기
const element = page.getByText(/텍스트/i).or(page.getByLabel(/라벨/i))

// 정규식 사용
const button = page.getByRole('button', { name: /검색/i })
```

## 🔍 디버깅

### 1. Playwright Inspector
```bash
npx playwright test --debug
```

### 2. Trace Viewer
실패한 테스트의 trace 파일 열기:
```bash
npx playwright show-trace trace.zip
```

### 3. 스크린샷 확인
실패 시 스크린샷이 `test-results/` 디렉토리에 저장됩니다.

## 📝 CI/CD 통합

### GitHub Actions

이미 `.github/workflows/frontend-deploy.yml`에 E2E 테스트가 포함되어 있습니다:

```yaml
- name: Run tests
  run: npm test
  continue-on-error: true
```

## 🐛 문제 해결

### 1. "Error: page.goto: net::ERR_CONNECTION_REFUSED"
**원인**: 개발 서버가 실행되지 않음
**해결**: playwright.config.ts의 `webServer` 설정이 자동으로 dev 서버를 시작합니다.

### 2. "Test timeout"
**원인**: 페이지 로딩이 너무 오래 걸림
**해결**: playwright.config.ts의 `timeout` 설정 증가

### 3. "Target closed"
**원인**: 페이지가 예기치 않게 닫힘
**해결**: `trace: 'on'`으로 설정하고 trace 파일 확인

## 📚 참고 자료

- [Playwright 공식 문서](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Selectors](https://playwright.dev/docs/selectors)
- [Assertions](https://playwright.dev/docs/test-assertions)

---

**작성일**: 2025-11-06 (Day 24)
**테스트 커버리지 목표**: >80%
