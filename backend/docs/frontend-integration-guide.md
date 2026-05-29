# 독수리 택시 - 프론트 연동 가이드 (백엔드 API 계약서)

작성: TL 이가람 / 대상: QA&Front 심지수
기준 코드: feature/backend (관리자 API까지 반영), 명세서 v0.4
백엔드: FastAPI + SQLite, 포트 8000, Swagger UI = http://localhost:8000/docs

이 문서는 React에서 백엔드 API를 연결할 때 필요한 "요청/응답 계약"을 한 곳에 정리한 것이다.
엔드포인트 경로와 응답 필드는 임의로 바꾸지 않는다. 변경이 필요하면 TL/PM 확인 후 명세서에 먼저 반영한다.

---

## 1. 네트워크 기준

| 항목 | 값 |
| --- | --- |
| 백엔드 주소 | http://localhost:8000 |
| API 문서 | http://localhost:8000/docs |
| 프론트 dev 서버 | http://localhost:5173 |
| API 호출 경로 | `/api/...` (Vite proxy가 8000으로 전달) |
| WebSocket 경로 | `/ws/...` (Vite proxy가 ws://8000으로 전달) |
| CORS 허용 출처 | 백엔드 `.env`의 `CORS_ORIGINS` (현재 http://localhost:5173) |

프론트는 `/api`, `/ws` 상대경로로 호출하면 Vite proxy가 백엔드로 넘긴다 (개발 계획안 §30 vite.config 기준).
같은 Wi-Fi 발표 시연 시에는 proxy 덕분에 프론트 코드 수정 없이 동작한다.

---

## 2. 인증 흐름

1. 회원가입 `POST /api/auth/register`
2. 로그인 `POST /api/auth/login` → 응답의 `access_token` 저장
3. 이후 인증이 필요한 모든 API는 헤더에 `Authorization: Bearer <access_token>` 추가
4. 내 정보 확인 `GET /api/auth/me`
5. 로그아웃: 백엔드 API 없음. 프론트에서 토큰만 삭제한다 (명세 F-AUTH-004).

- 토큰 저장은 로그인 토큰 용도로만 localStorage 사용 (개발 원칙 — 그 외 데이터는 localStorage 금지).
- 토큰 만료 기본 1440분(24시간). 만료/위조 토큰은 401.

---

## 3. 공통 규칙

- 요청 Body는 JSON (`Content-Type: application/json`).
- 시간 값은 KST 기준 ISO 8601 문자열. 예: `"2026-05-30T18:00:00"`.
  - timezone 없는 문자열은 KST로 해석한다.
  - `+09:00` 또는 `Z`(UTC)를 붙여 보내도 백엔드가 KST로 정규화한다.
- 인증 누락/실패 → `401`.
- 권한 부족(관리자 전용 등) → `403`.
- 없는 리소스 → `404`.

### 에러 응답 형식

입력값 검증 실패(Pydantic)는 `400`으로 통일되며 형식은 다음과 같다.

```json
{ "detail": "최대 인원은 2명에서 4명 사이여야 합니다.", "errors": [ { "field": "max_members", "type": "less_than_equal", "msg": "..." } ] }
```

그 외 비즈니스 예외(중복 참여, 정원 초과 등)는 `errors` 없이 `detail`만 내려온다.

```json
{ "detail": "이미 참여 중인 파티입니다." }
```

프론트는 항상 `detail` 문자열을 사용자 메시지로 그대로 노출할 수 있다 (모두 한글).

---

## 4. 엔드포인트 목록

인증 O = `Authorization: Bearer` 헤더 필요.

### 4-1. 인증 (Auth)

| 메서드 | 경로 | 인증 | 요청 | 성공 | 주요 에러 |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/auth/register` | X | RegisterRequest | 201 UserOut | 409 이메일 중복, 400 검증 |
| POST | `/api/auth/login` | X | `{email, password}` | 200 LoginResponse | 401 불일치, 403 비활성 |
| GET | `/api/auth/me` | O | - | 200 UserOut | 401 |

RegisterRequest: `{ email, password(8~64자), name(1~50자), gender("male"|"female") }`
LoginResponse: `{ access_token, token_type:"bearer", user: UserOut }`

### 4-2. 파티 (Parties)

| 메서드 | 경로 | 인증 | 요청 | 성공 | 주요 에러 |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/parties` | O | PartyCreateRequest | 201 PartyDetail | 400 과거시간/정원/성별 |
| GET | `/api/parties` | O | query: status?, page=1, limit=20 | 200 PartyListResponse | - |
| GET | `/api/parties/search` | O | query: start_place?, end_place?, departure_time?, status?, page, limit | 200 PartyListResponse | 400 시간형식 |
| GET | `/api/parties/recommend` | O | query: start_place*, end_place*, departure_time*, time_range_minutes=30, limit=10 | 200 RecommendResponse | 400 시간형식 |
| GET | `/api/parties/{id}` | O | - | 200 PartyDetail | 404 |
| POST | `/api/parties/{id}/join` | O | - | 200 PartyJoinResponse | 400 중복/정원/시간충돌/성별, 404 |
| DELETE | `/api/parties/{id}/leave` | O | - | 200 PartyDetail | 400 생성자/미참여/종료, 404 |
| PATCH | `/api/parties/{id}/cancel` | O | `{cancel_reason?}` | 200 PartyDetail | 403 생성자아님, 400 종료됨, 404 |

`*` = 필수 query 파라미터.

주의:
- 목록/검색 기본값은 `status=recruiting` + 출발시간이 현재 이후인 파티만 노출.
- `recommend`는 점수순(최대 100). 출발지/도착지 일치 각 +35, 시간 근접 +30/+20/+10.
- 같은 시간대(±60분)에 이미 참여 중인 파티가 있으면 join 차단.

### 4-3. 요금 (Fares)

| 메서드 | 경로 | 인증 | 요청 | 성공 |
| --- | --- | --- | --- | --- |
| GET | `/api/fares/estimate` | O | query: start_lat, start_lng, end_lat, end_lng | 200 FareEstimateOut |

- 파티 생성 전 미리보기용. 파티 생성 시에는 서버가 내부적으로 동일 산정을 다시 한다.
- Kakao Key가 없거나 호출 실패면 모든 값 0 + `fare_source: "fallback"`. 정상이면 `fare_source: "kakao_mobility"`.

### 4-4. 내 파티 (My)

| 메서드 | 경로 | 인증 | 성공 |
| --- | --- | --- | --- |
| GET | `/api/my/parties` | O | 200 `{created_parties: PartySummary[], joined_parties: PartySummary[]}` |

- 생성자는 `created_parties`에만 표시 (joined에 중복 노출 안 함).

### 4-5. 채팅 (Chat)

| 방식 | 경로 | 인증 | 비고 |
| --- | --- | --- | --- |
| GET | `/api/parties/{id}/messages` | O | 이전 메시지 목록 `{items: MessageOut[]}`. 비참여자 403, 없는 파티 404 |
| WS | `/ws/parties/{id}?token=<JWT>` | query token | 실시간 송수신 (아래 6장) |

### 4-6. 시스템 (System)

| 메서드 | 경로 | 인증 | 성공 |
| --- | --- | --- | --- |
| GET | `/api/health` | X | `{status:"ok", service:"eagle-taxi-api"}` |

### 4-7. 관리자 (Admin) - 관리자 페이지(S-12) 전용

모두 인증 O + 관리자 권한 필요. 일반 사용자/비활성/미로그인 → 401 또는 403.
관리자 화면은 PM 담당이지만, 연결할 API 계약은 아래와 같다.

| 메서드 | 경로 | 용도 |
| --- | --- | --- |
| GET | `/api/admin/stats` | 전체 통계(사용자/파티/상태별/메시지 수) |
| GET | `/api/admin/parties/recent` | 최근 파티 (limit=10) |
| GET | `/api/admin/parties` | 파티 목록 (status, keyword, page, limit=20) |
| GET | `/api/admin/parties/{id}` | 파티 상세 |
| PATCH | `/api/admin/parties/{id}/status` | 파티 상태 변경 |
| GET | `/api/admin/users` | 사용자 목록 (page, limit=20) |
| GET | `/api/admin/users/{id}` | 사용자 상세 |
| PATCH | `/api/admin/users/{id}/role` | 사용자 권한 변경 |
| PATCH | `/api/admin/users/{id}/status` | 사용자 활성 상태 변경 |
| GET | `/api/admin/messages/recent` | 최근 메시지 (limit=20, 읽기 전용) |

---

## 5. 응답 객체 스키마

### UserOut
```
id: int
email: string
name: string
gender: "male" | "female" | "none"
role: "user" | "admin"
is_active: boolean
created_at: datetime
```
(password_hash 등 민감 정보는 절대 응답에 없음)

### PartySummary (목록/생성/내 파티)
```
id, creator_id: int
start_place, end_place: string
departure_time: datetime
max_members, current_members: int
estimated_fare: int          // 전체 예상 요금(원)
per_person_fare: int         // 현재 인원 기준 1인 요금(원, 올림)
status: PartyStatus
gender_rule: "any" | "same_gender"
created_at: datetime
```

### PartyDetail (상세) = PartySummary + 아래 필드
```
start_lat, start_lng, end_lat, end_lng: float
meeting_point, meeting_note: string | null
toll_fare, distance_meters, duration_seconds: int
fare_source: "kakao_mobility" | "fallback"
party_gender: string | null
canceled_at: datetime | null
cancel_reason: string | null
creator_name: string          // 생성자 이름 (creator_id는 PartySummary에 있음)
members: PartyMemberOut[]
```

### PartyMemberOut
```
id: int
name: string
gender: "male" | "female" | "none"
```

### PartyJoinResponse (POST `/api/parties/{id}/join` 성공 응답)
```
result_code: int        // 성공 200
can_join: boolean        // 성공 true
reason: string           // "파티에 참여하였습니다."
id, current_members, max_members: int
estimated_fare, per_person_fare: int
status: PartyStatus
members: PartyMemberOut[]
```
- 참여 성공 시 위 래퍼로 내려온다. 실패는 HTTP 4xx + `{ detail }`.
- 좌표/생성자 등 상세 전체가 필요하면 `GET /api/parties/{id}` (PartyDetail) 사용.

### FareEstimateOut
```
estimated_fare, toll_fare, distance_meters, duration_seconds: int
fare_source: "kakao" | "fallback"
```
(미리보기에는 1인 요금 없음 - 인원이 아직 없으므로)

### RecommendedParty = PartySummary + `match_score: int`, `meeting_point`, `meeting_note`

### MessageOut
```
id, party_id, user_id: int
user_name: string
content: string
created_at: datetime
```

---

## 6. WebSocket 채팅 상세

- 연결 URL: `ws://<host>/ws/parties/{party_id}?token=<access_token>`
  - 프론트에서는 `/ws/parties/{id}?token=...` 상대경로로 열면 Vite proxy가 전달.
  - WebSocket은 Authorization 헤더를 못 쓰므로 token을 query로 전달한다 (명세 §7).
- 연결 거부(close code 1008) 조건: 토큰 없음 / 만료·위조 / 비활성 사용자 / 해당 파티 비참여자 / 없는 파티.
- 송신(프론트 → 서버): `{ "content": "보낼 메시지" }`
- 수신(서버 → 프론트, 방 전체 브로드캐스트):
  ```json
  { "id": 1, "party_id": 3, "user_id": 5, "user_name": "이가람", "content": "안녕", "created_at": "2026-05-29T18:00:00" }
  ```
- 빈 메시지(공백만)는 저장하지 않고 무시된다.
- 과거 메시지는 WebSocket 연결과 별개로 `GET /api/parties/{id}/messages`로 먼저 불러온다.

---

## 7. Enum 값 정리

| 구분 | 값 |
| --- | --- |
| 파티 상태 status | recruiting(모집중) / matched(매칭완료) / canceled(취소) / expired(시간만료) / completed(이용완료) |
| 성별 매칭 gender_rule | any(제한없음) / same_gender(동성만) |
| 사용자 성별 gender | male / female / none(none은 화면 기본값일 뿐 가입 시 거부) |
| 사용자 권한 role | user / admin |
| 요금 출처 fare_source | kakao_mobility / fallback |

회원가입에서는 `male`/`female`만 허용한다.

---

## 8. 프론트 연동 체크리스트

- [ ] 로그인 성공 시 `access_token` 저장, 이후 요청 헤더에 `Bearer` 부착
- [ ] 401 응답 시 로그인 화면으로 유도 (토큰 만료 처리)
- [ ] 에러는 `response.data.detail` 문자열을 그대로 표시
- [ ] 시간 입력은 ISO 8601(KST)로 전송
- [ ] 파티 생성/참여 후 응답의 `status`, `current_members`, `per_person_fare`로 화면 갱신
- [ ] 채팅: 먼저 메시지 목록 GET → WebSocket 연결 → 수신 메시지 append
- [ ] 관리자 화면은 admin 권한 토큰으로만 접근

---

## 9. 명세 정합 완료 / 회의 결정 대기 항목

정합 완료(2026-05-29, 명세 v0.4 기준으로 코드 일치):
- 파티 참여 응답에 `result_code` / `can_join` / `reason` 래퍼 추가 (PartyJoinResponse).
- `members`를 평탄 구조 `{id, name, gender}`로 통일 (이전 `{user, joined_at}` 폐기).
- 파티 상세의 생성자는 `creator_name` 문자열 (이전 `creator` 객체 폐기).
- `fare_source` 값은 `"kakao_mobility"` (이전 `"kakao"` 폐기).

아래는 임의 확정하지 않고 팀 회의 결정 후 갱신한다. 현재는 동작하는 코드 기준값을 적어둔 것이다.
- 비즈니스 예외 HTTP 코드: 코드는 참여/취소 실패를 대부분 `400 + detail`로 내려준다. 명세 v0.4(PARTY-006/007/008)는 중복·정원·상태 충돌 `409`, 성별 불일치 `403`을 규정 → "에러 코드 세분화" 회의 후 통일. 프론트는 당분간 `detail` 문자열로 분기.
- 환경변수 이름: 코드 `.env`는 `KAKAO_REST_API_KEY`, `JWT_EXPIRES_MINUTES`. 명세 §23-2/README는 `KAKAO_MOBILITY_REST_API_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`. 회의 후 통일.
- 검증 에러의 `errors` 배열 포함 여부/세분화 수준.
- 외부 API(Kakao) 실패 시 정책(현재는 fallback 0원 처리).

문의는 TL(이가람)에게.
