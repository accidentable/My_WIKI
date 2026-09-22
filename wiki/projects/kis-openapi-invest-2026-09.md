---
title: 한국투자증권 OpenAPI 투자대회 — MA5 돌파 역발상 봇
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/kis-openapi-invest-2026-09-readme.md]
tags: [자동매매, 한국투자증권, openapi, 이동평균, aws-lambda, telegram]
---

## 개요

- 대회명: 한국투자증권 OpenAPI 실전투자대회
- 기간: 2026-09 (자료 기준 시점. 정확한 대회 기간은 자료에 없음)
- 주제: 한투 OpenAPI 실전 계좌로 돌아가는 자동매매 봇 "MA5 돌파 역발상 봇"
- 결과(수상 여부): 자료에 없음
- 백테스트 수행 여부: 하지 않음(원자료 명시)

KOSPI100 종목 중 5일 이동평균선 아래에 눌려 있던 종목이 09:05에 5일선을 위로
넘으면 전액 매수하고, 익절·5일선 이탈·보유기간 만료 중 먼저 닿는 조건에서 청산한다.
매매 판단은 전부 코드가 하며 LLM은 쓰지 않는다.

## 문제 정의

장중에는 당일 종가가 없어서 5일선이 확정되지 않는다. 그래서 "지금 5일선을 넘었는가"를
실시간으로 판정할 방법이 필요했다. 또한 대회 계좌로 실주문을 내야 하므로,
2025년 이후 바뀐 한투 API 규격과 호가단위를 정확히 맞추지 못하면 주문이 거부된다.

## 접근

### 진입 조건 (매일 09:05, 전부 만족하는 종목 중 1종목)

1. 직전 5거래일 중 3일 이상 종가가 그날의 5일선 아래
2. 전일 종가 < 전일 5일선
3. 현재가 > 직전 4거래일 종가 평균 (= 5일선 돌파와 동치, [[ma5-intraday-breakout]])
4. 전일 종가 대비 상승률 ≤ 5% (급등 추격 배제)
5. 전일 종가 > 60일선 (하락추세 반등 실패 배제)
6. 20일 평균 거래대금 ≥ 30억 (전액 주문 소화 유동성)

### 종목 선정

후보가 여럿이면 depth(전일 이격도, 1.0) / thrust(돌파 강도, 0.5) / trend(60일 이격도, 0.5) /
value(20일 평균 거래대금, 0.3)를 후보 집단 내 백분위로 환산해 가중합하고 1위 하나만 잡는다.
절대값이 아니라 상대순위라 지표 간 단위 차이에 영향받지 않는다.

### 청산 (먼저 닿는 것)

| 조건 | 판정 시점 |
|---|---|
| +10% 익절 | 장중 10분 간격 감시 |
| 5일선 이탈 | 장중 감시 |
| 3거래일 경과 | 마감 정리(15:15)에만 |

손절선은 없다. 5일선 이탈이 유일한 방어선이고 갭하락은 그대로 맞는다
(`USE_STOP_LOSS=true`, `STOP_LOSS_PCT=3` 으로 추가 가능).
5일선 기준가는 매일 아침 갱신한다 — 진입 당시 값을 고정하면 청산 판정이 틀어진다.
보유일차는 진입일이 1일차.

### 포지션

1종목 × 100%. 분산이 없어 한 종목의 악재가 곧 계좌 전체다(`MAX_POSITIONS`/`POSITION_PCT`로 조정).
매수 수량은 한투의 **미수없는매수수량** 기준 — 미수를 쓰면 반대매매 위험과 대회 수익률 왜곡이 생긴다.

### 기술 스택 / 아키텍처

- 런타임 의존성은 `requests` 하나. 유니버스를 한투 종목마스터 `kospi_code.mst`
  고정폭 파싱으로 뽑아 pandas·FinanceDataReader·스크래핑이 전부 불필요하다
  ([[kis-master-file-universe]]).
- 운영 A(권장): 서버 1대 상주. `python cli.py serve` 하나로 APScheduler(09:05 진입 /
  10분 감시 / 15:15 마감, KST)와 텔레그램 롱폴링 스레드가 같은 프로세스에서 돈다.
  상태 `data/state.json`, 토큰 `data/kis_token.json`. `infra/ncp/setup.sh`가
  KST 설정·venv·의존성·`cli.py check`·systemd(`Restart=always`) 등록까지 처리
  ([[telegram-longpolling-ops]]).
- 운영 B(대안): AWS 람다 4개 + DynamoDB + SSM + EventBridge + API Gateway 웹훅
  (`python infra/deploy.py all`). 서버 장애 걱정은 없으나 컴포넌트가 5개로 늘고
  장애 시 CloudWatch를 뒤져야 한다. 구 스택 정리는 `infra/aws_cleanup.py`(기본 조회만, `--yes`로 삭제).
- 한투 API 규격 변경·호가단위·토큰 제한은 [[kis-openapi-2025-spec]] 참고.

## 잘된 점 / 안된 점

### 잘된 점
- 5일선 돌파 조건을 대수 변형해 장중 즉시 판정 가능하게 만든 것 (종가 없이도 판정)
- 마스터파일 파싱으로 외부 라이브러리를 걷어내 람다 패키지를 몇 MB로 유지
- 롱폴링 선택으로 공개 엔드포인트·인바운드 포트 없이 운영, 웹훅 409 충돌 구조적 제거
- `DRY_RUN` 기본 true, `cli.py check` / `tests/test_pipeline.py`(API 키 없이 실행)로 안전장치 확보

### 안된 점 / 한계 (원자료가 스스로 밝힌 부분)
- 09:05 판정은 5분치 데이터만 본다. 오전에 넘었다가 종가에 깨지는 whipsaw가 구조적으로 존재한다.
  판정을 늦추면 줄지만 당일 상승분을 놓치므로 즉시성을 택했다.
- 백테스트를 돌리지 않았다. `+10%`, `3거래일`, `5일 중 3일`은 합의된 규칙이지 검증된 최적값이 아니다.
- 코스피100 대형주가 3거래일 안에 +10% 가는 일은 드물어, 실제 청산은 대부분
  5일선 이탈이나 기간 만료로 끝날 가능성이 높다.
- 손절선 부재 + 1종목 100% 집중이라 갭하락 리스크가 그대로 노출된다.

## 재사용 가능한 것

```
config.py              환경변수 + 전략 파라미터
core/kis/auth.py       토큰 발급·캐싱 (파일 또는 SSM)
core/kis/client.py     호출 래퍼 — 유량제한, 재시도, 토큰 만료 자동 복구
core/kis/quotes.py     현재가 / 일봉 / 휴장일
core/kis/trading.py    주문·취소·잔고·미체결·체결내역
core/kis/tick.py       호가단위 보정 (지정가 거부 방지, 반드시 통과)
core/universe.py       KOSPI100 종목마스터 파싱
core/strategy.py       돌파 판정 + 백분위 점수화
core/state.py          포지션·이력 저장 (JSON 또는 DynamoDB)
core/trader.py         주문 실행 + 청산 판단
core/notify.py         텔레그램 발송
core/commands.py       텔레그램 명령 처리
jobs/{scan,entry,monitor,close}.py
handlers/aws.py        람다 진입점 4개
infra/deploy.py        AWS 배포 / infra/ncp/setup.sh 서버 부트스트랩
infra/aws_cleanup.py   구 스택 정리
cli.py                 로컬 실행 (check/scan/entry/monitor/close/serve/chatid)
tests/test_pipeline.py API 없이 도는 통합 점검
```

텔레그램 명령: `/status` `/scan` `/history` `/config` `/pause` `/resume` `/sell 005930`.

## 관련 문서 링크

- [[ma5-intraday-breakout]]
- [[kis-openapi-2025-spec]]
- [[kis-master-file-universe]]
- [[telegram-longpolling-ops]]
