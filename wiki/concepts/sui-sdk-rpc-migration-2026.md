---
title: 2026년 Sui 접속 방식 이전 (JSON-RPC 폐기, SDK 1.x→2.x)
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/blockthon-2026-memory-market-dev-memories.md, raw/done/blockthon-2026-memory-market-readme.md]
tags: [블록체인, Sui, SDK, gRPC, GraphQL, 개발환경]
cs_topics: [네트워크, 웹, 소프트웨어공학]
---

## 한 줄 정의

2026년 기준 Sui 공개 풀노드의 JSON-RPC가 폐기되어 웹의 예제 대부분이 그대로는 돌지 않는다. 쓰기와 객체 조회는 `@mysten/sui` 2.x의 gRPC, 목록과 이벤트는 GraphQL로 갈아타야 한다.

## 어디서 썼는가

- [[blockthon-2026-memory-market]], 컨트랙트 호출과 랜딩의 체인 조회 전부.

## 걸린 자리

- **JSON-RPC 폐기.** `new SuiClient({ url: getFullnodeUrl('testnet') })`로 트랜잭션을 보내면 `JsonRpcError: Method not found. JSON-RPC on public fullnodes has been deprecated` (code -32601). 브라우저에서 `sui_getObject`도 같은 -32601. 입문자가 여기서 막힌다.
- **1.x로는 안 된다.** 1.45.2의 gRPC 클라이언트는 (a) transaction resolution 미지원(`Transaction resolution is not supported with the GRPC client`, SDK 소스에서 해당 플러그인이 통째로 주석 처리), (b) 수동으로 다 채워도 노드가 `invalid read_mask path: transaction.transaction`으로 거절한다(노드 1.79 기준). 2.29로 올리면 둘 다 해결. 2026-09 기준 latest는 `@mysten/sui` 2.29.0, `@mysten/seal` 1.4.8. 오래된 예제를 보고 `^1.x`, `^0.9.x`로 잡으면 여기서 막힌다.
- **2.x 실행 API.** `client.signAndExecuteTransaction({ transaction, signer, include })`. **응답에 담을 필드를 `include`로 명시**해야 한다. `{ effects: true, objectTypes: true }`를 안 주면 `undefined`. 결과는 `$kind: 'Transaction' | 'FailedTransaction'` 유니온이라 `$kind`를 먼저 본다.
- **gRPC 응답에는 `objectChanges`가 없다.** 새 객체는 `res.effects.changedObjects`에서 `idOperation === 'Created'`로 거르고 타입은 `res.objectTypes`(id → type 맵)로 본다. 필드명은 `c.id`가 아니라 **`c.objectId`**.
- **가스와 객체 버전을 손으로 안 채워도 된다.** 2.x gRPC는 resolution과 가스 선택을 지원하므로 `tx.object(id)`만 넘기면 되고, 1.x 때 쓰던 `sharedObjectRef`/`objectRef` 수동 지정과 `setGasPrice/Budget/Payment`는 전부 걷어낸다. (1.x 한정) `keypair.signAndExecuteTransaction`이 sender를 안 채워 `Missing transaction sender`가 나던 문제도 2.x에는 없다.
- **목록과 이벤트는 GraphQL.** gRPC 이벤트 색인은 최근 체크포인트만 들고 있어 며칠 지난 이벤트가 안 나온다. 객체 조회도 `query($a:SuiAddress!){ object(address:$a){ asMoveObject{ contents{ json } } } }`로 필드가 그대로 나온다. CORS `*`라 브라우저에서 직접 읽힌다.
- **필드 이름을 넘겨짚지 말 것.** GraphQL로 읽은 값이 계속 0이길래 보니 필드명이 `price_mist`가 아니라 `fee`(MIST 단위)였고 `namespace`가 아니라 `source_namespace`였다. `contents{ json }`을 한 번 통째로 찍어 이름을 확인하고 쓴다.
- **Move 2024.** `vector::empty()`와 `dynamic_field::exists_`는 deprecated(각각 `vector[]` 리터럴, `df::exists`). `expected_failure(abort_code=...)` 테스트는 마지막에 도달 불가 코드가 필요해 `abort 0`으로 끝낸다.
- **Walrus aggregator는 content-type을 주지 않는다.** 같은 미리보기 목록에 JSON, JPEG, 순수 텍스트가 섞이므로 읽는 쪽이 첫 바이트로 종류를 나눈다(`89 50`=PNG, `ff d8`=JPG, `{`=JSON, 나머지는 글). 텍스트 미리보기를 "없음"으로 처리하면 팔 거리를 스스로 버리는 셈이다.

## Windows 환경 함정

- Sui CLI 릴리스에 Windows용 `.zip`은 없고 `.tgz`만 있다(`.zip`은 404). 내장 `tar`로 푼다.
- `.ps1` 안에서 `[Environment]::SetEnvironmentVariable("Path", ..., "User")`로 PATH를 등록해도 그 스크립트를 띄운 부모 창에는 반영되지 않는다. 현재 창은 `$env:Path += ...`로 직접, 영구분은 새 창부터 적용된다.
- `sui client --yes`는 Windows에서 여전히 대화형 질문을 띄운다. 스크립트에서 `| Out-Null`로 출력을 가리면 **멈춘 것처럼 보인다**. 출력을 가리지 말 것.
- 설정 파일이 없을 때 초기화는 아무 하위 명령(`sui client active-address` 등)으로 유발한다. 이때 복구 문구 12단어가 터미널에 그대로 찍히므로 녹화와 로그 공유에 주의한다.
- 한글이 든 `.ps1`은 UTF-8 BOM(`utf-8-sig`)으로 저장한다. 아니면 PowerShell 5.x가 CP949로 읽어 깨진다.
- 클라우드 샌드박스(egress 제한)에서는 `fullnode.testnet.sui.io:443`, `faucet.testnet.sui.io:443`가 프록시에서 차단된다. 체인에 닿는 명령은 로컬에서. `sui move build/test`는 네트워크 없이 된다.
- `dotenv/config`를 import하면 `.env`를 cwd에서 찾는다. 하위 폴더에서 `npm run` 하면 루트 `.env`를 못 찾으므로 `import.meta.url` 기준 절대 경로로 `loadEnv({ path: ... })`를 부른다.

## 참고 자료

- 관련: [[sui-timed-access-subscription]], [[seal-key-policy-and-session-traps]], [[stdio-mcp-server-hygiene]]

## 학습

### CS 주제
- 네트워크: RPC 프로토콜 세대교체(JSON-RPC → gRPC/GraphQL), CORS, 응답 필드 선택
- 웹: 브라우저에서 직접 체인 읽기, 오버페칭과 언더페칭
- 소프트웨어공학: 의존성 버전 고정, 오래된 예제의 부채, 환경별 빌드 함정

### 설명할 수 있어야 하는 것
- 공개 풀노드의 JSON-RPC가 폐기돼 선택지가 없었다는 점과, 쓰기는 gRPC로 목록·이벤트는 GraphQL로 나눈 것이 각 인터페이스의 색인 특성에 맞았던 이유를 설명할 수 있습니다.
- 1.x에 머무르면 예제를 그대로 쓸 수 있지만 transaction resolution이 없어 애초에 동작하지 않았다는 점과, 2.x로 올리며 API 형태 변경을 전부 떠안은 대가를 말할 수 있습니다.
- gRPC 이벤트 색인이 최근 체크포인트만 들고 있어서 며칠 지난 이벤트를 놓친다는 점을 이유와 함께 설명할 수 있습니다.

### 확인 질문
1. **Q:** (L1 개념) 2026년 기준으로 Sui에 접속하는 인터페이스에는 무엇이 있고, 각각 어디에 쓰셨나요?
   **A:** 공개 풀노드의 JSON-RPC는 폐기돼서 `new SuiClient({ url: getFullnodeUrl('testnet') })`로 트랜잭션을 보내면 `JsonRpcError: Method not found ... deprecated`가 code -32601로 나고, 브라우저의 `sui_getObject`도 같은 -32601이었습니다. 대체는 두 가지였는데 쓰기인 트랜잭션 실행과 객체 조회는 `@mysten/sui` 2.x의 gRPC로, 목록과 이벤트 같은 구조적 질의는 GraphQL로 갔습니다. Memory Market은 컨트랙트 호출을 gRPC로 하고 팩 목록과 랜딩의 체인 조회를 `graphql.testnet.sui.io`로 처리했습니다.
   **꼬리:** 그러면 같은 데이터를 gRPC로도 GraphQL로도 읽을 수 있을 때는 무엇을 기준으로 고르시나요?
   **틀리기 쉬운 답:** "RPC URL만 바꾸면 됩니다"라고 답하는 경우가 있는데, 실제로는 호출 형태와 응답 구조가 모두 다릅니다.
2. **Q:** (L2 판단) 목록과 이벤트만 GraphQL로 빼신 이유가 있나요?
   **A:** gRPC의 이벤트 색인이 최근 체크포인트만 들고 있어서 며칠 지난 `PackCreated` 이벤트가 조회되지 않았기 때문입니다. 시장 목록은 오래된 팩까지 다 보여야 해서 gRPC로는 성립하지 않았습니다. GraphQL은 `query($a:SuiAddress!){ object(address:$a){ asMoveObject{ contents{ json } } } }` 형태로 객체 필드가 그대로 나오고 CORS가 `*`라 브라우저에서 직접 읽을 수 있어서, 랜딩 페이지도 백엔드 없이 체인을 읽게 했습니다.
   **꼬리:** 그러면 오래된 이벤트가 필요한데 GraphQL도 못 쓰는 상황이면 무엇을 세우시겠어요?
   **틀리기 쉬운 답:** "이벤트가 안 나오면 트랜잭션이 실패한 것입니다"라고 답하는 경우가 있는데, 실제로는 색인 보존 범위의 문제입니다.
3. **Q:** (L3 한계) SDK 1.x로는 왜 안 됐고, 2.x로 올리면서 코드에서 무엇이 바뀌었나요?
   **A:** 1.45.2의 gRPC 클라이언트가 transaction resolution을 지원하지 않았고(`Transaction resolution is not supported with the GRPC client`, SDK 소스에서 해당 플러그인이 통째로 주석 처리돼 있었습니다), 수동으로 다 채워 봐도 노드가 `invalid read_mask path: transaction.transaction`으로 거절했습니다(노드 1.79 기준). 2.29로 올리니 둘 다 풀렸는데, 2.x에서는 `client.signAndExecuteTransaction({ transaction, signer, include })`로 부르면서 응답에 담을 필드를 `include`로 명시해야 하고(`{ effects: true, objectTypes: true }`를 안 주면 `undefined`가 됩니다), 결과가 `$kind: 'Transaction' | 'FailedTransaction'` 유니온이라 `$kind`를 먼저 봅니다. `objectChanges`가 없어져서 새 객체는 `res.effects.changedObjects`에서 `idOperation === 'Created'`로 걸렀고 필드명도 `c.id`가 아니라 `c.objectId`였습니다. 반대로 가스와 객체 버전 수동 지정인 `sharedObjectRef`/`objectRef`, `setGasPrice/Budget/Payment`는 전부 걷어냈습니다.
   **꼬리:** 그러면 `include`를 명시하게 하는 API 설계는 어떤 문제를 풀려는 것일까요?
   **틀리기 쉬운 답:** 오래된 예제를 보고 `^1.x`나 `^0.9.x`로 버전을 잡는 경우가 있는데, 2026-09 기준 latest는 `@mysten/sui` 2.29.0과 `@mysten/seal` 1.4.8입니다.
4. **Q:** (L2 판단) GraphQL로 읽은 값이 계속 0으로 나왔다고 하셨는데, 어떻게 찾으셨고 무엇을 배우셨나요?
   **A:** 필드명을 넘겨짚은 것이 원인이었습니다. `price_mist`가 아니라 `fee`였고 단위는 MIST였으며, `namespace`가 아니라 `source_namespace`였습니다. `contents{ json }`을 한 번 통째로 찍어 실제 이름을 확인하고 쓰는 것으로 해결했습니다. 비슷한 계열로 Walrus aggregator는 content-type을 주지 않아서 같은 미리보기 목록에 JSON과 JPEG와 순수 텍스트가 섞이는데, 읽는 쪽이 첫 바이트로 종류를 나누게 했습니다(`89 50`은 PNG, `ff d8`은 JPG, `{`는 JSON, 나머지는 글). 스키마나 메타데이터를 가정하지 말고 실제 응답을 먼저 덤프하라는 같은 이야기라고 생각합니다.
   **꼬리:** 그러면 타입 안전한 gRPC였다면 이 버그가 났을까요?
   **틀리기 쉬운 답:** 값이 0으로 나올 때 체인 데이터가 비었다고 결론짓는 경우가 있는데, 실제로는 필드명이 틀린 경우가 있습니다.

### 더 파볼 것
- [JSON-RPC Migration Guide (Sui Docs)](https://docs.sui.io/develop/accessing-data/json-rpc-migration) — 폐기 일정(2026-07-27 주 mainnet 차단, 10월 중순 코드 제거)과 메서드 대응표
- [gRPC Overview (Sui Docs)](https://docs.sui.io/concepts/grpc-overview) — gRPC가 겨냥하는 용도(저지연 조회, 트랜잭션 제출, 스트리밍)와 GraphQL과의 역할 분담
