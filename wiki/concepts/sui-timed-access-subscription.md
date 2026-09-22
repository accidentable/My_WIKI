---
title: Sui 객체 모델과 Clock으로 만든 기간 한정 접근권
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md]
tags: [블록체인, Sui, Move, 객체모델, 구독, Clock]
cs_topics: [운영체제, 분산시스템, 데이터베이스, 블록체인]
---

## 한 줄 정의

결제와 구독권 발급을 한 트랜잭션에 담고 만료를 온체인 `Clock`으로 재서, 에스크로도 정산 서버도 없이 "정해진 기간만 열리는 접근권"을 객체 하나로 만드는 구조.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], 경험 팩 구독. 0.05 SUI · 7일, 0.01 SUI · 24시간 등.

## 객체 셋과 dynamic field

| 객체 | 종류 | 역할 |
|---|---|---|
| `MemoryPack` | shared | 팩 하나. 이름 · 설명 · `fee`(MIST) · `ttl_ms` · 출처(`source_namespace`, `agent_label`) · `memory_count` · `subscriber_count` · `preview_blob_ids` |
| `PackCap` | owned, 판매자 | `publish` · `add_preview` · `set_terms` · `retract` 권한 |
| `Subscription` | owned, 구매자 | `subscribe`가 발급. `expires_at_ms`가 지나면 Seal 승인이 거부됨 |

나머지는 전부 팩 UID 아래 dynamic field로 붙인다. `String`(blob_id) → 표식 `u64`(등록된 암호문 블롭), `ReceiptKey{subscription_id}` → `Receipt`, `RetractKey{blob_id}` → `Retraction`. 덕분에 **v1 배포 뒤 객체 레이아웃을 바꾸지 않고** 영수증과 폐기 기능을 더할 수 있었다.

## 실제로 겪은 문제와 해결

- **정산이 필요 없다.** `subscribe`가 `Coin<SUI>`가 정확히 `fee`인지 확인하고 판매자에게 바로 보낸 뒤 `Subscription`을 돌려준다. 에스크로 계약도, 나중에 나눠 주는 배치도 없다.
- **시간을 컨트랙트가 잰다.** `expires_at_ms = now + ttl_ms`, `now`는 `Clock`(`0x6`). 오프체인 서버 없이 기간제가 성립한다.
- **접근 규칙이 컨트랙트에 있다.** `seal_approve(id, sub, pack, clock)`는 셋만 본다. 구독권이 이 팩 것인가, 만료 전인가, 열쇠 ID가 팩 ID로 시작하는가. 구독권이 **소유 객체**라 sender 소유 검증이 자연스럽게 된다.
- **PTB 하나로 올린다.** `create_pack` + `publish`×N + `add_preview`×3을 한 트랜잭션에. 15단계 + 미리보기 3건이 tx 한 건(`2umb7v5N…`)이다.
- **목록은 GraphQL, 쓰기는 gRPC.** gRPC의 이벤트 색인은 최근 체크포인트만 들고 있어 며칠 지난 `PackCreated`가 안 나온다. 그래서 팩 목록만 `graphql.testnet.sui.io`로 읽고, 랜딩도 CORS `*`인 같은 GraphQL을 브라우저에서 직접 읽는다. 자세한 함정은 [[sui-sdk-rpc-migration-2026]].
- **만료의 한계.** 만료는 새 세션·새 클라이언트에만 적용된다. 이미 키를 받아간 클라이언트에는 소급되지 않는다([[seal-key-policy-and-session-traps]]).
- **짧은 ttl 팩은 목록에서 자동 제외.** e2e 테스트 팩이 시장에 섞이지 않게 ttl 5분 미만은 숨긴다. 반대로 만료 시연용 팩을 만들 때는 이 규칙 때문에 6분 ttl을 써야 했다.

## 참고 자료

- `contracts/memory_market/`, 이벤트 `PackCreated` · `MemoryPublished` · `Subscribed` · `ReceiptLeft` · `Retracted`, Move 테스트 19개
- Seal 공식 예제 `MystenLabs/seal` `examples/move/sources/{allowlist,subscription}.move`

## 학습

### CS 주제
- 운영체제: 시간 출처의 신뢰(온체인 `Clock` vs 클라이언트 시계), 만료와 캐시 무효화
- 분산시스템: 합의를 거치는 shared object와 그렇지 않은 owned object, 원자적 트랜잭션
- 데이터베이스: 고정 스키마 대 확장 가능한 키-값(dynamic field) 설계
- 블록체인: 결제와 권한 발급의 원자성, 에스크로 없는 정산

### 설명할 수 있어야 하는 것
- 왜 이 방법을 골랐는가: 결제·구독권 발급·만료 판정을 전부 컨트랙트 안에 넣어 에스크로 계약도 정산 서버도 없애려고 객체 하나로 접근권을 표현했다.
- 대안은 무엇이었고 무엇을 포기했는가: 오프체인 서버가 기간을 관리하면 유연하지만 서버를 믿어야 한다. 온체인 `Clock`을 쓰는 대신 shared object 합의 비용을 받아들였다.
- 어떤 조건에서 깨지는가: 만료는 새 세션·새 클라이언트에만 적용되고 이미 키를 받아간 클라이언트에는 소급되지 않는다.

### 확인 질문
1. **Q:** (L1 개념) Sui의 shared object와 owned object 차이는 무엇이고, 이 설계에서 무엇을 어느 쪽으로 뒀는가?
   **A:** shared object는 누구나 접근할 수 있어 트랜잭션이 합의를 거쳐야 하고, owned object는 소유자 주소에 귀속돼 소유자만 쓸 수 있다. Memory Market은 팩 자체인 `MemoryPack`을 shared로 두어 누구나 구독할 수 있게 하고, 판매자 권한인 `PackCap`과 구매자 접근권인 `Subscription`을 owned로 뒀다. `Subscription`이 소유 객체라 `seal_approve`에서 sender 소유 검증이 자연스럽게 성립한다. 시간을 재는 `Clock`(`0x6`)도 shared object이므로 이 함수를 쓰는 트랜잭션은 합의를 거친다.
   **꼬리:** `Subscription`을 shared로 뒀다면 어떤 검사를 추가로 해야 하는가?
   **틀리기 쉬운 답:** "owned object라 온체인에 없다"는 답. 소유 여부와 온체인 존재는 별개다.
2. **Q:** (L2 판단) 객체 필드가 아니라 dynamic field로 영수증·폐기·블롭 목록을 붙인 이유는?
   **A:** 구조체 필드는 모듈을 배포할 때 고정되지만 dynamic field는 객체 생성 뒤에도 임의의 키로 붙였다 뗄 수 있고, 접근할 때만 가스에 영향을 준다. Memory Market은 팩 UID 아래에 `String`(blob_id) → 표식 `u64`, `ReceiptKey{subscription_id}` → `Receipt`, `RetractKey{blob_id}` → `Retraction`을 붙였다. 덕분에 v1 배포 뒤 객체 레이아웃을 바꾸지 않고 영수증과 폐기 기능을 더할 수 있었다. 블롭 수가 팩마다 다르고 미리 알 수 없다는 점도 고정 필드가 맞지 않는 이유였다.
   **꼬리:** 항목이 수만 개로 늘면 dynamic field 기반 목록 조회에서 무엇이 문제가 되는가?
   **틀리기 쉬운 답:** "dynamic field는 그냥 벡터를 대신한다"는 답. 조회 방식과 가스 특성이 다르다.
3. **Q:** (L3 한계) 온체인 `Clock`으로 만료를 재는데도 "만료된 사람이 계속 읽는" 일이 생긴다. 왜인가?
   **A:** `subscribe`가 `expires_at_ms = now + ttl_ms`를 박아 두고 `seal_approve(id, sub, pack, clock)`가 만료 전인지 검사하므로, 새 세션이나 새 클라이언트는 만료 후 열쇠를 받지 못한다. 그러나 만료는 새 세션·새 클라이언트에만 적용되고 이미 열쇠를 받아간 클라이언트에는 소급되지 않는다. 즉 온체인 시간 검사는 "열쇠 발급 시점"의 게이트이지 이미 나간 열쇠의 회수 수단이 아니다. 데모에서도 짧은 ttl 팩은 목록에서 자동 제외(5분 미만 숨김)되기 때문에 만료 시연용 팩은 6분 ttl로 만들어야 했다.
   **꼬리:** 진짜 회수가 필요한 서비스라면 어떤 계층을 추가해야 하는가?
   **틀리기 쉬운 답:** "만료를 컨트랙트가 강제하니 접근이 즉시 끊긴다"는 답.
4. **Q:** (L2 판단) 왜 목록 조회는 GraphQL, 쓰기는 gRPC로 나눠 썼는가?
   **A:** gRPC의 이벤트 색인은 최근 체크포인트만 들고 있어 며칠 지난 `PackCreated` 이벤트가 조회되지 않았다. 그래서 팩 목록만 `graphql.testnet.sui.io`로 읽고, 랜딩 페이지도 CORS가 `*`인 같은 GraphQL을 브라우저에서 직접 읽게 했다. 쓰기(트랜잭션 실행)는 gRPC 쪽이다. 또 `create_pack` + `publish`×N + `add_preview`×3을 PTB 하나에 담아 15단계 + 미리보기 3건을 트랜잭션 한 건으로 올렸다.
   **꼬리:** PTB로 묶은 트랜잭션 중 한 호출이 abort하면 나머지는 어떻게 되는가?
   **틀리기 쉬운 답:** "RPC는 다 같으니 아무거나 쓰면 된다"는 답. 색인 보존 범위가 다르다.

### 더 파볼 것
- [Access On-Chain Time (Sui Docs)](https://docs.sui.io/guides/developer/sui-101/access-time) — `0x6` Clock, `timestamp_ms`, 불변 참조로만 받아야 하는 이유와 합의 비용
- [Dynamic (Object) Fields (Sui Docs)](https://docs.sui.io/concepts/dynamic-fields) — 생성 후 추가, 임의 키, 접근할 때만 드는 가스
