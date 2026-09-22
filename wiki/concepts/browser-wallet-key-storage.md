---
title: 브라우저 지갑의 개인키 보관과 IndexedDB 신뢰 경계
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-trust404-readme.md]
tags: [IndexedDB, 브라우저지갑, 개인키, XSS, 보안]
cs_topics: [보안, 웹]
---

## 한 줄 정의

IndexedDB는 사이트별 데이터를 나눠 저장하지만, 같은 사이트에서 실행되는 코드가 지갑 개인키를 읽는 구조라면 XSS나 악성 배포 코드로부터 그 키를 격리해 주지는 않습니다.

## 어디서 썼는가

- [[blockchain-valley-2026-sabonx]] — 근로자 브라우저 지갑이 개인키와 VC를 IndexedDB에 저장하고 서명에 사용합니다.
- [[vc-key-binding-approval-jwt]] — 키를 빼앗기면 KB-JWT의 키 소유 증명도 도용될 수 있습니다.

## 실제로 겪은 문제와 해결

### 서버에 두지 않은 이유와 얻은 범위

SabonX는 서버에 전체 VC 사본을 캐시하지 않고 브라우저 지갑에 개인키와 VC를 둡니다. 서버에는 폐기 식별자·만료 시각 같은 발급 메타데이터만 남깁니다. 이 선택으로 서버에 사용자 개인키와 전체 VC 사본을 모으는 일을 피했지만, 키 보관 문제 자체가 사라진 것은 아닙니다. 브라우저 데이터가 지워지거나 키를 잃으면 현재 데모에는 복구 절차가 없어 새 세션을 시작해야 합니다.

### IndexedDB가 막는 것과 막지 못하는 것

브라우저의 동일 출처 정책은 다른 사이트가 SabonX 출처의 IndexedDB를 곧바로 읽지 못하게 합니다. 그러나 SabonX 출처에서 실행되는 정상 코드에는 접근이 필요하며, 같은 출처에서 실행된 악성 스크립트에도 저장소가 노출될 수 있습니다. OWASP는 IndexedDB를 비밀 저장소로 간주하지 말고 XSS와 브라우저 프로필에 접근하는 공격을 고려하라고 권합니다. 프로젝트의 `src/holder/keyStorage.ts`는 시드를 숫자 배열로 저장하고, `src/ui/pages/PayApp.tsx`도 앱 세션의 개인키 바이트를 숫자 배열로 저장합니다. 현재 구현을 두고 "서버에 키를 모으지 않는다"고 말할 수는 있지만 "사이트 코드가 침해돼도 개인키가 안전하다"고 말할 근거는 없습니다.

### 개선을 검토할 때

저장 시 키를 사용자 비밀번호로 암호화하면 잠긴 상태의 브라우저 데이터가 유출될 때 도움이 될 수 있습니다. 다만 사용자가 잠금을 풀어 서명하는 동안 같은 출처의 악성 코드가 접근하는 위험까지 없애지는 못합니다. 사이트 코드가 키 원본을 읽지 못하고 서명만 요청하는 별도 지갑이나 보안 저장소 연동은 향후 검토할 수 있지만, SabonX에는 아직 구현되지 않았습니다. 개선을 적용했다면 어떤 공격을 실제로 막는지 별도 테스트가 필요합니다.

## 참고 자료

- [MDN Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy) — IndexedDB의 출처별 분리.
- [OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) — IndexedDB의 비밀 저장과 XSS 위험.
- [SabonX 코드](https://github.com/accidentable/Trust404_th) — `src/holder/keyStorage.ts`, `src/ui/pages/PayApp.tsx`의 현재 키 저장 방식.

## 학습

### CS 주제

- 보안: XSS와 클라이언트 비밀 보관의 위협 모델
- 웹: 동일 출처 정책과 IndexedDB 접근 범위

### 설명할 수 있어야 하는 것

- 서버에 키가 없다는 주장과 브라우저의 키가 안전하다는 주장이 왜 다른지 설명할 수 있습니다.
- 다른 출처의 직접 접근과 같은 출처의 악성 코드 실행을 구분할 수 있습니다.
- 저장 시 암호화, 서명 시 잠금 해제, 키 원본 격리가 각각 막는 공격의 범위를 설명할 수 있습니다.

### 확인 질문

1. **Q:** (L1 개념) IndexedDB에 넣은 개인키는 다른 사이트에서 읽을 수 있나요?
   **A:** 브라우저는 저장소를 출처별로 나누므로 다른 출처의 사이트가 SabonX IndexedDB에 곧바로 접근하지 못합니다. SabonX 출처에서 실행되는 코드에는 접근이 허용됩니다. 같은 출처에서 악성 코드가 실행되면 저장된 시드를 읽을 수 있으므로 IndexedDB 자체를 개인키 금고로 보지 않았습니다.
   **꼬리:** 동일 출처 정책은 XSS로 실행된 스크립트에도 저장소 접근을 막아 주나요?
   **틀리기 쉬운 답:** "IndexedDB에 넣으면 브라우저가 자동으로 개인키를 암호화해 줍니다"라는 답은 이 구현에 맞지 않습니다.
2. **Q:** (L2 판단) SabonX에서 개인키와 VC를 브라우저에 두기로 한 이유와 그 대가는 무엇인가요?
   **A:** 서버의 전체 VC 캐시를 없애 지갑 밖에 사본을 남기지 않으려고 브라우저 지갑에 보관했습니다. 서버에는 발급 메타데이터만 남기므로 개인키와 전체 VC 사본을 서버에 모으지 않습니다. 대신 현재 사이트 코드는 브라우저에 저장된 키를 읽을 수 있고, 키를 잃었을 때 복구하는 흐름도 없어 새 세션이 필요합니다. 보관 위치를 바꾼 선택이 보안과 사용성 모두에 영향을 줬습니다.
   **꼬리:** 사용자가 브라우저 데이터를 지우면 기존 VC를 서버에서 다시 내려줄 수 있나요?
   **틀리기 쉬운 답:** "서버에 키가 없으므로 키 탈취 위험도 없습니다"라고 답하면 브라우저 측 위험을 놓칩니다.
3. **Q:** (L3 한계) 개인키를 비밀번호로 암호화해 IndexedDB에 저장하면 XSS 문제까지 해결되나요?
   **A:** 잠긴 상태의 저장 데이터가 유출되는 경우에는 비밀번호 기반 암호화가 도움이 될 수 있습니다. 사용자가 키를 풀어 서명하는 동안 같은 출처에서 악성 코드가 실행되는 문제는 별도로 남습니다. SabonX에는 저장 키 암호화나 외부 지갑 연동이 구현되지 않았으므로, 이 개선을 현재의 보장처럼 발표하면 안 됩니다. 실제 개선 시에는 잠금 상태와 서명 중 상태를 나눠 시험해야 합니다.
   **꼬리:** 사이트 코드가 키 원본을 읽지 않고 서명만 요청하려면 어떤 경계가 필요할까요?
   **틀리기 쉬운 답:** "암호화된 바이트를 IndexedDB에 두면 사용 중에도 키를 절대 읽을 수 없습니다"라고 답하면 잠금 해제 시점을 빠뜨립니다.

### 더 파볼 것

- [MDN Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy) — 출처별 저장소 접근 범위를 확인할 수 있습니다.
- [OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) — IndexedDB에 비밀을 저장할 때의 위협과 권고를 확인할 수 있습니다.
