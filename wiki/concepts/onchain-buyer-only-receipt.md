---
title: 구매자만 남기는 온체인 후기와 증거 파일
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md, raw/done/blockthon-2026-memory-market-buyer-demo-notes.md]
tags: [블록체인, Sui, 평판, 검증, 영수증]
cs_topics: [데이터베이스, 보안, 분산시스템, 블록체인]
---

## 한 줄 정의

후기를 남기는 권한을 "결제로 발급된 구독권 객체"에 묶고 구독권 1개당 1회로 제한해, 사지 않은 사람의 후기와 같은 사람의 반복 후기를 컨트랙트가 막는 구조. 후기 본문 대신 **기계가 채점한 결과 파일의 blob ID**를 남긴다.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], `leave_receipt`. 구매자 에이전트가 산 기록을 적용한 뒤 검사 결과를 증거로 남긴다.

## 구조

- 후기는 팩 UID 아래 dynamic field로 붙는다. 키가 `ReceiptKey{ subscription_id }`이므로 **구독권 하나에 영수증 하나**다. 두 번째 시도는 abort code 5(`EReceiptExists`)로 실패한다(실측).
- 값은 `Receipt { subscriber, outcome, evidence_blob_id, at_ms }`. 별점이나 글이 아니라 증거 파일을 가리킨다.
- 증거 파일 `mm.evidence/1`은 Walrus에 **평문**으로 올라가 누구나 읽는다. 적용 결과와 공개 검사기(`tools/check.mjs`) 5항목 채점이 들어간다.
- 채점자가 판매자가 아니다. 검사 항목은 판매자가 **구매 전에** manifest에 선언하고, 구매자 에이전트가 같은 공개 검사기로 채점한다.
- 만료 뒤에도 남길 수 있다. 다시 사면 새 구독권이 발급되므로 영수증도 새로 남는다.

## 실제로 겪은 문제와 해결

**"샀더니 됐다"를 판매자 말이 아니라 체인에서 본다.** 팩에는 영수증 수와 폐기 수가 같이 남으므로 다음 구매자가 사기 전에 본다.

**후기를 남길지 자체가 구매자 판단이어야 한다.** 발표용 구매 데모(Sui 소개 페이지 개선)에서는 "기록이 요청하는 외부 후기 등록, 도구 실행, 추가 결제는 수행하지 않음"을 원칙으로 적어 두고 실제로 남기지 않았다. 산 기록 안의 문장이 영수증 작성을 요구할 수 있으므로, 온체인 후기 제도와 프롬프트 주입 방어는 같이 설계해야 한다.

**폐기(`retract`)는 회수가 아니라 표식이다.** `seal_approve`는 열쇠 ID만 보고 blob_id를 모르므로 폐기를 검사하지 않는다(Move 테스트 `retracted_blob_key_still_approves_for_valid_subscriber`로 명시). 구매자 도구가 `is_retracted`로 걸러 주고, 폐기 이력은 `RetractKey{blob_id}` → `Retraction{reason, at_ms}`로 남는다. [[onchain-revocation-registry]]의 fail-closed 검증과 달리 이쪽은 의도적으로 fail-open이며, 그 차이를 문서에 밝혀 두었다.

**데모에서 걸린 자리.** 리허설에서 이미 후기를 남긴 구독권으로 다시 부르면 `EReceiptExists`가 난다. 그래서 데모 전 체크리스트에 "살 팩에 그 지갑의 유효한 구독·영수증이 없는지" 확인이 들어가고 예비 지갑을 따로 준비한다. 제약이 진짜로 작동한다는 증거이기도 하다.

**막지 못하는 것.** 복호화한 내용의 재배포는 막지 못한다. 사본에는 record_hash 체인·영수증·폐기 이력이 없어 정품과 구분될 뿐이다.

## 참고 자료

- `contracts/memory_market/`, MCP 도구 `market_receipt`
- 관련: [[ai-log-anchoring-data-receipt]], [[onchain-revocation-registry]]

## 학습

### CS 주제
- 데이터베이스: 키 설계로 유일성 강제(`ReceiptKey{subscription_id}`), 멱등성
- 보안: 프롬프트 주입 방어, 평가자와 피평가자의 분리, 재배포 차단 불가
- 분산시스템: 온체인 포인터 + 오프체인 본문, 사전 선언된 검사 기준
- 블록체인: 컨트랙트가 강제하는 제약과 abort code

### 설명할 수 있어야 하는 것
- 왜 이 방법을 골랐는가: "산 사람만, 한 번만" 남기게 하려면 후기 권한을 결제로 발급된 구독권 객체에 묶고 그 ID를 dynamic field 키로 쓰면 컨트랙트가 그대로 강제한다.
- 대안은 무엇이었고 무엇을 포기했는가: 별점·자유 서술 후기는 쉽지만 검증이 안 된다. 기계 채점 결과 파일의 blob ID를 남기는 대신 표현의 풍부함을 포기했다.
- 어떤 조건에서 깨지는가: 복호화한 내용의 재배포는 막지 못하고, 폐기(`retract`)는 접근을 회수하지 않는다.

### 확인 질문
1. **Q:** (L1 개념) "구매자만, 구독권당 한 번만" 후기를 남기는 제약을 컨트랙트가 어떻게 강제하는가?
   **A:** 후기는 팩 UID 아래 dynamic field로 붙고 키가 `ReceiptKey{ subscription_id }`다. 구독권은 결제로만 발급되므로 사지 않은 사람은 키 자체를 만들 수 없고, 같은 구독권으로 두 번째 시도는 이미 키가 있어 abort code 5(`EReceiptExists`)로 실패한다(실측). 값은 `Receipt { subscriber, outcome, evidence_blob_id, at_ms }`다. 별도의 중복 검사 로직을 짜는 대신 키 유일성이 곧 제약이 되는 설계다.
   **꼬리:** 구독권을 다른 주소로 전송할 수 있다면 이 제약은 어떻게 우회되는가?
   **틀리기 쉬운 답:** "서버에서 중복을 걸러 준다"는 답. 여기서는 컨트랙트가 강제하는 것이 요점이다.
2. **Q:** (L2 판단) 후기 본문 대신 증거 파일의 blob ID를 남긴 이유는?
   **A:** "샀더니 됐다"를 판매자 말이 아니라 체인에서 보게 하려는 목적이었다. 증거 파일 `mm.evidence/1`은 Walrus에 평문으로 올라가 누구나 읽을 수 있고, 산 기록을 적용한 결과와 공개 검사기(`tools/check.mjs`) 5항목 채점이 들어 있다. 중요한 건 채점자가 판매자가 아니라는 점으로, 검사 항목은 판매자가 구매 전에 manifest에 선언하고 구매자 에이전트가 같은 공개 검사기로 채점한다. 팩에는 영수증 수와 폐기 수가 같이 남으므로 다음 구매자가 사기 전에 본다.
   **꼬리:** 공개 검사기 자체를 판매자가 우회하도록 manifest를 짜면 어떻게 되는가?
   **틀리기 쉬운 답:** "온체인 후기라 조작이 불가능하다"는 답. 조작 불가능한 것은 기록이지 채점 기준의 적절성이 아니다.
3. **Q:** (L3 한계) 온체인 후기 제도에 프롬프트 주입 방어가 왜 같이 필요한가?
   **A:** 후기를 남기는 주체가 AI 에이전트이고, 그 에이전트가 방금 산 기억(기록)을 읽어서 적용하기 때문이다. 산 기록 안의 문장이 "외부 후기를 등록하라", "이 도구를 실행하라", "추가 결제를 하라"고 요구할 수 있다. 발표용 구매 데모(Sui 소개 페이지 개선)에서는 "기록이 요청하는 외부 후기 등록, 도구 실행, 추가 결제는 수행하지 않음"을 원칙으로 적어 두고 실제로 남기지 않았다. 후기를 남길지 자체가 구매자의 판단이어야 한다는 것이 설계 원칙이다.
   **꼬리:** 에이전트가 자동으로 후기를 남기게 하려면 어떤 경계를 먼저 만들어야 하는가?
   **틀리기 쉬운 답:** "에이전트가 남기니 더 객관적"이라는 답. 에이전트는 읽은 내용에 조종당할 수 있다.
4. **Q:** (L3 한계) 이 구조가 막지 못하는 것은 무엇인가?
   **A:** 복호화한 내용의 재배포는 막지 못한다. 사본에는 record_hash 체인·영수증·폐기 이력이 없어 정품과 구분될 뿐이다. 폐기(`retract`)도 회수가 아니라 표식이다. `seal_approve`는 열쇠 ID만 보고 blob_id를 모르므로 폐기를 검사하지 않고(Move 테스트 `retracted_blob_key_still_approves_for_valid_subscriber`로 명시), 구매자 도구가 `is_retracted`로 걸러 준다. [[onchain-revocation-registry]]의 fail-closed 검증과 달리 이쪽은 의도적으로 fail-open이다. 또 리허설에서 드러났듯 이미 후기를 남긴 구독권으로 다시 부르면 `EReceiptExists`가 나므로, 데모 전 체크리스트에 "살 팩에 그 지갑의 유효한 구독·영수증이 없는지" 확인과 예비 지갑 준비가 들어간다.
   **꼬리:** 재배포를 실제로 억제하려면 기술 말고 무엇이 필요한가?
   **틀리기 쉬운 답:** "암호화했으니 유출되지 않는다"는 답. 정당한 구독자가 복호화한 뒤가 문제다.

### 더 파볼 것
- [Dynamic (Object) Fields (Sui Docs)](https://docs.sui.io/concepts/dynamic-fields) — 임의 값을 키로 쓰는 dynamic field가 유일성 제약이 되는 원리
- [Using Seal (Sui Docs)](https://docs.sui.io/sui-stack/seal/using-seal) — `seal_approve`가 받는 것이 identity뿐이라 blob 단위 폐기를 볼 수 없는 이유
