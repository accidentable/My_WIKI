---
title: 무료 시장데이터를 직접 호출하고 실패를 fallback·엣지캐시로 덮기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/tacotrump-2026-03-code-overview.md]
tags: [yahoo-finance, fred, 스크래핑, fallback, 캐시, httpx]
cs_topics: [네트워크, 웹, 분산시스템]
---

# 무료 시장데이터 수집과 실패 흡수

## 1. 한 줄 정의

유료 금융데이터 API 없이 Yahoo Finance의 공개 chart 엔드포인트, FRED API, 웹 스크래핑만으로 시세·지표를 모으고, 각 소스마다 예외를 삼켜 하드코딩 fallback으로 대체한 뒤 HTTP 엣지 캐시로 호출량을 눌러 무과금·무중단처럼 보이게 하는 방식.

## 2. 어디서 썼는가

- [[taco-index-2026-03]]: TACO Index. 시장 5종은 Yahoo, 휘발유는 FRED, 대통령 지지율은 RealClearPolling 스크래핑으로 모았다.

## 3. 소스별 방법

**Yahoo Finance**: `yfinance` 라이브러리를 안 쓰고 `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1d`를 httpx로 직접 친다. 브라우저 User-Agent를 붙이고 `follow_redirects=True`. 응답의 `chart.result[0].meta`에서 `regularMarketPrice`, `chartPreviousClose`(없으면 `previousClose`), `fiftyTwoWeekHigh`를 꺼낸다. 티커 5~7개를 `asyncio.gather`로 동시에 친다. 라이브러리를 안 쓰면 서버리스 번들이 가벼워지고(pandas 미포함) 응답 형태를 직접 통제할 수 있다.

지수는 절대값이 아니라 **52주 고점 대비 하락률**로 변환해서 쓴다. `(현재가 - 52주고점) / 52주고점 * 100`. 지수 레벨은 시대에 따라 의미가 달라지지만 고점 대비 낙폭은 비교 가능한 값이 된다.

**FRED**: `api.stlouisfed.org/fred/series/observations`에 `series_id=GASREGW`(전국 평균 휘발유), `sort_order=desc`, `limit=2`로 최신 2개만 받아 현재/직전으로 쓴다. API 키가 없으면 호출 자체를 건너뛰고 바로 fallback.

**스크래핑**: RCP 지지율 페이지 HTML을 받아 `rcp_average` 문자열의 위치를 찾고, 그 뒤 500자 안에서 `r'Approve[^}]*?value[\\\":\s]+([\d.]+)'`로 숫자를 뽑는다. Next.js 류가 페이지에 박아 넣은 이스케이프된 JSON을 파싱기 없이 긁는 요령이다.

## 4. 실패를 흡수하는 3겹

1. **티커 단위 격리**: `_fetch_one`이 개별 예외를 잡아 `(key, None)`을 돌려주고, `gather(return_exceptions=True)`로 한 종목 실패가 나머지를 죽이지 않는다.
2. **소스 단위 fallback**: 결과가 비면 하드코딩 상수(`YAHOO_FALLBACK`, 휘발유 3.45, 지지율 41.3)로 대체한다.
3. **엣지 캐시**: 서버리스 응답에 `Cache-Control: s-maxage=30, stale-while-revalidate=60`(risk-level), 120/300(truths), 300/600(history)을 붙인다. 트래픽이 몰려도 Yahoo로 나가는 실호출은 캐시 주기당 1회로 줄고, 재검증 중에는 낡은 값이라도 즉시 응답한다.

## 5. 실제로 겪은 문제

- **fallback이 장애를 숨긴다.** 세 소스 모두 실패해도 화면은 그럴듯한 숫자를 보여준다. TACO Index에는 "이 값은 fallback입니다" 플래그가 응답에 없어서, 사용자도 개발자도 지금 보는 지지율 41.3이 실측인지 상수인지 구분할 수 없다. 최소한 응답에 `is_fallback` 같은 필드를 두거나 `updated_at`을 실제 fetch 성공 시각으로만 갱신해야 한다.
- **스크래핑은 조용히 깨진다.** 문자열 위치 + 정규식 조합은 페이지 리뉴얼 한 번에 무력화되는데, 예외가 아니라 "못 찾음 → fallback"으로 빠지므로 에러 로그도 거의 안 남는다.
- **같은 대상에 다른 티커를 쓰면 축이 어긋난다.** 실시간은 `ES=F`(E-mini 선물), 히스토리는 `^GSPC`(현물)를 써서 같은 차트에 성격이 다른 두 계열이 섞였다. 선물은 야간에도 움직이고 현물은 아니다.
- **거래일이 티커마다 다르다.** 유가 선물과 지수의 거래일이 어긋나 히스토리 날짜 축에 구멍이 생긴다. TACO Index는 날짜를 키로 합친 뒤 직전 값으로 forward-fill하고, 그래도 전 지표가 안 채워진 날은 버렸다.
- **Yahoo 공개 엔드포인트는 계약이 아니다.** 비공식 경로라 언제든 형식이 바뀌거나 막힐 수 있다. 데모·개인 프로젝트 수준에서 쓰는 게 안전하다.

## 6. 참고 자료

- `tacotrump/backend/app/services/yahoo_fetcher.py`, `fred_fetcher.py`, `approval_scraper.py`
- `tacotrump/api/_shared.py`: 서버리스용 축약판
- `tacotrump/api/history.py`: forward-fill과 날짜 축 병합

## 학습

### CS 주제
- 네트워크: HTTP 캐시 제어(`s-maxage`, `stale-while-revalidate`), User-Agent와 리다이렉트, 비공식 엔드포인트 의존
- 웹: 서버리스 응답 캐시와 엣지, HTML 스크래핑의 취약성
- 분산시스템: 부분 실패 격리와 graceful degradation, 조용한 실패(silent failure)

### 설명할 수 있어야 하는 것
- 라이브러리 대신 공개 엔드포인트를 직접 호출한 이유를 서버리스 번들 경량화와 응답 형태 통제로 설명할 수 있습니다.
- 유료 API와 yfinance라는 대안을 두고 안정성을 내주는 대신 무과금과 가벼움을 얻었다는 것을 말할 수 있습니다.
- 페이지 리뉴얼과 엔드포인트 형식 변경, 세 소스 동시 실패에서 이 방식이 깨진다는 것을 설명할 수 있습니다.

### 확인 질문
1. **Q:** (L1 개념) 실패를 흡수하는 세 겹이 각각 어떤 층위의 실패를 막는지 설명해 주시겠어요?
   **A:** 먼저 티커 단위로 격리해서 `_fetch_one`이 개별 예외를 잡아 `(key, None)`을 돌려주고 `gather(return_exceptions=True)`로 한 종목 실패가 나머지를 죽이지 않게 했습니다. 다음으로 소스 단위 fallback을 두어 결과가 비면 하드코딩 상수(`YAHOO_FALLBACK`, 휘발유 3.45, 지지율 41.3)로 대체합니다. 마지막이 엣지 캐시인데, 서버리스 응답에 `Cache-Control: s-maxage=30, stale-while-revalidate=60`(risk-level)과 120/300(truths), 300/600(history)을 붙여 Yahoo로 나가는 실호출을 캐시 주기당 1회로 줄이고 재검증 중에는 낡은 값이라도 즉시 응답하게 했습니다.
   **꼬리:** 그러면 `s-maxage`와 `max-age`는 무엇이 다르고, 서버리스 API 응답에 `s-maxage`를 쓰시는 이유는 무엇인가요?
   **틀리기 쉬운 답:** 캐시는 속도를 위한 것이라고 답하는 경우가 있는데, 여기서는 업스트림 호출량을 눌러 무료 엔드포인트가 막히지 않게 하는 장치이기도 합니다.

2. **Q:** (L2 판단) `yfinance`를 쓰지 않고 `query1.finance.yahoo.com/v8/finance/chart/{ticker}`를 httpx로 직접 치신 이유는 무엇인가요?
   **A:** 서버리스 번들이 가벼워지고(pandas 미포함) 응답 형태를 직접 통제할 수 있기 때문입니다. 브라우저 User-Agent를 붙이고 `follow_redirects=True`로 호출해 `chart.result[0].meta`에서 `regularMarketPrice`와 `chartPreviousClose`(없으면 `previousClose`), `fiftyTwoWeekHigh`만 꺼내 쓰고 티커 5~7개를 `asyncio.gather`로 동시에 칩니다. 대가는 비공식 경로 의존인데, Yahoo 공개 엔드포인트는 계약이 아니라 언제든 형식이 바뀌거나 막힐 수 있어서 데모나 개인 프로젝트 수준에서 쓰는 편이 안전하다고 생각합니다.
   **꼬리:** 그러면 응답 스키마가 바뀌면 이 코드는 어떤 증상으로 나타나나요?
   **틀리기 쉬운 답:** 라이브러리를 쓰면 더 안전하다고 답하는 경우가 있는데, 실제로 같은 비공식 엔드포인트를 감싼 라이브러리라면 깨지는 시점은 같고 깨졌을 때 고치기가 오히려 어렵습니다.

3. **Q:** (L2 판단) 지수를 절대값이 아니라 52주 고점 대비 하락률로 바꿔 쓰신 이유는 무엇인가요?
   **A:** 지수 레벨은 시대에 따라 의미가 달라지는데 고점 대비 낙폭은 비교할 수 있는 값이 되기 때문입니다. 계산은 `(현재가 - 52주고점) / 52주고점 * 100`이고, 이렇게 만든 하락률이 [[market-redline-composite-score]]의 safe=-3 / redline=-15 구간에 그대로 들어갑니다. 수집 단계의 편의가 아니라 점수화할 수 있는 단위를 만들려고 한 선택이었습니다.
   **꼬리:** 그러면 52주 고점이 최근에 갱신됐다면 이 지표는 어떻게 움직이나요?
   **틀리기 쉬운 답:** 지수 포인트를 그대로 쓰면 된다고 답하는 경우가 있는데, 실제로 2000포인트와 6000포인트 시대의 같은 숫자는 같은 위험이 아닙니다.

4. **Q:** (L3 한계) fallback이 있는데도 이 설계가 위험한 이유는 무엇이고 무엇을 고쳐야 할까요?
   **A:** fallback이 장애를 숨기기 때문입니다. 세 소스가 모두 실패해도 화면은 그럴듯한 숫자를 보여 주는데, TACO Index에는 이 값은 fallback입니다라는 플래그가 응답에 없어서 사용자도 개발자도 지금 보는 지지율 41.3이 실측인지 상수인지 구분할 수 없습니다. 최소한 응답에 `is_fallback` 같은 필드를 두거나 `updated_at`을 실제 fetch 성공 시각으로만 갱신해야 한다고 생각합니다. 스크래핑은 특히 조용히 깨지는데, 문자열 위치와 정규식 조합은 페이지 리뉴얼 한 번에 무력화되면서 예외가 아니라 못 찾음에서 fallback으로 빠지기 때문에 에러 로그도 거의 남지 않습니다.
   **꼬리:** 그러면 `updated_at`만 고쳐도 탐지가 되나요? 모니터링을 하나 더 붙인다면 무엇을 재시겠어요?
   **틀리기 쉬운 답:** fallback이 있으니 가용성이 높다고 답하는 경우가 있는데, 실제로 값이 항상 돌아오는 것과 값이 맞는 것은 다릅니다.

5. **Q:** (L3 한계) 여러 소스를 하나의 히스토리 차트로 합치면서 생긴 문제는 무엇이었나요?
   **A:** 두 가지였습니다. 같은 대상에 다른 티커를 쓰면 축이 어긋나는데, 실시간은 `ES=F`(E-mini 선물)이고 히스토리는 `^GSPC`(현물)여서 같은 차트에 성격이 다른 두 계열이 섞였고 선물은 야간에도 움직이는데 현물은 그렇지 않습니다. 거래일도 티커마다 달라 유가 선물과 지수의 거래일이 어긋나면서 날짜 축에 구멍이 생겼습니다. TACO Index는 날짜를 키로 합친 뒤 직전 값으로 forward-fill하고, 그래도 전 지표가 안 채워진 날은 버렸습니다.
   **꼬리:** 그러면 forward-fill로 채운 날의 총점은 어떤 의미로 읽어야 하나요?
   **틀리기 쉬운 답:** 결측은 보간하면 해결된다고 답하는 경우가 있는데, 실제로 보간된 값으로 계산한 총점은 관측이 아니라 가정이고 차트에는 그 구분이 남지 않습니다.

### 더 파볼 것
- [MDN: Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control) — `s-maxage`가 공유 캐시(CDN·프록시)에만 적용된다는 점과 `stale-while-revalidate`가 낡은 응답을 즉시 주면서 뒤에서 재검증하는 동작. 이 프로젝트의 30/60, 120/300, 300/600 설정을 근거를 갖고 읽게 해 준다.
