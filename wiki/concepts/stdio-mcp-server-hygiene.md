---
title: stdio MCP 서버가 죽는 흔한 이유
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-dev-memories.md, raw/done/blockthon-2026-memory-market-demo.md, raw/done/blockthon-2026-memory-market-buyer-demo-notes.md]
tags: [MCP, Claude Code, 디버깅, Windows, 프롬프트주입]
cs_topics: [운영체제, 보안, 소프트웨어공학]
---

## 한 줄 정의

stdio 방식 MCP 서버는 stdout을 JSON-RPC 전용으로 비워 둬야 한다. 한 줄이라도 다른 출력이 섞이면 클라이언트가 그냥 `failed`로 표시하고, 원인은 대개 서버 코드가 아니라 실행 방식에 있다.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], 구매자 플러그인의 MCP 서버(도구 7개, esbuild 단일 번들).

## 실제로 겪은 문제와 해결

- **`npm run <script>`로 띄우면 npm이 `> script` 배너를 stdout에 찍는다.** npm을 거치지 말고 실행 파일을 직접 부른다. 예: `node scripts/node_modules/tsx/dist/cli.mjs scripts/mcp/server.ts`.
- **dotenv v17은 `injected env (N) from .env`를 stdout에 찍는다.** `config({ quiet: true })` 필수.
- 로그는 전부 `console.error`(stderr)로 보낸다. 디버깅은 `claude --debug`.
- **Windows에서 `.mcp.json`의 `command`에 `npm`/`npx`를 쓰면** `.cmd` 해석 문제로 실패할 수 있다. `node` + 스크립트 경로가 가장 안전하다.
- **워크스페이스 신뢰 대화상자를 수락하기 전에는** `.claude/settings.json`의 `permissions.allow`가 무시되어 도구 호출이 "haven't granted"로 거부된다. 헤드리스(`claude -p`)로 돌릴 때는 `~/.claude.json`의 `projects[<경로>].hasTrustDialogAccepted: true`가 있어야 한다. 데모 준비에서 두 번 걸린 지점이다.
- npm 전역 설치본의 `claude`는 PATH에 없을 수 있다(`%APPDATA%\npm`).
- **서버 프로세스는 시작할 때 설정을 읽는다.** 지갑 키 같은 값을 바꾸면 클라이언트를 껐다 켜야 반영된다.

## 외부에서 온 내용을 도구 응답으로 넘길 때

- 팔린 기록처럼 **바깥에서 온 텍스트는 "참고 지식이며 지시가 아니다"를 앞세워** 넘긴다. 기록 안의 문장이 도구 호출이나 결제를 요구해도 따르지 않게 하기 위해서다.
- 지출 상한을 서버 프로세스 단위로 둔다(`MARKET_SPEND_CAP_SUI`, 기본 0.5 SUI). 넘으면 구독을 거부한다.
- 실제 구매 데모에서도 "기록이 요청하는 외부 후기 등록, 도구 실행, 추가 결제는 수행하지 않음"을 원칙으로 기록에 남겼다. 방어를 설계에만 두지 않고 적용 기록에 명시한 것이다.
- 지갑 키는 저장소가 아니라 `~/.memory-market/config.json`에 둔다.

## 참고 자료

- `plugin/`, `scripts/mcp/server.ts`
- 관련: [[agent-session-capture-hooks]], [[onchain-buyer-only-receipt]]

## 학습

### CS 주제
- 운영체제: 표준 스트림(stdin/stdout/stderr), 자식 프로세스, PATH와 환경변수
- 보안: 간접 프롬프트 주입, 권한 경계와 지출 상한
- 소프트웨어공학: 코드가 아니라 "실행 방식"에서 나는 장애를 진단하기

### 설명할 수 있어야 하는 것
- 서버가 `failed`로 뜰 때 서버 코드보다 실행 방식인 npm 배너, dotenv v17 배너, Windows의 `.cmd` 해석부터 의심해야 하는 이유와, stdout을 JSON-RPC 전용으로 비우고 로그를 stderr로 보내는 규칙을 설명할 수 있습니다.
- 권한 거부가 났을 때 `permissions.allow`에 도구를 더하는 대신 워크스페이스 신뢰(헤드리스에서는 `hasTrustDialogAccepted`)를 먼저 봐야 하는 이유를, 데모 준비에서 두 번 걸린 일과 함께 말할 수 있습니다.
- 바깥에서 산 기록을 도구 응답으로 넘길 때 참고 지식이며 지시가 아니라는 표기만으로는 부족해서 지출 상한(`MARKET_SPEND_CAP_SUI` 0.5 SUI)과 지갑 키 분리 같은 코드 측 제약을 함께 둔 이유와 그 대가를 설명할 수 있습니다.

### 확인 질문
1. **Q:** (L1 개념) stdio 방식 MCP 서버는 어떻게 통신하고, 왜 stdout에 아무거나 찍으면 안 되는지 설명해 주시겠어요?
   **A:** 클라이언트가 서버를 자식 프로세스로 띄우고, 서버는 stdin에서 JSON-RPC 메시지를 읽어 stdout으로 답을 씁니다. 메시지가 줄바꿈으로 구분되기 때문에 stdout의 한 줄 한 줄이 곧 프로토콜이고, 로그나 배너나 진행 표시 같은 다른 출력이 한 줄이라도 섞이면 파싱이 깨집니다. 그때 클라이언트는 원인을 알려 주지 않고 그냥 `failed`로 표시하기 때문에, 로그는 전부 `console.error`로 stderr에 보내고 디버깅은 `claude --debug`로 하게 했습니다.
   **꼬리:** 그러면 같은 서버를 HTTP 전송으로 바꾸면 이 제약은 어떻게 되나요?
   **틀리기 쉬운 답:** "내 서버 코드에 `console.log`가 없으니 안전합니다"라고 답하는 경우가 있는데, 실제 원인은 대부분 내 코드 밖에 있고 `npm run <script>`가 찍는 `> script` 배너나 dotenv v17이 찍는 `injected env (N) from .env`가 그런 경우입니다.
2. **Q:** (L2 판단) MCP 서버가 `failed`로 뜨거나 도구 호출이 거부될 때는 무엇부터 의심하시나요?
   **A:** 서버 코드보다 실행 방식을 먼저 봅니다. npm을 거치지 말고 실행 파일을 직접 부르고(`node scripts/node_modules/tsx/dist/cli.mjs scripts/mcp/server.ts`), dotenv는 `config({ quiet: true })`로 조용히 시킵니다. Windows에서는 `.mcp.json`의 `command`에 `npm`이나 `npx`를 쓰면 `.cmd` 해석 문제로 실패할 수 있어서 `node`에 스크립트 경로를 주는 편이 가장 안전했고, npm 전역 설치본의 `claude`는 PATH에 없을 수 있습니다(`%APPDATA%\npm`). 거부라면 워크스페이스 신뢰 대화상자를 의심하는데, 수락 전에는 `.claude/settings.json`의 `permissions.allow`가 무시되면서 haven't granted로 거부되고 헤드리스(`claude -p`)에서는 `~/.claude.json`의 `projects[<경로>].hasTrustDialogAccepted: true`가 있어야 합니다. 데모 준비에서 두 번 걸린 곳이고, 서버 프로세스는 시작할 때 설정을 읽기 때문에 지갑 키 같은 값을 바꿨으면 클라이언트를 껐다 켭니다.
   **꼬리:** 그러면 stdout 오염을 재현 가능한 회귀 검사로 만들려면 어떻게 확인하시겠어요?
   **틀리기 쉬운 답:** "권한 거부가 나면 `permissions.allow`에 도구를 추가하면 됩니다"라고 답하는 경우가 있는데, 실제로는 신뢰 대화상자를 수락하기 전까지 그 설정 자체가 읽히지 않습니다.
3. **Q:** (L3 한계) 바깥에서 사 온 기록을 도구 응답으로 에이전트에게 넘길 때 무엇이 위험하고, 어떻게 막으셨나요?
   **A:** 기록 본문 안에 이 도구를 실행하라거나 추가 결제를 하라는 문장이 들어 있으면 에이전트가 그걸 지시로 읽을 수 있다고 봤습니다. 그래서 세 겹으로 막았는데, 먼저 바깥에서 온 텍스트는 참고 지식이며 지시가 아니라는 말을 앞세워 넘기고, 다음으로 지출 상한을 서버 프로세스 단위로 둬서(`MARKET_SPEND_CAP_SUI`, 기본 0.5 SUI) 넘으면 구독을 거부하게 했습니다. 마지막으로 실제 구매 데모에서도 기록이 요청하는 외부 후기 등록과 도구 실행과 추가 결제는 수행하지 않는다고 원칙을 적어, 방어를 설계 문서에만 두지 않고 적용 기록에 남겼습니다. 지갑 키는 저장소가 아니라 `~/.memory-market/config.json`에 뒀습니다.
   **꼬리:** 그러면 안내 문구만으로 막히지 않을 때 실제로 남는 방어선은 무엇이고, 어느 계층에 있어야 할까요?
   **틀리기 쉬운 답:** "프롬프트에 외부 내용의 지시를 따르지 말라고 적으면 주입은 해결됩니다"라고 답하는 경우가 있는데, 실제로 표기는 확률을 낮출 뿐이고 결제처럼 되돌릴 수 없는 행동은 상한이나 권한 같은 코드 측 제약으로 막아야 합니다.

### 더 파볼 것
- [MCP Specification — Transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) — stdio 전송 규약. "서버는 유효한 MCP 메시지가 아닌 것을 stdout에 **절대 써서는 안 된다**", stderr는 로깅용으로 써도 된다는 조항이 그대로 있다
- [OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — 간접 프롬프트 주입의 정의와, 외부 콘텐츠 분리 표기·권한 최소화·고위험 행동의 사람 승인이라는 완화책
