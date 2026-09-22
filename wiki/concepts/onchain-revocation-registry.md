---
title: 온체인 폐기 레지스트리와 fail-closed 검증
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-sabonx-apis.md, raw/done/blockchain-valley-2026-trust404-readme.md, raw/done/blockthon-2026-memory-market-readme.md]
tags: [블록체인, Sepolia, Solidity, 폐기, VC]
cs_topics: [보안, 분산시스템, 네트워크, 블록체인]
---

## 한 줄 정의

VC의 폐기 여부를 개인정보 없이 **인덱스 번호만** 체인에 기록하고, 제출 시 그 상태를 RPC로 읽어 판정하는 구조. 조회에 실패해도 접수하지 않는 fail-closed가 핵심이다.

## 어디서 썼는가

- [[blockchain-valley-2026-sabonx]], 주소 변경으로 폐기된 이전 VC의 제출을 서버 검증에서 거절.
- [[blockthon-2026-memory-market]], 같은 계열이지만 **의도적으로 fail-open**인 대비 사례. 판매자가 낡은 단계를 `retract`하면 `RetractKey{blob_id}` → `Retraction{reason, at_ms}`가 팩에 남지만, 접근 승인 함수 `seal_approve`는 열쇠 ID만 보고 blob_id를 모르므로 폐기를 검사하지 않는다. 폐기된 단계도 구독자에게는 여전히 열리고(Move 테스트로 명시), 구매자 도구가 `is_retracted`로 걸러 준다. 즉 "더는 권하지 않음" 표식이지 회수가 아니다. 폐기를 어디서 판정하느냐(검증기 안이냐 클라이언트냐)가 fail-closed와 fail-open을 가른다. 자세한 것은 [[onchain-buyer-only-receipt]].

## 실제로 겪은 문제와 해결

**문제.** 주소가 바뀌어도 이전 VC의 서명은 수학적으로 여전히 유효하다. 화면 버튼만 막으면 서버 차원의 폐기 검증이 아니다.

**구현.**
- VC의 `statusIndex`는 발급기관 서명에 포함된 폐기 식별자다.
- 정보 변경 시 기관 권한으로 `revoke(statusIndex)` 트랜잭션을 보내고 성공을 기다린 뒤 변경 상태를 반영한다.
- 제출 시 검증기가 `revoked(statusIndex)`를 RPC로 읽는다. 폐기되었거나 **조회에 실패하면 접수하지 않는다(fail-closed)**.
- 체인 환경변수가 없으면 LOCAL STUB 폐기 목록을 쓴다. 스텁일 때는 온체인 확인으로 표시하지 않는다.

**결과.**
- 데모의 '무시하고 제출하기'는 화면 제한만 넘고 실제 서버 검증을 받는다.
- 폐기가 확인된 경우에만 거절 화면을 띄운다. RPC 장애를 폐기로 표시하지 않는다(둘을 구분한다).
- 새 VC를 발급받으면 기존 미완료 요청에 다시 제출할 수 있다.
- 폐기는 VC의 유효성 취소이지 개인키 삭제가 아니다.

**비용과 노출.**
- 조회는 `eth_call`이라 가스비도 새 트랜잭션도 없다. Etherscan 링크는 조회가 아니라 **폐기 트랜잭션**을 보여준다.
- RPC 제공자는 조회하는 식별자를 볼 수 있다.
- 체인에는 폐기 식별자와 상태·이벤트만 올라가고, 이름·주소·주민등록번호 원문은 올리지 않는다.

**블록체인이 보장하지 않는 것.** 여러 검증자가 폐기 기록을 같은 기준으로 확인하게 해줄 뿐, 개인정보의 진실성이나 기관의 정직함을 자동으로 보장하지 않는다.

## 참고 자료

- 구현: Solidity 컨트랙트 + Foundry 테스트, `viem` + Sepolia RPC, `src/shared/revocation.ts`
- 환경변수: `CHAIN_ID`(Sepolia `11155111`), `RPC_URL`, `REGISTRY_ADDRESS`, `ISSUER_CHAIN_KEY`(Sepolia 테스트 ETH 필요)
- 데모 컨트랙트: `0x6c30f02f3f5e31a9a0616c5b9756d8498a6b66e5`
- 상태 확인: `GET /api/chain`의 `isStub`, `GET /api/revocation/:index`
- 관련: [[testnet-reward-token]], 같은 EVM 테스트넷 컨트랙트 사례([[hana-ar-kowalk-2026]]의 ERC-20 리워드 토큰). 온체인에 무엇을 올릴지 기준이 대비된다.

## 학습

### CS 주제
- 보안: fail-closed / fail-open, 신뢰 경계와 클라이언트 측 검증의 무효함
- 분산시스템: 외부 상태 조회 실패의 처리, 장애와 부정 응답의 구분
- 네트워크: RPC 호출 실패 모드, 조회 메타데이터 노출
- 블록체인: 온체인에 무엇을 올릴지의 기준, `eth_call`과 트랜잭션의 차이

### 설명할 수 있어야 하는 것
- 왜 이 방법을 골랐는가: 서명이 수학적으로 유효한 옛 VC를 무효로 만들려면 서명 바깥에 상태 저장소가 필요했고, 여러 검증자가 같은 기준으로 볼 수 있어야 해서 체인을 썼다.
- 대안은 무엇이었고 무엇을 포기했는가: 화면 버튼 차단은 서버 검증이 아니어서 버렸다. 인덱스만 올려 개인정보 노출을 피하는 대신, RPC 제공자에게 조회 식별자가 보이는 것은 감수했다.
- 어떤 조건에서 깨지는가: RPC 장애 시 fail-closed라 정상 사용자도 접수되지 않는다. 가용성을 정합성과 맞바꾼 선택이다.

### 확인 질문
1. **Q:** (L1 개념) VC 폐기를 왜 체인에 따로 기록해야 하며, 무엇을 올리고 무엇을 올리지 않았는가?
   **A:** VC의 서명은 발급 시점의 내용에 대한 것이라, 주소가 바뀌어도 옛 VC의 서명은 수학적으로 여전히 유효하다. 따라서 "이 자격증명은 더는 유효하지 않다"는 사실은 서명 바깥의 상태 저장소에 있어야 한다. 이 프로젝트는 VC에 발급기관 서명으로 포함된 `statusIndex`(폐기 식별자)만 체인에 올리고, 상태와 이벤트 외에 이름·주소·주민등록번호 원문은 올리지 않았다. 체인을 쓴 이유는 여러 검증자가 같은 폐기 기록을 같은 기준으로 확인하게 하기 위해서다.
   **꼬리:** 인덱스만 올려도 남는 프라이버시 문제는 무엇인가?
   **틀리기 쉬운 답:** "블록체인에 올렸으니 개인정보의 진실성도 보장된다"는 답. 체인은 기록의 공유와 변조 저항을 줄 뿐 기관의 정직함을 보장하지 않는다.
2. **Q:** (L2 판단) 폐기 상태 조회에 실패했을 때 접수를 막는 fail-closed를 택한 이유는?
   **A:** 조회 실패를 "폐기 아님"으로 처리하면 공격자가 RPC를 방해하는 것만으로 폐기된 VC를 통과시킬 수 있다. 그래서 검증기는 `revoked(statusIndex)`를 읽어 폐기되었거나 조회에 실패하면 접수하지 않는다. 다만 화면에서는 둘을 구분해, 폐기가 확인된 경우에만 거절 화면을 띄우고 RPC 장애를 폐기로 표시하지는 않는다. 또 체인 환경변수가 없으면 LOCAL STUB 목록을 쓰되 그때는 온체인 확인으로 표시하지 않는다(`GET /api/chain`의 `isStub`).
   **꼬리:** fail-closed 때문에 정상 사용자가 막히는 상황은 어떻게 완화할 수 있는가?
   **틀리기 쉬운 답:** "조회 실패는 일시적이니 통과시키고 나중에 재검증"이라는 답. 접수 자체가 결과를 만드는 흐름에서는 되돌릴 수 없다.
3. **Q:** (L3 한계) 같은 계열 구조인데 Memory Market의 `retract`는 왜 fail-open인가? 무엇이 둘을 가르는가?
   **A:** 판매자가 낡은 단계를 `retract`하면 `RetractKey{blob_id}` → `Retraction{reason, at_ms}`가 팩에 남지만, 접근 승인 함수 `seal_approve`는 열쇠 ID만 보고 blob_id를 모르므로 폐기를 검사하지 않는다. 그래서 폐기된 단계도 구독자에게는 여전히 열리고(Move 테스트로 명시), 구매자 도구가 `is_retracted`로 걸러 준다. 즉 폐기 판정이 검증기 안에 있으면 fail-closed가 되고, 클라이언트에 있으면 fail-open이 된다. Memory Market의 폐기는 회수가 아니라 "더는 권하지 않음" 표식이다.
   **꼬리:** `seal_approve`가 blob_id를 볼 수 있게 하려면 열쇠 ID 설계를 어떻게 바꿔야 하는가?
   **틀리기 쉬운 답:** "온체인에 폐기 기록이 남으니 접근도 막힌다"는 답. 기록과 집행은 별개다.

### 더 파볼 것
- [Revocation List 2020 (W3C CCG)](https://w3c-ccg.github.io/vc-status-rl-2020/) — 인덱스 기반 폐기 목록의 표준형과, 인덱스 조회가 만드는 상관관계(correlation) 위험
- [OpenZeppelin Access Control](https://docs.openzeppelin.com/contracts/5.x/access-control) — 폐기 트랜잭션을 보낼 수 있는 "기관 권한"을 컨트랙트에서 어떻게 표현하는가
