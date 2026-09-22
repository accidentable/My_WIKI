---
title: Seal 열쇠 ID 정책과 세션 키 함정
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-dev-memories.md]
tags: [블록체인, Sui, Seal, 암호화, 접근제어]
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
