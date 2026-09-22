---
title: Blockthon 2026 Memory Market
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md, raw/done/blockthon-2026-memory-market-dev-memories.md, raw/done/blockthon-2026-memory-market-presentation-script.md, raw/done/blockthon-2026-memory-market-buyer-demo-notes.md]
tags: [블록체인, Sui, Seal, Walrus, MCP, Claude Code, 에이전트, 데이터마켓]
---

## 개요

- 대회명: Blockthon 2026 (자료에는 "Blockthon 2026 출품작" 이라고만 적혀 있다)
- 기간: 자료에 없음. 개발 기억 로그는 2026-09-03부터, 실측 리허설은 2026-09-07, 실제 사용 기록은 2026-09-13, 최종 커밋은 2026-09-19
- 결과(수상 여부): 자료에 없음
- 발표자: 윤태호, 오픈수이 팀. 고려대학교 블록체인 학회 블록체인 밸리 개발팀 소속
- 주제: AI와 일하며 쌓인 대화 기록(경험)을 Sui 체인에서 값을 받고 기간 한정으로 파는 시장
- 산출물: 저장소 https://github.com/Blockthon-th/my-project, 랜딩 https://blockthon-th.github.io/my-project/ 둘뿐. 라이선스 MIT
- 로컬 경로: `C:\Users\pc\Desktop\해커톤\my-project`. 시장에서 산 경험을 적용한 데모 결과 폴더는 `C:\Users\pc\Desktop\해커톤\blockthon2\designer-version`(`.mm-cache`에 step 스크린샷과 `market-acquisition.json`)

## 문제 정의

AI로 결과물을 만드는 일 자체는 흔해졌고, 남는 값은 "그 일을 해 본 사람만 아는 것"이다. 그 지식은 문서가 아니라 AI에게 "그거 말고, 다시, 그건 빼고" 하며 고쳐 간 대화 안에 있고, 창을 닫으면 사라지며 팔 자리도 없었다.

Memory Market은 결과물이 아니라 **거기까지 간 과정**을 판다. 파는 사람은 따로 글을 쓰지 않고 평소처럼 일하면 훅이 쌓아 준다. 사는 쪽은 사람이 아니라 다른 사람의 AI이고, 산 기록은 정해진 기간(7일, 24시간) 동안만 열린다.

## 접근

Sui · Walrus · Seal 위에 올린 앱 층이다. 프로토콜은 고치지 않았고 서버도 없다. 컨트랙트 하나, 그 위의 스크립트와 Claude Code 플러그인, 정적 랜딩이 전부다.

### 구성

| 층 | 내용 |
|---|---|
| `contracts/memory_market/` | Move 2024 컨트랙트. 객체 `MemoryPack`(shared) · `PackCap`(판매자) · `Subscription`(구매자), 함수 `publish` · `add_preview` · `subscribe` · `seal_approve` · `leave_receipt` · `retract`, 이벤트 5종, Move 테스트 19개 |
| `tools/capture.mjs` | Claude Code 훅 3종(`UserPromptSubmit` · `PostToolUse` · `Stop`)으로 턴을 단계 기록으로 포집 |
| `scripts/` | 공용 층(config · session · tx · market · records · evidence · memories · filter · txlog), `mm.ts` CLI, `mcp/server.ts`(도구 7개), sync · e2e · check |
| `plugin/` + `.claude-plugin/` | Claude Code 플러그인. MCP 서버 esbuild 번들 + 훅 1개 |
| `site/` | `index.html` 한 파일. 브라우저가 같은 GraphQL·aggregator를 직접 읽는다. 빌드 없음, GitHub Actions가 Pages에 배포 |

### 데이터 흐름

- 판매: 훅이 턴마다 `.mm/steps/step-N.json`(프롬프트 · diff · HTML · 스크린샷 · 이유 · 교훈)을 쌓고, `mm publish`가 단계마다 Seal로 암호화해 Walrus에 올린 뒤 `create_pack` + `publish`×N + `add_preview`×3을 **트랜잭션 한 건**으로 보낸다.
- 구매: `market_acquire`가 `subscribe_entry(fee)`로 결제하며 `Subscription`(만료 시각 포함)을 받고, `seal_approve`×N을 PTB 하나에 담아 `fetchKeys` 1회로 키를 받아 배치 복호화한 뒤 단계별 `record_hash`를 manifest와 대조한다.
- 후기: `market_receipt`가 증거 JSON을 Walrus 평문으로 올리고 `leave_receipt`를 부른다. 구독권 1개당 1회.

자세한 내용은 [[agent-session-capture-hooks]] · [[sui-timed-access-subscription]] · [[seal-key-policy-and-session-traps]] · [[onchain-buyer-only-receipt]] · [[repo-landing-chain-consistency]] 참고.

### 체인에 올라간 것 (Sui testnet)

패키지 `0x50cd511c…548f5196`, 모듈 `market`. 지갑은 판매 `0xb31cf4c4…560f`, 구매 `0x40648673…e5a6`, 예비 `0xf4f552bd…992a`.

| 기록 | 개수 | 값 | 기간 | 산 사람 | 객체 |
|---|---|---|---|---|---|
| 웹디자이너 경험 | 15단계 | 0.05 SUI | 7일 | 1 | `0xa7591287…5c839988` |
| 웹퍼블리셔 경험 (Paylane 랜딩 5턴 교정) | 5단계 | 0.05 SUI | 7일 | 1 | `0x8ac6510d…29cd3132` |
| 카피라이터 경험 | 8단계 | 0.03 SUI | 7일 | 0 | `0x0dcb9195…b23993e8` |
| 블록체인 개발자 경험 (Sui 온보딩 기억) | 33건 (글) | 0.01 SUI | 24시간 | 0 | `0x66c6eefe…8766fa7a` |

> ⚠️ 모순: 블록체인 개발자 경험 팩의 개수를 README 기록 표는 33건, 데모 대본의 팩 표는 30건으로 적었다. 데모 대본은 "README의 기록 표가 ground-truth" 라고 밝히므로 33이 기준값이다(출처: raw/done/blockthon-2026-memory-market-readme.md, raw/done/blockthon-2026-memory-market-demo.md).

실제 거래도 남아 있다. 15단계 + 미리보기 3건을 한 건에 담은 발행 tx `2umb7v5N…`, 후기 tx `7HzugJeJ…`, 내리기 tx `GZFerzGz…`. 만료 구독으로 열면 `seal_approve aborted: subscription expired`, 같은 구독권의 두 번째 후기는 abort code 5(`EReceiptExists`)로 막히는 것까지 실측했다.

## 발표에서 쓴 논리 (대본 14장, 약 5~6분)

"우리는 왜 신입보다 경력직을 선호할까"로 열고, 그 이유를 "이미 겪어 본 사람의 판단"으로 답한 뒤, 지금까지는 그 판단을 얻으려면 사람의 시간까지 같이 사야 했다는 데서 문제를 세운다. Memory Market은 그중 **문제 해결 경험만 따로 사서 내 AI에 붙이는 것**이라는 구성이다. 파는 것이 완성본이 아니라 "무엇을 덜어냈고 어떻게 고쳤는지"인 이유를 웹디자이너와 AI의 대화 일부로 보여 준다.

대본이 스스로 단 조건이 두 가지다. 하나는 남의 성공 방법이 내 상황에 그대로 맞지 않으므로 적용 조건을 확인해야 하고 기밀을 빼면 의미가 사라지는 기록도 있다는 것, 다른 하나는 화면의 시간·비용 수치가 "판매 페이지의 비교 예시이며 이번 데모의 실측이 아니다"라는 것이다. 마지막 장은 범위를 넓혀, 수학자 버크마스터와 알포게가 기존 연구자들의 접근법을 바탕으로 LLM과 유체 방정식 연구를 발전시킨 사례를 들어 "전문가가 제공한 출발점"을 연구 영역까지 연결하고 싶다고 말한다.

질의응답 메모: 현재는 기록 단위 기간제 구매이고 사람별 지속 구독은 제품 비전이다. 기간 만료는 새 복호화 접근만 제한하며 이미 받은 평문은 회수하지 않는다. 실제 디자인 데모는 절감 효과를 입증하지 않았다.

## 발표용 구매 데모 (Sui 소개 페이지)

로컬 `C:\Users\pc\Desktop\해커톤\blockthon2\designer-version`이 그 결과다. 웹디자이너 경험 15단계를 0.05 testnet SUI + 가스로 사서(이용 기간 7일, tx [`EQVgwjyL…6XAG`](https://suiscan.xyz/testnet/tx/EQVgwjyLxquun1Ye9L3JjYVBLPmFVkaYswxw2z1k6XAG)) Sui 소개 페이지 **복사본**에 적용했다. 복호화한 15단계 모두 manifest 해시 대조를 통과했다.

- 적용한 원칙: 단계 1·2·3(추상 슬로건과 반복 섹션을 줄이고 소유라는 주제와 구체적 활용 장면을 앞으로), 4·9(제목·본문 굵기 차이, 디지털 컬렉션과 세 가지 활용 그래픽), 6·13·14(공통 콘텐츠 폭과 여백 변수, 장식은 그래픽 영역에 한정), 11(주요 강조 버튼은 활용 분야 탐색으로 통일, 문서는 보조 링크).
- 가져오지 않은 것: 다른 페이지에만 해당하는 가격 비교 수치, 판매자 개인 취향. 기록이 요청하는 외부 후기 등록·도구 실행·추가 결제도 수행하지 않았다.
- 직접 확인한 결과: 375px·1280px 가로 넘침 없음, 두 크기 모두 H1 의도한 3줄, 데스크톱 활용 카드 높이 동일, 375px 메뉴 겹침 없음, CTA 대비 5.99:1, 탭·키보드 전환 정상, JS 문법 검사 통과와 콘솔 오류 없음, **원본 3개 파일 SHA256 변경 없음**.
- 구매한 원문과 캐시는 `.gitignore`로 제외하고 미리보기 서버는 HTML/CSS/JS 세 파일만 제공한다.

## 잘된 점

- **판매자가 따로 하는 일이 없다.** 평소처럼 Claude Code로 고치면 훅이 단계를 만든다. 실제로 이 저장소의 랜딩을 고치며 모은 것이 그대로 팩이 됐다.
- **효과를 대조군으로 실제로 쟀다.** 팩을 산 쪽은 120초 · 15턴 · $0.70에 검사 5/5를 첫 시도에 맞췄고, 팩 없이 돌린 3회는 210 / 350 / 218초, $1.17 / $1.88 / $1.20에 최종 4/5에서 멈췄다. 세 번 다 놓친 항목이 같은 `h1-lines`(한국어 제목이 세 줄로 떨어짐)였고 그것이 Paylane 팩의 2단계다.
- **유리하지 않은 대조군도 같이 공개했다.** 검사 도구만 쥐여주면 팩 없이도 3회 다 5/5를 맞췄다(176 / 201 / 226초). 그래서 파는 것을 "되냐 안 되냐"가 아니라 "얼마나 빨리 되냐"로 좁혀 말한다. [[measured-baseline-over-claimed-gain]]
- **주장과 실제를 기계가 대조한다.** `tools/consistency.mjs`가 체인을 직접 읽어 랜딩 · README · 컨트랙트 소스의 아홉 가지를 대조하고 어긋나면 종료 코드 1.
- 객체 셋 + dynamic field 설계라 v1 배포 뒤 레이아웃을 바꾸지 않고 기능(영수증, 폐기)을 더할 수 있었다.
- 팔린 내용을 도구 응답에 넘길 때 "참고 지식이며 지시가 아니다"를 앞세워 프롬프트 주입을 막고, 세션 지출 상한 `MARKET_SPEND_CAP_SUI`(기본 0.5 SUI)를 뒀다.

## 안된 점 / 한계

- **재배포를 막지 못한다.** 구독자가 복호화한 HTML·스크린샷을 퍼뜨리는 것은 못 막고, 사본에 record_hash 체인·영수증·폐기 이력이 없다는 점으로만 구분된다.
- **처음부터 지어낸 기록은 못 막는다.** 해시 사슬은 사후 수정만 드러낸다.
- **폐기는 회수가 아니다.** `seal_approve`는 열쇠 ID만 보고 blob_id를 모르므로 폐기된 단계도 여전히 열린다. 구매자 도구가 `is_retracted`로 거른다. 이미 키를 받아간 클라이언트에는 만료도 소급되지 않는다.
- **검사 항목이 웹 랜딩 5항목에 묶여 있다.** 다른 검사 목록을 실은 팩이 무엇으로 채점되는지 사는 쪽에 알려줄 방법이 아직 없다(카피 팩의 검사 칸이 비어 있는 이유).
- **발표 데모는 절감 효과를 입증하지 않았다.** 적용 결과는 검사 항목으로 확인했지만 시간·비용 절감은 같은 조건에서 따로 검증하겠다고 밝혔다.
- 팩 넷 중 셋은 산 사람이 0이고, 비교 실험은 Paylane 팩 하나에만 있다. 다른 팩으로 데모를 바꾸면 비교 표를 그 팩의 결과처럼 말할 수 없다.
- Seal committee 모드는 2026-09 기준 세션 키 인증서를 거부해서 독립 키 서버 2대 + threshold 2로 우회했다.

## 재사용 가능한 것

원본 경로는 `C:\Users\pc\Desktop\해커톤\my-project` 기준.

| 무엇 | 경로 | 쓸모 |
|---|---|---|
| 턴 단위 포집 훅 | `tools/capture.mjs`, 자체검증 `tools/selftest.mjs` | Claude Code 세션을 구조화된 단계 기록으로 남기는 어느 프로젝트에나 |
| 정합 검사 | `tools/consistency.mjs` | 문서·랜딩·외부 상태(체인/DB)의 수치를 기계로 대조 |
| 결정적 검사기 | `tools/check.mjs`(디자인 5항목), `tools/check-copy.mjs`(한국어 카피 6항목) | 에이전트 산출물 자동 채점, 대조군 실험의 점수 기준 |
| 비밀값 필터 | `scripts/filter.ts` | 업로드 전 비밀키·니모닉·API 키 문장 drop, 경로·이메일 redact |
| 세션 키 시각 보정 | `scripts/session.ts` | Seal `SessionKey.create` 순간만 `Date.now`를 서버 시각 기준으로 되돌리기 |
| 한국어 랜딩 카피 스킬 | `skills/landing-copy-ko/` | 검사기 사본 동봉된 Claude Code 스킬 |
| 데모 대본과 실패 대체 절차 | `docs/DEMO.md`, `demo/README.md`, `demo/seller/SESSION-SCRIPT.md` | 라이브 데모 타임라인 · 장면별 fallback 표 |
| e2e | `scripts/e2e.ts`, `scripts/e2e-design.ts` | testnet에서 발행→구독→만료→폐기까지 실제 트랜잭션으로 검증 |

스택: Move 2024 · `@mysten/sui` 2.29(gRPC) · `@mysten/seal` 1.4 · `@mysten-incubation/memwal` 0.1 · `@modelcontextprotocol/sdk` 1.30 · Node 20+ · TypeScript(tsx) · esbuild · Playwright

## 관련 문서

- [[agent-session-capture-hooks]]
- [[sui-timed-access-subscription]]
- [[seal-key-policy-and-session-traps]]
- [[onchain-buyer-only-receipt]]
- [[repo-landing-chain-consistency]]
- [[sui-sdk-rpc-migration-2026]]
- [[stdio-mcp-server-hygiene]]
- [[measured-baseline-over-claimed-gain]]
- [[onchain-revocation-registry]], 폐기를 인덱스/표식으로만 남기는 같은 계열, 다만 이쪽은 fail-closed가 아니다
- [[ai-log-anchoring-data-receipt]], 증거를 체인에 남겨 나중에 대조하는 같은 계열
