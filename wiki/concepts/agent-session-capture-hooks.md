---
title: 대화 턴을 판매 단위로 자동 포집하는 에이전트 훅
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md]
tags: [Claude Code, 훅, 에이전트, 해시체인, 기록]
---

## 한 줄 정의

코딩 에이전트 세션에 훅을 붙여, 파일이 실제로 바뀐 턴만 "프롬프트 · diff · 화면 · 왜 · 알게 된 것" 한 덩어리로 확정하고 해시 사슬로 묶어, 사람이 따로 글을 쓰지 않아도 팔 수 있는 기록이 쌓이게 하는 것.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], `tools/capture.mjs`. 판매자는 평소처럼 Claude Code로 랜딩을 고쳤고 그 세션이 그대로 15단계·5단계 팩이 됐다.

## 훅 3종

| 훅 | 하는 일 |
|---|---|
| `UserPromptSubmit` | 프롬프트를 `.mm/pending.json`에 모은다. 첫 턴이면 기준선 HTML 스냅샷 |
| `PostToolUse` (Edit · MultiEdit · Write) | 손댄 파일과 편집 방식(targeted / rewrite) 기록 |
| `Stop` | **파일이 바뀐 턴만** 한 단계로 확정. HTML 복사, 이전 단계와 unified diff(8KB), transcript에서 이유와 교훈 추출, Playwright로 1280×800·375×812 스크린샷, `check.mjs` 5항목 채점, `step-N.json` 저장, `git commit "mm step N"` |

## 실제로 겪은 문제와 해결

**기록이 진짜 그 순서였다는 보장.** 단계를 해시 사슬로 묶는다. `record_hash = sha256(canonical JSON)`, `prev_hash`는 앞 단계의 `record_hash`(1단계는 `sha256(pack_id + series_id)`). 목차(manifest)에 단계마다 `record_hash`를 평문으로 실으므로 구매자는 복호화한 것이 사기 전에 본 목차 그대로인지 대조할 수 있다. 다만 이 사슬은 **사후 수정**만 드러내고 처음부터 지어낸 기록은 못 막는다.

**훅이 세션을 망가뜨리면 안 된다.** 훅 안에서 LLM 호출도 네트워크 호출도 하지 않고, 예외는 전부 삼킨다. 실측에서 Stop 훅은 턴당 1.7~2.1초였다(판매자 5턴의 턴 자체는 41/70/46/55/40초).

**에이전트는 시키지 않으면 기억 도구를 안 부른다.** 그래서 구매자 쪽 플러그인의 `UserPromptSubmit` 훅이 주제어가 보이면 "먼저 시장을 확인하라" 한 줄을 프롬프트에 덧붙인다(MemWal 공식 플러그인의 패턴). 도구를 만들어 두는 것만으로는 호출되지 않는다는 뜻이다.

**올리기 전 걸러내기.** `filter.ts`가 비밀키·니모닉·API 키 형태는 문장째 버리고(drop), 경로와 이메일은 가린다(redact). 포집이 자동이므로 필터도 자동이어야 한다.

## 참고 자료

- `tools/capture.mjs`, `tools/selftest.mjs`(포집 훅 자체 검증), `scripts/filter.ts`
- 관련: [[sui-timed-access-subscription]], [[measured-baseline-over-claimed-gain]]
