---
title: 테스트넷 ERC-20으로 리워드 토큰 발행하기 (Base Sepolia)
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/hana-ar-kowalk-2026-plan.md]
tags: [블록체인, ERC-20, Base, Solidity, ethers.js]
---

## 1. 한 줄 정의

해커톤 프로토타입에서 "실물 자산"을 흉내 내야 할 때, 테스트넷에 기업별 ERC-20을 배포하고 서버가 조건 충족을 확인한 뒤 `onlyOwner mint`로 유저 지갑에 지급하는 구조.

## 2. 어디서 썼는가

- [[hana-ar-kowalk-2026]] — 퀴즈 통과 시 기업별 주식 토큰 지급 (계획 단계)

## 3. 실제로 겪은 문제와 해결

네트워크는 Base Sepolia 테스트넷. 선택 이유는 Ray가 Base 해커톤 수상 경험이 있어 익숙하고, 테스트넷이라 가스비가 없으며, 추후 Base 메인넷으로 옮길 수 있기 때문. 테스트넷 ETH는 faucet에서 무료 수급.

컨트랙트는 OpenZeppelin `ERC20` + `Ownable`을 상속한 최소 구성이고, 기업마다 별도 토큰을 둔다(예: `KO_005930` = 삼성전자).

```solidity
contract KoWalkToken is ERC20, Ownable {
    constructor(string memory name, string memory symbol)
        ERC20(name, symbol)
        Ownable(msg.sender) {}

    // 서버에서 퀴즈 통과 확인 후 호출
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```

핵심 설계 판단은 **지급 권한을 온체인이 아니라 서버에 둔 것**이다. 퀴즈 채점·위치 검증 같은 조건은 오프체인에서 하고, 컨트랙트는 owner만 mint할 수 있게 해 두어 단순하게 유지한다. 발행 트랜잭션 해시는 `visits.tx_hash`에 저장해 수집 성공 화면에서 그대로 보여 준다.

지갑은 별도 월렛 앱 연동 없이 앱 내장으로 만들고 privateKey를 Secure Storage에 저장한다. 온보딩에서 자동 생성되므로 유저가 지갑 개념을 몰라도 진입할 수 있다. 프론트 연동은 ethers.js v6로 잔액 조회·포트폴리오 표시.

범위 제한: 이 토큰은 실제 주식이 아니고, 화면의 가치 표기("만원 상당")도 표시용일 뿐이라고 원자료가 명시하고 있다.

## 4. 참고 자료

- OpenZeppelin Contracts (ERC20, Ownable)
- ethers.js v6
- Base Sepolia faucet
- 원자료: `raw/done/hana-ar-kowalk-2026-plan.md`
- 관련: [[onchain-revocation-registry]] — 같은 EVM 테스트넷(Sepolia 계열) 위에 컨트랙트를 올린 다른 사례. 이쪽은 리워드 발행, 저쪽은 자격증명 폐기 기록.
