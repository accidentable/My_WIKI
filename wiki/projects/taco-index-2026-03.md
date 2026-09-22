---
title: TACO Index (타코알리미), 트럼프 대이란 강경책 번복 가능성 지수
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/tacotrump-2026-03-code-overview.md]
tags: [taco, 시장지표, 대시보드, fastapi, react, vercel, 웹푸시, 크론]
---

# TACO Index (타코알리미)

## 1. 개요

- 기간: 2026-03-25 첫 커밋 ~ 2026-03-30 마지막 커밋 (git log 43개 커밋 기준). 약 6일.
- 주제: 트럼프의 대이란 강경책 번복("TACO", Trump Always Chickens Out) 가능성을 시장지표 6개로 점수화해 실시간으로 보여주는 웹 대시보드.
- 서비스 도메인: `tacotrump.space`. 저장소 https://github.com/accidentable/tacotrump
- 결과: **해커톤 여부 자료에 없음(개인 프로젝트 추정)**. 대회명, 수상, 제출 기록이 원자료에 전혀 없다. 광고(AdSense), SEO(sitemap/robots/JSON-LD/hreflang), 방문자 카운터, 공유 버튼 등 일반 공개 서비스 운영 흔적만 있다.

## 2. 문제 정의

"트럼프가 이번에도 물러날까"라는 질문은 뉴스 논평으로만 소비되고, 판단 근거가 흩어져 있다. 이 프로젝트는 그 질문을 **관측 가능한 시장 압력 지표의 합**으로 바꿔서 0~6점 한 숫자와 레벨 1~4로 보여준다. 트럼프 본인의 발언이 아니라 그를 압박하는 시장 쪽을 본다는 것이 설계의 핵심이다.

커밋 기록을 보면 대상 맥락이 두 번 바뀌었다. 처음에는 관세 맥락이었다가 `fix: 관세→이란-미국 전쟁 맥락으로 설명 전체 수정`(03-27)으로 옮겼고, 6분 뒤 `fix: 문구를 TACO 일반 개념(시장 압박→후퇴)으로 재수정`으로 다시 일반화했다. 지표 자체는 그대로 두고 설명 문구만 갈아 끼웠다(추정: 지표가 특정 사건에 묶여 있지 않아 가능했다).

## 3. 접근

### 3.1 지표와 점수

핵심 6개 지표. 각각 "안전값(safe)"과 "레드라인(redline)"을 두고 그 사이를 선형 보간해 0~1점을 매긴 뒤 단순 합산한다(가중치 없음, 만점 6.0).

| 키 | 지표 | 티커/출처 | safe | redline | 방향 |
| --- | --- | --- | --- | --- | --- |
| `sp500` | E-mini S&P 선물 52주 고점 대비 하락률(%) | `ES=F` (Yahoo) | -3.0 | -15.0 | below |
| `vix` | VIX 공포지수 | `^VIX` | 15.0 | 35.0 | above |
| `treasury_10y` | 미 10년물 국채금리(%) | `^TNX` | 4.0 | 4.5 | above |
| `oil` | 유가 WTI($/배럴) | `CL=F` | 75.0 | 100.0 | above |
| `dollar_index` | 달러 인덱스 | `DX-Y.NYB` | 97.0 | 110.0 | above |
| `approval_rating` | 대통령 지지율(%) | RealClearPolling 스크래핑 | 50.0 | 35.0 | below |

확장 지표 3개(`gasoline` FRED `GASREGW`, `treasury_30y` `^TYX`, `russell2000` `^RUT`)는 화면에 참고로 보여주되 총점에는 넣지 않는다.

총점 → 레벨: `<1.8` Lv.1 안전, `<3.0` Lv.2 주의, `<4.2` Lv.3 경고, 그 이상 Lv.4 위험. 각 레벨에 라벨·색·한국어 설명("시장 패닉. 트럼프 후퇴(타코) 임박.")이 붙는다.

지표 설계 자체는 [[market-redline-composite-score]]에 따로 정리했다.

### 3.2 아키텍처: 백엔드가 둘이다

같은 점수 로직이 두 곳에 **복제**되어 있다.

- `backend/`: FastAPI + APScheduler + aiosqlite + WebSocket. 1분마다 `collect_all_data()`가 돌면서 SQLite(`indicator_history`, `latest_indicators`)에 적재하고 WebSocket으로 브로드캐스트한다. 로컬 개발/전체 기능판(추정).
- `api/`: Vercel 파이썬 서버리스 함수 7개(`BaseHTTPRequestHandler` 직접 구현, 프레임워크 없음). 요청마다 Yahoo와 RCP를 실시간 fetch하고 `Cache-Control: s-maxage=...`로 엣지 캐시에 맡긴다. DB도 스케줄러도 없다. 실제 배포판.

`score_engine.py` 상단 주석이 "(Vercel 배포 버전과 동기화)"라고 스스로 밝힌다. 이 이중 구조의 득실은 [[dual-backend-local-vs-serverless]]에 정리했다.

### 3.3 프론트

React 19 + Vite 8 + TypeScript + Tailwind 4 + recharts. 컴포넌트는 GaugeBar, RiskCard, IndicatorGrid/IndicatorCard, ExtendedIndicators, HistoryTimeline, TruthFeed, ShareButton, NotificationCTA. 훅으로 `useIndicators`, `useTruths`, `usePageViews`, `useWebSocket`. i18n은 자체 구현(`i18n/ko.ts`, `en.ts`). 커밋 `feat: 토스 스타일 UI 리디자인`(03-27)으로 디자인을 한 번 갈아엎었다.

레벨별 트럼프 이미지(`level1_1.png`~`level4_2.png`, `print1`~`print10`)를 띄우는데, 도중에 `UI: 레벨 상관없이 전체 이미지 랜덤 표시`로 레벨-이미지 연결을 끊었다.

### 3.4 알림·크론

`vercel.json`의 `crons`로 `/api/cron/check-level`을 `0 * * * *`(매시)에 호출한다. 이 함수가 현재 레벨을 계산해 Redis의 `push_last_level`과 비교하고, **바뀐 경우에만** `push_subs` 셋에 있는 구독 전체에 pywebpush로 Web Push를 쏜다. 410 응답이 온 구독은 셋에서 제거한다. 요청은 `Authorization: Bearer <CRON_SECRET>`으로 검증한다. 자세한 건 [[vercel-python-cron-webpush]].

크론 주기는 `하루 1회로 변경 (Hobby 플랜 제한)`(03-27) → `하루 1회 → 매시간으로 변경`(03-30)으로 왕복했다.

### 3.5 부가 기능

- `/api/truths`: trumpstruth.org RSS를 defusedxml로 파싱해 트럼프 Truth Social 글을 가져오고, OpenAI `gpt-4o-mini`로 **한 번의 호출에 전부 묶어** 15~30자 한국어 헤드라인으로 요약한다(`[번호]` 프로토콜로 입출력 매칭). 키가 없으면 원문 그대로 반환. maxDuration 60초.
- `/api/pageviews`: Upstash/Vercel KV REST `incr`로 방문자 카운터. 환경변수 이름 4가지 패턴을 or로 훑는다(`fix: Redis 환경변수 다중 패턴 대응`).
- 보안: 03-29 `security:` 커밋 하나로 CORS 화이트리스트(`tacotrump.space`, `localhost:5173`), 에러 메시지 제거(모두 "Internal server error"), 푸시 구독 바디 4KB 제한과 필드 검증, `X-Frame-Options`/`HSTS`/`Referrer-Policy` 등 보안 헤더를 한꺼번에 넣었다.

## 4. 잘된 점 / 안된 점

### 잘된 점
- **한 숫자로 요약되는 컨셉**이 공유·바이럴과 잘 맞았다. 공유 버튼, OG 이미지, 레벨 팝오버 설명, 푸시 알림이 전부 "지금 몇 레벨?"이라는 한 질문에 수렴한다.
- **무료 데이터만으로 굴러간다.** Yahoo Finance v8 chart 엔드포인트, FRED, RCP 스크래핑 모두 무과금이고, 모든 fetch에 fallback 상수가 있어 외부가 죽어도 화면이 빈 채로 멈추지 않는다.
- **엣지 캐시로 서버 없이 버틴다.** 서버리스 함수가 상태를 안 가지고 `s-maxage`(risk 30초, truths 120초, history 300초)로 Yahoo 호출량을 눌렀다.
- 보안 강화를 한 커밋으로 몰아서 정리한 것, 만료된 푸시 구독(410)을 자동 청소하는 것은 깔끔하다.

### 안된 점
- **점수 로직 복제로 두 판이 이미 어긋났다.** `backend/`의 `data_collector.py`는 `core_values`를 만들 때 `approval_rating`을 빼고 5개만 넣는데, 총점은 여전히 만점 6.0 기준으로 레벨을 가른다. 즉 로컬판은 구조적으로 점수가 낮게 나온다. `api/_shared.py`는 6개를 다 넣는다. Lv.1 색도 `#16A34A`(backend) vs `#3CD5AF`(api)로 다르다.
- **주석이 코드와 안 맞는다.** `api/_shared.py`의 `calc_indicator_score`는 `# S&P 500: safe=-5, redline=-20`이라고 써 있지만 실제 상수는 `safe=-3.0, value=-15.0`이다. 임계값을 조정하면서 주석만 안 고쳤다(추정).
- **지지율에 과거 데이터가 없다.** `/api/history`는 "지지율은 과거 데이터 없으므로 현재값을 전 구간에 적용"한다고 명시한다. 따라서 히스토리 차트의 과거 총점은 지지율 항이 오늘 값으로 고정된 반사실적 값이다.
- **히스토리와 실시간의 S&P 티커가 다르다.** 실시간은 `ES=F`(E-mini 선물), 히스토리는 `^GSPC`(현물 지수)를 쓴다. 같은 축에 그려지지만 소스가 다르다.
- **RCP 지지율 스크래핑이 깨지기 쉽다.** `rcp_average` 문자열을 찾아 뒤 500자에서 정규식으로 숫자를 뽑는다. 페이지 구조가 바뀌면 조용히 fallback 41.3으로 떨어지고 화면은 정상으로 보인다.
- **레드라인 값의 근거가 코드 어디에도 없다.** VIX 35, 10년물 4.5, 유가 100 같은 숫자가 왜 그 값인지 문서화되어 있지 않다(추정: 감각으로 정한 값).
- `feat: 홈 위젯 기능 추가 (PWA + iOS Scriptable + Widget API)`는 3분 만에 Revert됐다.

## 5. 재사용 가능한 것

경로는 모두 `C:\Users\pc\Desktop\해커톤\tacotrump` 기준.

- `api/_shared.py`: Vercel 파이썬 서버리스에서 쓸 **CORS 헬퍼 + 공통 에러 응답 + Yahoo 병렬 fetch + fallback + 점수 엔진**이 한 파일에 다 있다. 다른 지표 대시보드에 그대로 이식 가능.
- `api/cron/check-level.py`: Vercel Cron + `CRON_SECRET` 검증 + Redis에 이전 상태 저장 + 상태 변화 시에만 Web Push + 410 구독 정리. 상태변화 알림의 최소 완성형.
- `api/push-subscribe.py`: Web Push 구독 POST/DELETE, 바디 크기 제한과 `endpoint`/`keys.p256dh`/`keys.auth` 검증.
- `scripts/generate-vapid.py`: VAPID 키 생성.
- `backend/app/services/yahoo_fetcher.py`: yfinance 없이 httpx로 Yahoo v8 chart를 직접 병렬 호출. 52주 고점 대비 하락률 계산 포함.
- `api/truths.py`의 `translate_posts()`: 여러 건을 `[번호]` 마커로 묶어 LLM 호출 1회로 처리하고 정규식으로 되돌리는 배치 번역 패턴.
- `api/history.py`의 forward-fill 구간: 티커마다 거래일이 다를 때 날짜 축을 합치고 빈 칸을 직전 값으로 채운 뒤, 모든 지표가 채워진 날만 남긴다.
- `vercel.json`: 프론트 빌드 + 파이썬 함수 + 크론 + 보안 헤더를 한 파일에 묶은 예시.

## 6. 관련 문서

- [[market-redline-composite-score]]: 서로 단위가 다른 시장지표를 레드라인 근접도로 0~1 정규화해 합산하기
- [[free-market-data-fetch-fallback]]: Yahoo·FRED·RCP 무료 소스를 직접 호출하고 실패를 fallback과 엣지 캐시로 덮기
- [[vercel-python-cron-webpush]]: Vercel 파이썬 서버리스 + 크론 + Redis 상태 비교로 상태변화 알림 보내기
- [[dual-backend-local-vs-serverless]]: FastAPI 로컬판과 서버리스 배포판을 같이 두었을 때 생기는 로직 표류
