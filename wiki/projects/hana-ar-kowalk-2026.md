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
