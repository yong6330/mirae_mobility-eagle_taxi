# 1주차_알고리즘 설계서_최우진_v0.4

> 변환 원본: `1주차_알고리즘 설계서_최우진_v0.4.docx`

탭 1

# 미래 모빌리티 알고리즘 설계 문서 v0.4

## 1. 문서 목적

본 문서는 Mirae Mobility 팀의 「독수리 택시」 프로젝트에서 사용되는 주요 알고리즘 기준을 정리한 내부 개발 기준 문서이다.

알고리즘 설계서는 단순히 아이디어를 설명하는 문서가 아니라, FastAPI 백엔드와 React 프론트엔드가 실제 기능을 구현할 때 참고할 수 있는 처리 기준을 제공하는 것을 목적으로 한다.

본 문서는 기능명세서, API 명세서, 개발 계획(안), 운영 계획(안)의 최신 기준을 따른다.

## 2. 알고리즘 설계 기준

<!-- 표 1 -->
| 항목 | 기준 |
| --- | --- |
| 프로젝트명 | 독수리 택시 |
| 팀명 | Mirae Mobility |
| 주요 사용자 | 연세대학교 미래캠퍼스 학생 |
| 핵심 기능 | 택시 파티 생성, 검색, 추천, 참여, 요금 자동 계산, 상태 변경, 채팅 |
| 파티 상태값 | recruiting / matched / canceled / expired / completed |
| 기술 기준 | React + FastAPI + SQLite |
| 지도 API | Kakao Maps JavaScript API |
| 예상 택시비 산정 | Kakao Mobility API |
| 데이터 저장 | SQLite |
| 실제 택시 호출 | 구현하지 않음 |
| 실제 결제 | 구현하지 않음 |
| 실시간 위치 추적 | 구현하지 않음 |

## 3. 알고리즘 구성도

사용자 입력 및 서비스 흐름은 아래 순서로 처리한다.

[랜딩 페이지]

↓

[회원가입 / 로그인]

↓

[메인 페이지]

↓

[출발지·도착지·출발 시간 입력]

↓

[유사 파티 추천]

↓

[추천 파티 상세 확인] ──→ [파티 참여 가능 여부 판단]

↓                              ↓

[조건에 맞는 파티 없음]          [파티 참여 처리]

↓                              ↓

[입력값 유지 후 파티 생성]       [1인 예상 요금 재계산]

↓                              ↓

[예상 택시비 자동 산정]          [파티 상태 변경]

↓                              ↓

[파티 상세 확인] ─────────→ [파티 채팅]

↓

[내 파티 목록 / 이력 확인]

↓

[관리자 통계 집계]

## 4. 알고리즘 목록

<!-- 표 2 -->
| 알고리즘 ID | 알고리즘명 | 관련 기능 | 우선순위 |
| --- | --- | --- | --- |
| ALG-01 | 파티 생성 처리 알고리즘 | 파티 생성 | Must |
| ALG-02 | 파티 검색 알고리즘 | 파티 목록 조회, 조건 검색 | Target |
| ALG-03 | 유사 파티 추천 알고리즘 | 유사 파티 추천 | Target |
| ALG-04 | 예상 택시비 자동 산정 알고리즘 | 요금 자동 산정 | Must |
| ALG-05 | 1인 예상 요금 계산 알고리즘 | 요금 자동 분할 | Must |
| ALG-06 | 파티 상태 변경 알고리즘 | 모집 중, 매칭 완료, 취소, 만료, 이용 완료 | Must |
| ALG-07 | 참여 가능 여부 판단 알고리즘 | 파티 참여 조건 확인 | Must |
| ALG-08 | 파티 참여 처리 알고리즘 | 참여자 추가 | Must |
| ALG-09 | 채팅 접근 및 메시지 처리 알고리즘 | 파티별 채팅 | Target |
| ALG-10 | 관리자 통계 집계 알고리즘 | 관리자 페이지 | Could |
| ALG-11 | 파티 참여 취소·파티 취소 처리 알고리즘 | 참여 취소, 파티 취소 | Target |

# 5. 알고리즘 상세 설계

## ALG-01. 파티 생성 처리 알고리즘

<!-- 표 3 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-01 |
| 알고리즘명 | 파티 생성 처리 알고리즘 |
| 목적 | 사용자가 입력한 이동 조건을 기준으로 새 택시 파티를 생성한다. |
| 입력값 | user_id, start_place, start_lat, start_lng, end_place, end_lat, end_lng, departure_time, meeting_point, meeting_note, max_members, gender_rule |
| 처리 기준 | 필수값 검증, 출발 시간 검증, 최대 인원 검증, 성별 매칭 옵션 검증, 예상 택시비 자동 산정, 생성자 자동 참여 |
| 출력값 | 생성된 파티 정보, estimated_fare, per_person_fare, current_members, status |
| 예외 상황 | 필수값 누락, 좌표값 없음, 과거 시간 선택, 최대 인원 범위 초과, 성별 매칭 옵션 오류, 요금 산정 실패 |
| 표시 방식 | 파티 생성 완료 후 파티 상세 화면으로 이동 |
| 우선순위 | Must |

관련 API: POST /api/parties

### 처리 흐름

로그인 사용자인지 확인한다.

출발지와 도착지 장소명이 있는지 확인한다.

출발지와 도착지 좌표값이 있는지 확인한다.

departure_time이 현재 시간 이후인지 확인한다.

max_members가 2명 이상 4명 이하인지 확인한다.

gender_rule이 any 또는 same_gender인지 확인한다.

gender_rule이 same_gender이면 생성자의 gender를 확인한다.

화면 기본값이 none이면 same_gender 파티 생성을 차단하고, DB에는 male 또는 female만 저장한다.

Kakao Mobility API를 호출해 예상 택시비를 자동 산정한다.

estimated_fare, toll_fare, distance_meters, duration_seconds, fare_source를 저장한다.

parties 테이블에 파티를 생성한다.

생성자를 party_members에 자동 추가한다.

current_members를 1로 계산한다.

per_person_fare를 estimated_fare 기준으로 계산한다.

status를 recruiting으로 저장한다.

생성된 파티 정보를 반환한다.

### 의사코드

파티 생성 요청이 들어오면

if 로그인 사용자가 아니면:

result_code = 401

reason = "로그인이 필요합니다."

생성 차단

if 출발지 또는 도착지 좌표가 없으면:

result_code = 400

reason = "출발지와 도착지를 검색 결과에서 선택해주세요."

생성 차단

if departure_time <= 현재 시간:

result_code = 400

reason = "희망 출발 시간은 현재 시간 이후여야 합니다."

생성 차단

if max_members < 2 or max_members > 4:

result_code = 400

reason = "최대 인원은 2명 이상 4명 이하로 입력해야 합니다."

생성 차단

if gender_rule == same_gender and 화면 기본값 gender == none:

result_code = 400

reason = "성별을 선택해야 동성 매칭 파티를 생성할 수 있습니다."

생성 차단

Kakao Mobility API로 예상 택시비 산정

if 요금 산정 실패:

result_code = 502

reason = "예상 택시비를 계산하지 못했습니다."

생성 차단

파티 생성

생성자 자동 참여

current_members = 1

per_person_fare = ceil(estimated_fare / current_members)

status = recruiting

생성된 파티 정보 반환

## ALG-02. 파티 검색 알고리즘

<!-- 표 4 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-02 |
| 알고리즘명 | 파티 검색 알고리즘 |
| 목적 | 사용자가 입력한 조건에 맞는 택시 파티 목록을 조회한다. |
| 입력값 | start_place, end_place, departure_time, status, page, limit |
| 처리 기준 | 출발지, 도착지, 희망 출발 시간, 상태 기준 필터링 |
| 출력값 | 파티 목록, total, page, limit, current_members, per_person_fare |
| 예외 상황 | 검색 결과 없음, 미로그인 |
| 표시 방식 | 조건에 맞는 파티 목록을 카드 형태로 표시 |
| 우선순위 | Target |

관련 API: GET /api/parties/search

### 처리 흐름

로그인 사용자인지 확인한다.

검색 조건을 확인한다.

status 값이 없으면 recruiting을 기본값으로 적용한다.

start_place 조건이 있으면 출발지가 일치하는 파티를 필터링한다.

end_place 조건이 있으면 도착지가 일치하는 파티를 필터링한다.

departure_time 조건이 있으면 가까운 출발 시간 기준으로 필터링한다.

expired 파티는 기본 검색 결과에서 제외한다.

각 파티의 current_members를 계산한다.

저장된 estimated_fare 기준으로 per_person_fare를 계산한다.

조건에 맞는 파티 목록을 반환한다.

### 의사코드

파티 검색 요청이 들어오면

if 로그인 사용자가 아니면:

result_code = 401

reason = "로그인이 필요합니다."

검색 차단

검색 조건 확인

if status가 없으면:

status = recruiting

후보 파티 목록 조회

if start_place 조건이 있으면:

start_place가 일치하는 파티만 남긴다.

if end_place 조건이 있으면:

end_place가 일치하는 파티만 남긴다.

if departure_time 조건이 있으면:

가까운 출발 시간 기준으로 정렬하거나 필터링한다.

expired 파티는 기본 검색 결과에서 제외한다.

각 파티마다:

current_members 계산

per_person_fare 계산

검색 결과 반환

if 검색 결과가 없으면:

빈 배열 반환

화면에서는 새 파티 생성을 안내

### 주의사항

파티 검색은 사용자를 자동 초대하지 않는다.

검색 결과를 보여준 뒤 사용자가 직접 파티 상세 화면에서 참여한다.

검색 결과가 없으면 자동으로 파티를 생성하지 않고 새 파티 생성을 안내한다.

## ALG-03. 유사 파티 추천 알고리즘

<!-- 표 5 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-03 |
| 알고리즘명 | 유사 파티 추천 알고리즘 |
| 목적 | 사용자의 조건과 유사한 기존 파티를 match_score 기준으로 추천한다. |
| 입력값 | start_place, end_place, departure_time, time_range_minutes, limit |
| 처리 기준 | 출발지 일치, 도착지 일치, 출발 시간 차이, 모집 상태, 성별 매칭 조건 |
| 출력값 | 추천 파티 목록, match_score, meeting_point, meeting_note, estimated_fare, per_person_fare |
| 예외 상황 | 추천 결과 없음, 미로그인, 성별 매칭 조건 불일치 |
| 표시 방식 | match_score 높은 순서로 추천 파티 표시 |
| 우선순위 | Target |

관련 API: GET /api/parties/recommend

### 추천 점수 기준

<!-- 표 6 -->
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

### 점수 계산 기준

match_score의 최대값은 100점이다.

출발지와 도착지가 모두 일치하고, 출발 시간이 10분 이내이면 최대 100점이다.

시간 점수는 중복 가산하지 않는다.

10분 이내이면 30점, 20분 이내이면 20점, 30분 이내이면 10점을 부여한다.

출발 시간이 30분을 초과하면 시간 점수는 0점이다.

status가 recruiting이 아니면 추천 후보에서 제외한다.

departure_time이 현재 시간 이전이면 추천 후보에서 제외한다.

same_gender 파티는 로그인 사용자 성별과 party_gender가 일치할 때만 추천한다.

### 처리 흐름

로그인 사용자인지 확인한다.

start_place, end_place, departure_time을 확인한다.

recruiting 상태인 파티만 후보로 조회한다.

departure_time이 현재 이후인 파티만 후보로 조회한다.

same_gender 파티는 사용자 gender와 party_gender를 비교한다.

출발지 일치 여부를 확인한다.

도착지 일치 여부를 확인한다.

희망 출발 시간과 후보 파티의 출발 시간 차이를 분 단위로 계산한다.

출발지 점수, 도착지 점수, 시간 점수를 합산한다.

match_score가 높은 순서로 정렬한다.

각 파티의 current_members와 per_person_fare를 계산한다.

추천 파티 목록을 반환한다.

### 의사코드

유사 파티 추천 요청이 들어오면

if 로그인 사용자가 아니면:

result_code = 401

reason = "로그인이 필요합니다."

추천 차단

후보 파티 목록 조회:

status == recruiting

departure_time > 현재 시간

for 각 후보 파티:

if gender_rule == same_gender and 사용자 gender != party_gender:

추천 후보에서 제외

match_score = 0

if start_place가 일치하면:

match_score += 35

if end_place가 일치하면:

match_score += 35

time_diff = abs(사용자 희망 시간 - 파티 출발 시간)

if time_diff <= 10분:

match_score += 30

else if time_diff <= 20분:

match_score += 20

else if time_diff <= 30분:

match_score += 10

else:

match_score += 0

current_members 계산

per_person_fare 계산

match_score 높은 순서로 정렬

if 추천 결과가 없으면:

빈 배열 반환

화면에서는 새 파티 생성을 안내

추천 결과 반환

## ALG-04. 예상 택시비 자동 산정 알고리즘

<!-- 표 7 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-04 |
| 알고리즘명 | 예상 택시비 자동 산정 알고리즘 |
| 목적 | 사용자가 요금을 입력하지 않아도 출발지·도착지·출발 시간 기준으로 예상 택시비를 산정한다. |
| 입력값 | start_lat, start_lng, end_lat, end_lng, departure_time |
| 처리 기준 | Kakao Mobility API 호출 및 응답값 추출 |
| 출력값 | estimated_fare, toll_fare, distance_meters, duration_seconds, fare_source |
| 예외 상황 | 좌표 없음, 출발 시간 없음, API Key 없음, 경로 조회 실패, 요금 정보 없음 |
| 표시 방식 | 예상 택시비, 예상 통행료, 예상 이동 거리, 예상 이동 시간 표시 |
| 우선순위 | Must |

관련 API: GET /api/fares/estimate, POST /api/parties 내부 로직

### 처리 흐름

출발지 좌표가 있는지 확인한다.

도착지 좌표가 있는지 확인한다.

departure_time이 있는지 확인한다.

Kakao Mobility REST API Key가 설정되어 있는지 확인한다.

origin 값에 start_lng, start_lat을 넣는다.

destination 값에 end_lng, end_lat을 넣는다.

departure_time을 Kakao Mobility API 요청 형식에 맞춘다.

Kakao Mobility API를 호출한다.

응답값에서 summary.fare.taxi를 estimated_fare로 추출한다.

summary.fare.toll을 toll_fare로 추출한다.

summary.distance를 distance_meters로 추출한다.

summary.duration을 duration_seconds로 추출한다.

fare_source를 kakao_mobility로 저장한다.

요금 산정 결과를 반환한다.

### 의사코드

요금 산정 요청이 들어오면

if 출발지 좌표가 없으면:

result_code = 400

reason = "출발지를 검색 결과에서 선택해주세요."

산정 차단

if 도착지 좌표가 없으면:

result_code = 400

reason = "도착지를 검색 결과에서 선택해주세요."

산정 차단

if departure_time이 없으면:

result_code = 400

reason = "출발 시간을 선택해주세요."

산정 차단

Kakao Mobility API 호출

if API 호출 실패:

result_code = 502

reason = "예상 택시비를 계산하지 못했습니다."

산정 차단

estimated_fare = summary.fare.taxi

toll_fare = summary.fare.toll

distance_meters = summary.distance

duration_seconds = summary.duration

fare_source = kakao_mobility

요금 산정 결과 반환

## ALG-05. 1인 예상 요금 계산 알고리즘

<!-- 표 8 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-05 |
| 알고리즘명 | 1인 예상 요금 계산 알고리즘 |
| 목적 | 자동 산정된 전체 예상 택시비를 현재 참여 인원 기준으로 나눈다. |
| 입력값 | estimated_fare, current_members |
| 처리 기준 | per_person_fare = ceil(estimated_fare / current_members) |
| 출력값 | per_person_fare |
| 예외 상황 | current_members=0, estimated_fare 없음 |
| 표시 방식 | 원 단위 올림 |
| 우선순위 | Must |

관련 API: POST /api/parties, POST /api/parties/{party_id}/join, DELETE /api/parties/{party_id}/leave

### 계산식

per_person_fare = ceil(estimated_fare / current_members)

### 계산 예시

<!-- 표 9 -->
| estimated_fare | current_members | per_person_fare |
| --- | --- | --- |
| 12,000원 | 1명 | 12,000원 |
| 12,000원 | 2명 | 6,000원 |
| 12,000원 | 3명 | 4,000원 |
| 12,000원 | 4명 | 3,000원 |
| 10,000원 | 3명 | 3,334원 |

### 처리 흐름

estimated_fare가 있는지 확인한다.

current_members가 1 이상인지 확인한다.

estimated_fare를 current_members로 나눈다.

소수점이 발생하면 원 단위 올림 처리한다.

per_person_fare를 반환한다.

### 의사코드

1인 예상 요금 계산 요청이 들어오면

if estimated_fare가 없으면:

result_code = 400

reason = "예상 택시비가 없습니다."

계산 차단

if current_members <= 0:

result_code = 400

reason = "현재 인원 값이 올바르지 않습니다."

계산 차단

per_person_fare = ceil(estimated_fare / current_members)

per_person_fare 반환

### 주의사항

참여자가 바뀌어도 Kakao Mobility API를 다시 호출하지 않는다.

파티 생성 시 저장된 estimated_fare를 유지한다.

참여자 수가 바뀌면 current_members만 재계산한다.

current_members가 바뀌면 per_person_fare만 재계산한다.

## ALG-06. 파티 상태 변경 알고리즘

<!-- 표 10 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-06 |
| 알고리즘명 | 파티 상태 변경 알고리즘 |
| 목적 | 파티의 참여 인원, 취소 여부, 출발 시간에 따라 상태를 변경한다. |
| 입력값 | party_id, current_members, max_members, status, departure_time, cancel_request |
| 처리 기준 | 인원, 취소, 출발 시간 기준 상태 변경 |
| 출력값 | status, status_label, result_code, reason |
| 예외 상황 | 최대 인원 초과, 이미 취소된 파티, 이미 만료된 파티, 이미 완료된 파티, 상태 변경 권한 없음 |
| 표시 방식 | 모집 중 / 매칭 완료 / 취소 / 출발시간 만료 / 이용 완료 |
| 우선순위 | Must |

관련 API: POST /api/parties/{party_id}/join, DELETE /api/parties/{party_id}/leave, PATCH /api/parties/{party_id}/cancel, GET /api/parties, GET /api/parties/{party_id}, PATCH /api/admin/parties/{party_id}/status

### 상태값 기준

<!-- 표 11 -->
| DB 값 | 화면 표시 | 의미 |
| --- | --- | --- |
| recruiting | 모집 중 | 참여 가능 |
| matched | 매칭 완료 | 최대 인원 도달 또는 매칭 완료 |
| canceled | 취소 | 생성자 또는 관리자가 파티를 취소함 |
| expired | 출발시간 만료 | 모집 중이었으나 출발 시간이 지나 참여 불가 |
| completed | 이용 완료 | 매칭 완료된 파티의 출발 시간이 지남 |

### 처리 흐름

현재 status를 확인한다.

생성자 또는 관리자가 파티를 취소하면 status를 canceled로 변경한다.

현재 시간이 departure_time을 지났고 status가 recruiting이면 expired로 변경한다.

현재 시간이 departure_time을 지났고 status가 matched이면 completed로 변경한다.

current_members가 max_members와 같으면 matched로 변경한다.

참여 취소 기능 구현 시 current_members가 max_members보다 작아지면 status를 recruiting으로 조정할 수 있다.

canceled 상태는 자동 복구하지 않는다.

completed 상태는 자동 복구하지 않는다.

### 의사코드

상태 변경 로직이 실행되면

if cancel_request == true:

status = canceled

reason = "파티가 취소되었습니다."

상태 반환

if status == canceled:

자동 변경하지 않음

상태 반환

if 현재 시간 > departure_time and status == recruiting:

status = expired

reason = "출발 시간이 지난 파티입니다."

상태 반환

if 현재 시간 > departure_time and status == matched:

status = completed

reason = "이용 완료된 파티입니다."

상태 반환

if current_members == max_members:

status = matched

reason = "최대 인원에 도달했습니다."

상태 반환

if 참여 취소 기능이 구현되어 있고 current_members < max_members and status == matched:

status = recruiting

reason = "다시 모집 중으로 변경되었습니다."

상태 반환

status = recruiting

reason = "모집 중입니다."

상태 반환

## ALG-07. 참여 가능 여부 판단 알고리즘

<!-- 표 12 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-07 |
| 알고리즘명 | 참여 가능 여부 판단 알고리즘 |
| 목적 | 사용자가 특정 파티에 참여할 수 있는지 판단한다. |
| 입력값 | user_id, party_id |
| 처리 기준 | 로그인 여부, 파티 존재 여부, 상태, 출발 시간, 중복 참여, 이동 시간대 중복 참여, 최대 인원, 성별 매칭 조건 |
| 출력값 | result_code, can_join, reason, party_join_state |
| 예외 상황 | 미로그인, 파티 없음, 이미 참여, 이동 시간대 중복, 최대 인원 초과, 매칭 완료, 취소, 만료, 이용 완료, 성별 조건 불일치 |
| 표시 방식 | 참여 가능 / 참여 불가 사유 표시 |
| 우선순위 | Must |

관련 API: POST /api/parties/{party_id}/join

### 결과 코드 기준

<!-- 표 13 -->
| result_code | can_join | party_join_state | reason |
| --- | --- | --- | --- |
| 200 | true | OKParty | 파티에 참여하였습니다. |
| 401 | false | NotOKParty | 로그인이 필요합니다. |
| 404 | false | NotOKParty | 존재하지 않는 파티입니다. |
| 409 | false | NotOKParty | 이미 참여한 파티입니다. |
| 409 | false | NotOKParty | 같은 시간대에 이미 참여 중인 파티가 있습니다. |
| 409 | false | NotOKParty | 최대 인원에 도달한 파티입니다. |
| 409 | false | NotOKParty | 이용 완료된 파티에는 참여할 수 없습니다. |
| 409 | false | NotOKParty | 매칭 완료된 파티에는 참여할 수 없습니다. |
| 409 | false | NotOKParty | 취소된 파티에는 참여할 수 없습니다. |
| 409 | false | NotOKParty | 출발 시간이 지난 파티입니다. |
| 403 | false | NotOKParty | 성별 매칭 조건에 맞지 않습니다. |

## 처리 흐름

로그인 사용자인지 확인한다.

party_id에 해당하는 파티가 존재하는지 확인한다.

파티 상태가 recruiting인지 확인한다.

departure_time이 현재 시간 이후인지 확인한다.

현재 사용자가 이미 해당 파티에 참여했는지 확인한다.

현재 사용자가 이미 참여 중인 활성 파티가 있는지 확인한다.

기존 참여 파티와 새로 참여하려는 파티의 이동 시간대가 겹치는지 확인한다.

current_members가 max_members보다 작은지 확인한다.

gender_rule이 same_gender이면 사용자 gender와 party_gender가 일치하는지 확인한다.

모든 조건을 통과하면 can_join=true를 반환한다.

조건을 통과하지 못하면 can_join=false와 reason을 반환한다.

### 의사코드

파티 참여 가능 여부 판단을 시작하면

if 로그인 사용자가 아니면:

result_code = 401

can_join = false

reason = "로그인이 필요합니다."

party_join_state = NotOKParty

반환

if party_id에 해당하는 파티가 없으면:

result_code = 404

can_join = false

reason = "존재하지 않는 파티입니다."

party_join_state = NotOKParty

반환

if 사용자가 이미 해당 파티에 참여했으면:

result_code = 409

can_join = false

reason = "이미 참여한 파티입니다."

party_join_state = NotOKParty

반환

if status == matched:

result_code = 409

can_join = false

reason = "매칭 완료된 파티에는 참여할 수 없습니다."

party_join_state = NotOKParty

반환

if status == canceled:

result_code = 409

can_join = false

reason = "취소된 파티에는 참여할 수 없습니다."

party_join_state = NotOKParty

반환

if status == expired:

result_code = 409

can_join = false

reason = "출발 시간이 지난 파티입니다."

party_join_state = NotOKParty

반환

if status == completed:

result_code = 409

can_join = false

reason = "이용 완료된 파티에는 참여할 수 없습니다."

party_join_state = NotOKParty

반환

if departure_time <= 현재 시간:

result_code = 409

can_join = false

reason = "출발 시간이 지난 파티입니다."

party_join_state = NotOKParty

반환

if 사용자가 이미 참여 중인 활성 파티가 있고 이동 시간대가 겹치면:

result_code = 409

can_join = false

reason = "같은 시간대에 이미 참여 중인 파티가 있습니다."

party_join_state = NotOKParty

반환

if current_members >= max_members:

result_code = 409

can_join = false

reason = "최대 인원에 도달한 파티입니다."

party_join_state = NotOKParty

반환

if gender_rule == same_gender and 사용자 gender != party_gender:

result_code = 403

can_join = false

reason = "성별 매칭 조건에 맞지 않습니다."

party_join_state = NotOKParty

반환

result_code = 200

can_join = true

reason = "파티에 참여하였습니다."

party_join_state = OKParty

반환

## ALG-08. 파티 참여 처리 알고리즘

<!-- 표 14 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-08 |
| 알고리즘명 | 파티 참여 처리 알고리즘 |
| 목적 | 참여 가능 판단 이후 실제 참여자 추가, 요금 재계산, 상태 변경을 처리한다. |
| 입력값 | user_id, party_id |
| 처리 기준 | party_members 추가, current_members 재계산, per_person_fare 재계산, max_members 도달 시 status=matched 변경 |
| 출력값 | 갱신된 파티 정보, current_members, per_person_fare, status |
| 예외 상황 | 참여 불가, 중복 참여, 최대 인원 초과, 성별 조건 불일치, 시간대 중복 |
| 표시 방식 | 참여 완료 안내와 갱신된 파티 정보 표시 |
| 우선순위 | Must |

관련 API: POST /api/parties/{party_id}/join

### 참여 처리 흐름

ALG-07로 참여 가능 여부를 먼저 판단한다.

can_join=true인 경우 party_members에 사용자를 추가한다.

current_members를 재계산한다.

저장된 estimated_fare 기준으로 per_person_fare를 재계산한다.

current_members가 max_members와 같으면 status를 matched로 변경한다.

갱신된 파티 정보를 반환한다.

## ALG-11. 파티 참여 취소·파티 취소 처리 알고리즘

관련 API: DELETE /api/parties/{party_id}/leave, PATCH /api/parties/{party_id}/cancel

우선순위: Target

### 참여 취소 처리 흐름

로그인 사용자인지 확인한다.

해당 파티 참여자인지 확인한다.

생성자가 나가려는 경우 참여 취소 대신 파티 취소를 안내한다.

참여자를 party_members에서 제거한다.

current_members를 재계산한다.

estimated_fare 기준으로 per_person_fare를 재계산한다.

필요 시 status를 recruiting으로 조정한다.

갱신된 파티 정보를 반환한다.

### 파티 취소 처리 흐름

로그인 사용자인지 확인한다.

파티 생성자인지 확인한다.

status를 canceled로 변경한다.

cancel_reason을 저장한다.

canceled_at을 저장한다.

취소된 파티 정보를 반환한다.

## ALG-09. 채팅 접근 및 메시지 처리 알고리즘

<!-- 표 15 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-09 |
| 알고리즘명 | 채팅 접근 및 메시지 처리 알고리즘 |
| 목적 | 같은 파티 참여자끼리만 채팅을 이용할 수 있도록 처리한다. |
| 입력값 | user_id, party_id, content, access_token |
| 처리 기준 | 토큰 검증, 파티 존재 확인, 참여자 여부 확인, 메시지 저장, WebSocket 브로드캐스트 |
| 출력값 | message_id, party_id, user_id, user_name, content, created_at |
| 예외 상황 | 토큰 없음, 토큰 만료, 비참여자 접근, 존재하지 않는 파티, 빈 메시지 |
| 표시 방식 | 채팅방 메시지 목록 및 실시간 메시지 표시 |
| 우선순위 | Target |

관련 API: GET /api/parties/{party_id}/messages, WS /ws/parties/{party_id}?token=<access_token>

### 처리 흐름

WebSocket query token을 확인한다.

토큰으로 사용자를 인증한다.

party_id에 해당하는 파티가 존재하는지 확인한다.

현재 사용자가 해당 파티 참여자인지 확인한다.

참여자이면 WebSocket 연결을 허용한다.

메시지를 수신한다.

빈 메시지인지 확인한다.

messages 테이블에 메시지를 저장한다.

같은 party_id 채팅방 참여자에게 메시지를 전송한다.

### 의사코드

채팅 연결 요청이 들어오면

if token이 없거나 유효하지 않으면:

연결 거부

if party_id에 해당하는 파티가 없으면:

연결 거부

if 사용자가 해당 파티 참여자가 아니면:

연결 거부

WebSocket 연결 허용

메시지 수신 시:

if content가 비어 있으면:

저장하지 않음

messages 테이블에 저장

같은 파티 참여자에게 브로드캐스트

## ALG-10. 관리자 통계 집계 알고리즘

<!-- 표 16 -->
| 항목 | 내용 |
| --- | --- |
| 알고리즘 ID | ALG-10 |
| 알고리즘명 | 관리자 통계 집계 알고리즘 |
| 목적 | 관리자 페이지에서 서비스 현황을 확인할 수 있도록 주요 데이터를 집계한다. |
| 입력값 | users, parties, messages |
| 처리 기준 | 전체 count, status별 count, 최근 파티 조회 |
| 출력값 | active_users, total_users, total_parties, recruiting_parties, matched_parties, canceled_parties, expired_parties, completed_parties, total_messages, recent_parties, recent_messages |
| 예외 상황 | 미로그인, 관리자 권한 없음 |
| 표시 방식 | 관리자 페이지 통계 카드와 최근 파티 목록 |
| 우선순위 | Could |

관련 API: GET /api/admin/stats, GET /api/admin/parties/recent, GET /api/admin/users, GET /api/admin/parties, PATCH /api/admin/parties/{party_id}/status, PATCH /api/admin/users/{user_id}/role, PATCH /api/admin/users/{user_id}/status, GET /api/admin/messages/recent, GET /api/admin/users/{user_id}, GET /api/admin/parties/{party_id}

### 처리 흐름

로그인 사용자인지 확인한다.

사용자 role이 admin인지 확인한다.

users 테이블의 전체 사용자 수를 계산한다.

parties 테이블의 전체 파티 수를 계산한다.

status=recruiting인 파티 수를 계산한다.

status=matched인 파티 수를 계산한다.

status=canceled인 파티 수를 계산한다.

status=expired인 파티 수를 계산한다.

messages 테이블의 전체 메시지 수를 계산한다.

최근 생성된 파티 목록을 조회한다.

관리자 통계 정보를 반환한다.

### 의사코드

관리자 통계 요청이 들어오면

if 로그인 사용자가 아니면:

result_code = 401

reason = "로그인이 필요합니다."

조회 차단

if role != admin:

result_code = 403

reason = "관리자 권한이 필요합니다."

조회 차단

total_users = users count
active_users = is_active == true count

total_parties = parties count

recruiting_parties = status == recruiting count

matched_parties = status == matched count

canceled_parties = status == canceled count

expired_parties = status == expired count
completed_parties = status == completed count

total_messages = messages count

recent_parties = created_at 최신순 조회

관리자 통계 반환

## 6. 알고리즘 간 연결 관계

<!-- 표 17 -->
| 선행 알고리즘 | 후속 알고리즘 | 연결 설명 |
| --- | --- | --- |
| ALG-03 | ALG-02 | 메인에서 입력한 출발지·도착지·출발 시간 조건을 기준으로 추천 파티를 먼저 확인 |
| ALG-03 | ALG-01 | 추천 결과가 없거나 사용자가 새 파티 생성을 선택하면 입력값을 유지한 채 파티 생성으로 이동 |
| ALG-04 | ALG-01 | 파티 생성 중 예상 택시비 자동 산정 |
| ALG-05 | ALG-01 | 파티 생성 직후 1인 예상 요금 계산 |
| ALG-07 | ALG-08 | 참여 가능 여부 판단 후 실제 참여 처리 |
| ALG-08 | ALG-05 | 참여자 수 변경 후 1인 예상 요금 재계산 |
| ALG-11 | ALG-05 | 참여 취소로 참여자 수가 변경되면 1인 예상 요금을 재계산 |
| ALG-11 | ALG-06 | 참여 취소 또는 파티 취소 후 상태를 갱신 |
| ALG-08 | ALG-06 | 참여자 수 변경 후 상태 변경 |
| ALG-06 | ALG-02 | 만료·취소·매칭 완료 파티는 검색 결과에서 제외 또는 상태 구분 |
| ALG-07 | ALG-09 | 파티 참여자만 채팅 접근 가능 |
| ALG-10 | 전체 알고리즘 | 관리자 페이지에서 전체 처리 결과를 집계 |

# 7. 예외 처리 기준

<!-- 표 18 -->
| 상황 | result_code | 처리 |
| --- | --- | --- |
| 미로그인 | 401 | 로그인 안내 |
| 파티 없음 | 404 | 존재하지 않는 파티 안내 |
| 필수값 누락 | 400 | 입력값 확인 안내 |
| 좌표값 없음 | 400 | 장소 검색 결과 선택 안내 |
| 과거 시간 선택 | 400 | 현재 이후 시간 선택 안내 |
| 최대 인원 오류 | 400 | 2~4명 기준 안내 |
| 요금 산정 실패 | 502 | 출발지·도착지 재확인 안내 |
| 이미 참여한 파티 | 409 | 중복 참여 차단 |
| 최대 인원 도달 | 409 | 참여 차단 |
| 매칭 완료 파티 | 409 | 참여 차단 |
| 취소된 파티 | 409 | 참여 차단 |
| 출발시간 만료 파티 | 409 | 참여 차단 |
| 성별 조건 불일치 | 403 | 참여 차단 |
| 관리자 권한 없음 | 403 | 관리자 접근 차단 |

# 8. 최종 점검표

알고리즘 설계서 반영 후 아래 항목을 확인한다.

□ 알고리즘 ID가 ALG-01 형식으로 통일되었는가

□ 입력값이 API 명세서 기준 변수명으로 통일되었는가

□ 파티 검색이 자동 초대가 아니라 목록 표시 기준으로 수정되었는가

□ 유사 파티 추천 점수표가 100점 기준으로 정리되었는가

□ match_score 계산 기준이 API 명세서와 일치하는가

□ 예상 택시비는 사용자가 입력하지 않는다고 명시되었는가

□ Kakao Mobility API 기반 estimated_fare 산정이 반영되었는가

□ per_person_fare 계산식이 ceil(estimated_fare / current_members)인가

□ 상태값이 recruiting / matched / canceled / expired / completed로 통일되었는가

□ matched 파티의 출발 시간이 지나면 completed로 처리되는가

□ completed 파티는 신규 참여가 차단되는가

□ 관리자 페이지에서 completed 파티 수를 확인할 수 있는가

□ Version 0.1.0-alpha(v0.1.0-alpha)가 문서와 화면 기준에 반영되었는가

□ 참여 가능 여부 판단에 result_code, can_join, reason이 포함되었는가

□ 성별 매칭 조건이 참여 가능 여부 판단에 포함되었는가

□ meeting_point, meeting_note가 검색·추천·상세 출력값에 포함되었는가

□ 추천 결과 없음 시 자동 생성이 아니라 새 파티 생성 안내로 정리되었는가

□ 채팅 접근 조건이 파티 참여자 기준으로 정리되었는가

□ 관리자 통계 집계 기준이 포함되었는가
