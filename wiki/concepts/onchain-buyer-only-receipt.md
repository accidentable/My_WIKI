---
title: 구매자만 남기는 온체인 후기와 증거 파일
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md, raw/done/blockthon-2026-memory-market-buyer-demo-notes.md]
tags: [블록체인, Sui, 평판, 검증, 영수증]
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
