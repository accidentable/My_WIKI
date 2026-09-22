---
title: Vercel 파이썬 서버리스 + 크론 + Redis로 상태변화 웹푸시 보내기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/tacotrump-2026-03-code-overview.md]
tags: [vercel, 서버리스, cron, web-push, vapid, redis, 알림]
---

# Vercel 파이썬 크론과 웹푸시 알림

## 1. 한 줄 정의

Vercel의 파이썬 서버리스 함수(`api/*.py`, `BaseHTTPRequestHandler` 클래스 하나)와 `vercel.json`의 `crons`, 그리고 Redis에 저장한 "직전 상태"를 조합해, 서버를 상시 띄우지 않고도 값이 바뀐 순간에만 브라우저 Web Push를 보내는 구조.

## 2. 어디서 썼는가

- [[taco-index-2026-03]]: TACO Index. 레벨 1~4가 바뀔 때만 구독자 전원에게 "타코 레벨 변경! Lv.3 경고" 푸시를 보낸다.

## 3. 구성 요소

**함수 형태.** Vercel 파이썬 런타임은 파일마다 `handler`라는 이름의 `BaseHTTPRequestHandler` 서브클래스를 요구한다. `do_GET` / `do_POST` / `do_DELETE` / `do_OPTIONS`를 직접 구현하고, 응답은 `send_response` → `send_header` → `end_headers` → `wfile.write`. FastAPI나 Flask 없이 표준 라이브러리만 쓴다. 비동기 코드는 `asyncio.run(...)`으로 감싸 진입한다. 공용 모듈은 `sys.path.insert(0, os.path.dirname(...))` 후 import하는 방식으로 끌어 쓴다(하위 디렉터리인 `api/cron/`에서는 `".."`을 넣는다).

**크론.** `vercel.json`에 선언한다.
```json
"crons": [{ "path": "/api/cron/check-level", "schedule": "0 * * * *" }]
```
크론은 그냥 해당 경로로 HTTP GET을 보낼 뿐이라 **누구나 칠 수 있는 공개 엔드포인트**다. 그래서 함수 안에서 `Authorization: Bearer <CRON_SECRET>`을 직접 검증하고 아니면 401을 낸다.

**상태 저장.** 서버리스 함수는 호출 간 메모리를 못 믿으므로 "직전 레벨"을 Redis(`push_last_level`)에 둔다. 구독 목록은 Redis 셋(`push_subs`)에 구독 JSON 문자열 자체를 원소로 저장한다. 저장 시 `json.dumps(sub, sort_keys=True)`로 정렬해야 같은 구독이 키 순서 차이로 중복 등록되지 않는다.

**푸시 발송.** `pywebpush`의 `webpush(subscription_info, data, vapid_private_key, vapid_claims={"sub": "mailto:..."})`. VAPID 키쌍은 `scripts/generate-vapid.py`로 미리 만들어 환경변수에 넣는다. 다국어 알림은 payload에 `{"title": {"ko": ..., "en": ...}}`처럼 넣고 서비스워커(`sw.js`)가 언어를 골라 표시한다.

**구독 만료 처리.** 발송 결과가 `WebPushException`이고 `status_code == 410`이면 그 구독은 죽은 것이므로 셋에서 `srem`한다. 이걸 안 하면 죽은 구독이 무한히 쌓여 크론 실행 시간이 늘어난다.

**구독 등록 엔드포인트.** `POST/DELETE /api/push-subscribe`. 바디를 4KB로 제한하고 `endpoint`, `keys.p256dh`, `keys.auth` 존재를 검증한 뒤에만 Redis에 넣는다. 브라우저에서 바로 호출하므로 `do_OPTIONS`로 preflight도 받아야 한다.

## 4. 알림 정책: 값이 아니라 변화

핵심은 매 실행마다 알리는 게 아니라 **이전 값과 다를 때만** 보내는 것이다.

```
prev = redis.get(LAST_LEVEL_KEY)
if prev is not None and current != prev:  # 첫 실행은 건너뜀
    발송
redis.set(LAST_LEVEL_KEY, current)
```

`prev is None`(최초 실행 또는 Redis 초기화 직후)에는 보내지 않는다. 기준선이 없는 상태에서 알림이 터지는 걸 막는 안전장치다. 또 연속값(0~6점) 대신 **레벨 1~4로 이산화한 뒤 비교**하기 때문에, 점수가 3.01과 2.99 사이를 오가지 않는 한 알림이 난사되지 않는다. 이산화 자체가 디바운스 역할을 한다(경계에서의 진동은 여전히 남는다).

## 5. 실제로 겪은 문제

- **Hobby 플랜은 크론을 하루 1회로 제한한다.** TACO Index는 이 때문에 `0 * * * *`(매시)에서 하루 1회로 내렸다가(`fix: Cron 주기를 하루 1회로 변경 (Hobby 플랜 제한)`) 사흘 뒤 다시 매시간으로 되돌렸다. 되돌린 이유는 자료에 없다(추정: 플랜 변경 또는 제한 확인 착오). 하루 1회 크론에 "변화 감지" 알림은 사실상 무의미해지므로, 플랜 제한은 기능 설계 전에 확인해야 한다.
- **iOS는 홈 화면에 추가해야 푸시가 온다.** 커밋에 `fix: iOS 알림 안내 문구에 공유 아이콘(⬆) 설명 추가`가 남아 있다. 미지원 환경용 안내 모달을 따로 만들었고(`feat: 알림 버튼 항상 표시 + 미지원 환경 안내 모달`), VAPID 키가 없어도 CTA 배너는 항상 띄우도록 했다.
- **환경변수 이름이 제품마다 다르다.** Vercel KV / Upstash Redis는 `KV_REST_API_URL`, `UPSTASH_REDIS_REST_URL`, `KV_URL` 등 이름이 섞여 나와서, 코드에서 `or`로 여러 패턴을 훑어야 했다(`fix: Redis 환경변수 다중 패턴 대응`).
- **`ignoreCommand` 설정이 자동 배포를 끊었다.** `fix: ignoreCommand 제거: Git 자동 배포 복구`.
- **실행 시간 제한.** 외부 API + LLM 호출이 들어가는 함수는 `functions: { "api/truths.py": { "maxDuration": 60 } }`처럼 따로 늘려 줘야 한다.

## 6. 참고 자료

- `tacotrump/api/cron/check-level.py`, `tacotrump/api/push-subscribe.py`
- `tacotrump/scripts/generate-vapid.py`, `tacotrump/frontend/public/sw.js`
- `tacotrump/vercel.json`
