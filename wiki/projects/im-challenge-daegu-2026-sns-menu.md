---
title: SNS 신메뉴 AI 컨설팅, 대구 소상공인 신메뉴 시험판매 지원
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/im-challenge-daegu-2026-sns-menu-readme.md, raw/done/im-challenge-daegu-2026-sns-menu-context.md, raw/done/im-challenge-daegu-2026-sns-menu-spec.md, raw/done/im-challenge-daegu-2026-sns-menu-trend-radar.md, raw/done/im-challenge-daegu-2026-sns-menu-impl-report.md]
tags: [소상공인, 골목상권, 유행, 공공데이터, Next.js, Prisma, LLM, 대구]
---

# SNS 신메뉴 AI 컨설팅

## 1. 개요

- 대회: **2026 AI Blockchain Challenge in Daegu**. 주최 iM뱅크, 주관 iM뱅크·대구디지털혁신진흥원(DIP), 후원 대구광역시. 공모 분야는 소상공인·골목상권 디지털 금융 → 골목상권 데이터 기반 AI 컨설팅.
- 기간: 기획 기준일 2026-09-13, 구현 보고 2026-09-14, 최종 커밋 2026-09-16. 예선 접수 마감은 2026-09-20 23:59로 확인된 기록(2026-09-13 확인 시점).
- 주제: SNS에서 유행하는 신메뉴를 발견하고, 그 가게의 재료·장비·예산에 맞춘 소규모 시험 판매를 돕는 AI 컨설팅.
- 결과(수상 여부): **자료에 없음.** 원자료 기준으로 대회 접수(붙임1~4)와 제출 ZIP 업로드는 아직 하지 않은 상태였다.
- 코드: `C:\Users\pc\Desktop\해커톤\IM-hack` (GitHub `https://github.com/IM-hack-TH/my_project`). 최종 커밋 "Move the store-fit judgement to the AI, keep rules as the verifier".
- 같은 대회의 다른 트랙 결과물: [[blockchain-valley-2026-sabonx]].

블록체인은 대회명에 있다는 이유만으로 넣지 않고 초기 구현에서 제외했다. 금융 맥락은 시험 예산·구매 현금·사용 원가·비용 회수 계산으로 붙였다.

## 2. 문제 정의

사장님은 신메뉴를 찾으려고 여러 SNS를 뒤지고, 우리 가게에서 만들 수 있는지 따지고, 재료를 사고, 시험 판매 결과를 판단해야 한다. 정보 탐색과 실행 사이에 시간·비용·판단 부담이 있다.

핵심 질문을 "이 메뉴가 정확히 얼마나 유행하는가"가 아니라 **"이런 메뉴가 나왔는데, 우리 가게에서 이 방식으로 시험해보겠습니까"**로 잡았다. 그래서 결과물은 인기 순위나 시장 보고서가 아니라 가게별 실행 제안이다. 관찰 범위는 서울을 포함한 전국, 초기 이용자는 대구 개인 카페다(서비스 이름에서는 서울을 뺐다).

명시적으로 범위 밖에 둔 것: 전국 인기 순위, 특정 메뉴 판매량 예측, 성공 확률 보장, 자동 대출 추천, 검증된 완제품 레시피 제공, SNS 전체 실시간 수집.

## 3. 접근

### 3.1. 기능 축 (F01~F09)

가게 등록·보유 자원(F01) → 관찰 계정·근거 자료 등록(F02) → LLM 메뉴 추출·운영자 검토(F03) → 후보 목록·상세(F04) → 공공데이터 상권 맥락(F05) → 가게별 적용안(F06) → 시험 비용 계산(F07) → 시험 계획·결과 기록(F08) → 운영·데모·출처 관리(F09). 구현 보고 기준 F01~F09 전부 "완료"로 표시되어 있고, 화면만 있는 항목은 없다고 적혀 있다.

### 3.2. 데이터

| 자료 | 규모·기준일 |
|---|---|
| 소진공 대구 상가정보 | 2026.06, 118,357행·39열, UTF-8. 카페 5,513 + 빵/도넛 1,509 + 떡/한과 485 = 7,507행 추출 |
| 법정동 성·연령 주민등록 인구 | 2026.08.31, 전국 18,624행·231열(CP949)에서 대구 383개 법정동/리 추출 |
| 유행 추적 | 네이버 Search Trend·블로그 검색, Google Trends, YouTube Data API, 구글 급상승 RSS |
| 미확보 | 실제 SNS 관찰 게시물, 사장님 실입력 원가, 실제 시험 판매 결과, DIP 카드·생활인구·주문 원본(설명서만 확보) |

상가 전체의 법정동코드가 인구 383개 지역 코드와 일치함을 확인했다. 거주 인구를 방문객이나 특정 메뉴 수요로 해석하지 않는다는 원칙을 문서·화면에 박아 두었다. 자세한 결합 방식은 [[public-store-population-context]].

### 3.3. 유행 감지·추적

발견(아직 이름이 없는 후보 찾기)과 추적(이름 잡힌 후보가 곡선의 어디에 있는지)을 분리했다. 발견은 도메인 씨앗어 10개로 블로그·유튜브 제목을 모아 n-gram 버스트로 뽑고([[ngram-burst-discovery]]), 추적은 네이버 일별 검색지수의 7일 이동평균 규칙으로 단계를 판정한다([[search-index-stage-rule]]). 공식 API와 공개 페이지만 쓰고 인스타그램·배달앱·커뮤니티 크롤링은 약관 위반 소지로 제외했다.

### 3.4. AI와 규칙의 역할 분담

비용 계산은 처음부터 AI 밖의 순수 함수(`src/domain/cost.ts`)로 두었다([[test-sale-cost-model]]). 반대로 화면에서 가장 큰 숫자인 "우리 가게 적합도 %"는 원래 규칙 계산이었는데, 2026-09-16에 AI 판단으로 옮기고 규칙을 상한 검증자로 남겼다([[ai-judgement-rule-ceiling]]). LLM 추출 결과는 서버가 본문 인용 포함 여부와 근거 ID 유효성을 다시 검사한다.

### 3.5. 기술 스택

Next.js 16.3.5(App Router, Turbopack) · React 19.2 · TypeScript 5 · Prisma 7.10 + `@prisma/adapter-better-sqlite3` · Zod 4.6 · csv-parse 7 · `openai` 7.15 · `@anthropic-ai/sdk` 0.125 · Vitest 5 · Tailwind CSS 4. Node 22.20 / npm 10.9 검증. 실행 경로는 로컬 `npm run dev`, GitHub Codespaces 자동 기동, `docker compose up --build` 세 가지이고 푸시마다 GitHub Actions가 lint·테스트·빌드·기동·Docker 이미지를 검사한다.

AI 키 변수는 `AI_API_KEY` 하나로 한정했다. 범용 `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`를 쓰지 않은 이유는 다른 도구의 키를 실수로 쓰지 않기 위해서다. 공급자는 `AI_PROVIDER=openai|anthropic`, 기본 모델은 OpenAI `gpt-5.6-terra`, Anthropic `claude-opus-5`. 총 AI 호출은 최대 2회(SDK 재시도 0, 서비스 층 재시도 1회).

## 4. 잘된 점 / 안된 점

### 잘된 점

- **이름을 모르는 유행을 실제로 찾아냈다.** 유행 이름을 전혀 주지 않고 도메인 씨앗어만으로, 조사자가 몰랐던 민음사빵(GS25×민음사 콜라보)과 진행 중이던 피자설기를 블로그·구글 트렌드 두 소스에서 교차로 잡았다.
- **실제 AI 경로를 키로 확인했다.** OpenAI `gpt-5.6-terra`로 연결 테스트, 추출, 적용안 생성까지 돌렸다. 본문에 "규칙 무시" 같은 지시문이 섞인 가상 자료를 넣어도 무시되고 인용 4건이 서버 검사를 통과했다(T05).
- **공공데이터를 실제로 적재했다.** 118,357행 상가(제외 0행, 좌표 오류 0행)와 대구 383개 법정동 인구(성별·연령 합계 검증 통과)를 앱 가져오기 경로로 적재 확인.
- **데모와 실제를 데이터 층에서 분리했다.** `dataMode` / `acquisitionMethod=demo` / `generationMode`를 DB·API에 두고 화면 배지로 노출. 키가 없으면 고정 샘플을 실제 AI 생성처럼 보여주지 않는다는 원칙을 명시했다.
- 단위 테스트 64개 통과, ESLint 0건, `tsc --noEmit` 0건, `next build` 성공. 수용 테스트 T01~T17·T19·T20 통과.

### 안된 점 / 한계

- **스파이크형 유행은 사전 포착이 구조적으로 불가능하다.** 버터떡은 12일 만에 정점을 찍어 감지일 = 정점일이었다. 재료를 사기 전에 끝나므로 아예 후보에서 제외하는 필터를 넣었다.
- **되돌리기 검증이 근사치다.** 네이버 블로그 API는 날짜 필터가 없고 최신 1,000건만 주므로 과거 시점의 버스트 순위가 샘플 편향에 흔들린다. 발견 층의 정량 평가는 실운영(일별 누적)에서만 가능하다.
- **조사 문서 자체에 오류가 있었다.** 구현 단계 검토에서 4.1 표의 "7일 규칙" 열이 실제로는 14일 규칙 값이고, 3개 유행은 주 단위 자료이며, 피자설기 정점이 두 기준으로 둘로 적혀 있음을 찾아냈다.
- **실시간 요구가 운영자 검토 원칙을 깼다.** 순위의 이름을 눌렀을 때 아직 후보가 아니면 `materializeKeyword`가 대표 글 3건을 자동 등록·추출·승인해 컨설팅으로 넘긴다. 상세기획서의 "운영자 검토 후 노출" 원칙에서 벗어나는 지점이며, 사후 통제('순위에서 숨기기')만 남는다고 문서에 명시했다.
- 규칙 기반 적합도가 대부분 55%로 몰리고 이유도 고정 문장이었다. 이것이 마지막 날 AI로 역할을 뒤집은 직접적 계기다.
- Anthropic 어댑터는 구현되어 있으나 Anthropic 키로 미검증. 로그인·가게별 접근 제어(T18)는 P1로 미구현이라 실제 사장님 데이터를 받는 파일럿은 아직 불가.
- 틱톡 Creative Center 목록 API는 로그인 없이 40101을 반환해 보류. 구글 트렌드는 공식 API가 없어 공개 RSS만 교차 확인 신호로 썼다.
- P0 자료 수집은 운영자 수동 등록 기반이다. 자동 수집은 P1, 소비자 먹거리 지도·유료 구독은 P2로 미착수.

## 5. 재사용 가능한 것

원본 저장소 `C:\Users\pc\Desktop\해커톤\IM-hack` 기준 경로.

- `sns-menu-consultant/src/domain/cost.ts`, 시험 판매 비용 순수 함수. 선제조/주문 후 제조, 포장 시점, 가중평균 단가, 회수 수량. 단위 테스트 T09~T13.
- `sns-menu-consultant/src/domain/ngram.ts`, `trend-stage.ts`, 사전 없는 n-gram 버스트 추출과 단계 판정 순수 규칙.
- `sns-menu-consultant/src/domain/store-fit.ts`, `fit.ts`, AI 점수의 상한 검증자와 대체안 검증(`verifySubstitutions`).
- `sns-menu-consultant/src/providers/naver/client.ts`, 블로그·이미지·검색어 트렌드. NAVER API HUB 인증(`X-NCP-APIGW-API-KEY-ID`/`X-NCP-APIGW-API-KEY`).
- `sns-menu-consultant/src/providers/youtube/client.ts`, `src/providers/google/trends-rss.ts`.
- `sns-menu-consultant/src/services/trend-radar.ts`, 스크립트 `npm run trends:collect`, 운영자 화면 `/admin/trends`.
- `sns-menu-consultant/scripts/import-public-data.ts`, 상가·인구 CSV 인코딩 판별·헤더 검증·행 검증·롤백 포함 적재.
- `tools/prepare_data.py`, `tools/verify_bundle.py`, `tools/update_manifest.py`, `data/manifest.json`(SHA-256), 원본에서 파생 데이터를 다시 만들고 해시로 대조하는 재현 절차. 표준 라이브러리만 필요.
- `sns-menu-consultant/scripts/prepare-submission-zip.mjs`, node_modules·.env·DB 제외 검사가 붙은 제출 ZIP 생성.
- 트렌드 조사 재현 코드(원자료 7절): 네이버 Search Trend 연령별 기준자 호출, pytrends 호출 간격 25~30초, m7 연속 상승 판정 스니펫.
- 결과 데이터 `data/derived/trend_radar/`: `gt_daily_<유행>.csv`(6종), `gt_lifecycle.json`, `naver_age_intensity.json`, 후보 목록 JSON 2종.

## 6. 관련 문서

- [[blockchain-valley-2026-sabonx]], 같은 2026 AI Blockchain Challenge in Daegu에 낸 다른 트랙 결과물
- [[ngram-burst-discovery]], 이름을 모르는 유행 후보를 사전 없이 찾기
- [[search-index-stage-rule]], 검색지수 이동평균으로 유행 단계와 훅 창 판정하기
- [[public-store-population-context]], 공공 상가·법정동 인구를 가게 맥락으로 결합하기
- [[ai-judgement-rule-ceiling]], AI가 판단하고 규칙은 상한 검증자로 남기기
- [[test-sale-cost-model]], 사전 현금과 사용 원가를 분리한 시험 판매 계산
- [[search-trend-api]], 검색어 트렌드 API의 정규화 문제와 기준자 방법
- [[supply-side-fad-signal]], 공급 측 신호로 유행 단계 판정하기
- [[fad-lifespan-metrics]], 유행 수명을 여러 정의로 재기
- [[rule-engine-llm-split]], 규칙과 LLM의 기본 분업(이 프로젝트는 마지막에 방향을 뒤집었다)
- [[evidence-linked-llm-output]], 인용·근거 ID를 서버가 다시 검사하기
- [[claim-scoping-in-hackathon-docs]], 근거가 받쳐 주는 범위까지 주장 좁히기
