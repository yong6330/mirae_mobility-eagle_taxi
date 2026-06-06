# 1주차_API 명세서_용석희_v0.4

> 변환 원본: `1주차_API 명세서_용석희_v0.4.docx`

탭 1

# Mirae Mobility API 명세서 v0.4

## 1. 문서 목적

본 문서는 「독수리 택시」 프로젝트의 프론트엔드와 백엔드가 같은 기준으로 개발될 수 있도록 API 구조를 정의한 내부 기준 문서이다.

React 프론트엔드는 본 명세서에 정의된 API 주소, 요청값, 응답값을 기준으로 화면을 구현한다.

FastAPI 백엔드는 본 명세서에 정의된 API를 기준으로 사용자, 파티, 참여자, 채팅, 요금 산정 데이터를 처리한다.

본 문서는 프론트엔드와 백엔드가 따로 개발되더라도 최종 통합 시 충돌이 발생하지 않도록 하는 개발 계약서 역할을 한다.

## 2. 프로젝트 기본 정보

<!-- 표 1 -->
| 구분 | 내용 |
| --- | --- |
| 프로젝트명 | 독수리 택시 |
| 팀명 | Mirae Mobility |
| GitHub 저장소 | https://github.com/yong6330/mirae_mobility-eagle_taxi |
| 프론트엔드 | React + Vite |
| 백엔드 | Python FastAPI |
| 데이터베이스 | SQLite |
| DB 접근 방식 | SQLAlchemy |
| 인증 방식 | JWT Bearer Token |
| 지도 API | Campus Map JavaScript API |
| 장소 검색 | Campus Map Places keywordSearch |
| 예상 택시비 산정 | External Mobility Directions API |
| 채팅 방식 | FastAPI WebSocket |
| 프론트엔드 주소 | http://localhost:5173 |
| 백엔드 주소 | http://localhost:8000 |
| API 문서 주소 | http://localhost:8000/docs |

## 3. API 기본 원칙

<!-- 표 2 -->
| 항목 | 기준 |
| --- | --- |
| 기본 API Prefix | /api |
| 데이터 형식 | JSON |
| 날짜 형식 | ISO 8601 문자열 |
| 시간 기준 | KST, Asia/Seoul |
| 인증 방식 | JWT Bearer Token |
| 핵심 데이터 저장 | SQLite |
| 프론트 DB 직접 접근 | 금지 |
| localStorage 사용 | 로그인 토큰 저장 외 금지 |
| API 변경 | PM, TL, QA&Front 확인 후 반영 |
| 실제 택시 호출 | 구현하지 않음 |
| 실제 배차 | 구현하지 않음 |
| 실제 결제 | 구현하지 않음 |
| 운전자 연결 | 구현하지 않음 |
| 예상 택시비 자동 산정 | 구현함 |
| 실제 결제 금액 확정 | 구현하지 않음 |
| 신고 저장 API | 구현하지 않음 |

## 4. 날짜·시간 기준

API에서 사용하는 날짜·시간 값은 ISO 8601 문자열을 사용한다.

본 프로젝트의 기본 시간 기준은 한국 시간, KST, Asia/Seoul로 한다.

프론트엔드는 사용자가 선택한 날짜·시간을 KST 기준으로 백엔드에 전달한다.

백엔드는 저장 및 응답 시 동일한 형식을 유지한다.

예시:

2026-05-10T18:00:00

<!-- 표 3 -->
| 필드 | 설명 |
| --- | --- |
| departure_time | 희망 출발 시간 |
| created_at | 생성 시간 |
| joined_at | 파티 참여 시간 |
| canceled_at | 취소 시간 |
| expired_at | 출발시간 만료 처리 시간, 선택 |
| message_created_at | 채팅 메시지 작성 시간 |

## 5. API 포함 기능 검토표

<!-- 표 4 -->
| 기능 | API 설계 여부 | 처리 방식 |
| --- | --- | --- |
| 랜딩 페이지 | API 불필요 | 프론트 정적 화면 / |
| 서비스 메인 | 일부 포함 | GET /api/auth/me, GET /api/my/parties, GET /api/parties/recommend 활용 |
| 서버 상태 확인 | 포함 | GET /api/health |
| 회원가입 | 포함 | POST /api/auth/register |
| 로그인 | 포함 | POST /api/auth/login |
| 내 정보 조회 | 포함 | GET /api/auth/me |
| 로그아웃 | 포함 | 백엔드 API 없이 프론트 토큰 삭제 |
| 계정/설정 조회 | 포함 | GET /api/auth/me 기반 사용자 정보 표시 |
| 장소명 검색 및 좌표 선택 | 포함 | Campus Map JavaScript API, Places keywordSearch |
| 예상 택시비 자동 산정 | 포함 | GET /api/fares/estimate |
| 1인 예상 요금 계산 | 포함 | 예상 택시비 산정 후 백엔드 내부 계산 |
| 파티 생성 | 포함 | POST /api/parties, 요금 자동 산정 포함 |
| 파티 목록 조회 | 포함 | GET /api/parties |
| 파티 검색 | 포함 | GET /api/parties/search |
| 유사 파티 추천 | 포함 | GET /api/parties/recommend |
| 파티 상세 조회 | 포함 | GET /api/parties/{party_id} |
| 파티 참여 | 포함 | POST /api/parties/{party_id}/join |
| 이동 시간대 중복 참여 차단 | 포함 | POST /api/parties/{party_id}/join 내부 처리 |
| 파티 참여 취소 | 포함 | DELETE /api/parties/{party_id}/leave |
| 파티 취소 | 포함 | PATCH /api/parties/{party_id}/cancel |
| 출발시간 만료 처리 | 포함 | 파티 목록·상세·참여 API 내부 처리 |
| 내 파티 목록 | 포함 | GET /api/my/parties |
| 채팅 메시지 목록 | 포함 | GET /api/parties/{party_id}/messages |
| 실시간 채팅 | 포함 | WS /ws/parties/{party_id}?token=<access_token> |
| 관리자 통계 | 포함 | GET /api/admin/stats |
| 최근 파티 조회 | 포함 | GET /api/admin/parties/recent |
| 관리자 사용자 목록 조회 | 포함 | GET /api/admin/users |
| 안전 안내 | API 불필요 | 프론트 정적 화면 /guide |
| 신고 버튼 | API 불필요 | 저장 기능 없이 안내 모달 또는 /guide 연결 |
| 이용약관 안내 | API 불필요 | 프론트 정적 화면 /terms, 원본 문서는 docs/terms.md로 관리 |
| 개인정보 처리방침 안내 | API 불필요 | 프론트 정적 화면 /privacy, 원본 문서는 docs/privacy.md로 관리 |
| 관리자 통계 | 포함 | GET /api/admin/stats |
| 관리자 파티 목록 조회 | 포함 | GET /api/admin/parties |
| 관리자 파티 상태 변경 | 포함 | PATCH /api/admin/parties/{party_id}/status |
| 관리자 사용자 목록 조회 | 포함 | GET /api/admin/users |
| 관리자 사용자 권한 변경 | 포함 | PATCH /api/admin/users/{user_id}/role |
| 관리자 사용자 활성 상태 변경 | 포함 | PATCH /api/admin/users/{user_id}/status |
| 관리자 최근 메시지 조회 | 포함 | GET /api/admin/messages/recent |
| 관리자 사용자 상세 조회 | 포함 | GET /api/admin/users/{user_id} |
| 관리자 파티 상세 조회 | 포함 | GET /api/admin/parties/{party_id} |
| completed 상태 처리 | 포함 | matched 파티의 departure_time 경과 시 completed 처리 |
| Version 고정 | API 불필요 | Version 0.1.0-alpha(v0.1.0-alpha) 기준을 문서와 화면에 표시 |
| 지도 표시 | API 일부 포함 | Campus Map + 파티 상세 좌표값 |
| 결제수단 버튼 | API 불필요 | 설정 화면 내 추후 기능 버튼, 실제 결제 기능 없음 |
| 실제 택시 호출 | 제외 | MVP 범위 제외 |
| 실제 배차 | 제외 | MVP 범위 제외 |
| 실제 결제 | 제외 | MVP 범위 제외 |
| 실제 결제 금액 확정 | 제외 | 예상 택시비 안내와 실제 결제 금액은 다를 수 있음 |
| 신고 저장 API | 제외 | 추후 기능 |
| 소셜 로그인 | 제외 | MVP 범위 제외 |
| 비밀번호 재설정 | 제외 | MVP 범위 제외 |
| 실시간 위치 추적 | 제외 | MVP 범위 제외 |

## 6. 공통 인증 Header

로그인이 필요한 API는 아래 Header를 사용한다.

Authorization: Bearer <access_token>

예시:

Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...

주의사항:

access_token은 로그인 성공 시 발급된다.

프론트엔드는 access_token을 localStorage에 저장한다.

access_token은 API 요청 시 Authorization Header에 포함한다.

access_token은 화면에 노출하지 않는다.

access_token은 GitHub에 업로드하지 않는다.

## 7. WebSocket 인증 기준

브라우저 기본 WebSocket은 일반 fetch 요청처럼 Authorization Header를 직접 넣기 어렵다.

따라서 WebSocket 연결은 아래처럼 query token 방식을 사용한다.

/ws/parties/{party_id}?token=<access_token>

프론트 연결 예시:

const token = localStorage.getItem('access_token')

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'

const socket = new WebSocket(

`${protocol}://${window.location.host}/ws/parties/${partyId}?token=${token}`

)

토큰 검증 후 사용자 is_active=false이면 WebSocket 연결을 거부한다.

백엔드는 WebSocket 연결 시 query token을 검증하고, 토큰이 없거나 유효하지 않으면 연결을 거부한다.

WebSocket token 관리 주의사항:

WebSocket 연결을 위해 access_token을 query parameter로 전달한다.

access_token은 개발 서버 로그나 화면에 출력하지 않는다.

access_token을 코드에 직접 작성하지 않는다.

해당 방식은 프로젝트 MVP 개발 기준이며, 실제 서비스화 단계에서는 보안 검토가 필요하다.

## 8. 공통 상태값

### 8-1. 사용자 성별

<!-- 표 5 -->
| 값 | 화면 표시 |
| --- | --- |
| male | 남성 |
| female | 여성 |

주의사항:

회원가입 화면의 기본 상태는 “선택 안 함”으로 두되, 제출 전 male 또는 female을 선택해야 한다.

“선택 안 함”은 화면의 미선택 상태일 뿐, 서버 저장값으로 사용하지 않는다.

API 요청값과 DB 저장값은 male, female만 허용한다.

성별을 선택하지 않으면 회원가입을 완료할 수 없다.

### 8-2. 사용자 권한

<!-- 표 6 -->
| 값 | 의미 |
| --- | --- |
| user | 일반 사용자 |
| admin | 관리자 |

관리자 권한 기준:

users.role 값이 admin인 경우 관리자 권한을 가진다.

MVP 개발 단계에서는 .env의 ADMIN_EMAILS에 등록된 이메일 또는 DB seed 방식으로 관리자 계정을 지정할 수 있다.

일반 사용자가 프론트 화면에서 직접 admin 권한을 선택할 수 없도록 한다.

### 8-3. 파티 상태

<!-- 표 7 -->
| 값 | 화면 표시 | 의미 |
| --- | --- | --- |
| recruiting | 모집 중 | 참여 가능 |
| matched | 매칭 완료 | 최대 인원 도달 또는 매칭 완료 |
| canceled | 취소 | 생성자 또는 관리자가 파티를 취소함 |
| expired | 출발시간 만료 | 모집 중이었으나 출발 시간이 지나 더 이상 참여 불가 |
| completed | 이용 완료 | 매칭 완료된 파티의 출발 시간이 지나 이용이 완료됨 |

상태 처리 기준:

현재 시간이 departure_time을 지났고 status가 recruiting인 파티는 expired로 처리한다.

현재 시간이 departure_time을 지났고 status가 matched인 파티는 completed로 처리한다.

expired 파티는 신규 참여가 불가능하다.

completed 파티는 신규 참여가 불가능하며, 내 파티 이력과 관리자 페이지에 표시된다.

canceled 상태는 자동으로 다른 상태로 변경하지 않는다.

내 파티 목록에는 expired, completed, canceled 파티가 표시될 수 있으며, 화면에서는 상태를 구분 표시한다.

관리자 통계에는 expired_parties, completed_parties를 포함한다.

### 8-4. 성별 매칭 기준

<!-- 표 8 -->
| 값 | 화면 표시 | 의미 |
| --- | --- | --- |
| any | 제한 없음 | 성별과 관계없이 참여 가능 |
| same_gender | 동성 매칭 | 생성자와 같은 성별 사용자만 참여 가능 |

성별 매칭 처리 기준:

gender_rule 기본값은 any로 한다.

gender_rule이 same_gender이면 생성자의 gender를 party_gender로 저장한다.

회원가입 또는 파티 생성 화면의 성별 기본값이 none인 상태에서는 same_gender 파티 생성을 제한한다.

same_gender 파티 참여 시 로그인 사용자의 gender와 party_gender가 일치해야 한다.

성별 매칭은 안전장치 성격의 Target 기능으로 본다.

## 9. 공통 에러 응답

{

"detail": "에러 메시지"

}

<!-- 표 9 -->
| 상태 코드 | 의미 | 예시 |
| --- | --- | --- |
| 400 | 잘못된 요청 | 필수값 누락, 잘못된 입력값 |
| 401 | 인증 실패 | 로그인 필요, 토큰 만료 |
| 403 | 권한 없음 | 관리자 권한 필요, 비참여자 접근, 성별 조건 불일치, 비활성화된 사용자 |
| 404 | 데이터 없음 | 존재하지 않는 파티 |
| 409 | 충돌 | 이미 참여한 파티, 최대 인원 초과, 만료된 파티 |
| 422 | 검증 실패 | 데이터 타입 오류 |
| 500 | 서버 오류 | 예외 처리 필요 |
| 502 | 외부 API 오류 | External Mobility API 오류, 요금 산정 실패 |

## 10. 공통 요금 산정 기준

### 10-1. 예상 택시비 자동 산정

예상 택시비는 사용자가 직접 입력하지 않는다.

예상 택시비는 출발지 좌표, 도착지 좌표, 출발 시간을 기준으로 백엔드가 External Mobility 길찾기 API를 호출해 자동 산정한다.

External Mobility API 응답에서 아래 값을 사용한다.

<!-- 표 10 -->
| External Mobility 응답값 | 프로젝트 저장/응답 필드 | 설명 |
| --- | --- | --- |
| routes[0].summary.fare.taxi | estimated_fare | 예상 택시비 |
| routes[0].summary.fare.toll | toll_fare | 예상 통행료 |
| routes[0].summary.distance | distance_meters | 예상 이동 거리 |
| routes[0].summary.duration | duration_seconds | 예상 이동 시간 |

요금 산정 기준:

사용자는 estimated_fare를 입력하지 않는다.

사용자는 per_person_fare를 입력하지 않는다.

사용자는 출발지와 도착지를 검색해 좌표를 선택한다.

사용자는 희망 출발 시간을 선택한다.

백엔드는 출발지 좌표, 도착지 좌표, 출발 시간을 기준으로 External Mobility API를 호출한다.

API 응답의 summary.fare.taxi를 estimated_fare로 사용한다.

API 응답의 summary.fare.toll을 toll_fare로 사용한다.

API 응답의 summary.distance를 distance_meters로 사용한다.

API 응답의 summary.duration을 duration_seconds로 사용한다.

estimated_fare는 DB에 저장한다.

toll_fare, distance_meters, duration_seconds도 파티 정보와 함께 저장한다.

fare_source는 external_mobility로 저장한다.

주의사항:

estimated_fare는 실제 결제 금액이 아니라 예상 택시비이다.

실제 택시 호출이나 실제 결제는 구현하지 않는다.

실제 택시요금은 교통 상황, 호출 방식, 택시 종류, 미터기 기준에 따라 달라질 수 있다.

본 프로젝트에서는 API 응답의 예상 택시비를 사용자 안내용으로 사용한다.

External Mobility REST API Key는 백엔드에서만 사용한다.

프론트엔드에 External Mobility REST API Key를 노출하지 않는다.

### 10-2. 1인 예상 요금 계산

1인 예상 요금은 백엔드가 계산한다.

사용자는 per_person_fare를 입력하지 않는다.

계산식:

per_person_fare = ceil(estimated_fare / current_members)

계산 기준:

<!-- 표 11 -->
| 항목 | 기준 |
| --- | --- |
| estimated_fare | External Mobility API로 자동 산정된 전체 예상 택시비 |
| current_members | party_members 테이블 기준 현재 참여 인원 |
| per_person_fare | estimated_fare를 current_members로 나눈 뒤 원 단위 올림 |
| 파티 생성 직후 | current_members = 1 |
| 파티 참여 후 | 참여자 추가 후 current_members 재계산 |
| 파티 참여 취소 후 | 참여자 제거 후 current_members 재계산 |

예시:

<!-- 표 12 -->
| estimated_fare | current_members | per_person_fare |
| --- | --- | --- |
| 12,000원 | 1명 | 12,000원 |
| 12,000원 | 2명 | 6,000원 |
| 12,000원 | 3명 | 4,000원 |
| 12,000원 | 4명 | 3,000원 |
| 10,000원 | 3명 | 3,334원 |

### 10-3. 요금 산정 실패 처리

요금 산정이 실패하면 파티 생성은 진행하지 않는다.

<!-- 표 13 -->
| 상황 | 처리 |
| --- | --- |
| 출발지 좌표 없음 | 파티 생성 차단 |
| 도착지 좌표 없음 | 파티 생성 차단 |
| 출발 시간 없음 | 파티 생성 차단 |
| External Mobility API Key 없음 | 파티 생성 차단 |
| 경로 조회 실패 | 파티 생성 차단 |
| fare.taxi 없음 | 파티 생성 차단 |
| API 호출 제한 또는 오류 | 다시 시도 안내 |

화면 안내 예시:

예상 택시비를 계산하지 못했습니다. 출발지와 도착지를 다시 확인해주세요.

### 10-4. 파티 참여·참여 취소 시 요금 처리

파티 참여 또는 참여 취소 시에는 External Mobility API를 다시 호출하지 않는다.

처리 기준:

파티 생성 시 저장된 estimated_fare를 유지한다.

파티 생성 시 저장된 toll_fare, distance_meters, duration_seconds를 유지한다.

참여자 수가 바뀌면 current_members만 재계산한다.

current_members가 바뀌면 per_person_fare만 다시 계산한다.

per_person_fare는 응답 시점 계산값으로 사용한다.

## 11. 파티 생성 기준

### 11-1. 최대 인원 기준

max_members는 최소 2명, 최대 4명으로 제한한다.

1명 파티는 합승 목적에 맞지 않으므로 허용하지 않는다.

5명 이상은 일반 택시 탑승 기준과 맞지 않으므로 허용하지 않는다.

### 11-2. 출발 시간 기준

departure_time은 현재 시간 이후여야 한다.

과거 시간으로 파티를 생성할 수 없다.

출발 시간이 지난 recruiting 파티는 expired로 처리한다.

### 11-3. 생성자 자동 참여 기준

파티 생성자는 생성과 동시에 party_members에 자동 추가된다.

파티 생성 직후 current_members는 1이다.

파티 생성 직후 per_person_fare는 estimated_fare와 같다.

estimated_fare는 사용자가 입력한 값이 아니라 External Mobility API로 자동 산정한 값이다.

### 11-4. 만남 장소 기준

meeting_point는 택시 탑승 전 실제로 모일 장소를 의미한다.

meeting_note는 만남 장소에 대한 추가 안내를 의미한다.

meeting_point와 meeting_note는 선택값으로 둔다.

파티 상세 화면에서 meeting_point와 meeting_note를 표시한다.

### 11-5. 성별 매칭 기준

gender_rule은 any 또는 same_gender만 허용한다.

gender_rule 기본값은 any이다.

gender_rule이 same_gender인 경우 생성자의 gender를 party_gender로 저장한다.

화면 기본값이 none인 상태에서는 same_gender 파티를 생성할 수 없으며, DB에는 male 또는 female만 저장한다.

same_gender 파티 참여 시 사용자 gender와 party_gender가 일치해야 한다.

## 12. DB 테이블 기준

### 12-1. users 테이블

<!-- 표 14 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 사용자 고유 ID |
| email | String, Unique | 로그인 이메일 |
| password_hash | String | 해시 처리된 비밀번호 |
| name | String | 이름 또는 닉네임 |
| gender | String | male / female. none은 회원가입 화면의 미선택 기본 상태로만 사용하고 DB에는 저장하지 않음 |
| role | String | user / admin |
| created_at | DateTime | 가입 시간 |
| is_active | Boolean | 사용자 활성 상태, 기본 true |

주의사항:

password_hash는 API 응답에 포함하지 않는다.

role은 기본 user로 생성한다.

is_active는 기본 true로 생성한다.

admin 권한은 seed 또는 ADMIN_EMAILS 기준으로 지정할 수 있다.

관리자는 관리자 페이지에서 사용자 role과 is_active 값을 변경할 수 있다.

gender는 male / female만 저장한다.

### 12-2. parties 테이블

<!-- 표 15 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 파티 고유 ID |
| creator_id | Integer, FK | 파티 생성자 ID |
| start_place | String | 출발지명 |
| start_lat | Float | 출발지 위도 |
| start_lng | Float | 출발지 경도 |
| end_place | String | 도착지명 |
| end_lat | Float | 도착지 위도 |
| end_lng | Float | 도착지 경도 |
| departure_time | DateTime | 희망 출발 시간 |
| meeting_point | String, Nullable | 만남 장소 상세 |
| meeting_note | String, Nullable | 만남 관련 추가 안내 |
| estimated_fare | Integer | External Mobility API로 산정한 예상 택시비 |
| toll_fare | Integer | External Mobility API로 산정한 예상 통행료 |
| distance_meters | Integer | External Mobility API로 산정한 예상 이동 거리 |
| duration_seconds | Integer | External Mobility API로 산정한 예상 이동 시간 |
| fare_source | String | 요금 산정 출처, external_mobility |
| max_members | Integer | 최대 인원, 2~4명 |
| gender_rule | String | any / same_gender |
| party_gender | String, Nullable | same_gender 파티의 기준 성별 |
| status | String | recruiting / matched / canceled / expired / completed |
| cancel_reason | String, Nullable | 취소 사유 |
| canceled_at | DateTime, Nullable | 취소 시간 |
| created_at | DateTime | 생성 시간 |

주의사항:

current_members는 DB 컬럼으로 저장하지 않고 party_members count로 계산한다.

per_person_fare는 DB 컬럼으로 저장하지 않고 응답 시점에 계산한다.

estimated_fare는 사용자가 입력한 값이 아니라 External Mobility API 응답값을 저장한다.

toll_fare, distance_meters, duration_seconds는 요금 안내와 검증을 위해 함께 저장한다.

실제 택시 호출 결과나 실제 결제 결과는 저장하지 않는다.

matched 파티의 departure_time이 지난 경우 completed로 처리할 수 있다.

completed 파티는 내 파티 이력과 관리자 페이지에 표시한다.

### 12-3. party_members 테이블

<!-- 표 16 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 참여 정보 ID |
| party_id | Integer, FK | 파티 ID |
| user_id | Integer, FK | 사용자 ID |
| joined_at | DateTime | 참여 시간 |

제약 조건:

같은 user_id는 같은 party_id에 중복 참여할 수 없다.

party_id와 user_id 조합은 unique로 관리한다.

파티 생성자는 파티 생성 시 자동으로 party_members에 추가된다.

### 12-4. messages 테이블

<!-- 표 17 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 메시지 ID |
| party_id | Integer, FK | 파티 ID |
| user_id | Integer, FK | 작성자 ID |
| content | Text | 메시지 내용 |
| created_at | DateTime | 작성 시간 |

주의사항:

채팅 메시지는 같은 파티 참여자만 조회할 수 있다.

채팅 메시지는 같은 파티 참여자만 전송할 수 있다.

빈 메시지는 저장하지 않는다.

## 13. API 전체 목록

<!-- 표 18 -->
| API ID | API 이름 | Method | Endpoint | 인증 | 우선순위 |
| --- | --- | --- | --- | --- | --- |
| SYS-001 | 서버 상태 확인 | GET | /api/health | X | Must |
| AUTH-001 | 회원가입 | POST | /api/auth/register | X | Must |
| AUTH-002 | 로그인 | POST | /api/auth/login | X | Must |
| AUTH-003 | 내 정보 조회 | GET | /api/auth/me | O | Must |
| AUTH-004 | 로그아웃 | 없음 | 프론트 처리 | X | Must |
| PLACE-001 | 장소명 검색 및 좌표 선택 | Campus Map SDK | mapProvider.places.keywordSearch | Map JavaScript Key | Must |
| FARE-001 | 예상 택시비 자동 산정 | GET | /api/fares/estimate | O | Must |
| PARTY-001 | 파티 생성 | POST | /api/parties | O | Must |
| PARTY-002 | 파티 목록 조회 | GET | /api/parties | O | Must |
| PARTY-003 | 파티 검색 | GET | /api/parties/search | O | Target |
| PARTY-004 | 유사 파티 추천 | GET | /api/parties/recommend | O | Target |
| PARTY-005 | 파티 상세 조회 | GET | /api/parties/{party_id} | O | Must |
| PARTY-006 | 파티 참여 | POST | /api/parties/{party_id}/join | O | Must |
| PARTY-007 | 파티 참여 취소 | DELETE | /api/parties/{party_id}/leave | O | Target |
| PARTY-008 | 파티 취소 | PATCH | /api/parties/{party_id}/cancel | O | Target |
| PARTY-009 | 내 파티 목록 조회 | GET | /api/my/parties | O | Target |
| MSG-001 | 채팅 메시지 목록 조회 | GET | /api/parties/{party_id}/messages | O | Target |
| MSG-002 | 파티 WebSocket 연결 및 메시지 송수신 | WS | /ws/parties/{party_id}?token=<access_token> | O | Target |
| ADMIN-001 | 관리자 통계 조회 | GET | /api/admin/stats | O, admin | Could |
| ADMIN-002 | 최근 파티 조회 | GET | /api/admin/parties/recent | O, admin | Could |
| ADMIN-003 | 사용자 목록 조회 | GET | /api/admin/users | O, admin | Could |
| ADMIN-004 | 관리자 파티 목록 조회 | GET | /api/admin/parties | O, admin | Could |
| ADMIN-005 | 관리자 파티 상태 변경 | PATCH | /api/admin/parties/{party_id}/status | O, admin | Could |
| ADMIN-006 | 관리자 사용자 권한 변경 | PATCH | /api/admin/users/{user_id}/role | O, admin | Could |
| ADMIN-007 | 관리자 사용자 활성 상태 변경 | PATCH | /api/admin/users/{user_id}/status | O, admin | Could |
| ADMIN-008 | 관리자 최근 메시지 조회 | GET | /api/admin/messages/recent | O, admin | Could |
| ADMIN-009 | 관리자 사용자 상세 조회 | GET | /api/admin/users/{user_id} | O, admin | Could |
| ADMIN-010 | 관리자 파티 상세 조회 | GET | /api/admin/parties/{party_id} | O, admin | Could |

# 14. System API

## SYS-001. 서버 상태 확인

<!-- 표 19 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 서버 상태 확인 |
| Method | GET |
| Endpoint | /api/health |
| 인증 | 불필요 |
| 사용 화면 | 없음, 개발 확인용 |
| 처리 내용 | 백엔드 서버가 정상 실행 중인지 확인한다. |
| 완료 기준 | FastAPI 서버 실행 후 정상 응답이 반환되어야 한다. |

### 응답 Body

{

"status": "ok",

"service": "eagle-taxi-api"

}

### 예외 상황

<!-- 표 20 -->
| 상태 | 처리 |
| --- | --- |
| 서버 미실행 | 요청 실패 |
| 서버 내부 오류 | 500 응답 |

# 15. Auth API

## AUTH-001. 회원가입

<!-- 표 21 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 회원가입 |
| Method | POST |
| Endpoint | /api/auth/register |
| 인증 | 불필요 |
| 사용 화면 | 회원가입 /signup |
| 처리 내용 | 이메일, 비밀번호, 이름, 성별을 입력받아 사용자를 생성한다. |
| 완료 기준 | 회원가입 후 로그인 가능한 사용자 계정이 생성되어야 한다. |

### 요청 Body

{

"email": "test@yonsei.ac.kr",

"password": "password1234",

"name": "테스트",

"gender": "male"

}

### 요청값 설명

<!-- 표 22 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | string | O | 로그인 이메일 |
| password | string | O | 비밀번호 |
| name | string | O | 이름 또는 닉네임 |
| gender | string | O | male / female 중 하나. 화면에는 남성 / 여성으로 표시한다. 선택 안 함 상태로는 회원가입을 완료할 수 없다. |

### 응답 Body

{

"id": 1,

"email": "test@yonsei.ac.kr",

"name": "테스트",

"gender": "male",

"role": "user",

"is_active": true,

"created_at": "2026-05-10T18:00:00"

}

### 처리 로직

이메일 형식 확인

비밀번호 입력 여부 확인

name 입력 여부 확인

gender 입력 여부 확인

gender 값이 male 또는 female인지 확인

gender 값이 비어 있거나 미선택 상태이면 회원가입 차단

이메일 중복 여부 확인

비밀번호 해시 처리

role 기본값을 user로 설정

is_active 기본값을 true로 설정

users 테이블에 사용자 생성

생성된 사용자 정보 반환

### 예외 응답

<!-- 표 23 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 400 | 필수값 누락 | 필수 항목을 입력해주세요. |
| 400 | 성별값 오류 | 성별 값이 올바르지 않습니다. |
| 400 | 성별 미선택 | 성별을 선택해주세요. |
| 409 | 이메일 중복 | 이미 가입된 이메일입니다. |

## AUTH-002. 로그인

<!-- 표 24 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 로그인 |
| Method | POST |
| Endpoint | /api/auth/login |
| 인증 | 불필요 |
| 사용 화면 | 로그인 /login |
| 처리 내용 | 이메일과 비밀번호를 검증하고 JWT access_token을 발급한다. |
| 완료 기준 | 로그인 성공 시 access_token과 user 객체가 반환되어야 한다. |

### 요청 Body

{

"email": "test@yonsei.ac.kr",

"password": "password1234"

}

### 응답 Body

{

"access_token": "jwt-token",

"token_type": "bearer",

"user": {

"id": 1,

"email": "test@yonsei.ac.kr",

"name": "테스트",

"gender": "male",

"role": "user"

}

}

### 처리 로직

이메일로 사용자 조회

사용자가 없으면 인증 실패 반환

비밀번호 해시 검증

사용자 is_active=false이면 로그인 차단

비활성화된 사용자입니다. 메시지와 함께 403 응답 반환

검증 실패 시 인증 실패 반환

JWT access_token 발급

token_type과 user 정보 반환

### 예외 응답

<!-- 표 25 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 로그인 실패 | 이메일 또는 비밀번호가 올바르지 않습니다. |
| 403 | 비활성 사용자 | 비활성화된 사용자입니다. |

## AUTH-003. 내 정보 조회

<!-- 표 26 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 내 정보 조회 |
| Method | GET |
| Endpoint | /api/auth/me |
| 인증 | 필요 |
| 사용 화면 | 공통 Header, 관리자 페이지 |
| 처리 내용 | JWT 토큰을 검증하고 현재 로그인한 사용자 정보를 반환한다. |
| 완료 기준 | 새로고침 후에도 로그인 사용자 정보와 권한을 확인할 수 있어야 한다. |

### 요청 Header

Authorization: Bearer <access_token>

### 응답 Body

{

"id": 1,

"email": "test@yonsei.ac.kr",

"name": "테스트",

"gender": "male",

"role": "user",

"created_at": "2026-05-10T18:00:00"

}

### 예외 응답

<!-- 표 27 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 토큰 없음 | 로그인이 필요합니다. |
| 401 | 토큰 만료 | 로그인 정보가 만료되었습니다. |
| 401 | 토큰 오류 | 유효하지 않은 토큰입니다. |
| 403 | 비활성 사용자 | 비활성화된 사용자입니다. |

## AUTH-004. 로그아웃

<!-- 표 28 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 로그아웃 |
| Method | 없음 |
| Endpoint | 없음 |
| 인증 | 불필요 |
| 사용 화면 | 공통 Header |
| 처리 내용 | 프론트엔드에서 localStorage의 access_token을 삭제하고 사용자 상태를 초기화한다. |
| 완료 기준 | 로그아웃 후 비로그인 상태로 전환되어야 한다. |

### 처리 방식

프론트엔드에서 access_token 삭제

user 상태 초기화

홈 또는 로그인 화면으로 이동

### 주의사항

백엔드 API를 만들지 않는다.

로그아웃은 프론트 처리로 충분하다.

localStorage는 access_token 저장과 삭제 용도 외에는 사용하지 않는다.

# 16. Place / Campus Map API

## PLACE-001. 장소명 검색 및 좌표 선택

<!-- 표 29 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 장소명 검색 및 좌표 선택 |
| Method | Campus Map JavaScript API |
| Endpoint | 백엔드 Endpoint 없음 |
| 사용 SDK | mapProvider.places.keywordSearch |
| 인증 | Map JavaScript API Key |
| 사용 화면 | 파티 생성 /parties/new, 파티 목록·검색 /parties, 파티 상세 지도 표시 |
| 처리 내용 | 사용자가 입력한 장소명을 Campus Map Places 검색으로 조회하고, 선택한 장소의 장소명·주소·위도·경도를 프론트에서 확보한다. |
| 완료 기준 | 사용자가 출발지와 도착지를 장소명으로 검색하고, 선택한 장소의 좌표가 파티 생성 API 요청값과 요금 산정 API 요청값에 포함되어야 한다. |

### 중요 기준

PLACE-001은 FastAPI 백엔드 API가 아니다.

React 프론트엔드에서 Campus Map JavaScript API를 호출하는 외부 SDK 기능이다.

따라서 FastAPI에는 GET /api/places를 구현하지 않는다.

### 입력값

<!-- 표 30 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| keyword | string | O | 사용자가 입력한 장소 검색어 |

### 프론트에서 확보할 값

<!-- 표 31 -->
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| place_name | string | 장소명 |
| address_name | string | 주소 |
| lat | number | 위도 |
| lng | number | 경도 |

### 처리 흐름

사용자가 출발지 또는 도착지 입력창에 장소명을 입력한다.

프론트엔드는 Campus Map Places keywordSearch를 호출한다.

검색 결과 목록을 사용자에게 표시한다.

사용자가 결과 중 하나를 선택한다.

선택한 장소명, 주소, 위도, 경도를 화면 상태에 저장한다.

파티 생성 시 선택된 장소명과 좌표를 POST /api/parties 요청 Body에 포함한다.

예상 택시비 미리보기가 필요하면 선택된 좌표를 GET /api/fares/estimate 요청 Query에 포함한다.

### 예외 상황

<!-- 표 32 -->
| 상황 | 처리 |
| --- | --- |
| 검색 결과 없음 | “검색 결과가 없습니다.” 표시 |
| Campus Map API 로딩 실패 | “지도를 불러오지 못했습니다.” 표시 |
| 좌표값 없음 | 파티 생성 불가 |
| 장소 미선택 | 필수값 누락 안내 |

### 주의사항

기존 GET /api/places 백엔드 API는 사용하지 않는다.

장소 검색과 좌표 선택은 프론트엔드에서 Campus Map JavaScript API로 처리한다.

백엔드는 사용자가 선택한 장소명과 좌표값을 저장한다.

사용자에게 경로 안내·내비게이션·실시간 이동 경로를 제공하는 기능은 구현하지 않는다.

예상 택시비 산정을 위한 백엔드 내부 경로 조회는 FARE-001 및 PARTY-001 내부 로직에서 External Mobility API로 처리한다.

실제 택시 호출, 배차, 결제, 실시간 위치 추적은 구현하지 않는다.

# 17. Fare API

## FARE-001. 예상 택시비 자동 산정

<!-- 표 33 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 예상 택시비 자동 산정 |
| Method | GET |
| Endpoint | /api/fares/estimate |
| 인증 | 필요 |
| 사용 화면 | 파티 생성 /parties/new, 파티 상세 /parties/:partyId |
| 처리 내용 | 출발지·도착지 좌표와 출발 시간을 기준으로 External Mobility 길찾기 API를 호출해 예상 택시비, 통행료, 이동 거리, 소요 시간을 산정한다. |
| 완료 기준 | 사용자가 요금을 입력하지 않아도 예상 택시비와 1인 예상 요금이 자동 계산되어야 한다. |

### 요청 Header

Authorization: Bearer <access_token>

### 요청 Query

<!-- 표 34 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| start_lat | number | O | 출발지 위도 |
| start_lng | number | O | 출발지 경도 |
| end_lat | number | O | 도착지 위도 |
| end_lng | number | O | 도착지 경도 |
| departure_time | string | O | 희망 출발 시간, ISO 8601 |
| current_members | integer | X | 현재 인원, 기본 1 |

### 백엔드 외부 API 호출 기준

백엔드는 External Mobility 길찾기 API를 직접 호출한다.

프론트엔드에서 External Mobility REST API Key를 직접 사용하지 않는다.

외부 호출 기준:

<!-- 표 35 -->
| 항목 | 내용 |
| --- | --- |
| 외부 API | External Mobility Directions API |
| 호출 주체 | FastAPI 백엔드 |
| 인증 방식 | Authorization: ProviderAuth ${MOBILITY_REST_API_KEY} |
| 주요 입력값 | origin, destination, departure_time |
| 주요 응답값 | summary.fare.taxi, summary.fare.toll, summary.distance, summary.duration |

### 외부 API 입력값 변환

<!-- 표 36 -->
| 프로젝트 필드 | External Mobility 요청값 |
| --- | --- |
| start_lng, start_lat | origin |
| end_lng, end_lat | destination |
| departure_time | departure_time |
| 출발지명 | origin name, 선택 |
| 도착지명 | destination name, 선택 |

External Mobility 요청값 예시:

origin=127.9000,37.2800

destination=127.9199,37.3422

departure_time=202605101800

### 응답 Body

{

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"current_members": 1,

"per_person_fare": 12000,

"fare_source": "external_mobility"

}

### 처리 로직

로그인 사용자 확인

출발지 좌표 확인

도착지 좌표 확인

departure_time 확인

current_members 기본값 1 적용

External Mobility API 요청값 생성

External Mobility 길찾기 API 호출

응답의 routes[0].summary.fare.taxi 값을 estimated_fare로 추출

응답의 routes[0].summary.fare.toll 값을 toll_fare로 추출

응답의 routes[0].summary.distance 값을 distance_meters로 추출

응답의 routes[0].summary.duration 값을 duration_seconds로 추출

per_person_fare = ceil(estimated_fare / current_members) 계산

요금 산정 결과 반환

### 예외 응답

<!-- 표 37 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 400 | 출발지 좌표 없음 | 출발지를 검색 결과에서 선택해주세요. |
| 400 | 도착지 좌표 없음 | 도착지를 검색 결과에서 선택해주세요. |
| 400 | 출발 시간 없음 | 출발 시간을 선택해주세요. |
| 400 | 현재 인원 오류 | 현재 인원 값이 올바르지 않습니다. |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 500 | API Key 없음 | 요금 산정 API 설정이 필요합니다. |
| 502 | External Mobility API 오류 | 예상 택시비를 계산하지 못했습니다. |
| 502 | 경로 없음 | 선택한 출발지와 도착지의 경로를 찾지 못했습니다. |
| 502 | 요금 정보 없음 | 예상 택시비 정보가 응답에 포함되지 않았습니다. |

### 주의사항

이 API는 실제 결제 금액을 확정하는 기능이 아니다.

이 API는 사용자에게 예상 택시비를 안내하기 위한 기능이다.

실제 택시 호출, 배차, 결제는 수행하지 않는다.

External Mobility REST API Key는 백엔드 .env에 저장한다.

프론트엔드에 External Mobility REST API Key를 노출하지 않는다.

프론트엔드는 이 API 응답값을 화면에 표시만 한다.

파티 생성 시에는 백엔드가 동일한 요금 산정 로직을 다시 실행하거나 서버 측 결과를 기준으로 저장한다.

프론트에서 임의로 estimated_fare를 조작해 보내지 않도록 POST /api/parties 요청값에는 estimated_fare를 포함하지 않는다.

# 18. Party API

## PARTY-001. 파티 생성

<!-- 표 38 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 생성 |
| Method | POST |
| Endpoint | /api/parties |
| 인증 | 필요 |
| 사용 화면 | 파티 생성 /parties/new |
| 처리 내용 | 사용자가 선택한 출발지, 도착지, 출발 시간, 만남 장소, 최대 인원, 성별 매칭 옵션을 기준으로 새 파티를 생성한다. 예상 택시비는 백엔드가 External Mobility 길찾기 API로 자동 산정한다. |
| 완료 기준 | 사용자가 예상 요금을 입력하지 않아도 파티가 생성되고, estimated_fare와 per_person_fare가 자동 표시되어야 한다. |

### 요청 Header

Authorization: Bearer <access_token>

### 요청 Body

{

"start_place": "연세대학교 미래캠퍼스",

"start_lat": 37.2800,

"start_lng": 127.9000,

"end_place": "원주역",

"end_lat": 37.3422,

"end_lng": 127.9199,

"departure_time": "2026-05-10T18:00:00",

"meeting_point": "정문 앞 택시 승강장",

"meeting_note": "정문 앞에서 모인 뒤 함께 택시 탑승",

"max_members": 4,

"gender_rule": "any"

}

### 요청값 설명

<!-- 표 39 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| start_place | string | O | 출발지명 |
| start_lat | number | O | 출발지 위도 |
| start_lng | number | O | 출발지 경도 |
| end_place | string | O | 도착지명 |
| end_lat | number | O | 도착지 위도 |
| end_lng | number | O | 도착지 경도 |
| departure_time | string | O | 희망 출발 시간 |
| meeting_point | string | X | 만남 장소 상세 |
| meeting_note | string | X | 만남 관련 추가 안내 |
| max_members | integer | O | 최대 모집 인원, 2~4명 |
| gender_rule | string | O | any 또는 same_gender, 기본 any |

중요:

estimated_fare는 요청값에 포함하지 않는다.

per_person_fare는 요청값에 포함하지 않는다.

current_members는 요청값에 포함하지 않는다.

toll_fare, distance_meters, duration_seconds는 요청값에 포함하지 않는다.

예상 택시비와 1인 예상 요금은 백엔드가 계산한다.

### 응답 Body

{

"id": 1,

"creator_id": 1,

"start_place": "연세대학교 미래캠퍼스",

"start_lat": 37.2800,

"start_lng": 127.9000,

"end_place": "원주역",

"end_lat": 37.3422,

"end_lng": 127.9199,

"departure_time": "2026-05-10T18:00:00",

"meeting_point": "정문 앞 택시 승강장",

"meeting_note": "정문 앞에서 모인 뒤 함께 택시 탑승",

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"max_members": 4,

"current_members": 1,

"per_person_fare": 12000,

"fare_source": "external_mobility",

"gender_rule": "any",

"party_gender": null,

"status": "recruiting",

"created_at": "2026-05-10T17:30:00"

}

### 처리 로직

로그인 사용자 확인

입력값 검증

출발지·도착지 장소명과 좌표값 존재 여부 확인

departure_time이 현재 시간 이후인지 확인

max_members가 2명 이상 4명 이하인지 확인

gender_rule이 any 또는 same_gender인지 확인

gender_rule이 same_gender인 경우 생성자의 gender 확인

gender_rule이 same_gender이고 성별 미선택 기본값이면 생성 제한

External Mobility 길찾기 API로 예상 택시비, 통행료, 거리, 소요시간 산정

API 응답의 summary.fare.taxi를 estimated_fare로 저장

API 응답의 summary.fare.toll을 toll_fare로 저장

API 응답의 summary.distance를 distance_meters로 저장

API 응답의 summary.duration을 duration_seconds로 저장

fare_source를 external_mobility로 저장

parties 테이블에 파티 생성

same_gender 선택 시 party_gender에 생성자 gender 저장

생성자를 party_members에 자동 추가

current_members = 1로 계산

per_person_fare = ceil(estimated_fare / current_members)로 계산

status = recruiting으로 저장

생성된 파티 정보 반환

### 예외 응답

<!-- 표 40 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 400 | 필수값 누락 | 필수 항목을 입력해주세요. |
| 400 | 좌표값 없음 | 출발지와 도착지를 검색 결과에서 선택해주세요. |
| 400 | 최대 인원 오류 | 최대 인원은 2명 이상 4명 이하로 입력해야 합니다. |
| 400 | 출발 시간 오류 | 희망 출발 시간은 현재 시간 이후여야 합니다. |
| 400 | 성별 매칭 옵션 오류 | 성별 매칭 옵션 값이 올바르지 않습니다. |
| 400 | 성별 미선택 | 성별 선택 안 함 상태에서는 동성 매칭 파티를 생성할 수 없습니다. |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 502 | 요금 산정 실패 | 예상 택시비를 계산하지 못했습니다. |

## PARTY-002. 파티 목록 조회

<!-- 표 41 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 목록 조회 |
| Method | GET |
| Endpoint | /api/parties |
| 인증 | 필요 |
| 사용 화면 | 파티 목록 /parties |
| 처리 내용 | 파티 목록을 최신순으로 조회한다. |
| 완료 기준 | 상태 필터에 따라 파티 목록이 정상 표시되어야 한다. |

### 요청 Query

<!-- 표 42 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| status | string | X | recruiting, matched, canceled, expired, completed |
| page | integer | X | 페이지 번호, 기본 1 |
| limit | integer | X | 조회 개수, 기본 20 |

### 처리 기준

status query가 없으면 recruiting 상태를 기본 조회한다.

필요 시 matched, canceled, expired 상태도 필터링할 수 있다.

목록 응답에는 current_members와 per_person_fare를 계산해서 포함한다.

기본 목록에서는 departure_time이 지난 recruiting 파티를 expired로 처리하거나 제외할 수 있다.

estimated_fare는 파티 생성 시 저장된 자동 산정값을 사용한다.

파티 목록 조회 시 External Mobility API를 다시 호출하지 않는다.

### 응답 Body

{

"items": [

{

"id": 1,

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:00:00",

"meeting_point": "정문 앞 택시 승강장",

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"max_members": 4,

"current_members": 2,

"per_person_fare": 6000,

"fare_source": "external_mobility",

"gender_rule": "any",

"status": "recruiting",

"created_at": "2026-05-10T17:30:00"

}

],

"total": 1,

"page": 1,

"limit": 20

}

### 예외 응답

<!-- 표 43 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 200 | 파티 없음 | items가 빈 배열인 응답 반환 |
| 401 | 미로그인 | 로그인이 필요합니다. |

## PARTY-003. 파티 검색

<!-- 표 44 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 조건 기반 파티 검색 |
| Method | GET |
| Endpoint | /api/parties/search |
| 인증 | 필요 |
| 사용 화면 | 파티 목록 /parties |
| 처리 내용 | 출발지, 도착지, 희망 시간, 상태 기준으로 파티를 검색한다. |
| 완료 기준 | 조건에 맞는 파티 목록이 화면에 표시되어야 한다. |

### 요청 Query

<!-- 표 45 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| start_place | string | X | 출발지 |
| end_place | string | X | 도착지 |
| departure_time | string | X | 희망 출발 시간 |
| status | string | X | recruiting, matched, canceled, expired, completed |
| page | integer | X | 페이지 번호, 기본 1 |
| limit | integer | X | 조회 개수, 기본 20 |

### 응답 Body

{

"items": [

{

"id": 1,

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:10:00",

"meeting_point": "정문 앞 택시 승강장",

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"max_members": 4,

"current_members": 2,

"per_person_fare": 6000,

"fare_source": "external_mobility",

"gender_rule": "any",

"status": "recruiting"

}

],

"total": 1,

"page": 1,

"limit": 20

}

### 처리 로직

로그인 사용자 확인

Query 조건 확인

status가 없으면 recruiting 기본 적용

출발지 조건이 있으면 start_place 기준 필터

도착지 조건이 있으면 end_place 기준 필터

departure_time 조건이 있으면 가까운 출발 시간 기준 필터

expired 파티는 기본 검색 결과에서 제외

페이지네이션 적용

current_members 계산

per_person_fare 계산

검색 결과 반환

### 예외 응답

<!-- 표 46 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 200 | 검색 결과 없음 | items가 빈 배열인 응답 반환 |
| 401 | 미로그인 | 로그인이 필요합니다. |

## PARTY-004. 유사 파티 추천

<!-- 표 47 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 유사 조건의 파티 추천 |
| Method | GET |
| Endpoint | /api/parties/recommend |
| 인증 | 필요 |
| 사용 화면 | 메인 /main, 파티 목록 /parties |
| 처리 내용 | 사용자가 입력한 출발지, 도착지, 희망 출발 시간을 기준으로 유사한 파티를 추천한다. |
| 완료 기준 | 조건이 유사한 파티가 match_score 높은 순서로 표시되어야 한다. |

### 요청 Query

<!-- 표 48 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| start_place | string | O | 출발지 |
| end_place | string | O | 도착지 |
| departure_time | string | X | 희망 출발 시간 |
| time_range_minutes | integer | X | 유사 시간 범위, 기본 30분 |
| limit | integer | X | 조회 개수, 기본 10 |

### 응답 Body

{

"items": [

{

"id": 1,

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:10:00",

"meeting_point": "정문 앞 택시 승강장",

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"max_members": 4,

"current_members": 2,

"per_person_fare": 6000,

"fare_source": "external_mobility",

"gender_rule": "any",

"status": "recruiting",

"match_score": 90

}

],

"total": 1

}

### 추천 점수 기준

<!-- 표 49 -->
| 조건 | 점수 |
| --- | --- |
| 출발지 일치 | +35 |
| 도착지 일치 | +35 |
| 출발 시간이 기준 시간에서 10분 이내 | +30 |
| 출발 시간이 기준 시간에서 20분 이내 | +20 |
| 출발 시간이 기준 시간에서 30분 이내 | +10 |
| 상태가 recruiting | 필수 조건 |
| departure_time이 현재 이후 | 필수 조건 |
| 성별 매칭 조건 충족 | 필수 조건 |

### 점수 산정 기준:

### match_score의 최대값은 100점이다.

### 출발지와 도착지가 모두 일치하고, 출발 시간이 10분 이내이면 최대 100점으로 계산한다.

### 시간 점수는 중복 가산하지 않고 가장 높은 시간 조건 하나만 적용한다.

### 출발 시간이 30분을 초과하면 시간 점수는 0점으로 처리한다.

### status가 recruiting이 아니면 추천 후보에서 제외한다.

### departure_time이 현재 시간 이전이면 추천 후보에서 제외한다.

### same_gender 파티는 로그인 사용자 성별과 party_gender가 일치할 때만 추천 후보에 포함한다.

### 처리 로직

로그인 사용자 확인

start_place, end_place, departure_time 입력값 확인

recruiting 상태 파티만 후보로 조회

departure_time이 현재 이후인 파티만 후보로 조회

same_gender 파티는 로그인 사용자 gender와 party_gender를 비교

출발지 일치 여부 확인

도착지 일치 여부 확인

departure_time과 후보 파티의 출발 시간 차이를 분 단위로 계산

출발지 점수, 도착지 점수, 시간 점수를 합산해 match_score 계산

match_score가 높은 순서로 정렬

current_members 계산

저장된 estimated_fare 기준으로 per_person_fare 계산

meeting_point, meeting_note를 포함해 추천 결과 반환

### 예외 응답

<!-- 표 50 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 200 | 추천 결과 없음 | items가 빈 배열인 응답 반환 |
| 401 | 미로그인 | 로그인이 필요합니다. |

## PARTY-005. 파티 상세 조회

<!-- 표 51 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 상세 조회 |
| Method | GET |
| Endpoint | /api/parties/{party_id} |
| 인증 | 필요 |
| 사용 화면 | 파티 상세 /parties/:partyId |
| 처리 내용 | 특정 파티의 상세 정보, 참여자 목록, 좌표, 요금, 상태를 조회한다. |
| 완료 기준 | 상세 화면에 파티 정보, 지도, 참여자, 자동 산정된 예상 택시비, 1인 예상 요금, 상태, 만남 장소가 정상 표시되어야 한다. |

### Path Parameter

<!-- 표 52 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### 응답 Body

{

"id": 1,

"creator_id": 1,

"creator_name": "테스트",

"start_place": "연세대학교 미래캠퍼스",

"start_lat": 37.2800,

"start_lng": 127.9000,

"end_place": "원주역",

"end_lat": 37.3422,

"end_lng": 127.9199,

"departure_time": "2026-05-10T18:00:00",

"meeting_point": "정문 앞 택시 승강장",

"meeting_note": "정문 앞에서 모인 뒤 함께 택시 탑승",

"estimated_fare": 12000,

"toll_fare": 0,

"distance_meters": 7200,

"duration_seconds": 1140,

"max_members": 4,

"current_members": 2,

"per_person_fare": 6000,

"fare_source": "external_mobility",

"gender_rule": "any",

"party_gender": null,

"status": "recruiting",

"members": [

{

"id": 1,

"name": "테스트",

"gender": "male"

},

{

"id": 2,

"name": "참여자",

"gender": "female"

}

],

"created_at": "2026-05-10T17:30:00"

}

### 처리 로직

로그인 사용자 확인

party_id에 해당하는 파티 조회

참여자 목록 조회

current_members 계산

저장된 estimated_fare 기준으로 per_person_fare 계산

생성자 정보 포함

좌표값 포함

요금 산정값 포함

상세 정보 반환

### 예외 응답

<!-- 표 53 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |

## PARTY-006. 파티 참여

<!-- 표 54 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 참여 |
| Method | POST |
| Endpoint | /api/parties/{party_id}/join |
| 인증 | 필요 |
| 사용 화면 | 파티 상세 /parties/:partyId |
| 처리 내용 | 로그인 사용자를 특정 파티 참여자로 추가하고, 인원·1인 예상 요금·상태를 갱신한다. |
| 완료 기준 | 참여 후 인원·요금·상태·참여자 목록이 즉시 갱신되어야 한다. |

### Path Parameter

<!-- 표 55 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### 응답 Body

{

"result_code": 200,

"can_join": true,

"reason": "파티에 참여하였습니다.",

"id": 1,

"current_members": 3,

"max_members": 4,

"estimated_fare": 12000,

"per_person_fare": 4000,

"status": "recruiting",

"members": [

{

"id": 1,

"name": "테스트",

"gender": "male"

},

{

"id": 2,

"name": "참여자",

"gender": "female"

},

{

"id": 3,

"name": "새참여자",

"gender": "female"

}

]

}

### 처리 로직

로그인 사용자 확인

party_id에 해당하는 파티 존재 여부 확인

파티 상태가 recruiting인지 확인

departure_time이 현재 시간 이후인지 확인

이미 해당 파티에 참여한 사용자인지 확인

현재 인원이 최대 인원보다 작은지 확인

로그인 사용자가 이미 참여 중인 활성 파티가 있는지 확인한다.

기존 참여 파티와 새로 참여하려는 파티의 이동 시간대가 겹치는지 확인한다.

이동 시간대가 겹치면 참여를 차단한다.

gender_rule이 same_gender이면 사용자 gender와 party_gender 비교

참여 가능하면 party_members에 참여자 저장

참여 후 current_members 재계산

저장된 estimated_fare 기준으로 per_person_fare 재계산

current_members=max_members이면 status=matched 변경

result_code, can_join, reason, 갱신된 파티 정보를 반환

### 주의사항

파티 참여 시 External Mobility API를 다시 호출하지 않는다.

파티 참여 시 estimated_fare는 유지한다.

current_members 변경에 따라 per_person_fare만 재계산한다.

같은 사용자는 같은 파티에 중복 참여할 수 없다.

같은 사용자는 이동 시간대가 겹치는 활성 파티에 동시에 참여할 수 없다.

활성 파티는 기본적으로 recruiting, matched 상태의 파티를 의미한다.

이동 시간대는 departure_time부터 departure_time + duration_seconds까지로 판단한다.

duration_seconds가 없는 경우 MVP에서는 기본 이동 시간 60분을 임시 기준으로 사용할 수 있다.

## 참여 가능 여부 판단 결과 코드

<!-- 표 56 -->
| result_code | can_join | reason | 처리 |
| --- | --- | --- | --- |
| 200 | true | 파티에 참여하였습니다. | 참여 허용 |
| 401 | false | 로그인이 필요합니다. | 참여 차단 |
| 404 | false | 존재하지 않는 파티입니다. | 참여 차단 |
| 409 | false | 이미 참여한 파티입니다. | 참여 차단 |
| 409 | false | 최대 인원에 도달한 파티입니다. | 참여 차단 |
| 409 | false | 같은 시간대에 이미 참여 중인 파티가 있습니다. | 참여 차단 |
| 409 | false | 매칭 완료된 파티에는 참여할 수 없습니다. | 참여 차단 |
| 409 | false | 취소된 파티에는 참여할 수 없습니다. | 참여 차단 |
| 409 | false | 출발 시간이 지난 파티입니다. | 참여 차단 |
| 409 | false | 이용 완료된 파티에는 참여할 수 없습니다. | 참여 차단 |
| 403 | false | 성별 매칭 조건에 맞지 않습니다. | 참여 차단 |

주의사항:

result_code는 HTTP 상태 코드와 같은 숫자 기준을 사용한다.

can_join은 프론트에서 버튼 처리와 안내 문구를 판단하는 데 사용한다.

reason은 사용자에게 표시할 안내 문구로 사용한다.

실제 API 실패 응답에서는 기존 공통 에러 응답의 detail도 함께 사용할 수 있다.

### 예외 응답

<!-- 표 57 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 성별 조건 불일치 | 성별 매칭 조건에 맞지 않습니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |
| 409 | 이미 참여 | 이미 참여한 파티입니다. |
| 409 | 최대 인원 초과 | 최대 인원에 도달한 파티입니다. |
| 409 | 매칭 완료 | 매칭 완료된 파티에는 참여할 수 없습니다. |
| 409 | 취소된 파티 | 취소된 파티에는 참여할 수 없습니다. |
| 409 | 출발 시간 만료 | 출발 시간이 지난 파티입니다. |

## PARTY-007. 파티 참여 취소

<!-- 표 58 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 참여 취소 |
| Method | DELETE |
| Endpoint | /api/parties/{party_id}/leave |
| 인증 | 필요 |
| 사용 화면 | 파티 상세 /parties/:partyId |
| 처리 내용 | 로그인 사용자를 파티 참여자 목록에서 제거하고, 인원·1인 예상 요금·상태를 갱신한다. |
| 완료 기준 | 참여 취소 후 인원과 1인 예상 요금이 갱신되어야 한다. |

### Path Parameter

<!-- 표 59 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### 응답 Body

{

"id": 1,

"current_members": 2,

"estimated_fare": 12000,

"per_person_fare": 6000,

"status": "recruiting"

}

### 처리 로직

로그인 사용자 확인

파티 존재 여부 확인

참여 여부 확인

생성자가 나가려는 경우 제한하거나 파티 취소 안내

canceled, expired 또는 completed 파티인지 확인

참여자 제거

current_members 재계산

저장된 estimated_fare 기준으로 per_person_fare 재계산

current_members가 max_members보다 작아지면 status = recruiting으로 조정 가능

갱신된 정보 반환

### 주의사항

참여 취소 시 External Mobility API를 다시 호출하지 않는다.

estimated_fare는 유지한다.

current_members 변경에 따라 per_person_fare만 재계산한다.

### 예외 응답

<!-- 표 60 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |
| 409 | 미참여 사용자 | 참여하지 않은 파티입니다. |
| 409 | 생성자 이탈 | 생성자는 참여 취소 대신 파티 취소를 진행해야 합니다. |
| 409 | 취소된 파티 | 취소된 파티입니다. |
| 409 | 만료된 파티 | 만료된 파티입니다. |
| 409 | completed 파티 | 이용 완료된 파티에서는 참여 취소를 할 수 없습니다. |

## PARTY-008. 파티 취소

<!-- 표 61 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티 취소 |
| Method | PATCH |
| Endpoint | /api/parties/{party_id}/cancel |
| 인증 | 필요 |
| 사용 화면 | 파티 상세 /parties/:partyId |
| 처리 내용 | 파티 생성자가 파티 상태를 canceled로 변경한다. |
| 완료 기준 | 취소된 파티는 신규 참여가 불가능하고 상세 화면에서 취소 상태가 표시되어야 한다. |

### Path Parameter

<!-- 표 62 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### 요청 Body

{

"cancel_reason": "인원이 모이지 않아 취소합니다."

}

### 응답 Body

{

"id": 1,

"status": "canceled",

"cancel_reason": "인원이 모이지 않아 취소합니다.",

"canceled_at": "2026-05-10T17:50:00"

}

### 처리 로직

로그인 사용자 확인

파티 존재 여부 확인

파티 생성자 권한 확인

status를 canceled로 변경

cancel_reason 저장

canceled_at 저장

취소된 파티 정보 반환

### 예외 응답

<!-- 표 63 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 생성자 아님 | 파티 생성자만 취소할 수 있습니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |
| 409 | 이미 취소됨 | 이미 취소된 파티입니다. |
| 409 | 만료된 파티 | 이미 출발 시간이 지난 파티입니다. |
| 409 | completed 파티 | 이용 완료된 파티는 취소할 수 없습니다. |

## PARTY-009. 내 파티 목록 조회

<!-- 표 64 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 내 파티 목록 조회 |
| Method | GET |
| Endpoint | /api/my/parties |
| 인증 | 필요 |
| 사용 화면 | 메인 /main, 내 파티 /my/parties |
| 처리 내용 | 현재 사용자가 생성한 파티와 참여한 파티를 구분해 조회한다. |
| 완료 기준 | 사용자가 자신이 만든 파티와 참여한 파티를 확인할 수 있어야 한다. |

### 응답 Body

{

"created_parties": [

{

"id": 1,

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:00:00",

"meeting_point": "정문 앞 택시 승강장",

"estimated_fare": 12000,

"current_members": 2,

"max_members": 4,

"per_person_fare": 6000,

"status": "recruiting"

}

],

"joined_parties": [

{

"id": 2,

"start_place": "원주역",

"end_place": "연세대학교 미래캠퍼스",

"departure_time": "2026-05-10T21:00:00",

"meeting_point": "원주역 1번 출구",

"estimated_fare": 12000,

"current_members": 4,

"max_members": 4,

"per_person_fare": 3000,

"status": "matched"

}

]

}

### 처리 로직

로그인 사용자 확인

creator_id가 현재 사용자 id인 파티 조회

party_members에 현재 사용자가 포함된 파티 조회

생성한 파티는 joined_parties에 중복 표시하지 않음

current_members 계산

저장된 estimated_fare 기준으로 per_person_fare 계산

created_parties와 joined_parties 반환

recruiting, matched, canceled, expired, completed 상태를 모두 포함할 수 있으며 화면에서 상태별로 구분 표시한다.

### 예외 응답

<!-- 표 65 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |

# 19. Message API

## MSG-001. 채팅 메시지 목록 조회

<!-- 표 66 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 특정 파티의 이전 채팅 메시지 목록 조회 |
| Method | GET |
| Endpoint | /api/parties/{party_id}/messages |
| 인증 | 필요 |
| 사용 화면 | 파티 채팅 /parties/:partyId/chat |
| 처리 내용 | 파티 참여자만 특정 파티의 이전 메시지 목록을 시간순으로 조회할 수 있다. |
| 완료 기준 | 채팅방 입장 시 이전 메시지가 표시되어야 한다. |

### Path Parameter

<!-- 표 67 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### 응답 Body

{

"items": [

{

"id": 1,

"party_id": 1,

"user_id": 1,

"user_name": "테스트",

"content": "정문 앞에서 만나요.",

"created_at": "2026-05-10T17:55:00"

}

]

}

### 처리 로직

로그인 사용자 확인

파티 존재 여부 확인

현재 사용자가 해당 파티 참여자인지 확인

메시지 목록을 created_at 오름차순으로 조회

메시지 목록 반환

### 예외 응답

<!-- 표 68 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 비참여자 | 파티 참여자만 채팅을 이용할 수 있습니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |

## MSG-002. 파티 WebSocket 연결 및 메시지 송수신

<!-- 표 69 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 파티별 WebSocket 연결 및 메시지 송수신 |
| Method | WS |
| Endpoint | /ws/parties/{party_id}?token=<access_token> |
| 인증 | 필요 |
| 사용 화면 | 파티 채팅 /parties/:partyId/chat |
| 처리 내용 | 같은 파티 참여자끼리 WebSocket으로 실시간 메시지를 송수신하고, 메시지를 DB에 저장한다. |
| 완료 기준 | 같은 파티 참여자끼리 실시간 메시지를 주고받을 수 있어야 한다. |

### 연결 URL 예시

/ws/parties/1?token=<access_token>

### 송신 메시지 예시

{

"content": "지금 정문으로 가는 중입니다."

}

### 수신 메시지 예시

{

"id": 2,

"party_id": 1,

"user_id": 2,

"user_name": "참여자",

"content": "저도 곧 도착합니다.",

"created_at": "2026-05-10T17:58:00"

}

### 처리 로직

WebSocket query token 확인

WebSocket 인증 후 is_active=false이면 연결 거부

token으로 사용자 인증

party_id에 해당하는 파티 존재 여부 확인

현재 사용자가 해당 파티 참여자인지 확인

연결 허용

메시지 수신

빈 메시지 검증

messages 테이블에 저장

같은 party_id 채팅방 참여자에게 브로드캐스트

### 예외 상황

<!-- 표 70 -->
| 상황 | 처리 |
| --- | --- |
| 토큰 없음 | 연결 거부 |
| 토큰 만료 | 연결 거부 |
| 비참여자 접근 | 연결 거부 |
| 존재하지 않는 파티 | 연결 거부 |
| 빈 메시지 | 저장하지 않음 |
| 비활성 사용자 | 연결 거부 |

### 주의사항

POST /api/parties/{party_id}/messages는 기본 API로 만들지 않는다.

메시지 송신은 WebSocket으로 처리한다.

이전 메시지 조회는 GET /api/parties/{party_id}/messages로 처리한다.

WebSocket 구현이 전체 개발 일정을 막을 정도로 불안정할 경우 PM 승인 후 메시지 저장형 방식으로 임시 축소할 수 있다.

# 20. Admin API

## ADMIN-001. 관리자 통계 조회

<!-- 표 71 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 통계 조회 |
| Method | GET |
| Endpoint | /api/admin/stats |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 사용자 수, 파티 수, 상태별 파티 수, 메시지 수를 집계한다. |
| 완료 기준 | 관리자 페이지에서 주요 통계가 표시되어야 한다. |

### 응답 Body

{

"active_users": 10,

"total_users": 12,

"total_parties": 8,

"recruiting_parties": 4,

"matched_parties": 2,

"canceled_parties": 1,

"expired_parties": 1,

"completed_parties": 1,

"total_messages": 25

}

### 처리 로직

로그인 사용자 확인

관리자 권한 확인

users count 조회

parties count 조회

status별 parties count 조회

messages count 조회

통계 반환

### 예외 응답

<!-- 표 72 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |

## ADMIN-002. 최근 파티 조회

<!-- 표 73 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 최근 파티 조회 |
| Method | GET |
| Endpoint | /api/admin/parties/recent |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 최근 생성된 파티 목록을 최신순으로 조회한다. |
| 완료 기준 | 관리자 페이지에서 최근 파티 목록이 표시되어야 한다. |

### 요청 Query

<!-- 표 74 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| limit | integer | X | 조회 개수, 기본 10 |

### 응답 Body

{

"items": [

{

"id": 1,

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:00:00",

"current_members": 2,

"max_members": 4,

"estimated_fare": 12000,

"per_person_fare": 6000,

"status": "recruiting",

"created_at": "2026-05-10T17:30:00"

}

]

}

### 예외 응답

<!-- 표 75 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |

## ADMIN-003. 사용자 목록 조회

<!-- 표 76 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 페이지 사용자 목록 조회 |
| Method | GET |
| Endpoint | /api/admin/users |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 가입한 사용자 목록을 읽기 전용으로 반환한다. 비밀번호 해시값은 반환하지 않는다. |
| 완료 기준 | 관리자 페이지에서 사용자 목록을 확인할 수 있어야 한다. |

### 요청 Query

<!-- 표 77 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호, 기본 1 |
| limit | integer | X | 조회 개수, 기본 20 |

### 응답 Body

{

"items": [

{

"id": 1,

"email": "test@yonsei.ac.kr",

"name": "테스트",

"gender": "male",

"role": "user",

"created_at": "2026-05-10T18:00:00"

}

],

"total": 1,

"page": 1,

"limit": 20

}

### 예외 응답

<!-- 표 78 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |

### 주의사항

password_hash는 절대 응답하지 않는다.

관리자 페이지에서는 사용자 목록 조회, 사용자 권한 변경, 사용자 활성 상태 변경을 제공할 수 있다.

관리자 페이지에서는 파티 목록 조회와 파티 상태 변경을 제공할 수 있다.

관리자 기능은 실제 결제, 실제 택시 호출, 신고 처리 프로세스와 연결하지 않는다.

관리자 권한 변경과 사용자 비활성화는 admin 권한 사용자만 수행할 수 있다.

## ADMIN-004. 관리자 파티 목록 조회

<!-- 표 79 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 파티 목록 조회 |
| Method | GET |
| Endpoint | /api/admin/parties |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 전체 파티 목록을 상태, 검색어, 페이지 기준으로 조회한다. |
| 완료 기준 | 관리자 페이지에서 전체 파티를 상태별로 확인할 수 있어야 한다. |

### 요청 Query

<!-- 표 80 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| status | string | X | recruiting, matched, canceled, expired, completed |
| keyword | string | X | 출발지, 도착지, 생성자명 검색어 |
| page | integer | X | 페이지 번호, 기본 1 |
| limit | integer | X | 조회 개수, 기본 20 |

### 응답 Body

{

"items": [

{

"id": 1,

"creator_id": 1,

"creator_name": "테스트",

"start_place": "연세대학교 미래캠퍼스",

"end_place": "원주역",

"departure_time": "2026-05-10T18:00:00",

"current_members": 2,

"max_members": 4,

"status": "recruiting",

"created_at": "2026-05-10T17:30:00"

}

],

"total": 1,

"page": 1,

"limit": 20

}

## ADMIN-005. 관리자 파티 상태 변경

<!-- 표 81 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 파티 상태 변경 |
| Method | PATCH |
| Endpoint | /api/admin/parties/{party_id}/status |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 관리자가 특정 파티의 상태를 변경한다. |
| 완료 기준 | 관리자 페이지에서 파티 상태 변경 후 목록과 통계가 갱신되어야 한다. |

### 요청 Body

{

"status": "canceled",

"admin_note": "관리자 확인 후 취소 처리"

}

### 허용 status

<!-- 표 82 -->
| 값 | 의미 |
| --- | --- |
| recruiting | 모집 중 |
| matched | 매칭 완료 |
| canceled | 취소 |
| expired | 출발시간 만료 |
| completed | 이용 완료 |

## ADMIN-006. 관리자 사용자 권한 변경

<!-- 표 83 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 사용자 권한 변경 |
| Method | PATCH |
| Endpoint | /api/admin/users/{user_id}/role |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 관리자가 사용자의 role을 user 또는 admin으로 변경한다. |
| 완료 기준 | 사용자 권한 변경 후 관리자 페이지와 내 정보 조회에서 변경된 role이 반영되어야 한다. |

### 요청 Body

{

"role": "admin"

}

## ADMIN-007. 관리자 사용자 활성 상태 변경

<!-- 표 84 -->
| 항목 | 내용 |
| --- | --- |
| 기능 | 관리자 사용자 활성 상태 변경 |
| Method | PATCH |
| Endpoint | /api/admin/users/{user_id}/status |
| 인증 | 필요 |
| 권한 | admin |
| 사용 화면 | 관리자 페이지 /admin |
| 처리 내용 | 관리자가 사용자의 활성 상태를 변경한다. |
| 완료 기준 | 비활성화된 사용자는 로그인 또는 주요 기능 이용이 제한되어야 한다. |

### 요청 Body

{

"is_active": false

}

## ADMIN-008. 관리자 최근 메시지 조회

기능: 관리자 페이지에서 최근 채팅 메시지를 읽기 전용으로 확인한다.

Method: GET

Endpoint: /api/admin/messages/recent

인증: 필요, 권한: admin

요청 Query: limit

응답 Body: recent_messages, party_id, user_id, user_name, content, created_at

주의사항: password_hash 등 민감 정보는 반환하지 않는다.

## ADMIN-009. 관리자 사용자 상세 조회

기능: 관리자가 특정 사용자의 서비스 이용 현황을 점검한다.

Method: GET

Endpoint: /api/admin/users/{user_id}

인증: 필요, 권한: admin

응답 Body: user, created_parties_count, joined_parties_count, message_count

주의사항: password_hash는 반환하지 않는다.

## ADMIN-010. 관리자 파티 상세 조회

기능: 관리자가 특정 파티의 상세 정보와 참여 현황을 점검한다.

Method: GET

Endpoint: /api/admin/parties/{party_id}

인증: 필요, 권한: admin

응답 Body: party, members, messages_count

주의사항: 상태 변경은 ADMIN-005를 사용한다.

### ADMIN-008 요청 Query

<!-- 표 85 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| limit | integer | X | 조회 개수, 기본 20 |

### ADMIN-008 응답 Body 예시

{

"recent_messages": [

{"id": 1, "party_id": 3, "user_id": 2, "user_name": "참여자", "content": "정문 앞에 도착했습니다.", "created_at": "2026-05-10T17:58:00"}

]

}

### ADMIN-008 예외 응답

<!-- 표 86 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |
| 403 | 비활성 사용자 | 비활성화된 사용자입니다. |

### ADMIN-009 Path Parameter

<!-- 표 87 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| user_id | integer | O | 사용자 ID |

### ADMIN-009 응답 Body 예시

{

"user": {"id": 2, "email": "user@yonsei.ac.kr", "name": "참여자", "gender": "female", "role": "user", "is_active": true, "created_at": "2026-05-10T18:00:00"},

"created_parties_count": 1,

"joined_parties_count": 2,

"message_count": 5

}

### ADMIN-009 예외 응답

<!-- 표 88 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |
| 403 | 비활성 사용자 | 비활성화된 사용자입니다. |
| 404 | 사용자 없음 | 존재하지 않는 사용자입니다. |

### ADMIN-010 Path Parameter

<!-- 표 89 -->
| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| party_id | integer | O | 파티 ID |

### ADMIN-010 응답 Body 예시

{

"party": {"id": 3, "start_place": "연세대학교 미래캠퍼스", "end_place": "원주역", "status": "recruiting", "current_members": 2, "max_members": 4},

"members": [{"id": 1, "name": "생성자", "gender": "male"}],

"messages_count": 4

}

### ADMIN-010 예외 응답

<!-- 표 90 -->
| 상태 코드 | 상황 | 메시지 예시 |
| --- | --- | --- |
| 401 | 미로그인 | 로그인이 필요합니다. |
| 403 | 관리자 아님 | 관리자 권한이 필요합니다. |
| 403 | 비활성 사용자 | 비활성화된 사용자입니다. |
| 404 | 파티 없음 | 존재하지 않는 파티입니다. |

# 21. 프론트 사용 화면별 API 연결표

<!-- 표 91 -->
| 화면 | 경로 | 사용하는 API |
| --- | --- | --- |
| 랜딩 | / | API 없음 |
| 회원가입 | /signup | AUTH-001 |
| 로그인 | /login | AUTH-002 |
| 메인 | /main | AUTH-003, PARTY-004, PARTY-009 |
| 로그아웃 | Header / Settings | AUTH-004 |
| 파티 목록·검색 | /parties | PARTY-002, PARTY-003, PARTY-004 |
| 파티 생성 | /parties/new | PLACE-001, FARE-001, PARTY-001 |
| 파티 상세 | /parties/:partyId | PARTY-005, PARTY-006, PARTY-007, PARTY-008 |
| 내 파티 | /my/parties | PARTY-009 |
| 파티 채팅 | /parties/:partyId/chat | MSG-001, MSG-002 |
| 안전 안내 | /guide | API 없음 |
| 계정·설정 | /settings | AUTH-003 |
| 관리자 페이지 | /admin | ADMIN-001, ADMIN-002, ADMIN-003, ADMIN-004, ADMIN-005, ADMIN-006, ADMIN-007, ADMIN-008, ADMIN-009, ADMIN-010 |
| 이용약관 | /terms | API 없음 |
| 개인정보 처리방침 | /privacy | API 없음 |

# 22. API 구현 우선순위

## 22-1. 1순위: Must API

<!-- 표 92 -->
| API ID | 기능 | 이유 |
| --- | --- | --- |
| SYS-001 | 서버 상태 확인 | 개발 확인 |
| AUTH-001 | 회원가입 | 기본 사용자 생성 |
| AUTH-002 | 로그인 | 인증 |
| AUTH-003 | 내 정보 조회 | 로그인 상태 유지 |
| AUTH-004 | 로그아웃 | 프론트 인증 상태 해제 |
| PLACE-001 | 장소명 검색 및 좌표 선택 | 파티 생성과 요금 자동 산정의 선행 조건 |
| FARE-001 | 예상 택시비 자동 산정 | 파티 생성 전후 자동 요금 계산 기준 |
| PARTY-001 | 파티 생성 | 핵심 기능 |
| PARTY-002 | 파티 목록 조회 | 핵심 기능 |
| PARTY-005 | 파티 상세 조회 | 핵심 기능 |
| PARTY-006 | 파티 참여 | 핵심 기능 |

## 22-2. 2순위: Target API

<!-- 표 93 -->
| API ID | 기능 | 이유 |
| --- | --- | --- |
| PARTY-003 | 파티 검색 | 조건 검색 |
| PARTY-004 | 유사 파티 추천 | 추천 기능 |
| PARTY-007 | 파티 참여 취소 | 화면에 버튼이 존재하므로 구현 목표 기능으로 관리 |
| PARTY-008 | 파티 취소 | 생성자 관리 기능으로 구현 목표 기능에 포함 |
| PARTY-009 | 내 파티 목록 조회 | 사용자 편의 및 이력 관리 |
| MSG-001 | 채팅 메시지 목록 조회 | 채팅 기록 |
| MSG-002 | WebSocket 채팅 연결 | 실시간 채팅 |

요금 산정 우선순위 해석 기준

FARE-001 GET /api/fares/estimate는 파티 생성 화면에서 예상 택시비를 미리 확인하기 위한 별도 미리보기 API이므로 Target API로 둔다.
다만 파티 생성 시 예상 택시비를 자동 산정하는 내부 로직은 PARTY-001 파티 생성의 필수 처리 조건에 포함된다.
따라서 사용자가 예상 요금을 직접 입력하지 않는 기준은 반드시 유지한다.

정리하면 아래와 같다.
- 파티 생성 내부 요금 자동 산정: Must
- 별도 예상 택시비 미리보기 API GET /api/fares/estimate: Target
- 실제 택시 호출, 배차, 결제, 실제 결제 금액 확정: 제외

## 22-3. 3순위: Could API

<!-- 표 94 -->
| API ID | 기능 | 이유 |
| --- | --- | --- |
| ADMIN-001 | 관리자 통계 조회 | 관리자 페이지 |
| ADMIN-002 | 최근 파티 조회 | 관리자 페이지 |
| ADMIN-003 | 사용자 목록 조회 | 관리자 페이지 |
| ADMIN-004 | 관리자 파티 목록 조회 | 관리자 페이지 |
| ADMIN-005 | 관리자 파티 상태 변경 | 관리자 페이지 |
| ADMIN-006 | 관리자 사용자 권한 변경 | 관리자 페이지 |
| ADMIN-007 | 관리자 사용자 활성 상태 변경 | 관리자 페이지 |
| ADMIN-008 | 관리자 최근 메시지 조회 | 관리자 페이지 확장 |
| ADMIN-009 | 관리자 사용자 상세 조회 | 관리자 페이지 확장 |
| ADMIN-010 | 관리자 파티 상세 조회 | 관리자 페이지 확장 |

# 23. 환경변수 기준

## 23-1. 프론트엔드 환경변수

파일 위치:

frontend/.env

예시:

VITE_API_BASE_URL=http://localhost:8000

VITE_MAP_JS_KEY=your-map-javascript-key

<!-- 표 95 -->
| 환경변수 | 사용 위치 | 설명 |
| --- | --- | --- |
| VITE_API_BASE_URL | 프론트엔드 | FastAPI 백엔드 주소 |
| VITE_MAP_JS_KEY | 프론트엔드 | Campus Map JavaScript API Key |

## 23-2. 백엔드 환경변수

파일 위치:

backend/.env

예시:

DATABASE_URL=sqlite:///./eagle_taxi.db

JWT_SECRET_KEY=change-this-secret-key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_EMAILS=yong6330@yonsei.ac.kr

MOBILITY_REST_API_KEY=your-mobility-rest-api-key

<!-- 표 96 -->
| 환경변수 | 사용 위치 | 설명 |
| --- | --- | --- |
| DATABASE_URL | 백엔드 | SQLite DB 연결 주소 |
| JWT_SECRET_KEY | 백엔드 | JWT 서명 키 |
| JWT_ALGORITHM | 백엔드 | JWT 알고리즘 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 백엔드 | 토큰 만료 시간 |
| ADMIN_EMAILS | 백엔드 | 관리자 계정 이메일 목록 |
| MOBILITY_REST_API_KEY | 백엔드 | External Mobility 길찾기 API 호출용 REST API Key |

주의사항:

VITE_MAP_JS_KEY는 프론트에서 사용하는 JavaScript Key이다.

MOBILITY_REST_API_KEY는 백엔드에서만 사용하는 REST API Key이다.

REST API Key를 프론트 코드에 노출하지 않는다.

.env 파일은 GitHub에 업로드하지 않는다.

.env.example에는 실제 키가 아니라 예시값만 작성한다.

# 24. 제외 API 기준

<!-- 표 97 -->
| 제외 API | 제외 사유 |
| --- | --- |
| 실제 택시 호출 API | 플랫폼 제휴 또는 별도 호출 API 검토 필요 |
| 실제 배차 API | 실제 운송 서비스 영역 |
| 실제 결제 API | 결제 시스템 및 금융정보 처리 필요 |
| 실제 결제 금액 확정 API | 예상 요금과 실제 미터기 요금은 다를 수 있음 |
| 신고 저장 API | 신고 처리, 관리자 조치, 데이터 보관 기준이 추가로 필요하므로 이번 MVP에서는 제외 |
| 소셜 로그인 API | 구현 범위 확장으로 인한 일정 부담 |
| 비밀번호 재설정 API | MVP 핵심 흐름 아님 |
| 실시간 위치 추적 API | 위치정보 처리 및 추가 기술 검토 필요 |
| 운전자 연결 API | 실제 운송 서비스 영역 |
| 사용자용 경로 안내 API | 예상 택시비 산정을 위한 내부 경로 조회는 구현하지만, 사용자에게 실제 경로 안내·내비게이션·실시간 이동 경로를 제공하는 기능은 MVP 범위에서 제외 |

요금 관련 주의 문구:

예상 택시비 자동 산정은 구현한다.

다만 실제 결제 금액 확정, 실제 택시 호출, 실제 운행 요금 정산은 구현하지 않는다.

# 25. API 변경 공유 기준

프론트엔드와 백엔드는 API 명세서를 기준으로 연결한다.

API 구조는 한쪽 담당자가 임의로 변경하지 않는다.

<!-- 표 98 -->
| 변경 상황 | 처리 기준 |
| --- | --- |
| Endpoint 변경 필요 | PM, TL, QA&Front 확인 후 변경 |
| 요청 데이터 변경 필요 | API 명세서 먼저 수정 |
| 응답 데이터 변경 필요 | 프론트 화면 영향 확인 후 수정 |
| 인증 방식 변경 필요 | PM/TL 확인 전 변경 금지 |
| DB 컬럼 추가 필요 | TL이 PM에게 공유 후 반영 |
| 화면에 필요한 데이터 누락 | QA&Front가 TL에게 요청 |
| 외부 API 호출 방식 변경 필요 | PM, TL 확인 후 반영 |
| API 오류 발생 | 오류 메시지, 요청값, 응답값을 함께 공유 |

API 변경 공유 형식:

[API 변경 요청]

요청자:

관련 화면:

현재 API:

변경 필요 내용:

변경 이유:

프론트 영향:

백엔드 영향:

DB 영향:

외부 API 영향:

# 26. 최종 점검표

API 명세서 반영 후 아래 항목을 확인한다.

□ GET /api/places가 백엔드 API에서 제거되고 Campus Places 기준으로 정리되었는가

□ 장소명 검색은 Campus Map JavaScript API 기준으로 작성되었는가

□ 파티 생성 요청값에 start_place, start_lat, start_lng, end_place, end_lat, end_lng가 포함되었는가

□ 파티 생성 요청값에 meeting_point, meeting_note, gender_rule이 포함되었는가

□ 파티 생성 요청값에서 estimated_fare가 제거되었는가

□ 파티 생성 요청값에서 per_person_fare가 제거되었는가

□ FARE-001 GET /api/fares/estimate가 추가되었는가

□ External Mobility REST API Key가 백엔드 환경변수로 분리되었는가

□ 프론트에서 External Mobility REST API Key를 직접 사용하지 않는다고 명시되었는가

□ estimated_fare는 External Mobility API의 summary.fare.taxi 기준인가

□ toll_fare, distance_meters, duration_seconds가 함께 저장되는가

□ fare_source가 external_mobility 기준으로 정리되었는가

□ per_person_fare는 ceil(estimated_fare / current_members) 기준인가

□ 파티 참여·참여 취소 시 estimated_fare는 유지하고 per_person_fare만 재계산하는가

□ 상태값에 expired가 추가되었는가

□ 검색과 추천이 /search, /recommend로 분리되었는가

□ 성별 매칭 조건이 파티 생성과 파티 참여 로직에 반영되었는가

□ WebSocket은 query token 방식으로 유지되었는가

□ POST 메시지 전송 API가 불필요하게 추가되지 않았는가

□ 관리자 사용자 목록 조회가 추가되었는가

□ password_hash를 응답하지 않는다고 명시되었는가

□ 신고 저장 API가 제외 기능으로 정리되었는가

□ 실제 결제, 실제 호출, 실제 배차는 제외되어 있는가
