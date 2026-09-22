---
title: 텔레그램 롱폴링으로 봇 운영하기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/kis-openapi-invest-2026-09-readme.md]
tags: [telegram, 운영, 인프라]
---

## 한 줄 정의

텔레그램 봇 명령을 웹훅 대신 롱폴링(`getUpdates`)으로 받으면
공개 엔드포인트도 인바운드 포트도 없이 서버 1대에서 봇을 운영할 수 있다.

## 어디서 썼는가

- [[kis-openapi-invest-2026-09]] — `core/commands.py`, `cli.py serve`

## 실제로 겪은 문제와 해결

- 롱폴링은 서버가 텔레그램 쪽으로 나가는 연결만 쓴다. 방화벽에 구멍을 내거나
  API Gateway 같은 공개 엔드포인트를 둘 필요가 없다.
- 웹훅을 쓰지 않으니 `getUpdates` 409 충돌이 구조적으로 생기지 않는다.
  단, 예전 배포에서 남은 웹훅이 걸려 있으면 `getUpdates`가 막혀 409가 난다.
  위 프로젝트는 `cli.py chatid --reset-webhook`으로 해제하고, `cli.py serve`도
  시작할 때 자동으로 해제한다.
- 스케줄러(APScheduler)와 롱폴링 스레드를 같은 프로세스에 두면 실행 단위가 하나로 끝난다.
  프로세스가 죽는 것이 유일한 단일 장애점이라 systemd `Restart=always`로 10초 뒤 자동 재기동한다.
- 대안인 AWS 람다 + API Gateway 웹훅 구성은 프로세스 사망 걱정이 없는 대신
  컴포넌트가 5개로 늘고 장애 추적에 CloudWatch를 뒤져야 한다.
- 봇 토큰은 `@BotFather`에게 `/newbot`, chat ID는 봇에게 메시지를 보낸 뒤 조회한다.

## 참고 자료

- raw/done/kis-openapi-invest-2026-09-readme.md
