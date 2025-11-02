# Contributing to Seoul Location Services App

우리 프로젝트에 관심을 가져주셔서 감사합니다! 🎉

## 기여 방법

### 1. 이슈 제기

버그를 발견하거나 새로운 기능을 제안하고 싶으시다면:

1. [GitHub Issues](https://github.com/daehyub71/seoul-location-services-app/issues)에서 유사한 이슈가 있는지 확인
2. 없다면 새 이슈 생성
3. 명확한 제목과 상세한 설명 작성
4. 가능하면 스크린샷이나 에러 로그 첨부

### 2. Pull Request 제출

#### 시작하기
```bash
# 1. Repository Fork
# GitHub에서 "Fork" 버튼 클릭

# 2. Clone
git clone https://github.com/YOUR-USERNAME/seoul-location-services-app.git
cd seoul-location-services-app

# 3. 원본 저장소를 upstream으로 추가
git remote add upstream https://github.com/daehyub71/seoul-location-services-app.git

# 4. 최신 변경사항 가져오기
git fetch upstream
git checkout main
git merge upstream/main
```

#### 브랜치 생성
```bash
# Feature 추가
git checkout -b feature/your-feature-name

# Bug 수정
git checkout -b fix/bug-description

# 문서 업데이트
git checkout -b docs/what-you-updated
```

#### 코드 작성
1. 코딩 스타일 가이드 준수 (아래 참고)
2. 변경사항에 대한 테스트 작성
3. 문서 업데이트 (필요시)

#### 커밋
```bash
# Staging
git add .

# Commit (Conventional Commits 스타일)
git commit -m "feat: add service category filter"
git commit -m "fix: resolve marker clustering issue"
git commit -m "docs: update API documentation"
```

**커밋 메시지 형식**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스 변경

#### Push 및 PR 생성
```bash
# Push to your fork
git push origin feature/your-feature-name

# GitHub에서 Pull Request 생성
# 1. "Compare & pull request" 버튼 클릭
# 2. PR 제목과 설명 작성 (아래 템플릿 사용)
# 3. "Create pull request" 클릭
```

**PR 템플릿**:
```markdown
## 변경 사항
<!-- 무엇을 변경했는지 설명 -->

## 변경 이유
<!-- 왜 이 변경이 필요한지 설명 -->

## 테스트 방법
<!-- 어떻게 테스트했는지 설명 -->

## 스크린샷 (선택사항)
<!-- UI 변경이 있다면 첨부 -->

## 체크리스트
- [ ] 코드가 스타일 가이드를 따름
- [ ] 테스트 작성 및 통과
- [ ] 문서 업데이트 (필요시)
- [ ] 커밋 메시지가 Conventional Commits 형식
```

---

## 코딩 스타일 가이드

### Python (Backend)
- **포맷터**: Black (line length: 88)
- **Linter**: Flake8
- **타입 힌팅**: mypy
- **Import 정렬**: isort

```bash
# 자동 포맷팅
black backend/
isort backend/

# 린팅
flake8 backend/
mypy backend/
```

**예시**:
```python
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    """서비스 응답 모델"""
    id: str
    name: str
    distance: float


async def get_nearby_services(
    lat: float,
    lon: float,
    radius: int = 2000
) -> List[ServiceResponse]:
    """주변 서비스 조회"""
    # Implementation
    pass
```

### TypeScript (Frontend)
- **포맷터**: Prettier
- **Linter**: ESLint
- **타입**: TypeScript strict mode

```bash
# 자동 포맷팅
npm run lint

# 타입 체크
npm run type-check
```

**예시**:
```typescript
interface Service {
  id: string;
  name: string;
  distance: number;
}

const fetchNearbyServices = async (
  lat: number,
  lon: number,
  radius: number = 2000
): Promise<Service[]> => {
  // Implementation
};
```

---

## 테스트 가이드

### Backend Tests
```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/test_services.py

# 커버리지
pytest --cov=app --cov-report=html
```

**테스트 작성 예시**:
```python
import pytest
from app.api.v1.endpoints.services import get_nearby_services


@pytest.mark.asyncio
async def test_get_nearby_services():
    """주변 서비스 조회 테스트"""
    result = await get_nearby_services(
        lat=37.5665,
        lon=126.9780,
        radius=2000
    )
    assert len(result) > 0
    assert result[0].distance < 2000
```

### Frontend Tests
```bash
# 단위 테스트
npm test

# E2E 테스트
npm run e2e
```

---

## 개발 환경 설정

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구
```

### Frontend
```bash
cd frontend
npm install
```

### Pre-commit Hooks (권장)
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 문서 작성 가이드

### README 업데이트
- 새 기능 추가 시 README의 "주요 기능" 섹션 업데이트
- API 엔드포인트 추가 시 "API 문서" 섹션 업데이트

### API 문서
- FastAPI의 docstring을 활용하여 Swagger 문서 자동 생성
- 모든 엔드포인트에 명확한 설명 추가

```python
@router.get("/nearby")
async def get_nearby_services(
    lat: float,
    lon: float,
    radius: int = 2000
):
    """
    주변 서비스 조회

    Args:
        lat: 위도
        lon: 경도
        radius: 검색 반경 (미터, 기본값: 2000)

    Returns:
        ServiceListResponse: 서비스 목록
    """
    pass
```

---

## 리뷰 프로세스

1. **자동 체크**: GitHub Actions에서 자동으로 테스트 및 린팅 실행
2. **코드 리뷰**: 최소 1명의 maintainer 승인 필요
3. **변경 요청**: 리뷰어가 요청한 변경사항 반영
4. **Merge**: 모든 체크 통과 시 main 브랜치에 병합

---

## 질문이나 도움이 필요하신가요?

- **이슈**: [GitHub Issues](https://github.com/daehyub71/seoul-location-services-app/issues)
- **토론**: [GitHub Discussions](https://github.com/daehyub71/seoul-location-services-app/discussions)

---

## 행동 강령

### 우리의 약속
- 모든 기여자를 존중하고 환영합니다
- 건설적인 피드백을 제공합니다
- 다양한 관점과 경험을 소중히 여깁니다

### 용납할 수 없는 행동
- 괴롭힘이나 차별
- 개인 공격이나 모욕
- 무례하거나 전문적이지 않은 행동

---

**모든 기여에 감사드립니다!** 🙏

함께 서울 시민들을 위한 더 나은 서비스를 만들어가요! 💪
