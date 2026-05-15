# 백엔드 캐비엇 / 주의 사항

팀이 알아둬야 하는 "구조적인 주의 사항"을 모은 문서.
일반적인 사용에는 문제 없지만, 모르고 코드 추가하면 미묘한 버그가 생길 수 있는 항목들.

---

## 1. 시간대 — `to_kst_naive`는 naive datetime을 "이미 KST"로 가정한다

위치: `app/utils/time.py`

```python
def to_kst_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt  # 이미 KST로 가정
    return dt.astimezone(KST).replace(tzinfo=None)
```

의도: 명세서 4. "기본 시간 기준은 KST"에 맞춰 외부에서 들어오는 naive ISO 문자열은 KST로 본다. 프론트가 `"2026-05-13T18:00:00"`을 보내면 18시 KST로 처리.

위험: 백엔드 내부 코드에서 실수로 naive UTC datetime을 만들어서 이 함수에 넣으면 9시간 어긋남 버그가 생긴다.

```python
# [금지] datetime.now()는 naive local time (Windows에서는 KST, 다른 OS는 다를 수 있음)
dt = datetime.now()
to_kst_naive(dt)

# [금지] naive UTC를 KST로 잘못 해석한다
dt = datetime.utcnow()
to_kst_naive(dt)  # 9시간 어긋남

# [권장] 항상 helper 사용
from app.utils.time import now_kst_naive
dt = now_kst_naive()

# [권장] timezone-aware datetime을 넣으면 자동 변환
dt = datetime.now(timezone.utc)
to_kst_naive(dt)  # 정확한 KST로 변환됨
```

규칙:
- 현재 시각이 필요하면 무조건 `now_kst_naive()` 사용. `datetime.now()` / `datetime.utcnow()` 금지.
- 외부에서 받은 datetime은 반드시 `to_kst_naive()`로 정규화하고 비교.
- timezone 명시한 datetime(`datetime.now(timezone.utc)` 등)을 만들 거면 OK — `to_kst_naive`가 알아서 변환.

---

---

## 2. `run-dev.bat` / `run-dev-mac.sh`는 repo 루트에서만 동작한다

위치: `독수리택시/run-dev.bat`, `독수리택시/run-dev-mac.sh` (개발 계획안 §41-2, §42-3 본문 그대로)

의도: 명세 §23 폴더 구조 기준 — repo 루트에 두고 `cd backend && ...`로 백엔드 가상환경을 활성화한 뒤 uvicorn을 실행한다. 프론트엔드도 같은 방식으로 `cd frontend`.

위험: 현재 `독수리택시/` 폴더는 향후 GitHub repo에서 `backend/` 서브폴더로 들어갈 예정이다. **현재 위치에서는 스크립트의 `cd backend`가 실패한다** (이 폴더 자체가 backend 역할이라 `backend/` 하위 폴더가 없음).

동작 조건:
- GitHub repo 정리 후 `mirae_mobility-eagle_taxi/run-dev.bat`로 옮긴다.
- 같은 repo 루트에 `frontend/`와 `backend/`가 함께 있어야 한다.
- `backend/.venv`가 생성되어 있어야 한다.
- `frontend/`에 `npm install`이 완료되어 있어야 한다.

당분간 로컬 테스트용 백엔드만 켤 때는:
```
cd /d "C:\Users\lee\Desktop\학교\독수리택시"
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
로 직접 실행한다. (명세 §41-1 1차 실행 방식과 동일한 의도)

---

(이 문서는 캐비엇이 새로 발견될 때마다 추가한다.)
