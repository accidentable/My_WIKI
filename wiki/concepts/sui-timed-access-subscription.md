---
title: Sui 객체 모델과 Clock으로 만든 기간 한정 접근권
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md]
tags: [블록체인, Sui, Move, 객체모델, 구독, Clock]
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
