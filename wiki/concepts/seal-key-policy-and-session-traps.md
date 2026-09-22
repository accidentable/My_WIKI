---
title: Seal 열쇠 ID 정책과 세션 키 함정
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-dev-memories.md]
tags: [블록체인, Sui, Seal, 암호화, 접근제어]
cs_topics: [암호학, 보안, 분산시스템, 운영체제]
---

## 한 줄 정의

Seal은 암호화 자체가 아니라 **"누구에게 열쇠를 줄지"를 내 Move 패키지의 `seal_approve` 함수로 정하는** 구조다. 열쇠 ID를 어떻게 잡느냐가 곧 접근 단위가 된다.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], 단계 기록·텍스트 기억 암호화, 구독 만료 시 복호화 거부.

## 열쇠 ID 설계가 접근 단위를 정한다

열쇠 ID 규약은 `[패키지 ID]::[정책 객체 ID][임의 nonce]`이고, `seal_approve` 안에서 `is_prefix(정책객체_id_bytes, id)`로 소관인지 확인한다. Memory Market은 **팩 ID 32바이트 ‖ 접미사**로 잡았다. 단계 기록은 접미사가 u16 big-endian 단계 번호, 텍스트 기억은 랜덤 5바이트다. 컨트랙트가 접두사만 보므로 구독권 하나로 그 팩의 블롭이 전부 열린다. 즉 **팩이 접근 단위**다.

대비되는 예가 MemWal이다. MemWal의 열쇠 ID는 `BCS(owner) ‖ BCS(counter)` 하나라 소유자당 열쇠가 1개고, 델리게이트를 등록하면 계정 전체가 열린다(최대 20개, 결제·만료 개념 없음). "기억 일부만 특정인에게 기간제로"가 구조적으로 불가능해서, 접근 규칙을 별도 패키지에 두고 열쇠 ID를 팩 단위로 다시 잡는 선택을 했다.

## 실제로 겪은 문제와 해결

**`ExpiredSessionKeyError: Session key has expired`의 진짜 원인은 PC 시계다.** 이 예외는 서버 응답 `InvalidCertificate`의 SDK 쪽 이름이고, 키 서버(`server.rs`)가 그걸 내는 조건은 셋뿐이다. ① TTL이 서버의 `session_key_ttl_max` 초과, ② 생성 시각이 서버 시계보다 미래, ③ 이미 만료. ②의 허용 오차가 **0**이라(`checked_duration_since()`가 `offset > now`면 `None`) **1ms만 빨라도 거부된다**. 진단은 HTTPS 응답 `date` 헤더와 `Date.now()` 비교. 해결은 `w32tm /resync /force`, 그리고 견고하게는 SDK가 `creationTimeMs`를 `Date.now()`로 찍으므로 `SessionKey.create()` 호출 동안만 `Date.now`를 (실제 − 측정 skew − 여유분)으로 감싸는 것(`scripts/session.ts`). 키 서버를 바꿔가며 시간 낭비하지 말 것.

**TTL도 서버 설정에 걸린다.** SDK는 `ttlMin` 1~30을 허용하지만 서버가 자기 `session_key_ttl_max`보다 길면 거부한다. 배포 예시에 `session_key_ttl_max: '60s'`가 있어 어떤 서버에서는 `ttlMin: 10`이 곧바로 에러다. 시계가 정상인데 이 에러면 TTL을 1로 낮춰 보고, 복호화 시도마다 세션 키를 새로 만드는 편이 안전하다.

**SealClient는 파생 키를 인스턴스에 캐시한다.** 한 번 `decrypt`에 성공하면 이후는 로컬에서 일어나므로 **구독이 만료돼도 같은 클라이언트로는 계속 읽힌다**. 이걸 모르면 "정책이 동작하지 않는다"고 오진한다. 만료·회수를 검증하거나 데모하려면 캐시가 빈 새 `SealClient`로 시도해야 한다(`mm recall --fresh`). 뒤집어 말하면 Seal의 접근 회수는 이미 키를 받아간 클라이언트에 소급되지 않는다. 설계상의 성질이라 서비스 설계에 반영해야 한다.

**배치 복호화와 그 함정.** 블롭 N개의 열쇠 ID로 `seal_approve`×N을 PTB 하나에 담아 `fetchKeys` 1회로 받고 블롭마다 `decrypt` 한다. 배치가 거부되면 블롭당 요청으로 물러난다. 판매자가 다른 팩 접두사의 블롭을 섞어 두면 **배치 전체가 거부돼 만료로 오인**되므로 먼저 걸러낸다.

**packageId는 첫 버전이어야 한다.** SDK가 `SessionKey.create`와 `encrypt`의 packageId를 패키지 첫 버전으로 검사한다. 업그레이드하면 `SEAL_PACKAGE_ID`를 따로 둔다.

**committee 모드는 2026-09 기준 못 썼다.** aggregator 경유 committee 서버(`0xb012…`, threshold 1)는 세션 키 인증서를 거부해서, testnet 독립 운영 서버 2대(`0x73d05d62…`, `0xf5d14a81…`) + threshold 2를 썼다(`SEAL_KEY_SERVERS`로 전환 가능). `@mysten/seal` 1.x의 `KeyServerConfig`에는 committee용 `aggregatorUrl` 필드가 있고 0.9.x에는 없다.

## 참고 자료

- `MystenLabs/seal` `crates/key-server/src/server.rs`(인증서 TTL·생성시각·서명 검사), `errors.rs`(에러명 매핑)
- 관련: [[sui-timed-access-subscription]], [[sui-sdk-rpc-migration-2026]]

## 학습

### CS 주제
- 암호학: 신원 기반 암호(IBE)와 threshold 키 서버, 접두사 기반 식별자 설계
- 보안: 접근 단위(granularity) 결정, 인증서 시각 검증, 회수 불가능성
- 분산시스템: 키 서버 정족수, 배치 요청의 부분 실패
- 운영체제: 시스템 시계 동기화(NTP/`w32tm`), 클라이언트 측 캐시

### 설명할 수 있어야 하는 것
- 기억 일부만 특정인에게 기간제로 열려면 열쇠 ID를 팩 단위로 다시 잡고 접근 규칙을 별도 패키지에 둬야 했던 이유를 설명할 수 있습니다.
- MemWal식으로 소유자당 열쇠를 하나만 두면 구현은 단순하지만 부분 공개와 기간제가 구조적으로 안 된다는 점과, 그 단순함을 버린 대가를 함께 말할 수 있습니다.
- 키를 한 번 받아간 클라이언트에는 회수가 소급되지 않는다는 점, PC 시계가 1ms만 빨라도 세션 키가 거부된다는 점을 말할 수 있습니다.

### 확인 질문
1. **Q:** (L1 개념) Seal에서 누가 열 수 있는지는 어디서 정해지고, 열쇠 ID 규약은 어떻게 되는지 설명해 주시겠어요?
   **A:** Seal은 암호화 자체를 맡는 게 아니라 접근 정책을 개발자의 Move 패키지 `seal_approve` 함수로 정하게 되어 있습니다. 열쇠 ID 규약은 `[패키지 ID]::[정책 객체 ID][임의 nonce]`이고, `seal_approve` 안에서 `is_prefix(정책객체_id_bytes, id)`로 그 열쇠가 자기 소관인지 확인합니다. 패키지 ID가 네임스페이스 역할을 하니까 그 뒤 접두사를 무엇으로 잡느냐가 곧 접근 단위가 된다고 이해했습니다. Memory Market의 `seal_approve(id, sub, pack, clock)`는 구독권이 이 팩 것인지, 만료 전인지, 열쇠 ID가 팩 ID로 시작하는지 셋만 봅니다.
   **꼬리:** 그러면 `is_prefix` 검사를 빼면 어떻게 되나요?
   **틀리기 쉬운 답:** "Seal이 데이터를 대신 암호화해 줍니다"라고 답하는 경우가 있는데, 실제로 Seal이 관리하는 것은 열쇠를 줄지 말지입니다.
2. **Q:** (L2 판단) 열쇠 ID를 팩 ID 접두사로 잡으신 이유는 무엇이고, MemWal 방식과는 어떻게 다른가요?
   **A:** 팩 ID 32바이트에 접미사를 붙이는 방식으로 잡았고, 단계 기록은 u16 big-endian 단계 번호를, 텍스트 기억은 랜덤 5바이트를 붙였습니다. 컨트랙트가 접두사만 보기 때문에 구독권 하나로 그 팩의 블롭이 전부 열리고, 팩이 곧 접근 단위가 됩니다. MemWal의 열쇠 ID는 `BCS(owner) ‖ BCS(counter)` 하나라서 소유자당 열쇠가 1개고 델리게이트를 등록하면 계정 전체가 열리는데(최대 20개, 결제·만료 개념 없음), 기억 일부만 특정인에게 기간제로 여는 게 구조적으로 불가능했습니다. 그래서 접근 규칙을 별도 패키지에 두고 열쇠 ID를 팩 단위로 다시 잡았습니다.
   **꼬리:** 그러면 블롭 하나 단위로 팔고 싶을 때 열쇠 ID와 `seal_approve`는 어떻게 되나요?
   **틀리기 쉬운 답:** "정책만 고치면 접근 단위를 바꿀 수 있습니다"라고 답하는 경우가 있는데, 실제로는 이미 암호화된 데이터의 열쇠 ID를 바꿀 수 없습니다.
3. **Q:** (L3 한계) `ExpiredSessionKeyError`가 떴을 때 실제 원인은 무엇이었고 어떻게 찾아내셨나요?
   **A:** 이 예외가 서버 응답 `InvalidCertificate`의 SDK 쪽 이름이라는 걸 먼저 확인했고, 키 서버(`server.rs`)가 그걸 내는 조건이 TTL이 서버 `session_key_ttl_max`를 넘었을 때, 생성 시각이 서버 시계보다 미래일 때, 이미 만료됐을 때 셋뿐이었습니다. 미래 시각 쪽은 허용 오차가 0이라(`checked_duration_since()`가 `offset > now`면 `None`) PC 시계가 1ms만 빨라도 거부되더군요. 진단은 HTTPS 응답 `date` 헤더와 `Date.now()`를 비교하는 것이었고, 해결은 `w32tm /resync /force`, 좀 더 견고하게는 `SessionKey.create()` 호출 동안만 `Date.now`를 실제 값에서 측정 skew와 여유분을 뺀 값으로 감싸는 것이었습니다. 시계가 정상인데도 같은 에러가 나면 TTL 쪽이라 `ttlMin`을 1로 낮춰 봤고(배포 예시에 `session_key_ttl_max: '60s'`가 있어서 `ttlMin: 10`이 곧바로 에러가 되는 서버가 있습니다), 키 서버를 바꿔 가며 시간 낭비하지 않는 편이 낫다고 생각합니다.
   **꼬리:** 그러면 에러 이름과 실제 원인이 어긋날 때는 무엇부터 보시겠어요?
   **틀리기 쉬운 답:** "만료 에러니 TTL을 늘리면 됩니다"라고 답하는 경우가 있는데, 실제로 미래 시각 거부는 TTL과 무관합니다.
4. **Q:** (L3 한계) 구독이 만료됐는데도 같은 클라이언트로 계속 읽힌다면, 이건 버그일까요?
   **A:** 버그는 아니라고 판단했습니다. `SealClient`가 파생 키를 인스턴스에 캐시하기 때문에 한 번 `decrypt`에 성공하면 이후 복호화는 로컬에서 일어납니다. 그래서 만료나 회수를 검증하거나 데모하려면 캐시가 빈 새 `SealClient`로 시도해야 하고(`mm recall --fresh`), 뒤집어 보면 Seal의 접근 회수는 이미 열쇠를 받아간 클라이언트에 소급되지 않습니다. 설계상의 성질이라 서비스 설계에 반영해야 하고, 이걸 모르면 정책이 동작하지 않는다고 오진하기 쉽습니다.
   **꼬리:** 그러면 구독 해지 즉시 차단을 약속하는 서비스는 무엇을 더 해야 하나요?
   **틀리기 쉬운 답:** "온체인 정책이 만료를 강제하니 즉시 막힙니다"라고 답하는 경우가 있는데, 실제로는 이미 받아간 키까지 막지 못합니다.
5. **Q:** (L2 판단) 배치 복호화를 쓰신 이유와 그때 생긴 함정을 말씀해 주시겠어요?
   **A:** 블롭 N개의 열쇠 ID로 `seal_approve`를 N번 담은 PTB 하나를 만들어 `fetchKeys`를 1회만 호출하고 블롭마다 `decrypt` 하는 식으로, 왕복을 줄이려는 최적화였고 배치가 거부되면 블롭당 요청으로 물러나게 했습니다. 함정은 판매자가 다른 팩 접두사의 블롭을 섞어 두면 `seal_approve` 하나가 실패하면서 배치 전체가 거부되고, 그게 만료로 오인된다는 것이었습니다. 그래서 배치를 만들기 전에 팩 접두사가 맞지 않는 블롭을 먼저 걸러 냈습니다. `packageId`는 패키지 첫 버전이어야 해서 업그레이드할 때는 `SEAL_PACKAGE_ID`를 따로 뒀습니다.
   **꼬리:** 그러면 부분 실패를 만료와 구분해 사용자에게 알리려면 어떤 정보가 필요할까요?
   **틀리기 쉬운 답:** 배치 거부를 곧바로 권한 없음으로 표시하는 경우가 있는데, 실제로는 접두사가 섞인 부분 실패일 수 있습니다.

### 더 파볼 것
- [Using Seal (Sui Docs)](https://docs.sui.io/sui-stack/seal/using-seal) — `seal_approve` 첫 인자가 패키지 ID 접두사를 제외한 identity라는 규칙, 세션 키 TTL, SDK의 복호화 키 캐시 권장
- [Seal Design (Sui Docs)](https://docs.sui.io/sui-stack/seal/design) — t-of-n threshold 키 서버, `[PkgId]*` 형태의 IBE identity, 암호화 후에는 키 서버 집합을 바꿀 수 없다는 제약
