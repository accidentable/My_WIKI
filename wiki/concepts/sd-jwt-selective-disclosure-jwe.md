---
title: SD-JWT 선택적 공개와 JWE 봉인을 함께 쓰기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-sabonx-apis.md, raw/done/blockchain-valley-2026-trust404-readme.md]
tags: [SD-JWT, JWE, 선택적공개, 개인정보, DID]
---

## 한 줄 정의

SD-JWT는 **무엇을 보여줄지**(공개 범위)를 정하고, JWE는 **보여준 값을 누가 읽을지**(기밀성)를 정한다. 둘은 대체재가 아니라 역할이 다르므로 한 제출 묶음에 함께 쓴다.

## 어디서 썼는가

- [[blockchain-valley-2026-sabonx]] — 급여 제출에서 이름은 선택 공개, 주민등록번호는 모의 국세청만 열 수 있게 봉인.

## 실제로 겪은 문제와 해결

**문제.** SD-JWT는 공개하지 않을 항목을 숨기지만, 공개한 항목을 암호화하지는 않는다. 세무 처리를 위해 전달해야 하는 주민등록번호는 검증자(사업주)가 읽으면 안 되는데, 그렇다고 빼면 신고가 안 된다.

**구현.**
- 발급기관이 선택 공개 항목마다 salt와 함께 해시해 다이제스트를 VC 본체에 넣고 서명한다.
- 지갑은 필요한 항목의 Disclosure만 붙여 제시한다(SabonX 급여 흐름에서는 이름만).
- 주민등록번호는 모의 국세청의 X25519 공개키로 `ECDH-ES+A256KW` / `A256GCM` JWE 암호화하고, 암호문을 발급기관 서명이 보호하는 `rrn_sealed` 클레임에 넣는다.

**결과.**
- 주소·사진 등 미제출 항목은 검증자에게 **다이제스트만** 남는다(API 응답의 `withheldDigests`). 키 이름도 값도 알 수 없다.
- 이름은 검증자가 읽고, 주민번호는 수신자 개인키로만 열린다. 이를 증명하려고 "항상 실패하는" 봉인 열기 엔드포인트(`POST /api/verifier/:sessionId/open`)를 데모에 두었다. 검증자 자신의 개인키로는 복호화가 실패하고, 국세청 공개키로는 `must be of type "private"` 오류가 난다.
- 발급 응답의 `plaintextRrnInCredential`은 자격증명 전체를 문자열 검색한 결과로, 항상 `false`여야 한다.
- 최종 결정권은 지갑에 있다. 제시 API의 `deny`로 요청받은 항목도 뺄 수 있다.

**남는 한계.** 데모의 기관 키가 같은 프로세스에 있으므로 서버 전체에 대한 키 격리를 보장하지는 않는다.

## 참고 자료

- 라이브러리: `@sd-jwt/sd-jwt-vc`, `jose`, `@noble/curves`
