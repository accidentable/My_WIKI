---
title: 온체인 폐기 레지스트리와 fail-closed 검증
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-sabonx-apis.md, raw/done/blockchain-valley-2026-trust404-readme.md]
tags: [블록체인, Sepolia, Solidity, 폐기, VC]
---

## 한 줄 정의

VC의 폐기 여부를 개인정보 없이 **인덱스 번호만** 체인에 기록하고, 제출 시 그 상태를 RPC로 읽어 판정하는 구조. 조회에 실패해도 접수하지 않는 fail-closed가 핵심이다.

## 어디서 썼는가

- [[blockchain-valley-2026-sabonx]] — 주소 변경으로 폐기된 이전 VC의 제출을 서버 검증에서 거절.

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
- 관련: [[testnet-reward-token]] — 같은 EVM 테스트넷 컨트랙트 사례([[hana-ar-kowalk-2026]]의 ERC-20 리워드 토큰). 온체인에 무엇을 올릴지 기준이 대비된다.
