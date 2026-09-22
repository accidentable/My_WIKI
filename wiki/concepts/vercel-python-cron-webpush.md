---
title: Vercel 파이썬 서버리스 + 크론 + Redis로 상태변화 웹푸시 보내기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/tacotrump-2026-03-code-overview.md]
tags: [vercel, 서버리스, cron, web-push, vapid, redis, 알림]
cs_topics: [클라우드, 웹, 보안]
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

## 학습

### CS 주제
- 클라우드: 서버리스 함수의 무상태성, 크론 스케줄과 플랜 제한, 실행 시간 상한
- 웹: 서비스워커와 Web Push, VAPID 키쌍, 구독 수명
- 보안: 공개로 열리는 크론 엔드포인트의 인증

### 설명할 수 있어야 하는 것
- 상시 서버 없이 알림을 보내기 위해 크론 + Redis에 저장한 "직전 레벨" + `pywebpush`를 조합한 구조와, 매 실행이 아니라 값이 바뀐 순간에만(그리고 `prev is None`이면 건너뛰고) 보내기로 한 판단
- 점수를 연속값(0~6) 그대로 비교하지 않고 레벨 1~4로 이산화해 알림 난사를 막은 대신 경계값(1.8/3.0/4.2) 근처 진동은 남겨 둔 교환, 그리고 크론 경로가 공개 URL이라 함수 안에서 `Bearer CRON_SECRET`을 직접 검증해야 했던 이유
- Hobby 플랜의 크론 하루 1회 제한이 "변화 감지" 알림을 사실상 무의미하게 만드는 지점과, 410 구독을 `srem`하지 않으면 죽은 구독이 쌓여 크론 실행 시간이 늘어나는 지점

### 확인 질문
1. **Q:** (L1 개념) 브라우저 Web Push가 동작하려면 무엇이 필요한가?
   **A:** 네 가지다. (1) 알림을 받아 표시할 **서비스워커**(`sw.js`). (2) 브라우저가 만들어 준 **구독 객체** — `endpoint`와 `keys.p256dh`, `keys.auth`. 이 셋의 존재를 서버가 검증한 뒤에만 저장한다. (3) 애플리케이션 서버 신원인 **VAPID 키쌍** — `scripts/generate-vapid.py`로 미리 만들어 환경변수에 넣는다. (4) 발송 측은 `pywebpush`의 `webpush(subscription_info, data, vapid_private_key, vapid_claims={"sub": "mailto:..."})`를 호출한다. 구독 등록은 `POST/DELETE /api/push-subscribe`가 받고, 브라우저에서 직접 호출하므로 `do_OPTIONS`로 preflight도 처리한다.
   **꼬리:** `endpoint`만 알면 그 브라우저에 아무나 알림을 보낼 수 있는가? VAPID는 그 문제의 어디를 막는가?
   **틀리기 쉬운 답:** "서버가 사용자의 브라우저에 직접 연결해 알림을 보낸다." 실제로는 구독의 `endpoint`가 가리키는 브라우저 벤더의 푸시 서비스로 보내고, 그 서비스가 기기에 전달한다.
2. **Q:** (L2 판단) 왜 매 실행마다 현재 값을 알리지 않고 "변화"에서만 알리며, 왜 점수를 레벨로 이산화했는가?
   **A:** 크론은 값이 바뀌었든 아니든 주기적으로 돈다. 그래서 Redis에 직전 레벨(`push_last_level`)을 저장해 두고 `prev is not None and current != prev`일 때만 발송한다. `prev is None`(최초 실행 또는 Redis 초기화 직후)에는 보내지 않는데, 기준선이 없는 상태에서 알림이 터지는 것을 막는 안전장치다. 또 0~6점 연속값 대신 **레벨 1~4로 이산화한 뒤 비교**하기 때문에 점수가 조금씩 흔들려도 알림이 난사되지 않는다 — 이산화 자체가 디바운스 역할을 한다. 다만 경계값(1.8/3.0/4.2) 근처에서의 진동은 여전히 남는다.
   **꼬리:** 경계 근처 진동까지 없애려면 무엇을 추가해야 하는가?
   **틀리기 쉬운 답:** "`prev`가 없을 때도 현재 레벨을 한 번 알려 주는 게 친절하다." 기준선 없는 상태의 알림 폭발을 막는 것이 그 분기의 목적이다.
3. **Q:** (L2 판단·보안) 크론으로만 호출되는 함수인데 왜 함수 안에서 인증을 직접 하는가?
   **A:** Vercel 크론은 `vercel.json`의 `crons`에 적은 경로로 **그냥 HTTP GET을 보낼 뿐**이다. 그 경로는 배포된 사이트의 일반 URL이므로 누구나 칠 수 있는 공개 엔드포인트다. 인증이 없으면 외부에서 반복 호출해 푸시를 난사하거나 외부 API 비용을 태울 수 있다. 그래서 함수가 직접 `Authorization: Bearer <CRON_SECRET>`을 비교하고 아니면 401을 낸다.
   **꼬리:** `CRON_SECRET` 환경변수가 비어 있으면 이 코드는 어떻게 동작하는가? 그 기본값은 안전한 쪽인가?
   **틀리기 쉬운 답:** "플랫폼 내부에서만 호출되니 인증은 필요 없다." 호출 경로가 공개 URL인 이상 내부 전용이라는 보장이 없다.
4. **Q:** (L3 한계) 서버리스로 만들면서 어디가 먼저 깨졌는가?
   **A:** 네 군데다. (1) **상태**: 호출 간 메모리를 믿을 수 없어 직전 레벨과 구독 목록을 Redis에 둬야 했고, 구독 JSON은 `json.dumps(sub, sort_keys=True)`로 정렬해 저장해야 키 순서 차이로 같은 구독이 중복 등록되지 않는다. (2) **죽은 구독**: 발송 결과가 `WebPushException`이고 `status_code == 410`이면 `srem`으로 지운다. 안 지우면 죽은 구독이 무한히 쌓여 크론 실행 시간이 늘어난다. (3) **플랜 제한**: Hobby 플랜은 크론을 하루 1회로 제한해, `0 * * * *`(매시)에서 하루 1회로 내렸다가(`fix: Cron 주기를 하루 1회로 변경 (Hobby 플랜 제한)`) 사흘 뒤 다시 매시간으로 되돌렸다 — 되돌린 이유는 자료에 없다(추정: 플랜 변경 또는 제한 확인 착오). 하루 1회 크론에 "변화 감지" 알림은 사실상 무의미해지므로 플랜 제한은 기능 설계 전에 확인해야 한다. (4) **실행 시간**: 외부 API + LLM 호출이 들어가는 함수는 `functions: { "api/truths.py": { "maxDuration": 60 } }`처럼 따로 늘려야 한다. 여기에 더해 iOS는 홈 화면에 추가해야 푸시가 오고, Redis 환경변수 이름이 제품마다 달라(`KV_REST_API_URL` / `UPSTASH_REDIS_REST_URL` / `KV_URL`) 코드에서 여러 패턴을 `or`로 훑어야 했다.
   **꼬리:** 크론이 한 번 빠지거나 같은 시각에 두 번 돌면 이 알림 로직은 각각 어떻게 동작하는가?
   **틀리기 쉬운 답:** "구독이 만료되면 발송이 실패할 뿐이니 그냥 두어도 된다." 실패가 쌓여 실행 시간이 늘고, 언젠가 함수 상한에 먼저 걸린다.

### 더 파볼 것
- [Vercel — Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs) — `CRON_SECRET`을 `Authorization` 헤더로 보내 준다는 규약, Hobby는 하루 1회 제한이며 더 잦은 표현식은 배포가 실패한다는 점, 실패해도 재시도하지 않으니 멱등·재조정으로 설계하라는 지침
- [MDN — Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API) — 푸시를 받으려면 활성 서비스워커가 있어야 한다는 전제, `endpoint`가 그 자체로 발송 권한이 되는 capability URL이라는 점, 구독이 무효화될 때의 `pushsubscriptionchange`
