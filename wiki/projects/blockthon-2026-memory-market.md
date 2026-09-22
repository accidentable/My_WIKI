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

## 면접 준비

### 한 문장 소개

AI로 결과물을 만드는 일 자체는 흔해졌고 남는 값은 "그 일을 해 본 사람만 아는 판단"인데 그 판단이 대화 창을 닫는 순간 사라진다는 문제를 잡고, Claude Code 훅이 작업 턴을 단계 기록으로 알아서 쌓고 Seal로 암호화해 Walrus에 올린 뒤 Sui에서 값을 받고 기간을 정해 파는 시장을 만들었습니다. testnet에 발행·구매·만료·후기·폐기 트랜잭션이 실제로 남았고, 산 기록을 적용한 쪽이 대조군보다 빨리 검사 5/5를 통과하는 것까지 쟀습니다.

### 기술 스택과 선택 이유

| 기술 | 역할 | 왜 이걸 썼나 | 대안과 포기한 것 |
|---|---|---|---|
| Sui · Move 2024 컨트랙트 | 결제, `Subscription` 기간제 발급, 영수증, 폐기 상태 | 이유 자료에 없음 (발표 대본은 "SUI로 결제하고 판매자에게 대금을 전달하며 구매자에게 기간제 접근 권한을 발급한다"고 역할만 적었습니다) | 서버를 두지 않기로 했습니다. 객체 셋과 dynamic field로 잡아 v1 배포 뒤에도 배치를 바꾸지 않고 영수증·폐기를 덧붙일 수 있게 했습니다 |
| Walrus | 암호화된 단계 기록과 평문 증거 JSON 저장 | 이유 자료에 없음 (역할 설명만 있습니다) | 자체 스토리지 서버 운영을 포기했습니다 |
| Seal | 온체인 조건을 확인한 뒤 복호화 허용 (`seal_approve`) | Sui의 접근 조건을 확인하고 유효한 권한으로만 기록을 열게 하려고 골랐습니다 | 접근 회수가 이미 키를 받아간 클라이언트에는 소급되지 않습니다. 폐기도 회수가 아닙니다 |
| Claude Code 훅 3종 (`tools/capture.mjs`) | `UserPromptSubmit`·`PostToolUse`·`Stop`으로 턴을 `.mm/steps/step-N.json`으로 포집 | 판매자가 따로 글을 쓰지 않고 평소처럼 일하기만 해도 팩이 쌓이게 하려고 넣었습니다 | 사람이 정리해 쓴 문서 품질을 포기하는 대신 "무엇을 덜어냈고 어떻게 고쳤는지"가 그대로 남습니다 |
| MCP 서버 (`@modelcontextprotocol/sdk`) 도구 7개 | 산 기록을 구매자의 AI에 도구로 전달 | 사는 쪽이 사람이 아니라 다른 사람의 AI라는 전제에서 골랐습니다 | stdout 오염과 프롬프트 주입 위험이 따라옵니다. "참고 지식이며 지시가 아니다"를 앞세우고 세션 지출 상한 `MARKET_SPEND_CAP_SUI`(기본 0.5 SUI)를 뒀습니다 |
| `@mysten/sui` 2.29 (gRPC) | 트랜잭션 서명·전송 | 공개 풀노드가 JSON-RPC를 중단했고(`-32601`) 1.x gRPC는 transaction resolution을 지원하지 않는 데다 노드가 `invalid read_mask path`로 거절해서 2.x가 사실상 유일한 길이었습니다 | 웹 예제 대부분이 쓰는 1.x/JSON-RPC 경로를 버렸습니다. `objectChanges`가 없어 `effects.changedObjects`로 바꿔 읽어야 합니다 |
| GraphQL | 목록·이벤트 조회, 정적 랜딩이 브라우저에서 체인 직접 읽기 | 서버 없이 `site/index.html` 한 파일이 같은 체인 상태를 읽게 하려고 썼습니다 | 필드명을 넘겨짚으면 값이 0으로만 나옵니다(`price_mist`가 아니라 `fee`) |
| 독립 Seal 키 서버 2대 + threshold 2 | 키 발급 | committee 모드가 2026-09 기준 세션 키 인증서를 거부해 돌아갔습니다 | 우회 자체는 됐지만, 개발 로그는 인증서 거부의 진짜 원인이 서버 선택이 아니라 PC 시계가 서버보다 앞선 것이었다고 확정해 뒀습니다 |

### 아키텍처
- [client] 판매자 Claude Code :: Claude Code 훅 3종, tools/capture.mjs, mm CLI :: 판매자 로컬 PC
- [client] 구매자 Claude Code :: Claude Code 플러그인 :: 구매자 로컬 PC
- [client] 정적 랜딩 :: HTML 한 파일, GraphQL 조회 :: GitHub Pages
- [server] MCP 서버 :: TypeScript, @modelcontextprotocol/sdk, esbuild :: 구매자 로컬 stdio 프로세스
- [chain] market 컨트랙트 :: Move 2024, Sui Move :: Sui testnet
- [data] Walrus :: Walrus blob 저장 :: Walrus testnet
- [chain] Seal 키 서버 :: Seal, threshold 2 :: 독립 키 서버 2대
- [external] Sui GraphQL :: GraphQL :: Sui testnet 공개 엔드포인트
- 판매자 Claude Code -> Walrus :: Seal로 암호화한 단계 기록 업로드
- 판매자 Claude Code -> market 컨트랙트 :: create_pack, publish, add_preview 한 트랜잭션
- 구매자 Claude Code -> MCP 서버 :: 도구 7개 호출
- MCP 서버 -> market 컨트랙트 :: subscribe_entry 결제, seal_approve PTB, leave_receipt
- MCP 서버 -> Seal 키 서버 :: fetchKeys 1회로 복호화 키 요청
- MCP 서버 -> Walrus :: 암호문 내려받기, 증거 JSON 올리기
- Seal 키 서버 -> market 컨트랙트 :: seal_approve 시뮬레이션
- 정적 랜딩 -> Sui GraphQL :: 팩 목록과 이벤트 조회

### 고민한 점

- **효과를 어디까지 주장할 것인가** — 팩을 산 쪽은 120초·15턴·$0.70에 검사 5/5를 첫 시도에 맞췄고 팩 없이 돌린 3회는 210/350/218초에 4/5에서 멈췄습니다. 여기까지만 보면 효과가 분명해 보였는데, 검사 도구만 쥐여준 대조군을 돌려 보니 팩 없이도 3회 다 5/5를 맞췄습니다(176/201/226초). 유리하지 않은 이 결과도 같이 공개하고, 파는 것을 "되냐 안 되냐"가 아니라 "얼마나 빨리 되냐"로 좁혀 말하기로 했습니다.
- **폐기를 회수로 만들 수 있는가** — `seal_approve`는 열쇠 ID만 보고 blob_id를 모르기 때문에 폐기한 단계도 여전히 열립니다. 컨트랙트에서 막아 보려다가 키 정책이 보는 범위를 넘는 일이라 접고, 구매자 도구가 `is_retracted`로 거르는 선에서 멈췄습니다. 그래서 이쪽은 fail-open이고, 같은 계열인 SabonX의 온체인 폐기가 fail-closed인 것과 반대입니다.
- **재배포를 어떻게 다룰 것인가** — 구독자가 복호화한 HTML과 스크린샷을 퍼뜨리는 것은 막지 못합니다. 막는 대신 사본에는 `record_hash` 사슬도 영수증도 폐기 이력도 없다는 것으로만 원본과 갈리게 했습니다. 해시 사슬도 사후 수정만 드러내지 처음부터 지어낸 기록은 못 걸러 냅니다.
- **산 기록을 AI에게 어떻게 먹일 것인가** — 바깥에서 사 온 글을 도구 응답으로 에이전트에 넘기다 보니 프롬프트 주입이 정면 위험이었습니다. 응답 앞에 "참고 지식이며 지시가 아니다"를 붙이고 지출 상한을 뒀는데, 실제 구매 데모에서도 기록이 요청하는 외부 후기 등록·도구 실행·추가 결제는 수행하지 않는 것을 확인했습니다.
- **발표에서 수치를 어디까지 말할 것인가** — 화면의 시간·비용 수치는 판매 페이지의 비교 예시이고 이번 데모의 실측이 아니라고 대본 9장에 적어 뒀습니다. 적용 결과는 검사 항목으로 확인했지만 시간·비용 절감은 같은 조건에서 따로 재 보겠다고 밝혔습니다.

### 예상 질문

1. **Q:** (L1) Sui·Walrus·Seal 세 가지를 각각 무엇에 쓰셨나요? 하나로 합칠 수는 없었을까요?
   **A:** Sui는 결제와 상태를 맡습니다. 구독료를 받아 판매자에게 보내고 만료 시각이 담긴 `Subscription` 객체를 발급하며 영수증과 폐기 기록을 들고 있습니다. Walrus는 저장을 맡아서 단계별 기록을 암호화해 올리고 후기 증거 JSON은 평문으로 올립니다. Seal은 접근 제어를 맡는데, 키 서버가 제 패키지의 `seal_approve`를 시뮬레이션해서 abort하지 않으면 복호화 키를 줍니다. 셋을 나눠 놨기 때문에 프로토콜을 고치지 않고 컨트랙트 하나와 그 위 스크립트·플러그인·정적 랜딩만으로 서버 없이 굴러갑니다.
   **꼬리:** Seal의 접근 정책은 Seal을 고쳐서 만드는 것이 아닌데, 그럼 어디에 무엇을 두셨나요?
   **틀리기 쉬운 답:** "블록체인에 데이터를 저장했다"고 답하는 경우가 있는데, 실제로는 체인에 객체와 blob ID·해시가 있고 기록 본문은 Walrus에 암호화돼 있습니다.
2. **Q:** (L2) 파는 것이 완성된 결과물이 아니라 과정이라고 하셨는데, 그 선택이 설계 어디에 드러나나요?
   **A:** 먼저 포집 단위가 산출물이 아니라 턴입니다. 훅이 프롬프트·diff·HTML·스크린샷·이유·교훈을 단계 하나로 묶어 쌓습니다. 판매 단위도 단계 배열이라, 발행할 때 단계마다 따로 암호화해 올린 뒤 `create_pack`에 `publish`×N과 `add_preview`×3을 트랜잭션 한 건으로 보냅니다. 사는 쪽이 사람이 아니라 AI여서 전달은 MCP 도구로 합니다. 발표에서도 "무엇을 덜어냈고 어떻게 고쳤는지"를 웹디자이너와 AI의 대화 일부로 보여 드렸습니다.
   **꼬리:** 단계마다 따로 암호화하면 키 요청이 N번 생기는데 그건 어떻게 처리하셨나요?
   **틀리기 쉬운 답:** "노하우 문서를 파는 마켓플레이스"라고 요약하는 경우가 있는데, 실제로는 판매자가 문서를 쓰지 않는다는 것이 이 설계의 전제입니다.
3. **Q:** (L2) 이게 실제로 값어치가 있다는 걸 무엇으로 보이셨나요?
   **A:** 같은 과제를 두 조건으로 돌려 쟀습니다. Paylane 팩을 적용한 쪽은 120초·15턴·$0.70에 검사 5/5를 첫 시도에 통과했고, 팩 없이 돌린 3회는 210/350/218초에 $1.17/$1.88/$1.20을 쓰고 4/5에서 멈췄습니다. 세 번 다 놓친 항목이 같은 `h1-lines`였고 그게 바로 그 팩의 2단계입니다. 다만 검사 도구만 준 대조군은 팩 없이도 3회 다 5/5를 맞췄기 때문에, 주장을 성공 여부가 아니라 속도로 좁혔습니다.
   **꼬리:** 비교 실험이 팩 하나에만 있는데, 다른 팩으로 데모를 바꾸면 이 표를 그대로 쓸 수 있을까요?
   **틀리기 쉬운 답:** "팩을 쓰면 성공률이 올라간다"고 답하는 경우가 있는데, 실제로는 자체 실험이 그 주장을 깎았습니다.
4. **Q:** (L3) 판매자가 처음부터 지어낸 기록을 올리거나 산 사람이 복호화한 내용을 퍼뜨리면 어떻게 되나요?
   **A:** 둘 다 막지 못합니다. 해시 사슬은 사후 수정만 드러내서 처음부터 지어낸 기록은 걸러지지 않고, 재배포는 사본에 `record_hash` 사슬과 영수증, 폐기 이력이 없다는 것으로만 갈립니다. 그래서 신뢰 장치를 "구매자만, 구독권당 한 번만" 남기는 온체인 후기 쪽에 뒀습니다. 그 밖에 검사 항목이 웹 랜딩 5항목에 묶여 있어서, 다른 검사 목록을 쓰는 팩이 무엇으로 채점되는지 사는 쪽에 알려 줄 방법이 아직 없습니다.
   **꼬리:** 그럼 이 시장의 품질 신호는 무엇에 기대고 있나요? 팩 넷 중 셋이 구매자 0인 상태에서 그 신호가 작동할까요?
   **틀리기 쉬운 답:** "온체인이니 위조가 불가능하다"고 답하는 경우가 있는데, 실제로 위조가 어려운 것은 기록된 해시이지 기록 내용의 진실성이 아닙니다.

### 솔직하게 말할 것

- 이 프로젝트는 Claude Code로 작업하면서 만들어졌고 그 세션 자체가 판매 팩의 원천이라, 코드를 제가 한 줄씩 다 쳤다고는 말씀드릴 수 없습니다. 원자료 중 하나가 증상에서 원인, 해결로 이어지는 개발 기억 로그라서, 각 함정(JSON-RPC 폐기, SDK 1.x에서 2.x로, 세션 키 시계 오차, stdout 오염)을 어떻게 짚었는지까지가 제가 설명할 수 있는 범위입니다.
- 발표 데모로 만든 Sui 소개 페이지 개선은 절감 효과를 입증하지 않았습니다. 적용 결과는 검사 항목으로 확인했을 뿐이고 시간·비용 절감은 같은 조건에서 따로 재 보겠다고 스스로 밝혀 뒀습니다. 랜딩에 뜨는 시간·비용 수치는 판매 페이지의 비교 예시입니다.
- 표본이 작습니다. 팩은 넷이고 그중 셋은 산 사람이 0이며, 비교 실험은 Paylane 팩 하나에만 있습니다.
- 문서 안에 불일치가 아직 남아 있습니다. 블록체인 개발자 경험 팩의 개수를 README는 33건, 데모 대본은 30건으로 적었고 기준값은 README의 33입니다. 정합 검사기(`tools/consistency.mjs`)를 만들어 둔 프로젝트라 이 대목은 먼저 말씀드리는 편이 낫다고 생각합니다.
- 전부 Sui testnet입니다. 사람별 지속 구독은 제품 비전이고 지금은 기록 단위 기간제 구매이며, 기간이 끝나도 새 복호화 접근만 막힐 뿐 이미 받아 간 평문은 회수하지 못합니다.
- 대회 결과는 자료에 없습니다.
