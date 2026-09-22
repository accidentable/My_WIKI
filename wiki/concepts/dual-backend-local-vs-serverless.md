---
title: 백엔드 이중 구조 (FastAPI 로컬판 vs 서버리스 배포판)와 로직 표류
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/tacotrump-2026-03-code-overview.md]
tags: [아키텍처, fastapi, 서버리스, 중복코드, 캐시, websocket]
---

# 백엔드 이중 구조와 로직 표류

## 1. 한 줄 정의

같은 서비스의 백엔드를 "풀 기능 로컬판(FastAPI + 스케줄러 + DB + WebSocket)"과 "배포용 서버리스판(요청마다 실시간 fetch, 상태 없음)" 둘로 두고 핵심 로직을 손으로 복제해 유지하는 구조. 빠르게 배포되지만 두 판이 곧 어긋난다.

## 2. 어디서 썼는가

- [[taco-index-2026-03]]: TACO Index. `backend/`(FastAPI)와 `api/`(Vercel 파이썬 함수)에 점수 엔진이 각각 들어 있고, `score_engine.py` 주석이 "(Vercel 배포 버전과 동기화)"라고 스스로 밝힌다.

## 3. 두 판이 어떻게 다른가

| | `backend/` (FastAPI) | `api/` (Vercel 서버리스) |
| --- | --- | --- |
| 프레임워크 | FastAPI + uvicorn, 라우터 3개 | 없음. `BaseHTTPRequestHandler` 직접 |
| 데이터 갱신 | APScheduler가 1분 간격 `collect_all_data()` | 요청이 올 때마다 fetch |
| 저장 | aiosqlite (`indicator_history`, `latest_indicators`) | 없음. Redis에 알림용 상태만 |
| 캐시 | 프로세스 메모리 전역 변수 `_latest_data` | HTTP `Cache-Control: s-maxage` (엣지) |
| 실시간 전파 | WebSocket 브로드캐스트 | 없음. 프론트가 폴링 |
| 수집 지표 | 확장 지표(휘발유·30년물·러셀2000) 포함 | 핵심 6개만 |

즉 서버리스판은 **"상시 프로세스가 없다"는 제약을 캐시 헤더와 Redis로 치환**한 축약판이다. 스케줄러는 크론으로, 메모리 캐시는 엣지 캐시로, DB 히스토리는 Yahoo에서 과거 구간을 매번 다시 받아 계산하는 방식(`/api/history`)으로 각각 대체됐다.

## 4. 왜 이렇게 되는가

원인은 대개 순서다. 먼저 익숙한 FastAPI로 전체를 만들고, 배포 단계에서 Vercel 무료 플랜(상시 프로세스 없음, WebSocket 없음, 로컬 파일 저장 불가)에 맞춰 급히 축약판을 따로 썼다. 첫 커밋 이틀째에 `fix: TS errors for Vercel deploy`가 나오는 걸 보면 배포가 초반 관심사였다(추정).

이 선택 자체는 합리적일 수 있다. 로컬판은 개발 중 WebSocket으로 즉시 확인하고 SQLite에 이력을 쌓을 수 있어 디버깅이 편하고, 배포판은 가볍고 공짜다.

## 5. 실제로 겪은 문제: 표류

TACO Index의 두 판은 이미 다음이 어긋나 있다.

- **총점 구성이 다르다.** `backend/app/services/data_collector.py`는 `core_values`를 만들 때 `["sp500", "vix", "treasury_10y", "oil", "dollar_index"]` 5개만 넣고 `approval_rating`을 빠뜨렸다. 그런데 `get_risk_level()`의 경계값(1.8/3.0/4.2)은 만점 6.0 기준 그대로다. 로컬판은 구조적으로 점수가 낮게 나온다. `api/_shared.py`의 `fetch_all()`은 6개를 모두 넣는다.
- **레벨 색이 다르다.** Lv.1이 backend는 `#16A34A`, api는 `#3CD5AF`.
- **주석과 상수가 다르다.** `api/_shared.py`에 `# S&P 500: safe=-5, redline=-20`이라 써 있지만 실제는 `-3.0 / -15.0`.
- **히스토리 티커가 다르다.** 실시간 `ES=F`, 히스토리 `^GSPC`.

어느 쪽도 에러를 내지 않고 사용자에게 보이지도 않는다. 이게 복제 유지의 성질이다. 같은 이름의 상수와 같은 모양의 함수가 두 곳에 있으면, 한쪽만 고친 것을 리뷰에서 잡아낼 방법이 없다.

## 6. 다음에 어떻게 할 것인가

- **순수 로직은 프레임워크 없는 모듈 하나로 빼고 양쪽이 import한다.** 점수 엔진은 외부 의존이 없는 순수 함수라 공유가 쉬웠다. 이 프로젝트는 그러지 않고 복사했다.
- 공유가 구조상 불가능하면(서버리스 번들 경로 제약 등) **같은 입력에 두 구현이 같은 점수를 내는지 확인하는 테스트 하나**라도 둔다.
- **배포 환경의 제약을 먼저 확인하고 로컬판을 그 제약 안에서 만든다.** WebSocket과 상시 스케줄러를 쓸 수 없는 곳에 배포할 것이라면 로컬판에도 굳이 넣지 않는 편이 낫다.
- 배포판만 살아 있다면 **로컬판을 지우는 것도 선택지**다. TACO Index에서 `backend/`가 실제로 어디에 배포됐는지는 자료에 없다(추정: 로컬 개발용).

## 7. 참고 자료

- `tacotrump/backend/app/main.py`, `tacotrump/backend/app/services/data_collector.py`, `score_engine.py`
- `tacotrump/api/_shared.py`, `tacotrump/vercel.json`
