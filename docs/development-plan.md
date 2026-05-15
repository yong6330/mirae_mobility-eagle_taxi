# 미래 모빌리티 프로젝트 개발 계획(안)

> 변환 원본: `미래 모빌리티 프로젝트 개발 계획(안).docx`

# Mirae Mobility 프로젝트 개발 계획(안) v0.4

## 1. 문서 목적

본 문서는 Mirae Mobility 팀의 컴퓨팅사고 팀 프로젝트 「독수리 택시」 개발을 위한 실행 기준을 정리한 내부 개발 문서이다.

본 개발 계획(안)은 개발팀이 GitHub, VS Code, React, FastAPI, SQLite, Kakao Maps API, WebSocket, AI 개발 도구를 활용하여 프로젝트 MVP를 구현할 때 따라야 할 개발 절차와 작업 기준을 제공하는 것을 목적으로 한다.

본 문서는 최종 보고서나 제출용 기획서가 아니라, 팀원들이 실제 개발 과정에서 계속 참고하는 개발 매뉴얼이다.

## 2. 프로젝트 기본 정보

<!-- 표 1 -->
| 구분 | 내용 |
| --- | --- |
| 프로젝트명 | 독수리 택시 |
| 팀명 | Mirae Mobility |
| 개발 버전 | Version 0.1.0-alpha(v0.1.0-alpha) |
| 저장소명 | mirae_mobility-eagle_taxi |
| GitHub 저장소 | https://github.com/yong6330/mirae_mobility-eagle_taxi |
| 개발 기준 | React + FastAPI + SQLite |
| 코드 관리 | GitHub |
| 개발 도구 | VS Code |
| 프론트엔드 포트 | 5173 |
| 백엔드 포트 | 8000 |
| API 문서 주소 | http://localhost:8000/docs |
| 최종 실행 방식 | 발표자 PC 로컬 서버 실행 후 같은 Wi-Fi 접속 |

## 3. 개발 계획(안)의 사용 방법

<!-- 표 2 -->
| 사용 상황 | 참고할 부분 |
| --- | --- |
| 개발 전 준비 | Git, GitHub, VS Code, Node.js, Python 설치 및 확인 |
| 저장소 연결 | GitHub clone, 브랜치 생성, Pull Request 방식 |
| 프론트엔드 개발 | React 폴더 구조, 페이지 구성, API 연결 방식 |
| 백엔드 개발 | FastAPI 폴더 구조, SQLite DB, API 구현 기준 |
| AI 개발 도구 사용 | 작업 단위, 금지사항, 결과 검토 기준 |
| 로컬 AI 참고 문서 사용 | _AI_Context/ 기준 문서 확인 |
| 오픈소스 레퍼런스 사용 | _Reference_bank/ 참고 범위 확인 |
| 오류 발생 | 오류 대응표, 개발 난항 시 처리 기준 |
| 최종 실행 | Windows / macOS 서버 실행 방법, run-dev 스크립트 |
| 발표 시연 | 같은 Wi-Fi 접속 기준, 최종 점검표 |

## 4. 개발 기준 요약

<!-- 표 3 -->
| 항목 | 개발 기준 |
| --- | --- |
| 프론트엔드 | React + Vite |
| 프론트엔드 언어 | JavaScript + JSX |
| 프론트엔드 스타일 | 기본 CSS |
| 백엔드 | Python FastAPI |
| 데이터베이스 | SQLite |
| DB 접근 방식 | SQLAlchemy ORM |
| 인증 방식 | JWT 기반 로그인 |
| 비밀번호 저장 | passlib 기반 해시 저장 |
| 지도 API | Kakao Maps JavaScript API |
| 장소 검색 | Kakao Maps Places keywordSearch |
| 예상 택시비 산정 | Kakao Mobility Directions API |
| 채팅 | FastAPI WebSocket 기반 실시간 채팅 |
| 관리자 페이지 | React 내부 /admin 경로 |
| API 테스트 | FastAPI 자동 문서 /docs |
| 패키지 관리 | requirements.txt, package.json |
| 개발 환경 | 팀원 개발 기준은 Windows 중심 |
| 서버 실행 | Windows / macOS 모두 가능하도록 관리 |
| 배포 방식 | 외부 배포 없음, 로컬 네트워크 실행 |
| AI 참고 문서 | _AI_Context/ 로컬 폴더 |
| 오픈소스 참고자료 | _Reference_bank/ 로컬 폴더 |

### 4-1. 반응형 화면 최적화 기준

본 프로젝트는 발표 시연과 실제 사용 가능성을 고려해 다양한 화면 크기에서 사용할 수 있도록 반응형 기준을 적용한다.

<!-- 표 4 -->
| 기기 구분 | 기준 화면 | 구현 기준 |
| --- | --- | --- |
| 대형 모니터 | 27~32인치 데스크톱 모니터 | 관리자 페이지, 파티 목록, 통계 차트가 넓은 화면에서 깨지지 않도록 구성 |
| 노트북 | 14인치 내외 노트북 | 발표자 PC와 일반 개발 환경에서 핵심 화면이 정상 표시되도록 구성 |
| 태블릿 | 9~12인치 태블릿 | 카드형 목록, 상세 화면, 채팅 화면이 세로·가로 화면에서 사용 가능하도록 구성 |
| 스마트폰 | 소형~대형 스마트폰 | 파티 검색, 파티 생성, 파티 상세, 채팅 기능을 모바일에서도 사용할 수 있도록 구성 |

반응형 구현 기준:

주요 화면은 모바일, 태블릿, 노트북, 대형 모니터에서 모두 깨지지 않아야 한다.

파티 목록은 작은 화면에서 1열 카드형, 넓은 화면에서 2~3열 카드형으로 표시할 수 있다.

관리자 페이지의 차트와 테이블은 작은 화면에서 세로 배치, 넓은 화면에서 그리드 배치한다.

Header는 모바일에서 메뉴 버튼 또는 접힘 구조를 사용할 수 있다.

Footer의 안전 안내, 이용약관, 개인정보 처리방침, 개발팀 정보 링크는 모든 화면 크기에서 접근 가능해야 한다.

## 5. 절대 변경하면 안 되는 개발 원칙

<!-- 표 5 -->
| 원칙 | 내용 |
| --- | --- |
| 버전 임의 변경 금지 | 개발 기준 버전은 Version 0.1.0-alpha(v0.1.0-alpha)로 고정한다. PM 허가 없이 AI 도구나 팀원이 버전명을 임의로 변경하지 않는다. |
| 기술 스택 고정 | React + FastAPI + SQLite 구조를 변경하지 않는다. |
| 프론트 단독 구현 금지 | 백엔드 없이 React localStorage만으로 기능을 구현하지 않는다. |
| 임시 배열 저장 금지 | 사용자, 파티, 참여자, 채팅 데이터를 코드 내부 배열로만 저장하지 않는다. |
| SQLite 저장 필수 | 사용자, 파티, 참여자, 채팅 데이터는 SQLite에 저장한다. |
| React 역할 제한 | React는 화면 구성과 API 호출을 담당한다. |
| FastAPI 역할 고정 | FastAPI는 데이터 처리, 인증, 파티 로직, 채팅 로직을 담당한다. |
| localStorage 제한 | localStorage는 로그인 토큰 저장 외의 용도로 사용하지 않는다. |
| Streamlit 전환 금지 | Streamlit 기반 프로젝트로 전환하지 않는다. |
| 기술 축소 금지 | 임의로 “간단한 MVP”라며 백엔드, DB, API 구조를 제거하지 않는다. |
| 실제 택시 호출 제외 | 실제 택시 호출, 배차, 결제, 운전자 연결은 구현하지 않는다. |
| API 변경 절차 | API 변경 시 API 명세서와 프론트·백엔드 담당자 확인 후 반영한다. |
| AI 임의 변경 금지 | AI 도구가 기술 스택, 저장 방식, 폴더 구조를 바꾸면 즉시 수정한다. |
| 레퍼런스 무단 전환 금지 | 레퍼런스 프로젝트의 Docker, PostgreSQL, Redis, MongoDB, TypeScript, Tailwind, OAuth, 결제, GPS 추적 기능을 임의로 도입하지 않는다. |
| 레퍼런스 활용 원칙 | 레퍼런스는 구조·패턴·구현 힌트를 적극 참고하되, 우리 프로젝트 기준에 맞게 재구성한다. |

## 6. 개발 금지선 체크리스트

아래 항목 중 하나라도 해당하면 잘못된 개발 방향으로 판단하고 즉시 수정한다.

□ React만으로 모든 기능을 구현하고 있는가

□ 백엔드 API 없이 localStorage에 사용자·파티·채팅 데이터를 저장하고 있는가

□ SQLite 없이 임시 배열로 데이터를 처리하고 있는가

□ FastAPI가 아닌 다른 백엔드 구조로 바꾸고 있는가

□ Streamlit 또는 단일 Python 화면 앱으로 전환하고 있는가

□ 실제 택시 호출, 결제, 운전자 연결 기능을 구현하려고 하는가

□ API 명세서와 다른 Endpoint를 임의로 만들고 있는가

□ DB 테이블 구조를 임의로 바꾸고 있는가

□ 프론트와 백엔드가 서로 다른 데이터 형식을 기대하고 있는가

□ main 브랜치에 검토 없이 직접 코드를 반영하고 있는가

□ 레퍼런스 프로젝트의 기술 스택을 우리 프로젝트에 그대로 바꾸어 적용하고 있는가

□ 레퍼런스 코드를 가져오면서 출처와 LICENSE를 기록하지 않았는가

□ _AI_Context 또는 _Reference_bank 폴더가 GitHub에 올라가고 있는가

위 항목이 발견되면 해당 작업은 중단하고, PM 또는 TL 확인 후 다시 진행한다.

## 7. 역할별 개발 범위

<!-- 표 6 -->
| 역할 | 담당자 | 개발 관련 역할 |
| --- | --- | --- |
| PM | 용석희 | 개발 계획 관리, GitHub 구조 관리, API 명세서 관리, Kakao API Key 관리, 관리자 페이지 구현, README 작성, _AI_Context 배포, _Reference_bank 기준 정리, 최종 실행 및 시연 점검 |
| TL | 이가람 | FastAPI 백엔드, SQLite DB, SQLAlchemy 모델, Auth API, Party API, WebSocket, Admin API, 프론트·백엔드 통합 |
| QA&Front | 심지수 | React 프론트엔드, 화면 구현, 라우팅, API 연결, Kakao Map 표시, 채팅 화면, 테스트 기획 및 오류 기록 |
| OM | 최우진 | 알고리즘 문서, 설문조사 데이터, 보고서용 개발 근거 정리, 테스트·결과 정리 지원 |

README 작성 기준:

README 최종 작성과 품질 관리는 PM이 담당한다.

TL은 실제 실행 명령어, 백엔드 실행 방법, API 문서 주소, 환경변수 항목을 PM에게 제공한다.

QA&Front는 프론트엔드 실행 방법, 주요 화면, 사용 흐름, 화면 캡처가 필요한 경우 PM에게 제공한다.

OM은 설문조사와 결과 보고서 관련 요약이 필요한 경우 PM에게 제공한다.

최종 README는 PM이 프로젝트 소개, 기술 스택, 팀원 역할, 실행 방법, 주요 기능, 시연 흐름을 통합해 작성한다.

# 8. 개발 전 준비물

## 8-1. 필수 계정 및 도구

<!-- 표 7 -->
| 준비물 | 사용 목적 | 필수 여부 |
| --- | --- | --- |
| GitHub 계정 | 저장소 접근, 코드 공유 | 필수 |
| Git | commit, push, pull, branch 작업 | 필수 |
| VS Code | 코드 편집 및 실행 | 필수 |
| Node.js LTS | React 실행 | 필수 |
| Python 3.11 이상 | FastAPI 실행 | 필수 |
| Kakao Developers API Key | 지도 표시 | PM 관리 |
| ChatGPT / Codex / Claude Code 등 | 코드 생성 및 수정 | 개발팀 사용 |
| Google Drive | 문서 산출물 및 AI Context 배포 | 필수 |
| _AI_Context/ | AI 참고용 기준 문서 | PM 배포 |
| _Reference_bank/ | 오픈소스 레퍼런스 참고자료 | 로컬 설치 |

## 8-2. 설치 확인 명령어

Windows 기준으로 명령 프롬프트(cmd) 또는 PowerShell에서 아래 명령어를 실행한다.

git --version

node -v

npm -v

python --version

Python은 아래 명령어로도 확인할 수 있다.

py --version

정상 기준:

<!-- 표 8 -->
| 항목 | 정상 예시 |
| --- | --- |
| Git | git version 2.xx.x |
| Node.js | v20.xx.x 이상 |
| npm | 10.xx.x 등 |
| Python | Python 3.11.x 이상 |

# 9. Git 설치 및 기본 설정

## 9-1. Git 설치 확인

git --version

정상 예시:

git version 2.xx.x

오류 예시:

'git'은 내부 또는 외부 명령, 실행할 수 있는 프로그램 또는 배치 파일이 아닙니다.

이 경우 Git을 설치해야 한다.

## 9-2. Git 설치 방법

<!-- 표 9 -->
| 단계 | 내용 |
| --- | --- |
| 1 | Git 공식 사이트 접속 |
| 2 | Download for Windows 클릭 |
| 3 | 설치 파일 실행 |
| 4 | 설치 옵션은 기본값으로 진행 |
| 5 | 설치 완료 후 cmd 또는 VS Code 터미널 재시작 |
| 6 | git --version으로 설치 확인 |

## 9-3. Git 사용자 정보 설정

Git 설치 후 아래 명령어를 실행한다.

git config --global user.name "본인 GitHub 이름"

git config --global user.email "본인 GitHub 이메일"

예시:

git config --global user.name "yong6330"

git config --global user.email "yong6330@yonsei.ac.kr"

설정 확인:

git config --global --list

# 10. GitHub 로그인 및 인증 방법

## 10-1. 기본 원칙

GitHub 저장소를 clone, push, pull 하려면 GitHub 계정 인증이 필요하다.

인증은 보통 아래 중 하나로 진행된다.

<!-- 표 10 -->
| 방식 | 설명 | 추천 |
| --- | --- | --- |
| VS Code GitHub 로그인 | VS Code에서 GitHub 계정으로 로그인 | 초보자 추천 |
| 브라우저 인증 | push 또는 clone 중 브라우저 로그인 창이 열림 | 가능 |
| GitHub CLI | 터미널에서 gh auth login으로 로그인 | push 오류 시 추천 |
| Personal Access Token | 토큰을 직접 발급해 인증 | 초보자 비추천 |

## 10-2. VS Code에서 GitHub 로그인

<!-- 표 11 -->
| 단계 | 내용 |
| --- | --- |
| 1 | VS Code 실행 |
| 2 | 왼쪽 아래 계정 아이콘 클릭 |
| 3 | Sign in with GitHub 클릭 |
| 4 | 브라우저가 열리면 GitHub 로그인 |
| 5 | VS Code로 돌아와 로그인 완료 확인 |

로그인이 완료되면 VS Code에서 GitHub 저장소 clone과 push가 더 쉽게 진행된다.

## 10-3. GitHub CLI 인증 방법

GitHub push가 계속 실패하면 GitHub CLI를 사용할 수 있다.

설치 확인:

gh --version

설치되어 있지 않으면 GitHub CLI를 설치한다.

로그인:

gh auth login

선택 기준:

1. GitHub.com 선택

2. HTTPS 선택

3. Authenticate Git with your GitHub credentials 선택

4. Login with a web browser 선택

5. 브라우저에서 GitHub 로그인

6. 인증 완료 후 터미널로 복귀

인증 확인:

gh auth status

# 11. Node.js 설치 및 확인

## 11-1. 설치 확인

node -v

npm -v

정상 예시:

v20.xx.x

10.xx.x

## 11-2. 설치 기준

<!-- 표 12 -->
| 항목 | 기준 |
| --- | --- |
| 설치 버전 | Node.js LTS 권장 |
| 사용 목적 | React + Vite 실행 |
| 포함 도구 | npm 자동 포함 |

# 12. Python 설치 및 확인

## 12-1. 설치 확인

python --version

또는:

py --version

정상 예시:

Python 3.11.x

## 12-2. 설치 기준

<!-- 표 13 -->
| 항목 | 기준 |
| --- | --- |
| 권장 버전 | Python 3.11 이상 |
| 사용 목적 | FastAPI 백엔드 실행 |
| 주의사항 | 설치 시 Add Python to PATH 체크 권장 |

# 13. VS Code 준비

## 13-1. 설치할 확장 프로그램

<!-- 표 14 -->
| 확장 프로그램 | 사용 목적 |
| --- | --- |
| Python | FastAPI 개발 |
| Pylance | Python 코드 분석 |
| ESLint | React 코드 오류 확인 |
| Prettier | 코드 정리 |
| GitHub Pull Requests | PR 확인 |
| GitLens | Git 변경 이력 확인 |
| SQLite Viewer | SQLite DB 확인 |

# 14. GitHub 저장소 Clone 방법

## 14-1. 저장소 초대 수락

<!-- 표 15 -->
| 단계 | 내용 |
| --- | --- |
| 1 | GitHub 로그인 |
| 2 | 저장소 초대 알림 확인 |
| 3 | Accept invitation 클릭 |
| 4 | 저장소 접근 가능 여부 확인 |

저장소 주소:

https://github.com/yong6330/mirae_mobility-eagle_taxi

## 14-2. VS Code에서 Clone

<!-- 표 16 -->
| 단계 | 내용 |
| --- | --- |
| 1 | VS Code 실행 |
| 2 | Source Control 아이콘 클릭 |
| 3 | Clone Repository 클릭 |
| 4 | GitHub 저장소 주소 붙여넣기 |
| 5 | 저장할 폴더 선택 |
| 6 | Open 클릭 |

터미널 명령어로 clone할 경우:

git clone https://github.com/yong6330/mirae_mobility-eagle_taxi.git

폴더 이동:

cd mirae_mobility-eagle_taxi

# 15. GitHub 협업 방식

본 프로젝트는 main 브랜치에 직접 작업하지 않고, develop 브랜치를 중심으로 통합한 뒤 최종 안정본만 main에 반영한다.

## 15-1. 브랜치 구조

<!-- 표 17 -->
| 브랜치 | 담당 | 용도 |
| --- | --- | --- |
| main | PM / TL 관리 | 최종 발표용 안정본 |
| develop | TL | 프론트·백엔드 통합 개발본 |
| feature/backend | TL | FastAPI 백엔드, SQLite, API, WebSocket 구현 |
| feature/frontend | QA | React 화면, 라우팅, API 연결, Kakao Map 표시 |
| feature/admin | PM | 관리자 페이지, 문서 보조, 실행 스크립트 |
| docs/project-docs | PM | README, docs 등 공개 문서 정리 필요 시 사용 |

## 15-2. 브랜치 기본 원칙

<!-- 표 18 -->
| 원칙 | 내용 |
| --- | --- |
| main 직접 수정 금지 | 최종 안정본 보호 |
| develop 통합 기준 | 각 기능 브랜치는 develop으로 Pull Request 업로드 |
| 작업 전 pull | 최신 코드 기준으로 작업 |
| 담당 브랜치 사용 | 각자 맡은 브랜치에서 작업 |
| 작업 단위 commit | 기능별로 commit |
| 작업 완료 후 push | GitHub에 작업 내용 업로드 |
| Pull Request 생성 | feature 브랜치에서 develop으로 PR 생성 |
| main 반영 | develop에서 통합 테스트 후 main으로 PR한다. |
| PM/TL 확인 후 merge | 충돌과 구조 변경을 방지한다. |

# 16. 작업 시작 전 기본 루틴

개발을 시작할 때마다 아래 순서를 따른다.

1. VS Code 실행

2. 프로젝트 폴더 열기

3. 현재 브랜치 확인

4. main 최신 내용 받기

5. 자기 작업 브랜치로 이동

6. 필요한 패키지 설치 여부 확인

7. _AI_Context 기준 문서 확인

8. _Reference_bank 참고자료 확인

9. 백엔드 또는 프론트엔드 실행 확인

10. 오늘 작업할 기능 하나를 정함

11. AI 개발 도구에 작업 단위를 나눠 요청

12. 생성된 코드 직접 실행 확인

명령어 예시:

git status

git checkout main

git pull origin main

git checkout develop

git pull origin develop

관리자, 문서 담당:

git checkout feature/admin

git pull origin feature/admin

공개 문서 정리 담당:

git checkout docs/project-docs

git pull origin docs/project-docs

백엔드 담당:

git checkout feature/backend

git pull origin feature/backend

프론트 담당:

git checkout feature/frontend

git pull origin feature/frontend

# 17. 작업 종료 전 기본 루틴

개발을 끝낼 때마다 아래 순서를 따른다.

1. 실행 중인 서버에서 오류 확인

2. 구현한 기능 직접 테스트

3. AI가 기준 문서와 다른 구조를 만들지 않았는지 확인

4. 레퍼런스에서 가져온 코드가 있다면 출처와 LICENSE 기록 여부 확인

5. git status 확인

6. 변경 파일 확인

7. _AI_Context, _Reference_bank, .env, DB 파일이 git status에 뜨지 않는지 확인

8. git add .

9. git commit

10. git push

11. Pull Request 생성 또는 업데이트

12. 카카오톡 또는 회의 자료에 작업 내용 공유

13. 막힌 부분이 있으면 이슈 관리표에 기록

명령어 예시:

git status

git add .

git commit -m "feat: 파티 생성 API 추가"

git push

# 18. 브랜치 생성 방법

처음에는 PM이 main에서 develop 브랜치를 만든다.

PM 최초 설정:
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop

역할별 브랜치 생성:
git checkout develop
git pull origin develop
git checkout -b feature/backend
git push -u origin feature/backend
git checkout develop
git checkout -b feature/frontend
git push -u origin feature/frontend
git checkout develop
git checkout -b feature/admin
git push -u origin feature/admin

팀원은 본인 담당 브랜치로 이동해 작업한다.

TL:
git fetch origin
git checkout feature/backend

QA&Front:
git fetch origin
git checkout feature/frontend

PM:
git fetch origin
git checkout feature/admin

브랜치 확인:
git branch
현재 브랜치 앞에 * 표시가 붙는다.

# 19. commit / push 방법

## 19-1. 변경사항 확인

git status

## 19-2. 변경사항 추가

git add .

## 19-3. commit 작성

git commit -m "feat: 회원가입 API 추가"

## 19-4. GitHub에 push

처음 push:

git push -u origin feature/backend-api

이후 같은 브랜치에서 push:

git push

# 20. commit 메시지 규칙

<!-- 표 19 -->
| 유형 | 의미 | 예시 |
| --- | --- | --- |
| feat | 새 기능 추가 | feat: 파티 생성 API 추가 |
| fix | 오류 수정 | fix: 파티 참여 인원 계산 오류 수정 |
| docs | 문서 수정 | docs: 개발 계획안 추가 |
| style | 디자인/스타일 수정 | style: 파티 카드 CSS 수정 |
| refactor | 코드 구조 개선 | refactor: auth router 분리 |
| test | 테스트 추가 | test: 파티 생성 테스트 추가 |
| chore | 설정/기타 작업 | chore: requirements.txt 업데이트 |

커밋 메시지 작성 기준:

유형: 작업 내용

# 21. Pull Request 생성 및 Merge 기준

## 21-1. PR 생성 방법

<!-- 표 20 -->
| 단계 | 내용 |
| --- | --- |
| 1 | GitHub 저장소 접속 |
| 2 | Pull requests 클릭 |
| 3 | New pull request 클릭 |
| 4 | base: develop 선택 |
| 5 | compare: 본인작업 브랜치 선택 |
| 6 | 변경 내용 확인 |
| 7 | Create pull request 클릭 |
| 8 | 작업 내용 요약 작성 |
| 9 | PM 또는 TL 확인 후 develop에 merge |

주의사항:
- feature 브랜치에서 main으로 바로 Pull Request를 올리지 않는다.
- 기능 개발은 feature → develop 순서로 합친다.
- 최종 발표 전 안정화된 develop만 main으로 Pull Request를 올린다.

## 21-2. PR 방향

<!-- 표 21 -->
| 작업 유형 | base | compare |
| --- | --- | --- |
| 백엔드 작업 반영 | develop | feature/backend |
| 프론트엔드 작업 반영 | develop | feature/frontend |
| 관리자·문서 작업 반영 | develop | feature/admin 또는 docs/project-docs |
| 최종 안정본 반영 | main | develop |

## 21-4. Merge 기준

<!-- 표 22 -->
| 항목 | 기준 |
| --- | --- |
| PR 생성자 | 작업 담당자 |
| PR 확인자 | PM 또는 TL |
| Merge 권한 | PM 또는 TL 중심 |
| Merge 전 확인 | 실행 가능 여부, API 명세서 일치 여부 |
| 충돌 발생 시 | PM/TL이 담당자와 함께 수정 |
| main 반영 기준 | 실행 가능한 상태만 반영 |
| 레퍼런스 코드 반영 기준 | 출처와 LICENSE 기록 후 반영 |
| 로컬 폴더 반영 기준 | _AI_Context, _Reference_bank는 merge 대상 아님 |

## 21-5. Pull Request 리뷰 체크리스트

Pull Request를 main에 merge하기 전 아래 항목을 확인한다.

□ 작업 브랜치가 main이 아닌가

□ commit 메시지가 작업 내용을 설명하는가

□ 실행했을 때 오류가 없는가

□ 기존 기능이 삭제되지 않았는가

□ React + FastAPI + SQLite 구조가 유지되었는가

□ localStorage에 핵심 데이터를 저장하지 않았는가

□ API Endpoint가 명세서와 일치하는가

□ DB 테이블 구조가 임의로 변경되지 않았는가

□ .env 파일이 포함되지 않았는가

□ API Key가 코드에 직접 작성되지 않았는가

□ _AI_Context 폴더가 포함되지 않았는가

□ _Reference_bank 폴더가 포함되지 않았는가

□ 레퍼런스 코드를 가져온 경우 출처와 LICENSE 기록이 있는가

□ README 또는 문서 수정이 필요한 경우 반영했는가

Merge 처리 기준:

<!-- 표 23 -->
| 상황 | 처리 |
| --- | --- |
| 문제 없음 | PM 또는 TL이 merge |
| 실행 오류 있음 | merge 금지, 담당자 수정 |
| API 구조 변경 있음 | PM, TL, QA&Front 확인 후 반영 |
| DB 구조 변경 있음 | PM, TL 확인 후 반영 |
| 충돌 발생 | PM/TL이 담당자와 함께 해결 |
| .env 또는 API Key 노출 | 즉시 제거 후 commit history 확인 |
| _AI_Context 노출 | merge 금지, .gitignore 확인 |
| _Reference_bank 노출 | merge 금지, .gitignore 확인 |
| LICENSE 누락 | 출처 및 LICENSE 기록 후 재검토 |

# 22. 초기 개발 세팅 완료 기준

팀원은 본격 개발 전 아래 상태를 완료해야 한다.

□ GitHub 저장소 초대 수락 완료

□ VS Code에서 저장소 clone 완료

□ Git 사용자 이름과 이메일 설정 완료

□ 본인 작업 브랜치 생성 완료

□ Node.js와 npm 버전 확인 완료

□ Python 3.11 이상 확인 완료

□ frontend 폴더에서 npm install 완료

□ backend 폴더에서 가상환경 생성 완료

□ backend 패키지 설치 완료

□ frontend 서버 실행 확인

□ backend 서버 실행 확인

□ http://localhost:5173 접속 확인

□ http://localhost:8000/docs 접속 확인

□ .env 파일은 생성했지만 GitHub에 업로드하지 않음

□ _AI_Context 폴더를 PM이 배포한 파일로 구성 완료

□ _Reference_bank 폴더 구성 완료

□ git status에 _AI_Context, _Reference_bank, .env, *.db가 뜨지 않음

초기 세팅 완료 후 각 담당자는 아래 형식으로 공유한다.

[초기 세팅 완료]

이름:

담당:

브랜치:

frontend 실행 여부:

backend 실행 여부:

_AI_Context 구성 여부:

_Reference_bank 구성 여부:

git status 확인 여부:

막힌 부분:

# 23. 프로젝트 폴더 구조

최종 프로젝트 구조는 아래를 기준으로 한다.

mirae_mobility-eagle_taxi/

├─ frontend/

│  ├─ src/

│  │  ├─ api/

│  │  ├─ components/

│  │  ├─ pages/

│  │  ├─ routes/

│  │  ├─ hooks/

│  │  ├─ utils/

│  │  ├─ App.jsx

│  │  └─ main.jsx

│  ├─ public/

│  ├─ package.json

│  ├─ vite.config.js

│  └─ .env

│

backend/

├─ app/

│ ├─ main.py

│ ├─ database.py

│ ├─ models.py

│ ├─ schemas.py

│ ├─ auth.py

│ ├─ services/

│ │ └─ kakao_mobility.py

│ └─ routers/

│ ├─ auth.py

│ ├─ fares.py

│ ├─ parties.py

│ ├─ messages.py

│ └─ admin.py

├─ requirements.txt

└─ .env

│

├─ docs/

│  ├─ development-plan.md

│  ├─ api-spec.md

│  ├─ database-schema.md

│  ├─ testing-checklist.md

│  ├─ terms.md

│  ├─ privacy.md

│  └─ reference-usage.md

│

├─ _AI_Context/

│  ├─ 00_Project_Brief.md

│  ├─ 01_Development_Plan.md

│  ├─ 02_API_Spec.md

│  ├─ 03_Feature_Spec.md

│  ├─ 04_DB_Model.md

│  ├─ 05_Screen_Flow.md

│  ├─ 06_Algorithm.md

│  ├─ 07_Test_Checklist.md

│  ├─ 08_Issue_Rules.md

│  └─ 99_AI_Working_Rules.md

│

├─ _Reference_bank/

│  ├─ fastapi_full_stack_template/

│  ├─ fastapi_react_boilerplate/

│  ├─ fastapi_react_ws_chat/

│  ├─ fastapi_react_websocket_app/

│  ├─ simple_chat_fastapi/

│  ├─ ridepool_strps/

│  └─ README.md

│

├─ run-dev.bat

├─ run-dev-mac.sh

├─ .env.example

├─ .gitignore

└─ README.md

추가 설명

backend/app/services/kakao_mobility.py는 Kakao Mobility API 호출을 담당한다.
backend/app/routers/fares.py는 GET /api/fares/estimate 엔드포인트를 담당한다.
파티 생성 API는 내부에서 kakao_mobility.py의 요금 산정 로직을 호출한다.

# 24. 폴더별 역할

<!-- 표 24 -->
| 폴더/파일 | 담당 | 역할 |
| --- | --- | --- |
| frontend | QA&Front | React 화면 개발 |
| frontend/src/api | QA&Front | API 호출 함수 관리 |
| frontend/src/components | QA&Front | 공통 UI 컴포넌트 |
| frontend/src/pages | QA&Front | 랜딩, 회원가입, 로그인, 메인, 파티 목록, 파티 생성, 파티 상세, 내 파티, 채팅, 안전 안내, 설정, 약관/개인정보, 관리자 페이지 단위 화면 |
| frontend/src/routes | QA&Front | 라우팅 구조 |
| backend | TL | FastAPI 백엔드 개발 |
| backend/app/models.py | TL | DB 테이블 모델 |
| backend/app/schemas.py | TL | 요청/응답 데이터 구조 |
| backend/app/routers | TL | 기능별 API |
| backend/app/auth.py | TL | JWT, 비밀번호 해시 처리 |
| docs | PM | GitHub 업로드용 공식 개발 문서 |
| docs/guide.md | PM | 안전 안내 원본 문서 |
| docs/terms.md | PM | 이용약관 원본 문서 |
| docs/privacy.md | PM | 개인정보 처리방침 원본 문서 |
| _AI_Context | PM 배포, 전원 사용 | AI 도구가 참고하는 로컬 기준 문서 |
| _Reference_bank | PM 기준 정리, 전원 사용 | 오픈소스 레퍼런스 로컬 보관소 |
| run-dev.bat | PM/TL | Windows 통합 실행 스크립트 |
| run-dev-mac.sh | PM | macOS 통합 실행 스크립트 |
| README.md | PM | 프로젝트 소개 및 실행 방법 |
| .gitignore | PM/TL | 업로드 금지 파일 및 폴더 관리 |

# 25. 로컬 AI Context 관리 기준

## 25-1. 목적

_AI_Context/ 폴더는 ChatGPT, Codex, Claude Code 등 AI 개발 도구가 프로젝트 기준을 일관되게 참고할 수 있도록 만드는 로컬 전용 기준 문서 폴더이다.

이 폴더는 GitHub에 업로드하지 않는다.

PM이 기준 문서를 .md 파일로 제작한 뒤 Google Drive에 배포하고, 팀원은 해당 파일을 프로젝트 루트의 _AI_Context/ 폴더에 넣는다.

## 25-2. _AI_Context/ 구성 기준

<!-- 표 25 -->
| 파일명 | 내용 | 담당 |
| --- | --- | --- |
| 00_Project_Brief.md | 프로젝트 목적, 문제 정의, MVP 범위 | PM |
| 01_Development_Plan.md | 개발 계획(안) 전체 | PM |
| 02_API_Spec.md | API 명세서 | PM |
| 03_Feature_Spec.md | 기능명세서 | TL/QA/PM 종합 |
| 04_DB_Model.md | DB 모델 설계표 | TL |
| 05_Screen_Flow.md | 화면 구성표 및 화면 흐름표 | QA&Front |
| 06_Algorithm.md | 매칭 알고리즘, 요금 계산, 상태 변경 기준 | OM |
| 07_Test_Checklist.md | 테스트 체크리스트 | QA&Front |
| 08_Issue_Rules.md | 이슈 관리표 및 오류 공유 규칙 | PM |
| 99_AI_Working_Rules.md | AI 사용 규칙, 금지사항, 레퍼런스 활용 기준 | PM |

## 25-3. AI에게 전달할 기본 지시

AI 개발 도구에 작업을 요청할 때는 먼저 아래 기준을 전달한다.

먼저 프로젝트 루트의 _AI_Context 폴더를 확인하라.

특히 00_Project_Brief.md, 01_Development_Plan.md, 02_API_Spec.md, 04_DB_Model.md, 99_AI_Working_Rules.md를 우선 참고하라.

이 프로젝트는 React + FastAPI + SQLite 구조이다.

기술 스택을 바꾸지 마라.

백엔드 없는 프론트 단독 구현을 하지 마라.

사용자, 파티, 참여자, 채팅 데이터는 SQLite에 저장한다.

localStorage는 로그인 토큰 저장 외에는 사용하지 않는다.

API 명세서와 DB 모델을 기준으로 구현하라.

## 25-4. AI Context 배포 방법

<!-- 표 26 -->
| 단계 | 내용 |
| --- | --- |
| 1 | PM이 기준 문서를 .md 파일로 변환 |
| 2 | Google Drive에 _AI_Context.zip 또는 개별 .md 파일 업로드 |
| 3 | 팀원은 프로젝트 루트에 _AI_Context/ 폴더 생성 |
| 4 | 배포받은 .md 파일을 _AI_Context/에 복사 |
| 5 | git status로 _AI_Context/가 Git 추적 대상이 아닌지 확인 |
| 6 | AI 도구 사용 전 _AI_Context를 먼저 읽도록 지시 |

## 25-5. _AI_Context/ 업로드 금지 기준

_AI_Context 폴더는 GitHub에 업로드하지 않는다.

개발 기준 문서는 팀 내부 로컬 참고용으로 사용한다.

AI 도구는 해당 폴더를 참고해 구현 방향을 맞춘다.

PM이 공식 공유가 필요하다고 판단한 문서만 docs/ 폴더로 별도 정리한다.

# 26. Reference Bank 관리 기준

## 26-1. 목적

_Reference_bank/ 폴더는 개발 시간 단축과 구현 품질 향상을 위해 검증된 오픈소스 프로젝트를 로컬에 보관하는 참고자료 폴더이다.

AI 개발 도구는 이 폴더를 적극적으로 참고할 수 있다.

단, 레퍼런스는 우리 프로젝트의 기술 스택과 구조를 바꾸기 위한 자료가 아니라, 구현 방식·폴더 구조·API 흐름·인증 처리·WebSocket 처리·관리자 화면 구성·라이드셰어 기능 흐름을 참고하기 위한 자료이다.

## 26-2. Reference Bank 기본 원칙

1. _Reference_bank 폴더는 GitHub에 업로드하지 않는다.

2. 레퍼런스는 적극적으로 참고한다.

3. 우리 프로젝트의 기술 스택은 React + FastAPI + SQLite로 고정한다.

4. 레퍼런스의 Docker, PostgreSQL, Redis, MongoDB, TypeScript, Tailwind, OAuth, 결제, GPS 추적, 운전자 관리 기능을 임의로 도입하지 않는다.

5. MIT 라이선스 레퍼런스를 우선 사용한다.

6. 코드 일부를 가져와 재구성할 수 있으나, 출처와 LICENSE를 반드시 기록한다.

7. 레퍼런스 코드를 그대로 붙여 넣기보다 우리 API 명세서, DB 모델, 폴더 구조에 맞게 변환한다.

8. AI에게 “레퍼런스를 참고하되 우리 프로젝트 기준을 우선하라”고 명확히 지시한다.

## 26-3. Reference Bank 선정 기준

<!-- 표 27 -->
| 기준 | 설명 |
| --- | --- |
| 기술 유사성 | React, FastAPI, WebSocket, JWT, SQLAlchemy 등 우리 프로젝트와 유사한 요소 포함 |
| 활용 가능성 | 인증, API 구조, 채팅, 관리자 화면, 라이드셰어 흐름에 직접 참고 가능 |
| 라이선스 | MIT 등 재사용이 비교적 명확한 오픈소스 우선 |
| 과도한 기능 배제 | 실제 결제, 운전자 관리, GPS 추적, 배포 자동화 등은 참고만 하고 도입하지 않음 |
| AI 활용성 | Codex/Claude가 폴더를 읽고 구조를 참고하기 쉬운 프로젝트 우선 |

## 26-4. Reference Bank 후보 목록

<!-- 표 28 -->
| 우선순위 | 폴더명 | 레퍼런스 | 참고할 부분 | 활용 범위 |
| --- | --- | --- | --- | --- |
| 1 | fastapi_full_stack_template | fastapi/full-stack-fastapi-template | FastAPI + React 풀스택 구조, 인증, 환경변수, API 문서, 프로젝트 분리 구조 | 구조 적극 참고, 과한 Docker/PostgreSQL/TypeScript 요소는 제외 |
| 2 | fastapi_react_boilerplate | Nowado/fastapi-react-boilerplate | FastAPI backend, React frontend, SQLAlchemy setup, ProtectedRoutes | 백엔드/프론트 분리 구조와 인증 흐름 참고 |
| 3 | fastapi_react_ws_chat | YuriiMotov/fastapi-react-ws-chat | React + FastAPI 채팅, 메시지 목록, 메시지 송수신, 채팅방 구조 | WebSocket 채팅 구조 적극 참고 |
| 4 | fastapi_react_websocket_app | GabrielReira/fastapi-react-websocket-app | FastAPI + React + WebSocket 기본 앱 구조, backend/frontend 분리 | 단순 WebSocket 구조 참고 |
| 5 | simple_chat_fastapi | mikhailofff/simple-chat-fastapi | JWT 인증, WebSocket, 실시간 메시징, 온라인 유저 표시, 시스템 메시지 | 채팅 UX와 WebSocket 처리 참고 |
| 6 | ridepool_strps | H0NEYP0T-466/RidePool-STRPS | 라이드풀링, 매칭, 관리자 대시보드, JWT, 실시간 업데이트, 요금 계산 아이디어 | 서비스 흐름·매칭·관리자 화면 참고, GPS/운전자/결제는 제외 |
| 7 | layoutstudio_reference | 사용자 제공 LayoutStudio 프로젝트 | 랜딩 페이지 구성, 서비스 소개 섹션, 기능 안내, 사용 방법, 개발자 정보, 제품형 웹앱 톤 | 랜딩 페이지 구조와 UX 흐름 참고. 기술 스택은 우리 프로젝트 기준 유지 |

FastAPI 공식 Full Stack FastAPI Template은 FastAPI 공식 문서에서도 초기 설정, 보안, 데이터베이스, 일부 API 엔드포인트를 포함한 시작점으로 설명되어 있어 풀스택 구조 참고 가치가 높다. 해당 GitHub 저장소도 FastAPI와 React 기반 풀스택 템플릿이며 MIT 라이선스가 확인된다.

Nowado의 fastapi-react-boilerplate는 FastAPI 백엔드, React 프론트엔드, SQLAlchemy setup으로 구성된 minimal boilerplate이며 MIT license가 표시되어 있다.

YuriiMotov의 fastapi-react-ws-chat은 FastAPI+ReactJS 채팅 프로젝트로, 채팅 목록 요청, 사용자 추가, 이전 메시지 로딩, 메시지 송수신 기능이 구현되어 있고 MIT license가 표시되어 있다.

GabrielReira의 fastapi-react-websocket-app은 backend/frontend 폴더를 가진 FastAPI, React, WebSocket 예제이며 MIT license가 표시되어 있다.

mikhailofff의 simple-chat-fastapi는 React, FastAPI, WebSocket 기반 실시간 채팅 프로젝트이며 JWT 인증, SQLAlchemy, 실시간 메시징 구조를 포함하고 MIT license가 표시되어 있다. 단, PostgreSQL, Redis, Alembic 등은 우리 프로젝트에 그대로 도입하지 않는다.

RidePool-STRPS는 React, TypeScript, FastAPI, MongoDB, WebSocket, JWT 인증, ride matching, dynamic fare calculation, admin dashboard 등을 포함한 ride-pooling 레퍼런스이며 MIT license가 표시되어 있다. 단, MongoDB, GPS tracking, driver role, payment/booking lifecycle은 우리 MVP에 도입하지 않는다.

## 26-5. Reference Bank 설치 명령어

아래 명령어는 프로젝트 루트에서 실행한다.

Windows PowerShell 또는 macOS 터미널 공통 기준:

mkdir _Reference_bank

cd _Reference_bank

레퍼런스 프로젝트 다운로드:

git clone https://github.com/fastapi/full-stack-fastapi-template.git fastapi_full_stack_template

git clone https://github.com/Nowado/fastapi-react-boilerplate.git fastapi_react_boilerplate

git clone https://github.com/YuriiMotov/fastapi-react-ws-chat.git fastapi_react_ws_chat

git clone https://github.com/GabrielReira/fastapi-react-websocket-app.git fastapi_react_websocket_app

git clone https://github.com/mikhailofff/simple-chat-fastapi.git simple_chat_fastapi

git clone https://github.com/H0NEYP0T-466/RidePool-STRPS.git ridepool_strps

git clone https://github.com/yong6330/Layoutstudio.git layoutstudio_reference

프로젝트 루트로 복귀:

cd ..

설치 후 확인:

dir

macOS:

ls

## 26-6. Reference Bank 활용 범위

<!-- 표 29 -->
| 레퍼런스 | 적극 참고할 것 | 그대로 가져오면 안 되는 것 |
| --- | --- | --- |
| full-stack-fastapi-template | 백엔드/프론트 분리 구조, 환경변수 관리, 인증 흐름, API 문서화 흐름 | Docker Compose, PostgreSQL, SQLModel, 배포 구조 전체 |
| fastapi-react-boilerplate | FastAPI + React + SQLAlchemy 최소 구조, ProtectedRoutes 흐름 | Docker/Traefik/Let’s Encrypt/production 설정 |
| fastapi-react-ws-chat | 채팅 목록, 메시지 로딩, 메시지 송수신 흐름 | TypeScript 구조를 그대로 도입하는 것 |
| fastapi-react-websocket-app | 단순 WebSocket 연결, backend/frontend 분리 | Docker 기반 실행을 필수화하는 것 |
| simple-chat-fastapi | JWT 인증, WebSocket 메시징, 시스템 메시지, 온라인 유저 처리 | PostgreSQL, Redis, rate limit, Alembic 강제 도입 |
| ridepool_strps | ride matching 개념, fare calculation 아이디어, admin dashboard 정보 구조 | MongoDB, GPS tracking, driver role, booking/payment lifecycle, Socket.IO 구조 전면 도입 |
| layoutstudio_reference | 랜딩 페이지 섹션 구성, 서비스 설명 구조, 사용 방법 안내, 프로젝트 소개 톤, 공통 헤더·푸터 구성 | LayoutStudio 고유 브랜드, 서비스명, 공간 배치 기능, 프로젝트별 고유 문구 |

## 26-7. 레퍼런스 코드 활용 기준

1. MIT 라이선스 레퍼런스는 코드 구조와 일부 구현 패턴을 적극 참고할 수 있다.

2. 코드 일부를 가져와 사용할 경우 해당 레퍼런스의 LICENSE 파일을 _Reference_bank에 보관한다.

3. 실제 프로젝트 코드에 직접 복사한 부분이 있다면 PR 설명에 참고 레퍼런스를 적는다.

4. 파일 단위로 크게 가져오는 경우 해당 파일 상단 또는 docs/reference-usage.md에 출처를 기록한다.

5. 레퍼런스 코드는 우리 프로젝트의 API 명세서, DB 구조, 폴더 구조에 맞게 수정한다.

6. 레퍼런스의 기술 스택이 우리 기준과 다르면 구현 아이디어만 가져오고 기술은 변경하지 않는다.

7. 레퍼런스 코드가 우리 프로젝트와 충돌하면 우리 개발 계획(안), API 명세서, DB 모델을 우선한다.

## 26-8. Reference Bank README 작성 기준

_Reference_bank/README.md 파일에는 아래 내용을 작성한다.

# Reference Bank

이 폴더는 Mirae Mobility 프로젝트 개발 중 AI 도구가 참고할 수 있는 오픈소스 레퍼런스 모음이다.

사용 목적:

- FastAPI + React 프로젝트 구조 참고

- JWT 인증 흐름 참고

- SQLAlchemy 모델 구성 참고

- WebSocket 채팅 구조 참고

- 라이드셰어 서비스 화면·기능 흐름 참고

- 관리자 대시보드 구성 참고

- 매칭 및 요금 계산 아이디어 참고

사용 원칙:

- React + FastAPI + SQLite 기준을 유지한다.

- 레퍼런스의 기술 스택을 그대로 도입하지 않는다.

- 레퍼런스의 Docker, PostgreSQL, Redis, MongoDB, GPS, 결제, 운전자 기능은 참고만 한다.

- MIT 라이선스 레퍼런스를 우선 활용한다.

- 코드 일부를 활용할 경우 출처와 LICENSE를 기록한다.

- 이 폴더는 GitHub에 업로드하지 않는다.

## 26-9. AI에게 Reference Bank를 사용하게 하는 지시문

AI 개발 도구에 기능 구현을 요청할 때 아래 문구를 함께 전달한다.

프로젝트 루트의 _Reference_bank 폴더를 적극적으로 참고하라.

특히 FastAPI + React 구조, JWT 인증, WebSocket 채팅, 라이드셰어 매칭 흐름, 관리자 대시보드 구조를 참고하라.

단, 우리 프로젝트의 기준은 React + FastAPI + SQLite이다.

레퍼런스의 Docker, PostgreSQL, Redis, MongoDB, TypeScript, Tailwind, OAuth, GPS 추적, 실제 결제, 운전자 기능을 임의로 도입하지 마라.

레퍼런스 코드를 그대로 붙여 넣지 말고, 우리 API 명세서와 DB 모델에 맞게 재구성하라.

필요한 구현 패턴은 적극적으로 가져오되, 폴더 구조와 기술 스택은 Mirae Mobility 개발 계획(안)을 우선하라.

## 26-10. Reference Bank 사용 후 점검표

□ 어떤 레퍼런스를 참고했는가

□ 해당 레퍼런스의 LICENSE가 확인되었는가

□ 우리 프로젝트 기술 스택을 변경하지 않았는가

□ SQLite 기준이 유지되었는가

□ API 명세서와 Endpoint가 일치하는가

□ DB 모델과 컬럼명이 일치하는가

□ 레퍼런스의 과한 기능을 그대로 가져오지 않았는가

□ 복사한 코드가 있다면 출처를 기록했는가

□ PR 설명에 참고 레퍼런스를 적었는가

□ _Reference_bank 폴더가 GitHub에 올라가지 않았는가

# 27. .gitignore 관리 기준

## 27-1. 목적

.gitignore는 GitHub에 올라가면 안 되는 파일과 폴더를 막기 위한 기준이다.

본 프로젝트에서는 환경변수, DB 파일, 로컬 AI 문서, 오픈소스 레퍼런스 뱅크가 GitHub에 올라가지 않도록 관리한다.

## 27-2. .gitignore에 반드시 포함할 항목

# Dependencies

node_modules/

frontend/node_modules/

# Build outputs

dist/

frontend/dist/

.vite/

# Python

__pycache__/

*.py[cod]

*.pyo

*.pyd

.venv/

venv/

env/

# Environment variables

.env

.env.*

!.env.example

frontend/.env

backend/.env

# Local database

*.db

*.sqlite

*.sqlite3

backend/eagle_taxi.db

# Local AI context docs

_AI_Context/

# Local reference bank

_Reference_bank/

# OS files

.DS_Store

Thumbs.db

# Logs

*.log

logs/

npm-debug.log*

yarn-debug.log*

## 27-3. .gitignore 확인 방법

git status

확인 기준:

□ _AI_Context/가 표시되지 않는가

□ _Reference_bank/가 표시되지 않는가

□ .env가 표시되지 않는가

□ backend/eagle_taxi.db가 표시되지 않는가

□ node_modules/가 표시되지 않는가

만약 표시된다면 .gitignore 반영이 잘못된 것이다.

# 28. 환경변수 관리 기준

## 28-1. 원칙

<!-- 표 30 -->
| 항목 | 기준 |
| --- | --- |
| .env | 실제 개발 환경변수 파일 |
| .env.example | 팀원 공유용 예시 파일 |
| GitHub 업로드 | .env 업로드 금지 |
| API Key | 코드에 직접 작성 금지 |
| Kakao API Key | PM이 관리 |
| SECRET_KEY | 백엔드 .env에 저장 |
| ADMIN_EMAILS | 관리자 계정 이메일 목록 |

## 28-2. frontend/.env 예시

VITE_API_BASE_URL=/api

VITE_WS_BASE_URL=

VITE_KAKAO_MAP_API_KEY=your-kakao-map-javascript-key

## 28-3. backend/.env 예시

DATABASE_URL=sqlite:///./eagle_taxi.db

JWT_SECRET_KEY=change-this-secret-key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_EMAILS=admin@yonsei.ac.kr

KAKAO_MOBILITY_REST_API_KEY=your-kakao-mobility-rest-api-key

주의사항:

VITE_KAKAO_MAP_API_KEY는 프론트엔드에서 사용하는 JavaScript Key이다.

KAKAO_MOBILITY_REST_API_KEY는 백엔드에서만 사용하는 REST API Key이다.

REST API Key를 프론트 코드에 노출하지 않는다.

.env 파일은 GitHub에 업로드하지 않는다.

.env.example에는 실제 키가 아니라 예시값만 작성한다.

# 29. 프론트엔드 환경 세팅

## 29-1. frontend 폴더 이동

cd frontend

## 29-2. React + Vite 프로젝트 생성

frontend 폴더가 비어 있을 경우:

npm create vite@latest . -- --template react

## 29-3. 패키지 설치

npm install

라우터 설치:

npm install react-router-dom

## 29-4. 개발 서버 실행

npm run dev

정상 실행 시:

Local:   http://localhost:5173/

Network: http://내IP주소:5173/

접속 주소:

http://localhost:5173

# 30. Vite 설정 기준

frontend/vite.config.js는 아래 기준으로 설정한다.

import { defineConfig } from 'vite'

import react from '@vitejs/plugin-react'

export default defineConfig({

plugins: [react()],

server: {

host: '0.0.0.0',

port: 5173,

proxy: {

'/api': {

target: 'http://localhost:8000',

changeOrigin: true

},

'/ws': {

target: 'ws://localhost:8000',

ws: true

}

}

}

})

<!-- 표 31 -->
| 설정 | 의미 |
| --- | --- |
| host: 0.0.0.0 | 같은 Wi-Fi 기기에서도 접속 가능 |
| port: 5173 | 프론트엔드 포트 고정 |
| /api proxy | 프론트에서 /api로 요청하면 백엔드 8000번으로 전달 |
| /ws proxy | WebSocket 요청을 백엔드로 전달 |

# 31. 백엔드 환경 세팅

## 31-1. backend 폴더 이동

cd backend

## 31-2. Python 가상환경 생성

Windows:

python -m venv .venv

또는:

py -m venv .venv

macOS:

python3 -m venv .venv

## 31-3. 가상환경 활성화

Windows PowerShell:

.venv\Scripts\Activate.ps1

Windows 명령 프롬프트:

.venv\Scripts\activate

macOS:

source .venv/bin/activate

활성화되면 터미널 앞에 (.venv)가 표시된다.

## 31-4. 패키지 설치

pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose[cryptography] python-dotenv websockets httpx

설치 목록 저장:

pip freeze > requirements.txt

다른 팀원이 설치할 때:

pip install -r requirements.txt

## 31-5. 백엔드 서버 실행

Windows / macOS 공통:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

정상 접속 주소:

http://localhost:8000

API 문서 주소:

http://localhost:8000/docs

# 32. SQLite 데이터베이스 설계

본 프로젝트는 SQLite를 기준으로 데이터를 저장한다.

## 32-1. 테이블 목록

<!-- 표 32 -->
| 테이블 | 목적 |
| --- | --- |
| users | 사용자 정보 저장 |
| parties | 택시 파티 정보 저장 |
| party_members | 파티 참여자 정보 저장 |
| messages | 파티별 채팅 메시지 저장 |

## 32-2. users 테이블

<!-- 표 33 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 사용자 고유 ID |
| email | String, Unique | 로그인 이메일 |
| password_hash | String | 해시 처리된 비밀번호 |
| name | String | 이름 또는 닉네임 |
| gender | String | male / female. none은 화면 기본값으로만 사용하고 DB에는 저장하지 않음 |
| role | String | user / admin |
| created_at | DateTime | 가입 시간 |
| is_active | Boolean | 사용자 활성 상태, 기본 true |

## 32-3. parties 테이블

<!-- 표 34 -->
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
| estimated_fare | Integer | Kakao Mobility API로 산정한 예상 택시비 |
| toll_fare | Integer | Kakao Mobility API로 산정한 예상 통행료 |
| distance_meters | Integer | Kakao Mobility API로 산정한 예상 이동 거리 |
| duration_seconds | Integer | Kakao Mobility API로 산정한 예상 이동 시간 |
| fare_source | String | 요금 산정 출처, kakao_mobility |
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

estimated_fare는 사용자가 입력한 값이 아니라 Kakao Mobility API 응답값을 저장한다.

실제 택시 호출 결과나 실제 결제 결과는 저장하지 않는다.

## 32-4. party_members 테이블

<!-- 표 35 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 참여 정보 ID |
| party_id | Integer, FK | 파티 ID |
| user_id | Integer, FK | 사용자 ID |
| joined_at | DateTime | 참여 시간 |

## 32-5. messages 테이블

<!-- 표 36 -->
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | Integer, PK | 메시지 ID |
| party_id | Integer, FK | 파티 ID |
| user_id | Integer, FK | 작성자 ID |
| content | Text | 메시지 내용 |
| created_at | DateTime | 작성 시간 |

## 33. 파티 상태값 기준

<!-- 표 37 -->
| DB 값 | 화면 표시 | 의미 |
| --- | --- | --- |
| recruiting | 모집 중 | 참여 가능 |
| matched | 매칭 완료 | 최대 인원 도달 |
| canceled | 취소 | 생성자 또는 관리자가 파티를 취소함 |
| expired | 출발시간 만료 | 모집 중 상태에서 출발 시간이 지나 더 이상 참여 불가 |
| completed | 이용 완료 | 매칭 완료된 파티의 출발 시간이 지남 |

상태 변경 기준:

current_members = max_members이면 status = matched로 변경한다.

생성자가 파티를 취소하면 status = canceled로 변경한다.

현재 시간이 departure_time을 지났고 status가 recruiting이면 expired로 처리한다.

파티 참여 취소로 current_members가 max_members보다 작아질 경우 status를 recruiting으로 되돌릴 수 있다.

단, canceled 상태는 자동 복구하지 않는다.

matched 상태는 자동 expired 처리 대상에서 제외하고, 현재 시간이 departure_time을 지났고 status가 matched이면 completed로 처리한다.

# 34. 주요 장소 데이터 기준

초기 지도 기능은 사전 등록 장소 목록 방식이 아니라 Kakao Maps JavaScript API의 장소 검색 기능을 활용한다.

기준:

- 사용자는 출발지와 도착지를 직접 입력한다.

- 프론트엔드는 Kakao Maps Places keywordSearch로 장소명을 검색한다.

- 사용자는 검색 결과 중 하나를 선택한다.

- 선택한 장소명, 위도, 경도를 파티 생성 API에 전달한다.

- 백엔드는 선택된 장소명과 좌표를 parties 테이블에 저장한다.

- 실시간 위치 추적과 실제 경로 탐색은 구현하지 않는다.

# 35. API 개발 기준

## 35-1. 공통 API 원칙

<!-- 표 38 -->
| 원칙 | 내용 |
| --- | --- |
| 기본 prefix | /api |
| 인증 방식 | Authorization Header Bearer Token |
| 응답 형식 | JSON |
| DB 접근 | FastAPI에서 SQLAlchemy로 처리 |
| 프론트 역할 | API 호출 후 화면 표시 |
| React DB 직접 접근 | 금지 |
| API 변경 | API 명세서 수정 후 반영 |

## 35-2. Auth API

<!-- 표 39 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 회원가입 | POST | /api/auth/register |
| 로그인 | POST | /api/auth/login |
| 내 정보 조회 | GET | /api/auth/me |
| 로그아웃 | 없음 | 프론트 처리 |

## 35-3. Fare API

<!-- 표 40 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 예상 택시비 자동 산정 | GET | /api/fares/estimate |

기준:

GET /api/fares/estimate는 파티 생성 화면에서 예상 택시비를 미리 확인하기 위한 API이다.

파티 생성 시에는 POST /api/parties 내부에서 동일한 요금 산정 로직을 실행한다.

사용자는 estimated_fare를 직접 입력하지 않는다.

## 35-4. Party API

<!-- 표 41 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 파티 생성 | POST | /api/parties |
| 파티 목록 조회 | GET | /api/parties |
| 파티 상세 조회 | GET | /api/parties/{party_id} |
| 파티 검색 | GET | /api/parties/search |
| 유사 파티 추천 | GET | /api/parties/recommend |
| 파티 참여 | POST | /api/parties/{party_id}/join |
| 파티 참여 취소 | DELETE | /api/parties/{party_id}/leave |
| 파티 취소 | PATCH | /api/parties/{party_id}/cancel |
| 내 파티 목록 조회 | GET | /api/my/parties |

## 35-5. Message API

<!-- 표 42 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 메시지 목록 조회 | GET | /api/parties/{party_id}/messages |
| WebSocket 연결 | WS | /ws/parties/{party_id}?token=<access_token> |

## 35-6. Static / Policy 화면 기준

<!-- 표 43 -->
| 화면 | URL Path | 처리 방식 |
| --- | --- | --- |
| 랜딩 | / | 프론트 정적 화면 |
| 안전 안내 | /guide | 프론트 정적 화면, 원본 문서는 docs/guide.md로 관리 |
| 이용약관 안내 | /terms | 프론트 정적 화면, 원본 문서는 docs/terms.md로 관리 |
| 개인정보 처리방침 안내 | /privacy | 프론트 정적 화면, 원본 문서는 docs/privacy.md로 관리 |
| 신고 안내 모달 | 파티 상세 내부 | API 없이 안내 모달 또는 /guide 연결 |
| 결제수단 버튼 | 설정 화면 내부 | 실제 결제 기능 없이 안내 모달 표시 |
| 개발팀 정보 | 랜딩 및 Footer | 연세대학교 미래캠퍼스 컴퓨팅사고(YHX1001.07-00) 프로젝트 6팀 Mirae Mobility 정보 표시 |

## 35-7. Admin API

<!-- 표 44 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 관리자 통계 조회 | GET | /api/admin/stats |
| 최근 파티 조회 | GET | /api/admin/parties/recent |
| 사용자 목록 조회 | GET | /api/admin/users |
| 관리자 파티 목록 조회 | GET | /api/admin/parties |
| 관리자 파티 상태 변경 | PATCH | /api/admin/parties/{party_id}/status |
| 관리자 사용자 권한 변경 | PATCH | /api/admin/users/{user_id}/role |
| 관리자 사용자 활성 상태 변경 | PATCH | /api/admin/users/{user_id}/status |
| 최근 메시지 조회 | GET | /api/admin/messages/recent |
| 사용자 상세 조회 | GET | /api/admin/users/{user_id} |
| 파티 상세 조회 | GET | /api/admin/parties/{party_id} |

## 35-8. API 계약 변경 기준

프론트엔드와 백엔드는 API 명세서를 기준으로 연결한다.

API 구조는 한쪽 담당자가 임의로 변경하지 않는다.

<!-- 표 45 -->
| 변경 상황 | 처리 기준 |
| --- | --- |
| Endpoint 변경 필요 | PM, TL, QA&Front 확인 후 변경 |
| 요청 데이터 변경 필요 | API 명세서 먼저 수정 |
| 응답 데이터 변경 필요 | 프론트 화면 영향 확인 후 수정 |
| 인증 방식 변경 필요 | PM/TL 확인 전 변경 금지 |
| DB 컬럼 추가 필요 | TL이 PM에게 공유 후 반영 |
| 화면에 필요한 데이터 누락 | QA&Front가 TL에게 요청 |
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

# 36. API 응답 형식 기준

프론트엔드와 백엔드가 서로 다른 형식을 예상하면 연결이 실패한다.

따라서 주요 API는 아래 응답 형식을 기준으로 맞춘다.

## 36-1. 로그인 응답 예시

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

## 36-2. 파티 상세 응답 예시

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

"fare_source": "kakao_mobility",

"gender_rule": "any",

"party_gender": null,

"status": "recruiting",

"members": [

{

"id": 1,

"name": "테스트",

"gender": "male"

}

]

}

## 36-3. 파티 목록 응답 예시

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

"fare_source": "kakao_mobility",

"gender_rule": "any",

"status": "recruiting"

}

],

"total": 1,

"page": 1,

"limit": 20

}

# 37. 백엔드 개발 기준

## 37-1. FastAPI 기본 서버

목표:

백엔드 서버가 정상 실행되고 /docs 접속이 가능해야 함

완료 기준:

http://localhost:8000/docs 접속 가능

## 37-2. SQLite 연결

목표:

SQLAlchemy로 SQLite DB 파일을 생성하고 연결한다.

완료 기준:

backend 폴더에 eagle_taxi.db 생성

## 37-3. 사용자 인증 구현

구현 기능:

<!-- 표 46 -->
| 기능 | 내용 |
| --- | --- |
| 회원가입 | 이메일, 비밀번호, 이름, 성별 저장 |
| 비밀번호 해시 | passlib로 비밀번호 저장 |
| 로그인 | 이메일·비밀번호 검증 |
| JWT 발급 | access_token 반환 |
| 내 정보 조회 | 로그인 사용자 정보 반환 |
| 로그아웃 | 프론트에서 토큰 삭제 |

완료 기준:

/api/auth/register

/api/auth/login

/api/auth/me

위 3개 API가 /docs에서 테스트 가능해야 한다.

## 37-4. 파티 API 구현

구현 기능:

<!-- 표 47 -->
| 기능 | 내용 |
| --- | --- |
| 파티 생성 | 출발지, 도착지, 출발 시간, 만남 장소, 최대 인원, 성별 매칭 옵션을 입력받고, 예상 택시비는 Kakao Mobility API로 자동 산정 |
| 파티 목록 | 모집 중인 파티를 기본 조회하고, 필요 시 matched / canceled / expired / completed 상태 필터 제공 |
| 파티 상세 | 특정 파티의 장소, 좌표, 만남 장소, 참여자, 예상 택시비, 1인 예상 요금, 상태 조회 |
| 파티 검색 | start_place, end_place, departure_time, status 기준 조건 검색 |
| 유사 파티 추천 | 출발지, 도착지, 출발 시간 기준 match_score 계산 후 추천 |
| 파티 참여 | 참여 가능 여부 판단 후 참여자 추가, 요금 재계산, 상태 변경 |
| 파티 참여 취소 | 참여자 제거, current_members 재계산, per_person_fare 재계산 |
| 파티 취소 | 생성자가 파티 상태를 canceled로 변경 |
| 내 파티 조회 | 생성한 파티와 참여한 파티를 구분 조회하고 recruiting / matched / canceled / expired / completed 상태를 표시 |

완료 기준:

파티 생성 후 목록과 상세 API에서 조회 가능해야 한다.

사용자는 예상 택시비를 직접 입력하지 않아야 한다.

파티 생성 시 estimated_fare, toll_fare, distance_meters, duration_seconds가 자동 산정되어야 한다.

파티 참여 후 current_members, per_person_fare, status가 갱신되어야 한다.

유사 파티 추천은 match_score 높은 순서로 반환되어야 한다.

## 37-5. 파티 참여 로직

구현 순서:

로그인 사용자 확인

party_id에 해당하는 파티 존재 여부 확인

파티 상태가 recruiting인지 확인

departure_time이 현재 시간 이후인지 확인

이미 참여한 사용자인지 확인

현재 인원이 최대 인원보다 작은지 확인

gender_rule이 same_gender이면 사용자 gender와 party_gender 비교

참여 가능하면 party_members에 참여자 저장

참여 후 current_members 재계산

저장된 estimated_fare 기준으로 per_person_fare 재계산

current_members=max_members이면 status=matched 변경

result_code, can_join, reason, 갱신된 파티 정보를 반환

참여 가능 여부 결과 코드:

<!-- 표 48 -->
| result_code | can_join | reason |
| --- | --- | --- |
| 200 | true | 파티에 참여하였습니다. |
| 401 | false | 로그인이 필요합니다. |
| 404 | false | 존재하지 않는 파티입니다. |
| 409 | false | 이미 참여한 파티입니다. |
| 409 | false | 같은 시간대에 이미 참여 중인 파티가 있습니다. |
| 409 | false | 최대 인원에 도달한 파티입니다. |
| 409 | false | 매칭 완료된 파티에는 참여할 수 없습니다. |
| 409 | false | 취소된 파티에는 참여할 수 없습니다. |
| 409 | false | 출발 시간이 지난 파티입니다. |
| 409 | false | 이용 완료된 파티에는 참여할 수 없습니다. |
| 403 | false | 성별 매칭 조건에 맞지 않습니다. |

완료 기준:

참여 버튼 클릭 후 현재 인원, 1인 요금, 상태가 변경되어야 한다.

참여 불가 상황에서는 result_code와 reason을 기준으로 안내 문구를 표시할 수 있어야 한다.

same_gender 파티는 성별 조건을 통과한 사용자만 참여할 수 있어야 한다.

## 37-6. WebSocket 채팅

기본 목표:

FastAPI WebSocket으로 파티별 실시간 채팅 구현

구현 기능:

<!-- 표 49 -->
| 기능 | 내용 |
| --- | --- |
| 파티별 채팅방 | party_id 기준 WebSocket 연결 |
| WebSocket 인증 | query token 방식 |
| 메시지 전송 | 참여자가 메시지 입력 |
| 메시지 저장 | messages 테이블 저장 |
| 메시지 표시 | 같은 파티 참여자에게 메시지 표시 |

예외 기준:

WebSocket 구현이 전체 개발 일정을 막을 정도로 불안정할 경우, PM 승인 후 메시지 저장형 채팅으로 임시 축소할 수 있다.

단, 기본 목표는 WebSocket 실시간 채팅 구현이다.

## 37-7. Admin API

구현 기능:

<!-- 표 50 -->
| 기능 | Method | Endpoint |
| --- | --- | --- |
| 관리자 통계 조회 | GET | /api/admin/stats |
| 최근 파티 조회 | GET | /api/admin/parties/recent |
| 사용자 목록 조회 | GET | /api/admin/users |
| 관리자 파티 목록 조회 | GET | /api/admin/parties |
| 관리자 파티 상태 변경 | PATCH | /api/admin/parties/{party_id}/status |
| 관리자 사용자 권한 변경 | PATCH | /api/admin/users/{user_id}/role |
| 관리자 사용자 활성 상태 변경 | PATCH | /api/admin/users/{user_id}/status |
| 최근 메시지 조회 | GET | /api/admin/messages/recent |
| 사용자 상세 조회 | GET | /api/admin/users/{user_id} |
| 파티 상세 조회 | GET | /api/admin/parties/{party_id} |

완료 기준:

관리자 페이지는 단순 읽기 전용이 아니라 기본 관리 기능을 포함한다.

관리자 페이지는 통계 차트, 사용자 목록, 파티 목록, 파티 상태 변경, 사용자 권한 변경, 사용자 활성 상태 변경을 제공한다.

관리자 기능은 admin 권한 사용자만 접근할 수 있다.

실제 결제, 실제 택시 호출, 신고 처리 프로세스는 관리자 페이지에서도 구현하지 않는다.

## 관리자 페이지 단계별 구현 기준

<!-- 표 51 -->
| 단계 | 구현 범위 | 기준 |
| --- | --- | --- |
| 관리자 1단계 | 통계 카드, 최근 파티, 사용자 목록 | Could 범위의 우선 구현 |
| 관리자 2단계 | 파티 목록, 파티 상세, 사용자 상세 | 데이터 점검 확장 |
| 관리자 3단계 | 파티 상태 변경, 사용자 권한 변경, 사용자 활성 상태 변경, 최근 메시지 | 시스템 전체 관리 기능 확장 |

# 38. 프론트엔드 개발 기준

프론트엔드 화면은 아래 화면 ID와 URL Path를 기준으로 구현한다.

<!-- 표 52 -->
| 화면 ID | 화면명 | URL Path | 구현 우선순위 |
| --- | --- | --- | --- |
| S-01 | 랜딩 | / | Must |
| S-02 | 회원가입 | /signup | Must |
| S-03 | 로그인 | /login | Must |
| S-04 | 메인 | /main | Must |
| S-05 | 파티 목록·검색 | /parties | Must |
| S-06 | 파티 생성 | /parties/new | Must |
| S-07 | 파티 상세 | /parties/:partyId | Must |
| S-08 | 내 파티 | /my/parties | Target |
| S-09 | 파티 채팅 | /parties/:partyId/chat | Target |
| S-10 | 안전 안내 | /guide | Target |
| S-11 | 계정·설정 | /settings | Target |
| S-12 | 관리자 페이지 | /admin | Could |
| S-13 | 이용약관 안내 | /terms | Target |
| S-14 | 개인정보 처리방침 안내 | /privacy | Target |

## 38-1. React 기본 구조

목표:

React 프로젝트가 정상 실행되어야 함

완료 기준:

http://localhost:5173 접속 가능

## 38-2. 페이지 경로

<!-- 표 53 -->
| 화면 | 경로 |
| --- | --- |
| 홈 | / |
| 회원가입 | /signup |
| 로그인 | /login |
| 파티 목록 | /parties |
| 파티 생성 | /parties/new |
| 파티 상세 | /parties/:partyId |
| 파티 채팅 | /parties/:partyId/chat |
| 안전 안내 | /guide |
| 관리자 페이지 | /admin |
| 메인 | /main |
| 내 파티 | /my/parties |
| 계정·설정 | /settings |
| 이용약관 | /terms |
| 개인정보 처리방침 | /privacy |

## 38-3. 공통 레이아웃

구현 요소:

<!-- 표 54 -->
| 요소 | 내용 |
| --- | --- |
| Header | 로고, 파티 찾기, 파티 만들기, 안전 안내 |
| Layout | 공통 페이지 여백 |
| Button | 공통 버튼 스타일 |
| Card | 파티 카드 UI |
| Form | 입력 폼 스타일 |

## 38-4. 회원가입·로그인 화면

회원가입 입력값:

이메일

비밀번호

이름 또는 닉네임

성별

로그인 입력값:

이메일

비밀번호

완료 기준:

회원가입 후 로그인 가능

로그인 성공 시 토큰 저장

로그인 후 파티 목록 화면 이동

## 38-5. 파티 목록·검색 화면

표시 데이터:

<!-- 표 55 -->
| 항목 | 내용 |
| --- | --- |
| 기본 파티 목록 | GET /api/parties로 모집 중 파티 조회 |
| 조건 검색 | start_place, end_place, departure_time, status 기준 검색 |
| 유사 추천 | GET /api/parties/recommend로 match_score 높은 순서 표시 |
| 파티 카드 | 출발지, 도착지, 출발 시간, 만남 장소, 현재/최대 인원, 1인 예상 요금, 상태, 성별 매칭 기준 |
| 새 파티 생성 | 검색·추천 결과가 없거나 마음에 드는 파티가 없을 경우 파티 생성 화면으로 이동 |

완료 기준:

기본 모집 중 파티 목록이 표시되어야 한다.

사용자가 출발지, 도착지, 출발 시간을 입력해 조건 검색을 할 수 있어야 한다.

유사 파티 추천 결과가 match_score 높은 순서로 표시되어야 한다.

파티 카드에서 상세 화면으로 이동할 수 있어야 한다.

검색 또는 추천 조건을 유지한 채 파티 생성 화면으로 이동할 수 있어야 한다.

## 38-6. 파티 생성 화면

## 38-6. 파티 생성 화면

입력값:

출발지

도착지

희망 출발 시간

만남 장소

만남 안내

최대 인원

성별 매칭 옵션

자동 처리:

Kakao Places 검색으로 출발지·도착지 좌표 선택

출발지·도착지·희망 출발 시간이 모두 선택되면 예상 택시비 자동 산정

현재 인원 기준 1인 예상 요금 자동 계산

메인 또는 파티 목록에서 입력한 검색 조건이 있으면 파티 생성 화면에 기본값으로 유지

표시 데이터:

전체 예상 택시비

예상 통행료

예상 이동 거리

예상 이동 시간

1인 예상 요금

완료 기준:

사용자가 예상 요금을 직접 입력하지 않아도 파티가 생성되어야 함

예상 택시비와 1인 예상 요금은 자동으로 갱신되어야 함

파티 생성 후 파티 상세 화면으로 이동해야 함

과거 시간 선택 시 생성이 차단되어야 함

최대 인원은 2~4명 기준으로 제한되어야 함

예상 택시비 산정 실패 시 파티 생성이 차단되어야 함

## 38-7. 파티 상세 화면

표시 항목:

출발지

도착지

지도

출발 시간

만남 장소

만남 안내

현재 인원

최대 인원

전체 예상 택시비

예상 통행료

예상 이동 거리

예상 이동 시간

1인 예상 요금

성별 매칭 기준

상태

참여자 목록

참여하기 버튼

참여 취소 버튼

파티 취소 버튼

채팅하기 버튼

신고하기 버튼

버튼 표시 기준:

<!-- 표 56 -->
| 사용자 상태 | 표시 버튼 |
| --- | --- |
| 미참여자 | 참여하기, 신고하기 |
| 참여자 | 참여 취소, 채팅하기, 신고하기 |
| 생성자 | 파티 취소, 채팅하기, 신고하기 |
| matched | 채팅하기, 신고하기 |
| canceled | 버튼 비활성, 신고하기 |
| expired | 버튼 비활성, 신고하기 |
| completed | 채팅 기록 보기 또는 목록으로 돌아가기, 신고하기 |

완료 기준:

참여하기 클릭 시 현재 인원과 1인 요금이 갱신되어야 한다.

최대 인원 도달 시 매칭 완료로 표시되어야 한다.

출발 시간이 지난 파티는 출발시간 만료로 표시되어야 한다.

취소된 파티는 취소 상태로 표시되어야 한다.

참여 불가 상황에서는 result_code와 reason 기준으로 안내 문구를 표시할 수 있어야 한다.

신고하기 버튼은 저장 API 없이 안전 안내 또는 신고 준비 중 안내 모달로 연결한다.

## 38-8. 파티 채팅 화면

구현 요소:

메시지 목록

메시지 입력창

보내기 버튼

WebSocket 연결 상태

이전 메시지 조회

완료 기준:

같은 파티에 참여한 사용자끼리 메시지를 주고받을 수 있어야 함

## 38-9. Kakao Map 표시

구현 기준:

파티 상세 화면에서 출발지와 도착지 마커 표시

완료 기준:

Kakao Maps API Key를 사용해 지도 표시

출발지·도착지 마커 표시

## 38-10. 관리자 페이지

경로:

/admin

구현 항목:

사용자 수

전체 파티 수

모집 중 파티 수

매칭 완료 파티 수

취소 파티 수

전체 메시지 수

최근 생성 파티 목록

기준:

관리자 페이지는 frontend 내부 /admin 경로로 구현한다.

기존 admin 폴더는 별도 관리자 앱을 만들지 않는 한 사용하지 않는다.

# 39. 프론트·백엔드 연결 기준

## 39-1. API 호출 기준

프론트엔드는 직접 localhost:8000을 하드코딩하지 않고, 기본적으로 /api 경로를 사용한다.

예시:

fetch('/api/parties')

이유:

발표자 PC의 IP로 접속한 다른 기기에서도 API 요청이 정상 전달되도록 하기 위함

## 39-2. Authorization Header 기준

로그인 이후 인증이 필요한 API 요청에는 JWT 토큰을 포함한다.

예시:

fetch('/api/parties', {

headers: {

Authorization: `Bearer ${token}`

}

})

## 39-3. WebSocket 연결 기준

WebSocket은 현재 접속한 host를 기준으로 연결한다.

const token = localStorage.getItem('access_token')

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'

const socket = new WebSocket(`${protocol}://${window.location.host}/ws/parties/${partyId}?token=${token}`)

장점:

localhost 접속과 같은 Wi-Fi 접속을 모두 처리할 수 있음

## 39-4. 프론트·백엔드 연결 점검표

프론트와 백엔드를 연결할 때 아래 순서로 확인한다.

□ 백엔드 서버가 실행 중인가

□ http://localhost:8000/docs 접속이 가능한가

□ 프론트 서버가 실행 중인가

□ http://localhost:5173 접속이 가능한가

□ vite.config.js에 /api proxy가 설정되어 있는가

□ vite.config.js에 /ws proxy가 설정되어 있는가

□ 프론트 API 호출 경로가 /api로 시작하는가

□ 로그인 후 토큰이 저장되는가

□ 인증 필요한 요청에 Authorization Header가 포함되는가

□ WebSocket 연결에 query token이 포함되는가

□ API 응답 데이터 이름이 프론트에서 기대하는 이름과 같은가

□ 오류 발생 시 콘솔과 백엔드 터미널을 함께 확인했는가

연결 오류 공유 형식:

[연결 오류 공유]

화면:

사용한 API:

입력값:

프론트 콘솔 오류:

백엔드 터미널 오류:

예상 응답:

실제 응답:

# 40. 개발 작업 단위 카드

개발자는 AI 도구를 사용할 때 한 번에 전체 기능을 맡기지 않고, 아래 작업 카드 단위로 요청한다.

## 40-1. 백엔드 작업 카드

<!-- 표 57 -->
| 항목 | 작성 기준 |
| --- | --- |
| 작업 목표 | 이번에 구현할 API 또는 로직 1개 |
| 수정 위치 | backend/app 내부의 특정 파일 |
| 참조 문서 | API 명세서, DB 구조, 알고리즘 문서 |
| 참고 레퍼런스 | _Reference_bank 내 관련 프로젝트 |
| 반드시 지킬 것 | FastAPI + SQLAlchemy + SQLite 유지 |
| 금지할 것 | localStorage, 임시 배열 저장, 프론트 단독 구현 |
| 완료 기준 | /docs에서 API 테스트 성공 |
| GitHub 반영 | commit 후 PR 생성 |

예시:

작업 목표: 회원가입 API 구현

수정 위치: backend/app/models.py, schemas.py, routers/auth.py, auth.py

참조 기준: users 테이블, POST /api/auth/register

참고 레퍼런스: _Reference_bank/fastapi_react_boilerplate

완료 기준: /docs에서 이메일, 비밀번호, 이름, 성별 입력 후 사용자 생성 성공

금지사항: 비밀번호 평문 저장 금지, SQLite 외 저장 금지

## 40-2. 프론트엔드 작업 카드

<!-- 표 58 -->
| 항목 | 작성 기준 |
| --- | --- |
| 작업 목표 | 이번에 구현할 화면 또는 연결 기능 1개 |
| 수정 위치 | frontend/src 내부의 특정 폴더 |
| 참조 문서 | 화면 구성표, 화면 흐름표, API 명세서 |
| 참고 레퍼런스 | _Reference_bank 내 관련 프로젝트 |
| 반드시 지킬 것 | React + API 호출 구조 유지 |
| 금지할 것 | 백엔드 없이 localStorage로만 기능 처리 |
| 완료 기준 | 화면에서 실제 API 연결 확인 |
| GitHub 반영 | commit 후 PR 생성 |

예시:

작업 목표: 파티 생성 화면 구현

수정 위치: frontend/src/pages, frontend/src/api

참조 기준: S-05 파티 생성 화면, POST /api/parties

참고 레퍼런스: _Reference_bank/full-stack-fastapi-template

완료 기준: 입력값 제출 시 백엔드 API로 파티가 생성되고 파티 상세 화면으로 이동

금지사항: 파티 데이터를 localStorage에 저장하지 않음

## 40-3. PM 작업 카드

<!-- 표 59 -->
| 항목 | 작성 기준 |
| --- | --- |
| 작업 목표 | 문서, API 기준, 관리자 페이지, 실행 스크립트 중 1개 |
| 수정 위치 | docs, README, frontend/src/pages/Admin 등 |
| 참조 문서 | 운영 계획, 개발 계획, API 명세서 |
| 참고 레퍼런스 | _Reference_bank 내 관련 프로젝트 |
| 반드시 지킬 것 | 팀 전체 기준과 실제 코드 구조 일치 |
| 완료 기준 | 팀원이 그대로 따라 할 수 있어야 함 |
| GitHub 반영 | docs 또는 admin 브랜치에서 PR 생성 |

# 41. Windows 실행 방식

## 41-1. 1차 실행 방식: 터미널 2개 사용

터미널 1: 백엔드 실행

cd backend

.venv\Scripts\activate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

터미널 2: 프론트엔드 실행

cd frontend

npm run dev

접속 주소:

http://localhost:5173

## 41-2. 2차 실행 방식: run-dev.bat 사용

프로젝트 루트에 run-dev.bat 파일을 생성한다.

@echo off

chcp 65001 >nul

echo =====================================

echo Mirae Mobility - Eagle Taxi Dev Server

echo =====================================

echo.

echo [1] 현재 PC의 IPv4 주소 확인

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (

set IP=%%a

)

set IP=%IP: =%

echo.

echo 접속 주소:

echo Frontend Local: http://localhost:5173

echo Backend Local : http://localhost:8000

echo API Docs      : http://localhost:8000/docs

echo Network URL   : http://%IP%:5173

echo.

echo [2] Backend 서버 실행

start "Eagle Taxi Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [3] Frontend 서버 실행

start "Eagle Taxi Frontend" cmd /k "cd frontend && npm run dev"

echo.

echo 서버 실행 명령을 보냈습니다.

echo 브라우저에서 http://localhost:5173 으로 접속하세요.

echo 같은 Wi-Fi 접속자는 http://%IP%:5173 으로 접속하세요.

pause

# 42. macOS 실행 방식

서버 실행은 macOS에서도 가능해야 한다. PM 또는 발표자 PC가 Mac인 경우 아래 기준을 따른다.

## 42-1. 1차 실행 방식: 터미널 2개 사용

터미널 1: 백엔드 실행

cd backend

source .venv/bin/activate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

터미널 2: 프론트엔드 실행

cd frontend

npm run dev

접속 주소:

http://localhost:5173

## 42-2. Mac IP 확인

ipconfig getifaddr en0

또는 Wi-Fi 환경에 따라 아래 명령어를 사용한다.

ifconfig | grep "inet "

같은 Wi-Fi 접속 주소 예시:

http://Mac의IP주소:5173

## 42-3. 2차 실행 방식: run-dev-mac.sh 사용

프로젝트 루트에 run-dev-mac.sh 파일을 생성한다.

#!/bin/bash

echo "====================================="

echo "Mirae Mobility - Eagle Taxi Dev Server"

echo "====================================="

echo ""

IP=$(ipconfig getifaddr en0)

echo "[1] 접속 주소"

echo "Frontend Local: http://localhost:5173"

echo "Backend Local : http://localhost:8000"

echo "API Docs      : http://localhost:8000/docs"

echo "Network URL   : http://$IP:5173"

echo ""

echo "[2] Backend 서버 실행"

osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"'

echo "[3] Frontend 서버 실행"

osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/frontend && npm run dev"'

echo ""

echo "서버 실행 명령을 보냈습니다."

echo "브라우저에서 http://localhost:5173 으로 접속하세요."

echo "같은 Wi-Fi 접속자는 http://$IP:5173 으로 접속하세요."

실행 권한 부여:

chmod +x run-dev-mac.sh

실행:

./run-dev-mac.sh

# 43. 같은 Wi-Fi 접속 기준

최종 발표 시 발표자 PC에서 프론트엔드와 백엔드 서버를 실행한다.

접속 안내:

1. 발표자 PC와 같은 교내 Wi-Fi에 접속

2. 실행창에 표시된 Network URL 확인

3. 브라우저에 아래 주소 입력

http://발표자IP:5173

예시:

http://192.168.0.15:5173

Windows 방화벽 알림이 뜨면 허용을 선택한다.

# 44. AI 개발 도구 사용 기준

AI 개발 도구는 코드 작성과 수정 과정에서 적극적으로 사용한다.

단, AI가 프로젝트 기준을 벗어나면 즉시 수정한다.

## 44-1. 반드시 고정할 기준

React + FastAPI + SQLite 구조 유지

백엔드 없는 프론트 단독 구현 금지

Streamlit 전환 금지

localStorage 중심 데이터 저장 금지

임시 배열 기반 데이터 저장 금지

사용자, 파티, 참여자, 채팅 데이터는 SQLite 저장

React는 API 호출과 화면 담당

FastAPI는 데이터 처리와 핵심 로직 담당

기존 폴더 구조 유지

API 명세서와 DB 구조 유지

_AI_Context 기준 문서 우선 참고

_Reference_bank 적극 참고

레퍼런스 기술 스택 임의 도입 금지

## 44-2. AI 작업 단위 기준

한 번에 큰 기능을 맡기지 않고 작은 단위로 진행한다.

<!-- 표 60 -->
| 잘못된 요청 | 올바른 요청 |
| --- | --- |
| 전체 백엔드 만들어줘 | 회원가입 API만 구현 |
| 앱 전체 만들어줘 | 파티 생성 화면만 구현 |
| 알아서 구조 잡아줘 | 기존 폴더 구조를 유지하고 parties router만 작성 |
| MVP로 줄여서 만들어줘 | 지정된 Must 기능을 유지하고 해당 기능만 구현 |
| 간단히 localStorage로 해줘 | SQLite 저장 구조를 유지하고 API로 연결 |
| 백엔드 없이 먼저 만들자 | FastAPI API와 연결되는 구조로 작성 |
| DB는 나중에 하자 | SQLite 모델과 API를 함께 작성 |
| 레퍼런스랑 똑같이 바꿔줘 | 레퍼런스는 참고하고 우리 기준에 맞게 재구성 |

## 44-3. AI 결과 검토 기준

AI가 코드를 생성한 뒤 아래를 확인한다.

□ React + FastAPI + SQLite 구조를 유지했는가

□ 지정된 폴더 구조를 벗어나지 않았는가

□ localStorage에 핵심 데이터를 저장하지 않았는가

□ 임시 배열에 데이터를 저장하고 끝내지 않았는가

□ API Endpoint가 명세서와 일치하는가

□ DB 테이블 구조가 계획안과 일치하는가

□ 기존 기능을 삭제하지 않았는가

□ 레퍼런스 기술 스택을 임의로 도입하지 않았는가

□ 레퍼런스 코드 활용 시 출처와 LICENSE를 기록했는가

□ 실행했을 때 오류가 없는가

□ Git commit 전에 직접 테스트했는가

## 44-4. AI에게 공통으로 전달할 기준 문장

이 프로젝트는 Mirae Mobility의 독수리 택시 프로젝트이다.

React + FastAPI + SQLite 구조를 반드시 유지하라.

먼저 _AI_Context 폴더의 기준 문서를 확인하라.

특히 00_Project_Brief.md, 01_Development_Plan.md, 02_API_Spec.md, 04_DB_Model.md, 99_AI_Working_Rules.md를 우선 참고하라.

필요하면 _Reference_bank 폴더의 오픈소스 레퍼런스를 적극 참고하라.

단, 레퍼런스의 기술 스택을 그대로 가져오지 말고 우리 프로젝트 기준에 맞게 재구성하라.

프론트 단독 구현, localStorage 중심 구현, Streamlit 전환, DB 없는 임시 배열 구현은 금지한다.

사용자, 파티, 참여자, 채팅 데이터는 SQLite에 저장한다.

# 45. 오류 대응표

<!-- 표 61 -->
| 문제 | 확인할 것 | 해결 방향 |
| --- | --- | --- |
| git 명령어가 안 됨 | Git 설치 여부 | Git 설치 후 터미널 재시작 |
| push가 안 됨 | GitHub 로그인 여부 | VS Code 로그인 또는 gh auth login |
| npm 명령어가 안 됨 | Node 설치 여부 | Node.js LTS 설치 |
| python 명령어가 안 됨 | Python 설치 여부 | Python 설치 후 PATH 확인 |
| 가상환경 실행 안 됨 | PowerShell 실행 정책 | cmd에서 activate 사용 |
| 백엔드 서버 안 켜짐 | 가상환경, 패키지 설치 | pip install -r requirements.txt 실행 |
| /docs 접속 안 됨 | uvicorn 실행 여부 | 백엔드 터미널 오류 확인 |
| 프론트 서버 안 켜짐 | npm install 여부 | npm install 후 재실행 |
| API 연결 안 됨 | 백엔드 실행 여부, proxy 설정 | Vite proxy와 FastAPI 포트 확인 |
| WebSocket 연결 안 됨 | /ws proxy 설정, token 전달 여부 | vite.config.js와 query token 확인 |
| DB 파일 안 생김 | SQLAlchemy 연결 | database.py와 실행 위치 확인 |
| push 실패 | 권한, 브랜치 확인 | GitHub 초대 수락 및 branch 확인 |
| merge 충돌 | 같은 파일 수정 여부 | PM/TL이 충돌 파일 확인 |
| API Key 노출 위험 | .env 확인 | .env GitHub 업로드 금지 |
| _AI_Context가 git status에 뜸 | .gitignore 확인 | _AI_Context/ 추가 |
| _Reference_bank가 git status에 뜸 | .gitignore 확인 | _Reference_bank/ 추가 |
| AI가 레퍼런스 기술스택으로 바꿈 | 작업 기준 확인 | 우리 기준으로 재요청 |

# 46. 개발 난항 시 처리 기준

<!-- 표 62 -->
| 상황 | 처리 기준 |
| --- | --- |
| 30분 이상 같은 오류 해결 실패 | 오류 메시지 캡처 후 PM/TL에게 공유 |
| AI가 기존 구조를 바꿈 | 즉시 되돌리고 기존 폴더 구조 기준으로 재요청 |
| 백엔드 없이 프론트만 구현됨 | 작업 중단 후 FastAPI API 연결 구조로 수정 |
| localStorage 중심으로 구현됨 | 로그인 토큰 외 localStorage 사용 제거 |
| API 응답 형식이 다름 | API 명세서 기준으로 백엔드 또는 프론트 수정 |
| DB 저장이 안 됨 | SQLAlchemy 모델과 database.py 확인 |
| PR 충돌 발생 | 담당자 단독 해결 금지, PM/TL과 함께 처리 |
| 기능 범위 축소 제안 발생 | PM 확인 전 임의 축소 금지 |
| 레퍼런스 기능이 과하게 들어옴 | 필요한 패턴만 남기고 제거 |
| 라이선스 기록이 누락됨 | 출처와 LICENSE 기록 후 재검토 |

# 47. 담당자별 체크리스트

## 47-1. TL 체크리스트

□ backend 폴더 구조 생성

□ FastAPI 서버 실행

□ SQLite 연결

□ users 모델 생성

□ parties 모델 생성

□ party_members 모델 생성

□ messages 모델 생성

□ 회원가입 API 구현

□ 로그인 API 구현

□ JWT 인증 구현

□ 파티 생성 API 구현

□ 파티 목록 API 구현

□ 파티 상세 API 구현

□ 파티 참여 API 구현

□ 파티 참여 취소 API 구현

□ 파티 취소 API 구현

□ 내 파티 목록 API 구현

□ 요금 분할 로직 구현

□ 상태 변경 로직 구현

□ WebSocket 채팅 구현

□ Admin API 구현

□ /docs에서 API 테스트

□ _AI_Context 기준 확인

□ _Reference_bank 참고 여부 확인

□ Pull Request 생성

## 47-2. QA&Front 체크리스트

□ frontend React 프로젝트 생성

□ 라우터 구성

□ 공통 Layout 구현

□ 회원가입 화면 구현

□ 로그인 화면 구현

□ 로그아웃 처리 구현

□ 파티 목록 화면 구현

□ 파티 검색 UI 구현

□ 파티 생성 화면 구현

□ 파티 상세 화면 구현

□ 파티 참여 버튼 연결

□ 파티 참여 취소 버튼 연결

□ 1인 요금 표시

□ 상태 표시

□ 채팅 화면 구현

□ WebSocket token 연결 확인

□ Kakao Map 표시

□ 안전 안내 화면 구현

□ /admin 화면 구현 지원

□ API 연결 확인

□ _AI_Context 기준 확인

□ _Reference_bank 참고 여부 확인

□ 테스트 결과 기록

□ Pull Request 생성

## 47-3. PM 체크리스트

□ GitHub 저장소 구조 관리

□ 브랜치 생성 여부 확인

□ Pull Request 확인

□ API 명세서 정리

□ 개발 계획(안) 관리

□ Kakao API Key 관리

□ 환경변수 기준 정리

□ _AI_Context 제작 및 배포

□ _Reference_bank 구성 기준 정리

□ .gitignore 확인

□ 관리자 페이지 구현

□ README 작성

□ run-dev.bat 정리

□ run-dev-mac.sh 정리

□ 최종 시연 흐름 점검

# 48. 최종 시연 기준

최종 시연은 아래 순서로 진행한다.

1. run-dev.bat 또는 run-dev-mac.sh 실행

2. 백엔드 서버 실행 확인

3. 프론트엔드 서버 실행 확인

4. Network URL 확인

5. 테스트 계정으로 회원가입

6. 로그인

7. 파티 생성

8. 다른 계정으로 로그인

9. 파티 목록 조회

10. 파티 검색 확인

11. 파티 상세 확인

12. 파티 참여

13. 1인 예상 요금 변경 확인

14. 최대 인원 도달 시 매칭 완료 확인

15. 내 파티 목록 확인

16. 파티 채팅 확인

17. 지도 표시 확인

18. 관리자 페이지에서 데이터 현황 확인

# 49. README 작성 기준

README는 PM이 최종 정리한다.

포함 항목:

1. 프로젝트 소개

2. 팀명 및 팀원 역할

3. 기술 스택

4. 주요 기능

5. 제외 기능

6. 폴더 구조

7. 개발 환경 준비

8. frontend 실행 방법

9. backend 실행 방법

10. run-dev.bat 실행 방법

11. run-dev-mac.sh 실행 방법

12. 환경변수 설정 방법

13. 최종 시연 방법

14. AI Context 사용 기준

15. Reference Bank 사용 기준

16. 레퍼런스 및 라이선스 기록

README는 개발자뿐 아니라 교수님이 저장소를 확인했을 때도 프로젝트 구조를 이해할 수 있도록 작성한다.

단, _AI_Context/와 _Reference_bank/는 GitHub에 업로드하지 않으므로 README에는 “로컬 참고 폴더이며 저장소에는 포함되지 않는다”고 명시한다.

# 50. 최종 제출 전 점검표

□ main 브랜치에 최종 코드가 반영되었는가

□ frontend 실행이 가능한가

□ backend 실행이 가능한가

□ /docs 접속이 가능한가

□ 회원가입이 가능한가

□ 로그인이 가능한가

□ 로그아웃 처리가 가능한가

□ 파티 생성이 가능한가

□ 파티 목록 조회가 가능한가

□ 파티 검색이 가능한가

□ 파티 상세 조회가 가능한가

□ 파티 참여가 가능한가

□ 파티 참여 취소가 가능한가

□ 1인 요금이 자동 계산되는가

□ 최대 인원 도달 시 매칭 완료로 바뀌는가

□ 내 파티 목록이 표시되는가

□ 채팅이 작동하는가

□ WebSocket token 연결이 작동하는가

□ 지도 마커가 표시되는가

□ 관리자 페이지가 표시되는가

□ README가 최신 상태인가

□ .env 파일이 GitHub에 올라가지 않았는가

□ API Key가 코드에 직접 노출되지 않았는가

□ _AI_Context 폴더가 GitHub에 올라가지 않았는가

□ _Reference_bank 폴더가 GitHub에 올라가지 않았는가

□ 레퍼런스 코드 활용 시 출처와 LICENSE를 기록했는가

□ 테스트 결과표가 작성되었는가

□ 시연 순서를 1회 이상 점검했는가

# 51. 최종 개발 기준 문장

본 프로젝트는 React + FastAPI + SQLite 구조를 기준으로 개발한다. React는 사용자 화면과 API 호출을 담당하며, FastAPI는 회원가입, 로그인, 파티 생성, 파티 조회, 파티 참여, 요금 계산, 상태 변경, 채팅 저장 등 핵심 로직을 담당한다. 사용자, 파티, 참여자, 채팅 데이터는 SQLite에 저장하며, localStorage는 로그인 토큰 저장 외의 용도로 사용하지 않는다.

개발 과정에서는 GitHub 브랜치와 Pull Request를 활용하여 공동 작업을 진행한다. main 브랜치는 최종 안정본으로 관리하고, TL은 백엔드 브랜치, QA&Front는 프론트엔드 브랜치, PM은 관리자 및 문서 브랜치를 기준으로 작업한다. 작업 완료 후 Pull Request를 통해 변경사항을 확인하고 main에 반영한다.

_AI_Context/ 폴더는 AI 개발 도구가 프로젝트 기준 문서를 참고하기 위한 로컬 전용 폴더이며, PM이 Google Drive로 배포한다. _Reference_bank/ 폴더는 개발 효율 향상을 위해 MIT 라이선스 기반 오픈소스 레퍼런스를 로컬에 보관하는 폴더이며, AI 도구가 구조와 구현 패턴을 적극적으로 참고하도록 한다. 단, 두 폴더는 GitHub에 업로드하지 않는다.

최종 시연은 발표자 PC에서 프론트엔드와 백엔드를 실행한 뒤, 같은 교내 Wi-Fi에 접속한 기기에서 http://발표자IP:5173 주소로 접속하는 방식으로 진행한다. 최종 목표는 회원가입, 로그인, 파티 생성, 파티 조회, 파티 참여, 요금 분할, 상태 변경, 지도 표시, 파티별 실시간 채팅, 관리자 페이지 확인이 가능한 프로젝트 MVP를 완성하는 것이다.
