---
title: Ko-Walk — 코스피와 걷다 (하나금융 AR 해커톤)
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/hana-ar-kowalk-2026-plan.md]
repo: https://github.com/accidentable/ko-walk
tags: [하나금융, AR, 위치기반, 블록체인, LLM, 모바일]
---

## 1. 개요

- **코드 저장소**: https://github.com/accidentable/ko-walk (출처: 로컬 git 원격, 2026-09-22 확인)

- 대회명: 하나금융 AR 해커톤
- 기간: 자료에 없음 (개발 계획은 4주 단위로 짜여 있음)
- 주제: 코스피 상장기업 본사를 직접 걸어서 방문하고, AR로 그 기업의 토큰화된 주식을 수집하는 위치 기반 투자 플랫폼
- 결과(수상 여부): 자료에 없음

원자료는 실행 결과 보고가 아니라 **기획·설계 문서**다. 아래 내용은 모두 계획 단계의 설계이며, 실제 구현 여부는 자료에 없음.

### 핵심 플로우

1. 지도에서 주변 상장기업 본사 확인
2. 도보로 본사 반경 100m 이내 진입
3. GPS 감지 → AR 모드 활성화
4. AR 화면에 해당 기업 주식 토큰 3D 오브젝트 렌더링
5. 토큰 탭 → 퀴즈 화면
6. AI가 기업 IR 자료·공시로 자동 생성한 4지선다 퀴즈 3문제
7. 2문제 이상 정답 → 토큰 수집 성공, 유저 지갑으로 전송
8. 포트폴리오에 추가

## 2. 문제 정의

원자료에 문제 정의가 별도 절로 적혀 있지는 않다. 설계에서 읽히는 의도는 "상장기업을 화면 속 종목코드가 아니라 실제로 걸어가 만나는 대상으로 바꾸고, 방문·퀴즈를 거쳐야만 토큰을 얻게 해서 기업 학습을 게임화한다"는 것이다. (추정)

## 3. 접근

### 프론트엔드 (모바일)

- React Native + Expo (SDK 51+) — iOS/Android 동시 개발
- ViroReact (v2.41+) — ARKit / ARCore 양쪽 지원, JS로 AR 씬·3D 오브젝트·인터랙션 처리
  - Expo managed workflow와 호환 안 됨 → `expo prebuild`로 bare workflow 전환 필요
- react-native-maps — 본사 위치 지도·마커
- expo-location — GPS 실시간 추적, geofencing으로 반경 진입 감지

AR 씬 구조는 `ViroARSceneNavigator > ViroARScene > ViroNode(GPS 좌표 기반) > Viro3DObject(.glb 토큰 모델)`이고, 오브젝트에 회전·부유 애니메이션과 `onClick` 퀴즈 전환을 붙인다. 좌표 변환은 [[gps-ar-object-anchoring]] 참고.

### 백엔드

- Node.js + Express REST API (기업 목록, 퀴즈 생성, 방문 기록, 포트폴리오)
- Supabase (PostgreSQL) — Supabase Auth, 기업/퀴즈/방문/포트폴리오/루트 테이블
- 배포: Vercel (API) + Supabase (DB)

주요 엔드포인트: `GET /api/companies`, `GET /api/companies/:id/quiz`, `POST /api/visits`, `GET /api/users/:id/portfolio`, `GET /api/routes`, `POST /api/quiz/generate/:id`(어드민), `POST /api/token/mint`(서버 내부).

DB 테이블: `users`, `companies`(종목코드 PK + 위경도 + 토큰 컨트랙트 주소), `quizzes`(questions jsonb), `visits`(quiz_score, quiz_passed, token_amount, tx_hash), `routes`(company_ids 배열).

### AI 퀴즈 자동 생성

OpenAI GPT-4o + DART 전자공시 API(opendart.fss.or.kr). 크론잡으로 코스피 100 기업 공시를 일 1회 수집해 GPT-4o에 넣고 4지선다 3문제 JSON을 받아 DB에 저장. 자세한 내용은 [[llm-quiz-from-disclosure]].

### 블록체인 (토큰)

Base Sepolia 테스트넷, Solidity ERC-20, 기업별 개별 토큰(예: `KO_005930` = 삼성전자). 서버가 퀴즈 통과를 확인한 뒤 `onlyOwner mint`를 호출해 유저 지갑에 전송. 프론트는 ethers.js v6, 지갑은 앱 내장(privateKey를 Secure Storage에 보관). Base 선택 이유는 Ray가 Base 해커톤 수상 경험이 있어 익숙하고 테스트넷 가스비가 무료이기 때문. 자세한 내용은 [[testnet-reward-token]].

### 화면 구성

스플래시/온보딩(지갑 자동 생성) → 홈 지도(수집완료 초록 / 미수집 금색 마커, 하단 근접 기업 카드 슬라이더) → AR 수집 → 퀴즈(문제별 즉시 정답·해설) → 수집 성공(파티클 + 트랜잭션 해시 표시) → 포트폴리오(총 가치, 섹터별 파이차트) → 루트 탐색(선택) → 프로필.

### MVP 범위

- 반드시: 지도 마커 10~20개, 반경 100m 진입 감지, AR 3D 토큰 렌더링, 퀴즈 3문제 출제·채점, 수집 성공 화면, 탐방 포트폴리오, Base Sepolia 토큰 발행·전송
- 있으면 좋음: 테마 루트 추천("여의도 금융 코스"), 기업 상세, 도감, 걸음 수 트래킹, 랭킹
- 가짜 데이터 처리: 토큰은 실제 주식이 아닌 테스트넷 ERC-20, 퀴즈는 실제 DART 공시를 쓰되 품질은 데모 수준, 토큰 가치는 "만원 상당"처럼 표기만

### 개발 순서 (4주)

1주 기초 세팅 + 지도 / 2주 GPS + AR / 3주 AI 퀴즈 + 블록체인 / 4주 포트폴리오 + 데모 영상 + PPT.

## 4. 잘된 점 / 안된 점

원자료가 계획 문서라 실행 회고는 없다. 다만 사전에 파악해 둔 제약이 정리되어 있다.

- ViroReact는 Expo Go에서 동작하지 않음 → `expo prebuild` 후 네이티브 빌드 필수
- iOS AR 테스트는 실제 기기 필요 (시뮬레이터 AR 미지원)
- GPS 테스트는 실외에서 해야 정확. 실내는 mock location 사용
- 비용: DART API 키 무료, Base Sepolia ETH는 faucet 무료, OpenAI API는 유료지만 퀴즈 생성 정도는 비용 미미

## 5. 재사용 가능한 것

- GPS → AR 좌표 변환 함수 `gpsToArPosition()` (Haversine 기반 x/z 평면 변환, y=1.5로 눈높이 고정) — 원문: `raw/done/hana-ar-kowalk-2026-plan.md`
- 퀴즈 JSON 스키마 (`company_id`, `questions[].question/options/answer/explanation`)
- 퀴즈 생성 프롬프트: "다음 기업 공시를 바탕으로 4지선다 퀴즈 3문제를 JSON으로 생성해줘"
- Supabase DDL 5종(users/companies/quizzes/visits/routes) 전문
- 서울 주요 상장기업 10곳 본사 좌표 샘플 JSON (삼성전자, SK하이닉스, 현대자동차, 하나금융지주, KB금융, 신한금융지주, NAVER, 카카오, 삼성SDI, LG화학)
- `KoWalkToken` ERC-20 컨트랙트 (OpenZeppelin ERC20 + Ownable, onlyOwner mint)

## 6. 관련 문서 링크

- [[gps-ar-object-anchoring]]
- [[llm-quiz-from-disclosure]]
- [[testnet-reward-token]]
- [[bc-card-bigdata-2026]] — 같은 금융 도메인 해커톤. 이쪽은 데이터 분석 제안, Ko-Walk은 모바일 AR 서비스 구현으로 성격이 다름
- [[blockchain-valley-2026-sabonx]] — 같은 EVM 테스트넷 컨트랙트를 쓴 다른 프로젝트. 폐기 레지스트리는 [[onchain-revocation-registry]]
- [[miraeasset-ai-festival-2026]] — 같은 DART 전자공시를 쓴 다른 프로젝트

## 면접 준비

> 원자료는 실행 보고가 아니라 **기획·설계 문서**다. 아래 답은 계획 단계에서 정한 것과 사전에 파악해 둔 제약까지이고, 실제 구현·실행 결과는 자료에 없다. 면접에서 구현했다고 말하면 안 된다.

### 한 문장 소개

상장기업이 화면 속 종목코드로만 존재한다는 데서 출발해, 코스피 기업 본사 반경 100m까지 걸어 들어가면 AR로 그 기업의 토큰화된 주식 오브젝트가 뜨고 DART 공시로 자동 생성한 퀴즈 3문제 중 2문제를 맞혀야 테스트넷 토큰을 받는 위치 기반 투자 학습 앱을 설계했습니다. React Native와 ViroReact, Supabase, GPT-4o, Base Sepolia로 4주 MVP 계획까지 짰습니다.

### 기술 스택과 선택 이유

| 기술 | 역할 | 왜 이걸 썼나 | 대안과 포기한 것 |
|---|---|---|---|
| React Native + Expo (SDK 51+) | iOS/Android 앱 | 크로스 플랫폼으로 같이 개발하고 Expo Go로 빠르게 테스트하려고 골랐습니다 | ViroReact가 managed workflow와 맞지 않아 `expo prebuild`로 bare workflow까지 내려가야 합니다. 고른 이유였던 Expo Go 빠른 테스트를 스스로 포기하게 됩니다 |
| ViroReact v2.41+ | AR 씬·3D 오브젝트·인터랙션 | ARKit(iOS)과 ARCore(Android)를 둘 다 지원하고 AR 씬을 JS로 다룰 수 있어서 골랐습니다 | 네이티브 AR SDK를 직접 쓰는 길을 포기했습니다. iOS 시뮬레이터는 AR을 지원하지 않아 실기기 테스트가 필수가 됩니다 |
| react-native-maps · expo-location | 본사 마커 지도, GPS 실시간 추적, geofencing 반경 진입 감지 | 이유 자료에 없음 | 이유 자료에 없음 |
| Node.js + Express | REST API (기업 목록, 퀴즈, 방문 기록, 포트폴리오) | 이유 자료에 없음 | 이유 자료에 없음 |
| Supabase (PostgreSQL) | Auth + `users`/`companies`/`quizzes`/`visits`/`routes` 5개 테이블 | 이유 자료에 없음 | 이유 자료에 없음 |
| OpenAI GPT-4o + DART 전자공시 API | 크론잡으로 코스피 100 공시를 일 1회 수집해 4지선다 3문제 JSON 생성 | DART API 키는 무료이고 OpenAI는 유료여도 퀴즈 생성 정도면 비용이 미미하다고 봤습니다 | 사람이 문제를 쓰는 안을 포기했습니다. 퀴즈 품질은 "데모 수준"이라고 적어 뒀습니다 |
| Base Sepolia + Solidity ERC-20 (`KoWalkToken`, OpenZeppelin ERC20+Ownable) | 기업별 개별 토큰을 `onlyOwner mint`로 지급 | Base 해커톤 수상 경험이 있어 익숙하고 테스트넷이라 가스비가 들지 않아서 골랐습니다 | 메인넷은 나중에 옮기는 항목으로 미뤘습니다. 토큰은 실제 주식이 아닙니다 |
| 앱 내장 지갑(privateKey → Secure Storage) + ethers.js v6 | 온보딩 때 자동 지갑 생성, 잔액 조회와 포트폴리오 | 이유 자료에 없음 | 외부 지갑 연동을 하지 않습니다 |

### 아키텍처
- (계획 단계, 구현 없음)
- [client] 모바일 앱 :: React Native, Expo SDK 51+, ViroReact 2.41+, react-native-maps, expo-location :: iOS/Android 실기기
- [client] 앱 내장 지갑 :: privateKey, Secure Storage, ethers.js v6 :: 기기 내부
- [server] REST API :: Node.js, Express :: Vercel
- [data] Supabase :: PostgreSQL, Supabase Auth :: Supabase
- [ops] 퀴즈 생성 크론잡 :: 크론잡, 일 1회 :: 호스팅 자료에 없음
- [external] DART 전자공시 API :: opendart.fss.or.kr :: 금융감독원
- [external] GPT-4o :: OpenAI API :: OpenAI
- [chain] KoWalkToken :: Solidity ERC-20, OpenZeppelin Ownable :: Base Sepolia 테스트넷
- 모바일 앱 -> REST API :: 기업 목록, 퀴즈, 방문 기록, 포트폴리오
- 모바일 앱 -> 앱 내장 지갑 :: 온보딩 시 지갑 생성, 주소 조회
- REST API -> Supabase :: 기업·퀴즈·방문·포트폴리오 조회와 저장
- REST API -> KoWalkToken :: 퀴즈 통과 확인 후 onlyOwner mint
- 퀴즈 생성 크론잡 -> DART 전자공시 API :: 코스피 100 공시 일 1회 수집
- 퀴즈 생성 크론잡 -> GPT-4o :: 4지선다 3문제 JSON 생성
- 퀴즈 생성 크론잡 -> Supabase :: 생성한 퀴즈 저장
- 앱 내장 지갑 -> KoWalkToken :: 토큰 잔액 조회

### 고민한 점

- **Expo의 개발 편의와 AR 구현 사이** — ViroReact는 Expo Go에서 돌아가지 않습니다. Expo를 고른 이유가 빠른 테스트였는데 AR을 넣는 순간 `expo prebuild` 후 네이티브 빌드로 내려가야 한다는 것을 미리 확인하고, 그 값을 치르기로 했습니다.
- **테스트를 어디서 할 것인가** — iOS AR은 시뮬레이터가 지원하지 않아 실기기가 필요하고, GPS는 실외에서 해야 정확하며 실내에서는 mock location을 쓴다는 것을 참고 사항으로 미리 적어 뒀습니다. 그런데 4주 계획을 다시 보니 AR과 GPS가 2주차에 몰려 있었습니다.
- **MVP에 무엇을 넣을 것인가** — '반드시 구현' 8개(지도 마커 10~20개, 반경 100m 감지, AR 렌더링, 퀴즈 출제·채점, 수집 성공 화면, 포트폴리오, Base Sepolia 발행·전송)와 '있으면 좋음' 5개(테마 루트, 기업 상세, 도감, 걸음 수, 랭킹)를 갈랐습니다. 게임성을 더하는 기능은 전부 뒤로 미뤘습니다.
- **가짜 데이터를 어디까지 인정할 것인가** — 토큰은 실제 주식이 아닌 테스트넷 ERC-20이고, 퀴즈는 실제 DART 공시를 쓰되 품질은 데모 수준이며, 토큰 가치 환산은 "만원 상당"처럼 표기만 한다고 계획서에 적었습니다. 무엇이 진짜이고 무엇이 연출인지를 먼저 선언해 두는 편이 낫다고 봤습니다.
- **비용을 감당할 수 있는가** — DART API 키는 무료이고 Base Sepolia ETH는 faucet으로 받으며 OpenAI만 유료인데, 퀴즈 생성 규모에서는 미미하다고 보고 넘어갔습니다.

### 예상 질문

1. **Q:** (L1) 이 앱의 핵심 루프를 30초로 설명해 주시고, 왜 퀴즈를 거쳐야 토큰을 주게 하셨는지도 말씀해 주시겠어요?
   **A:** 지도에서 주변 상장기업 본사를 보고, 걸어서 반경 100m에 들어가면 GPS가 감지해 AR 모드가 켜지고, AR 화면의 토큰 3D 오브젝트를 탭하면 그 기업 공시로 만든 4지선다 3문제가 뜹니다. 2문제 이상 맞히면 서버가 토큰을 민팅해 지갑으로 보내고 포트폴리오에 쌓입니다. 방문과 퀴즈를 모두 거쳐야 토큰을 얻게 해서 기업 학습을 게임처럼 만든다는 것이 설계에서 읽히는 의도입니다. 다만 원자료에 문제 정의가 따로 적혀 있지 않아 이 의도는 제 해석입니다.
   **꼬리:** 걸어간 사실만으로 주지 않고 퀴즈를 끼운 것이 이탈률에는 어떻게 작용할까요? 2문제 기준은 무엇으로 정하셨나요?
   **틀리기 쉬운 답:** "실제 주식 조각을 준다"고 답하는 경우가 있는데, 실제로는 테스트넷 ERC-20이고 가치 환산은 화면 표기뿐입니다.
2. **Q:** (L2) 굳이 AR이어야 했을까요? 지도에서 버튼을 누르게 해도 같은 기능일 것 같은데요.
   **A:** 솔직히 말씀드리면 계획서에 AR을 택한 이유가 따로 적혀 있지 않습니다. 대회가 하나금융 AR 해커톤이라는 것이 확인되는 유일한 전제입니다. 설계상 AR이 맡는 일은 "그 자리에 실제로 가 있다"는 사실을 화면에서 느끼게 하는 것이고, 진입 판정 자체는 GPS geofencing이 하기 때문에 AR을 빼도 기능은 성립합니다. 그래서 AR은 기능 요건이 아니라 경험 요건이라고 보는 편이 정확합니다.
   **꼬리:** 그렇다면 AR을 빼고도 남는 값은 무엇인가요? AR 때문에 치른 비용(prebuild, 실기기 테스트, 시뮬레이터 불가)과 견주면 어떤가요?
   **틀리기 쉬운 답:** 없는 이유를 만들어 내는 경우가 있는데, "몰입감을 높이려고"는 계획서에 없는 말입니다.
3. **Q:** (L2) 실제 주식이 아닌데 투자 플랫폼이라고 부를 수 있을까요? 사용자 오인이나 규제 위험은 어떻게 보셨나요?
   **A:** 계획서에 프로토타입에서 가짜로 처리할 것을 따로 정리해 뒀습니다. 토큰은 실제 주식이 아닌 테스트넷 ERC-20이고, 토큰 가치 환산은 "만원 상당"처럼 화면 표기만 하며, 퀴즈는 실제 DART 공시를 쓰되 품질은 데모 수준이라고 적었습니다. 오인 소지를 알고 범위를 좁혀 둔 것은 맞습니다. 다만 금융 규제 검토나 문구 심의에 대한 서술은 자료에 없습니다.
   **꼬리:** 수집 성공 화면에 "삼성전자 토큰 10,000원 상당 수집"이라고 띄우는데, 이 문구 하나가 만드는 위험은 무엇일까요?
   **틀리기 쉬운 답:** "테스트넷이니 아무 문제 없다"고 답하는 경우가 있는데, 실제로는 사용자가 보는 화면의 금액 표기가 위험을 만듭니다.
4. **Q:** (L3) 서버가 퀴즈 통과를 확인하고 `onlyOwner mint`를 부르는데, GPS를 위조한 사용자는 어떻게 거르시겠어요?
   **A:** 계획서에 위치 위조 방어 서술이 없습니다. 오히려 실내 테스트를 위해 mock location을 쓴다고 전제하고 있어서, 같은 수단이 그대로 공격 경로가 됩니다. 진입 판정이 클라이언트의 GPS 값에 기대고 서버는 `POST /api/visits`로 결과를 받기만 해서, 지금 설계대로면 좌표를 조작한 요청과 실제 방문을 가를 근거가 서버에 없습니다. 실제로 만든다면 여기를 먼저 손봐야 한다고 생각합니다.
   **꼬리:** 서버가 방문을 검증하려면 무엇이 더 필요할까요? 기기 신호, 시간 간격, 연속 방문 경로 중 무엇부터 보시겠어요?
   **틀리기 쉬운 답:** "`onlyOwner`라서 안전하다"고 답하는 경우가 있는데, 실제로 `onlyOwner`는 누가 민팅을 부를 수 있는지만 정할 뿐 부를 자격이 있는지는 판단하지 않습니다.
5. **Q:** (L3) 이 4주 계획에서 어디가 먼저 무너질까요?
   **A:** 2주차라고 봅니다. `expo prebuild`로 bare workflow 전환, ViroReact 설치, AR 씬 세팅, GPS에서 AR 좌표로 바꾸는 작업이 한 주에 몰려 있는데 이 중 하나만 막혀도 3주차의 블록체인·퀴즈 작업이 통째로 밀립니다. iOS는 시뮬레이터로 확인할 수 없어 실기기가 필요하고 GPS는 실외에서만 정확하다는 제약도 여기 겹칩니다. 계획서가 이 제약들을 참고 사항으로 이미 적어 뒀으니 위험을 몰랐던 것은 아닌데, 일정에는 그 여유가 반영돼 있지 않습니다.
   **꼬리:** 순서를 바꾼다면 무엇을 1주차로 당기시겠어요? 그 판단의 기준은 무엇인가요?
   **틀리기 쉬운 답:** "AI 퀴즈 생성이 제일 어렵다"고 답하는 경우가 있는데, 실제로 계획서가 스스로 어렵다고 표시한 것은 AR 빌드와 기기 제약 쪽입니다.

### 솔직하게 말할 것

- 구현 여부가 자료에 없습니다. 원자료는 계획·설계 문서 한 건뿐이고, 저장소 링크(`accidentable/ko-walk`)는 확인했지만 그 안에 무엇이 들어 있는지는 위키 원자료로 뒷받침되지 않습니다. 어디까지 만들었는지는 저장소를 직접 열어 본 뒤에 말씀드리겠습니다.
- 문제 정의가 원자료에 없습니다. 위키 본문의 "기업 학습을 게임화한다"는 서술은 설계에서 제가 읽어낸 추정이라, 기획 의도를 물으시면 이 점을 먼저 밝히겠습니다.
- 계획서 속 숫자는 예시입니다. 퀴즈 JSON 예시의 "2025년 4분기 영업이익 10.2조 원"은 형식을 보여주는 예시이지 검증된 사실이 아니고, 기업 본사 좌표 10곳도 계획서에 적힌 값이지 실측이 아닙니다.
- 퀴즈 품질을 검증하는 절차가 없습니다. 공시 텍스트를 GPT-4o에 넣고 JSON을 받아 그대로 DB에 저장하는 흐름이라 오답과 환각을 걸러내는 단계가 설계에 없고, 스키마에 `explanation`과 `source`(DART 공시 번호) 칸을 둔 것이 사후에 따라가 볼 수 있는 유일한 장치입니다.
- Base를 고른 이유는 기술적 비교가 아닙니다. "Base 해커톤 수상 경험이 있어 익숙해서, 그리고 테스트넷 가스비가 무료여서"가 계획서에 적힌 그대로이고 다른 체인과 비교 검토한 기록은 없어서, 그렇게 말씀드리는 편이 정확합니다.
- 대회 기간과 수상 여부는 자료에 없습니다.
