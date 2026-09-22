---
title: SabonX, 신분증 사본 없이 월급 확인·소득 신고 (DID/VC)
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-sabonx-apis.md, raw/done/blockchain-valley-2026-trust404-readme.md]
repo: https://github.com/accidentable/Trust404_th
tags: [블록체인, DID, VC, SD-JWT, 개인정보, 프로토타입]
---

# SabonX, 주민등록증, 안전하게

## 1. 개요

- **코드 저장소**: https://github.com/accidentable/Trust404_th — SabonX-iM-Challenge 폴더는 같은 코드의 iM 제출본 (출처: 로컬 git 원격, 2026-09-22 확인)

- 대회: **2026 AI Blockchain Challenge in Daegu** 제출용 프로토타입. 같은 결과물을 **TRUST404 Track 02** 해커톤 프로토타입으로도 제출했다(두 README가 동일 구현을 각 대회명으로 소개).
- 기간: 자료에 없음.
- 주제: 신분증 사본을 사업주에게 넘기지 않고, DID·VC로 필요한 정보만 증명해 월급 확인부터 소득 신고까지 연결하는 서비스.
- 결과(수상 여부): **자료에 없음.**
- 데모: `https://211-233-200-43.nip.io/` (앱은 `/app`), Sepolia 폐기 레지스트리 컨트랙트 `0x6c30f02f3f5e31a9a0616c5b9756d8498a6b66e5`.
- AI 활용: 초기 구현은 Claude Code, 현재 앱 UI·급여 승인·변경 요청·폐기 결과·테스트·문서 개선은 OpenAI Codex. 문제 정의와 시연 방향은 사람이 정하고 결과를 검토·수정.

> 참고: SabonX와 TRUST404는 별개 프로젝트가 아니라, **같은 SabonX 구현의 두 대회 제출본**이다. 차이는 배지(TRUST404 Track 02)와 로컬 실행 안내(제출 ZIP 폴더명·저장 키 안내)뿐이다.

## 2. 문제 정의

급여 처리를 위해 신분증 사본 전체를 넘기면 업무에 필요 없는 사진·주소까지 상대에게 간다. SabonX는 신분증 이미지 대신 발급기관이 서명한 자격증명(VC)을 쓰고, 필요한 항목만 제출하는 흐름을 제안한다.

- 근로자는 월별 급여 내역을 확인하고 직접 서명한다. 금액이 틀리면 정정 메시지를 보낸다.
- 이름은 선택 공개하고, 주민등록번호는 모의 국세청만 복호화하도록 JWE로 봉인한다.
- 사업주는 근로자 이름·급여 요청 상태·모의 접수 결과만 본다.
- 정보 변경으로 폐기된 VC는 서명이 유효해도 제출 단계에서 거절한다.

## 3. 접근

### 아키텍처(논리 역할)

모의 주민센터(Issuer) → SD-JWT VC 발급 → 근로자 브라우저 지갑(Holder). 사업주 화면이 월 급여를 요청하면 SabonX 요청 관리가 서명된 요청을 지갑에 보내고, 지갑은 선택 공개 + KB-JWT + 승인 JWT를 모의 국세청(Verifier)에 제출한다. 검증기는 Sepolia IssuerRegistry에 폐기 상태를 RPC로 조회한 뒤 모의 접수 결과를 돌려준다.

단, 데모에서는 요청 관리·발급기관·세무 검증기가 **하나의 Node.js/Express 프로세스**에서 돈다. 기관 키가 인프라 수준으로 격리된 구조는 아니다.

### 기술 스택

TypeScript, React, Vite, Node.js/Express, Solidity, Docker. 암호 연산은 `jose`, `@noble/curves`, `@sd-jwt/sd-jwt-vc`. 지갑 저장은 IndexedDB + `idb-keyval`. 체인 접근은 viem + Sepolia RPC. 배포는 Ncloud + Docker Compose + Caddy.

| 기술 | 역할 |
|---|---|
| `did:key` · Ed25519 | 공개키 기반 식별자와 전자서명 (DID 자체가 실명 확인은 아님) |
| SD-JWT VC | 기관 서명 + 홀더 공개키 결합, 항목별 선택 공개 |
| `cnf.jwk` · KB-JWT | 제시자가 VC에 묶인 키의 소유자임을 nonce·aud·sd_hash로 증명 |
| JWS · 승인 JWT | 특정 급여 요청과 제출 묶음에 대한 동의를 해시로 결합 |
| JWE · X25519 | 주민번호를 `ECDH-ES+A256KW`/`A256GCM`으로 봉인 |
| Solidity · Sepolia | 폐기 기록 쓰기와 제출 시 폐기 상태 읽기 |

개념 상세는 [[sd-jwt-selective-disclosure-jwe]], [[vc-key-binding-approval-jwt]], [[onchain-revocation-registry]] 참고.

### 데모 시나리오

근로자 **윤태호**, 사업장 **카페 온유**, 테스트 번호 `010-0000-1234`(전부 가상 데이터).
발급 → 9월 급여 950,000원 접수 → 10월 승진·인상 요청 → 이사로 주소 변경(기존 VC 온체인 폐기) → 이전 VC로 '무시하고 제출하기' 시 서버 폐기 검증에서 거절 → 재발급 후 같은 10월 요청 정상 접수.

'무시하고 제출하기'는 화면의 사전 제한만 건너뛴다. 서버의 서명·폐기 검증은 우회하지 않는다.

### 데이터 보관과 신뢰 경계

| 위치 | 보관 내용 |
|---|---|
| 브라우저 지갑 | 개인키, 현재 VC, 폐기 시연용 이전 VC |
| 서버 발급 메타데이터 | 공개키, 폐기 식별자, 만료 시각, 변경 상태, 폐기 이력 (전체 VC 사본은 없음) |
| 서버 업무 기록 | 급여 요청, 이름, 정정 메시지, 처리 상태, 최소 검증 결과, 서명된 접수증 |
| 모의 기관 데이터 | 데모 발급용 가상 신원정보와 기관 키 |
| Sepolia | 폐기 식별자와 상태·이벤트·트랜잭션 (이름·주소·주민번호 원문은 올리지 않음) |

제출된 VP·승인 토큰·복호화한 주민번호는 업무 기록에 저장하지 않는다. 다만 모의 기관 원천 데이터는 남으므로 '데모 서버 전체에 주민번호가 없다'고 주장하지 않는다.

### API 표면 (레거시 단계별 검증 흐름)

`raw/done/blockchain-valley-2026-sabonx-apis.md`는 역할별 엔드포인트를 단계별로 눌러 보는 흐름을 설명한다. 현재 앱(`server/payrollRoutes.ts`) 이전의 검증 데모 경로로 보인다(추정, README가 `/legacy/*` 경로와 단계별 검증 스크립트를 "기존 암호 검증 흐름 재현용"으로 유지한다고 적음). 이 흐름에서 검증자는 국세청이 아니라 **사장님**이다.

- `POST /api/issuer/issue`, 발급. 응답의 `plaintextRrnInCredential`은 자격증명 전체를 문자열 검색한 결과로 항상 `false`여야 한다.
- `POST /api/issuer/revoke`, 분실 신고. 폐기 레지스트리에 **인덱스 번호만** 기록하고 txHash·Etherscan 링크를 돌려준다.
- `GET /api/holder/:holderId` / `POST /api/holder/:holderId/present`, 지갑 확인과 제시 생성. `deny`로 요청받은 항목도 뺄 수 있어 최종 결정권은 지갑에 있다. (이 엔드포인트의 지갑은 내용 확인용으로 서버가 대신 든다. 폰 흐름 `/wallet`에서는 개인키가 폰 IndexedDB에만 있다.)
- `GET /api/verifier/:sessionId`, 내부 검사 11개(`issuer-trusted` `issuer-signature` `validity` `credential-type` `disclosure-digests` `kb-signature` `kb-nonce` `kb-audience` `kb-sd-hash` `revocation` `library-crosscheck`)와 화면용 4줄 요약. `withheldDigests`로 미제출 항목은 다이제스트만 남는다.
- `POST /api/verifier/:sessionId/open`, **항상 실패하는** 엔드포인트. 사장님 개인키로도, 국세청 공개키로도 봉인이 열리지 않음을 보여주는 것이 목적이다.
- `POST /api/tax/unseal`, 국세청 개인키로 봉인을 열어 일용근로소득 지급명세서를 만든다. 세액은 0원이어도 명세서에는 주민번호 13자리가 필요하다는 점이 이 데모의 논거다.
- 그 외: `GET /api/chain`(브라우저가 직접 RPC를 읽도록 레지스트리 설정 제공), `GET /api/revocation/:index`, `POST /api/merchant`, `POST /api/session`, `POST /api/session/:id/vp`.

## 4. 잘된 점 / 안된 점

### 잘된 점
- 새 암호 알고리즘을 만들지 않고, SD-JWT/JWE/KB-JWT/온체인 폐기 각각의 **보장 범위를 구분해** 하나의 업무 요청에 결합했다.
- 데모가 "막혀야 할 것이 실제로 막히는지"를 보여준다: 이전 VC 제출 거절, 봉인 열기 실패 엔드포인트, 미제출 항목의 다이제스트 노출.
- 서버 VC 캐시를 제거해 지갑 밖에 전체 VC 사본이 남지 않게 했다.
- 통합 테스트(`npm run test:payroll`)가 발급·선택공개·접수, 잘못된 키·승인 변조·중복 제출 거절, 정정 메시지, 권한 거부, 이전 VC 거절/재발급 접수, 시계 오차 허용 범위를 확인한다.

### 안된 점 / 한계 (문서가 스스로 밝힌 범위)
- 기관 키가 같은 프로세스에 있어 인프라 수준 키 격리가 없다.
- 브라우저 내장 지갑이라 사이트 코드가 개인키를 읽을 수 있다. XSS·악성 배포에 대한 하드웨어 수준 보호 없음. 외부 지갑 연동은 미구현.
- 서버 상태가 메모리 Map이라 재시작하면 새 데모를 시작해야 하고, 다중 인스턴스에는 DB 트랜잭션이 필요하다.
- 기관 신원 확인, 이름·주소 변경 승인, 전화번호 라우팅, 세무 접수는 전부 모의. 실제 SMS·푸시·송금·세액 계산·납부 없음. 알림은 폴링.
- 요청은 데모당 50건, 세션 24시간·서버당 최대 200개.
- 기기 변경·키 복구, 실서비스 인증·인가, 공식 기관 연동과 법적 효력은 범위 밖. 키까지 잃으면 새 세션이 필요하다.
- 로컬 스텁 테스트 통과가 실제 Sepolia 쓰기 성공을 뜻하지 않는다.

## 5. 재사용 가능한 것

- `src/issuer`, `src/holder`, `src/verifier`, `src/tax`: 발급·제시·검증·복호화 모듈
- `src/shared/revocation.ts`: 온체인 및 로컬 스텁 폐기 레지스트리 (체인 환경변수가 없으면 **LOCAL STUB** 사용)
- `contracts`: Solidity 컨트랙트와 Foundry 테스트
- `scripts/payroll-test.ts`: 현재 앱 통합 테스트
- `src/ui/pages/PayApp.tsx`, `src/ui/pages/PayReview.tsx`: 역할별 앱과 급여 확인·선택 공개·승인 슬라이드 UI
- `server/payrollRoutes.ts`: 현재 앱 API
- 운영 패턴: Docker Compose + Caddy(HTTPS) 앱 갱신 절차, `/api/chain`으로 `isStub` 확인
- 환경변수 규약: `ISSUER_SEED`/`TAX_SEED`(base64url 32바이트), `CHAIN_ID`(Sepolia `11155111`), `RPC_URL`, `REGISTRY_ADDRESS`, `ISSUER_CHAIN_KEY`, `SITE_ADDRESS`/`ACME_EMAIL`
- 문서 구성: [frontend README 템플릿](https://github.com/yewon-Noh/readme-template/tree/main/frontend)을 따른 소개·화면 구성·기술 스택·기술적 이슈 구조

## 6. 관련 문서

- [[sd-jwt-selective-disclosure-jwe]], 선택적 공개와 봉인 암호화를 함께 쓰는 이유
- [[vc-key-binding-approval-jwt]], 키 바인딩과 업무 승인을 결합하기
- [[onchain-revocation-registry]], 온체인 폐기 레지스트리와 fail-closed 검증
- [[testnet-reward-token]], 같은 EVM 테스트넷 컨트랙트를 쓴 다른 프로젝트([[hana-ar-kowalk-2026]])
- [[im-challenge-daegu-2026-sns-menu]], 같은 2026 AI Blockchain Challenge in Daegu에 낸 다른 트랙 결과물(소상공인·골목상권 분야)
