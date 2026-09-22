---
title: 키 바인딩(KB-JWT)과 업무 승인 JWT 결합
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-sabonx-apis.md, raw/done/blockchain-valley-2026-trust404-readme.md]
tags: [KB-JWT, JWS, VC, 키바인딩, 동의]
---

## 한 줄 정의

KB-JWT는 "지금 제출한 사람이 그 VC의 주인"임을 증명하고, 별도의 승인 JWT는 "그 사람이 **이 금액·이 달의 요청**에 동의했다"를 증명한다. 신원 증명과 업무 동의는 다른 문제라서 서명을 두 개 쓴다.

## 어디서 썼는가

- [[blockchain-valley-2026-sabonx]] — 월 급여 요청 승인과 소득 신고 제출.

## 실제로 겪은 문제와 해결

### 문제 1: 복사한 VC로 다른 사람이 제출

발급기관 서명만으로는 제출자가 정당한 소유자인지 알 수 없다.

- 기관이 홀더 공개키를 `cnf.jwk`로 VC에 결합한다.
- 지갑이 그 개인키로 KB-JWT를 만들어 요청의 `nonce`, 수신자 `aud`, 제시 내용의 `sd_hash`를 서명한다.
- 검증기는 VC에 묶인 공개키로 확인한다.

결과: VC만 복사하거나 다른 키로 서명한 제출은 거절된다. nonce·aud 검증이 제출 묶음의 다른 요청 재사용도 막는다. 단, **개인키 자체가 탈취되는 문제는 해결하지 못한다.**

### 문제 2: 유효한 신원 제시 ≠ 특정 금액 동의

지급 요청이나 제시 묶음을 바꿔 끼우는 공격도 막아야 한다.

- 서버가 금액·월·사업체·근로자 공개키·nonce를 담은 **요청 JWT**를 서명한다.
- 브라우저가 요청 서명을 검증하고 화면 내용과 대조한다.
- 지갑이 별도의 **승인 JWT**를 서명한다.

```text
request_id        = 승인할 급여 요청
request_hash      = SHA-256(서명된 요청 JWT)
presentation_hash = SHA-256(SD-JWT 제시 + KB-JWT)
decision          = approve
```

결과: 서버는 두 서명과 요청 대상 공개키를 함께 검증한다. 9월에 승인했더라도 금액이 다른 10월 요청에는 새 승인이 필요하다.

### 문제 3: 실기기 시계 차이

실기기 시연에서 브라우저의 `iat`가 서버 시각보다 앞서 발급이 거절됐다. JWT 검증에 **60초 Clock Tolerance**를 적용했다. 시간 검증을 없앤 것이 아님을 확인하려고, 30초 미래 요청은 허용하고 과도한 미래·만료 요청은 거절하는 테스트를 둔다.

### 동시 제출

같은 요청의 동시 제출은 세션 잠금과 `pending → accepted` 상태 전이로 한 번만 접수한다. 정정 요청은 `correction` 상태로 바꿔 승인을 막는다. 단일 서버 메모리 기반이라 다중 인스턴스에는 DB 트랜잭션이 필요하다.

## 참고 자료

- 검증기 내부 검사 중 관련 항목: `kb-signature`, `kb-nonce`, `kb-audience`, `kb-sd-hash`
