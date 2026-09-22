---
title: 정정공시 체인 — 최신 유효 판과 정정 전후 값을 함께 보존하기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/miraeasset-ai-festival-2026-readme.md, raw/done/miraeasset-ai-festival-2026-early-design-readme.md]
tags: [dart, 공시, 데이터모델링, sqlite, 이력관리]
---

# 정정공시 체인

## 1. 한 줄 정의

정정공시를 원공시와 `superseded_by` / `supersedes`로 연결해 두고,
일반 조회는 최신 유효 판만 돌려주되 "정정 전에는 얼마였나"는 별도 테이블에서 읽게 하는 데이터 모델.

## 2. 어디서 썼는가

- [[miraeasset-ai-festival-2026]] — DART 공시 4,204건을 SQLite `disclosure.db`로 적재하면서 적용. `corrections` 테이블 2,160행.

## 3. 실제로 겪은 문제와 해결

### 왜 필요한가

공시 데이터에서 같은 계약 한 건이 원공시 + 정정공시 여러 건으로 존재한다.
그냥 쌓아 두면 두 가지가 동시에 깨진다.

- 금액을 물었을 때 낡은 원공시 값이 나온다.
- "정정 이력이 있었나"를 물었을 때 답할 수 없다.

### 모델

- 원본 공시는 `superseded_by`로 무효화 표시하고, 정정공시는 `supersedes`로 원본을 가리킨다. 초기 설계 단계에서 이미 "본문 표가 정정후 최신값, 원본은 `superseded_by`로 무효화"라는 판단 기준을 세워 두었다.
- 도구 조회의 **기본값은 최신 유효 판**이다.
- 정정 전후 값은 `corrections` 테이블(정정 전·후 항목)에서 읽는다.
- 계약 관련 질의는 `contracts` / `corrections` / `terminations`(1,106 / 2,160 / 20행)를 함께 본다.

### 답변 쪽에서의 규칙

- 인용은 질문이 특정한 **공시 체인 안에서만** 한다. 같은 유형의 다른 연도 공시가 함께 검색돼도 그 값을 끌어오지 않는다.
- 검증 단계에서 철회·정정 사실을 답변에 덧붙인다.

### 남은 한계

같은 달에 같은 상대방과 맺은 계약이 여럿이면, 질문만으로 어느 건인지 특정하지 못할 수 있다.
체인은 "같은 건의 버전"은 묶지만 "다른 건의 구분"까지 해결해 주지는 않는다.

## 4. 참고 자료

- [[miraeasset-ai-festival-2026]] 3-5절
- [[deterministic-rule-path]] — 계약 정정 체인을 다루는 결정론 규칙
