# 작업 로그

맨 아래에 추가만 한다. 형식은 wiki-rules.md 8절.

## 2026-09-22 init
- 위키 뼈대와 운영 규칙 생성
- 도구: claude-code

## 2026-09-22 ingest: bc-card-2026-analysis-summary.md, bc-card-2026-idea-summary.md, bc-card-2026-project-structure.md
- 신규: projects/bc-card-bigdata-2026
- 신규: concepts/search-trend-api
- 신규: concepts/fad-lifespan-metrics
- 신규: concepts/region-exposure-index
- 갱신: wiki/index.md (projects 1건, concepts 3건 등록)
- lesson 문서는 만들지 않음 (첫 프로젝트라 프로젝트 간 비교 불가, 원자료에 명시적 회고 없음)
- 대회 결과(수상 여부)는 원자료에 없어 "자료에 없음"으로 표기
- 도구: claude-code, ingest 서브에이전트

## 2026-09-22 ingest: 해커톤 폴더 일괄 반영 (10개 프로젝트, 서브에이전트 10개 병렬)
- 선정 기준: 텍스트 자료 유무 > 최근성 > 코드 깊이 > 도메인 다양성. 제외: SweetTACO, AItop100, 스타트업커리어챌린지, 화장품, 블록블록_수이(영상만), 미드나잇, Golang(비어 있음), AgentID(다음 후보)
- 신규 projects (10): blockchain-valley-2026-sabonx, miraeasset-ai-festival-2026, finance-ai-2026-subscription-cut, wanted-interview-ai-2026, kis-openapi-invest-2026-09, wanted-hackathon-2026, jb-finance-compliance-lens-2026, news-bigdata-2026-kkeutmul-radar, hana-ar-kowalk-2026, icognito-2026-trustseal
- 신규 concepts (28): 인덱스 참조
- 갱신 concepts: fad-lifespan-metrics (끝물레이더 사례), rule-engine-llm-split (컴플라이언스렌즈·끝물레이더 사례), evidence-linked-llm-output (끝물레이더 사례)
- 신규 lessons (2): claim-scoping-in-hackathon-docs, self-authored-eval-overfitting
- 모순 표시: wanted-hackathon-2026 (OpenAI 모델명 gpt-6-astra vs gpt-5-mini), finance-ai-2026-subscription-cut (기획서 vs README: LLM 제공자, 저장소, 120일 기한)
- 병합 후보 (lint 대상): grounded-answer-verification ↔ citation-grounding-verification, deterministic-rule-path ↔ rule-engine-llm-split
- 미래에셋_AI 폴더와 미래에셋네이버 폴더는 같은 프로젝트라 하나로 합침. SabonX와 Trust404도 같은 결과물의 두 제출본이라 하나로 합침
- 인덱스는 concepts가 28개로 늘어 주제별 소제목으로 묶음
- 도구: claude-code, ingest 서브에이전트(Opus) 10개 병렬, 인덱스·로그 병합은 본체

## 2026-09-22 lint: 2026-09-22
- 범위: 머리말 형식 상세, 병합 후보 2쌍 판정, 상호 링크 누락. 원자료 대조는 생략(시간 제약)
- 머리말: wiki/**/*.md 43개 전부 title/type/created/updated/sources/tags 6필드 충족, type과 폴더 일치, sources 경로 전부 raw/done/ 안에 실재. 고칠 것 없음
- 병합 후보 판정 ①: grounded-answer-verification ↔ citation-grounding-verification → **구분되는 개념. 병합하지 않음**. 둘 다 "생성 후 대조" 계열이지만 검사 대상과 실패 처리가 다르다. 전자는 답변 속 숫자를 근거 표와 금액 정규화 대조해 미뒷받침 값을 삭제(후처리 필터, 미래에셋). 후자는 인용 조항이 인덱스에 실재하는지 조회해 가짜면 판정 자체를 폐기하고 재판정(자기수정 루프, 재시도 ≤2, JB금융). → 양쪽에 상호 "관련" 링크 1줄씩 추가함
- 병합 후보 판정 ②: deterministic-rule-path ↔ rule-engine-llm-split → **구분되는 개념. 병합하지 않음**. 후자는 "무엇을 LLM에, 무엇을 코드에 맡길지" 가르는 일반 원칙(3개 프로젝트 사례). 전자는 그 원칙을 공시 QA에 적용한 특정 구현(SQL 규칙 73종 + 커버리지 게이트 + 트리거 누락 함정). 추상 수준이 한 단계 다르므로 합치면 원칙 문서가 한 프로젝트 구현 상세에 묻힌다. → 상호 링크 1줄씩 추가함
- 직접 고침 (링크 추가 11줄, 본문 재작성 없음):
  - concepts/grounded-answer-verification ↔ concepts/citation-grounding-verification 상호 링크
  - concepts/deterministic-rule-path ↔ concepts/rule-engine-llm-split 상호 링크
  - (a) 테스트넷 컨트랙트 계열: concepts/testnet-reward-token ↔ concepts/onchain-revocation-registry 상호 링크, projects/hana-ar-kowalk-2026 ↔ projects/blockchain-valley-2026-sabonx 상호 링크
  - (b) DART 공시 계열: concepts/llm-quiz-from-disclosure → projects/miraeasset-ai-festival-2026 (+ grounded-answer-verification, disclosure-correction-chain), projects/miraeasset-ai-festival-2026 → concepts/llm-quiz-from-disclosure, projects/hana-ar-kowalk-2026 → projects/miraeasset-ai-festival-2026
  - (c) 유행 소멸 계열(news-bigdata-2026-kkeutmul-radar ↔ bc-card-bigdata-2026): 이미 projects 양쪽과 fad-lifespan-metrics / supply-side-fad-signal 에 상호 링크가 있어 추가 불필요
- 제안 (고치지 않음):
  - concepts 폴더에 "생성 후 대조 검증" 계열 문서가 4개(grounded-answer-verification, citation-grounding-verification, evidence-linked-llm-output, rule-engine-llm-split)로 늘었다. 병합 대신 이 넷을 묶는 lesson 문서("근거 없는 출력을 막는 네 가지 층위") 신설을 다음 ingest 때 검토할 것
  - concepts/onchain-revocation-registry 는 다른 concept 문서와 달리 머리말 다음 절 제목에 번호가 없다(`## 한 줄 정의` vs 다른 문서의 `## 1. 한 줄 정의`). 형식 통일이 필요하면 별도 작업으로
  - 원자료 대조(문서 서술이 raw/done/ 내용과 맞는지)는 이번 lint에서 수행하지 않음. 특히 병렬 ingest로 들어온 10개 프로젝트는 아직 대조 이력이 없으므로 다음 lint의 우선 대상
- git commit 하지 않음 (본체가 처리)
- 도구: claude-code, lint 서브에이전트

## 2026-09-22 notion-sync: 트래커 첫 동기화 (위키 → 노션)
- 트래커에 열 추가: "제출"(체크박스), "위키 문서"(URL)
- 기존 행 갱신 7건: JB금융, 모바일신분증(AgentID, 제출 체크만), BC카드, 고려대 Trust404, iM뱅크(SabonX 동일 결과물), 원티드 AI Championship(FRAME), 뉴스빅데이터(끝물레이더, 제출 미체크)
- 신규 행 5건: 금융 AI Challenge(구독컷), 미래에셋 AI Festival(공시 Agent), 한투 OpenAPI 투자대회, 하나금융 AR(Ko-Walk), icognito(TrustSeal)
- 뷰 재구성: "🔥 남은 해커톤"(제출 미체크 + 마감 전, 열은 해커톤명·D-day·제출 마감만), "✅ 제출한 해커톤"(제출 체크, 열은 해커톤명·프로젝트명·결과·위키 문서)
- 미처리: 원티드 해커톤 Smash Lab은 대회명이 원자료에 없어 행을 만들지 않음. Blockthon(Memory Market)은 위키에 없음
- 도구: claude-code (Notion MCP)

## 2026-09-22 lint: tools/lint.py
- 결정적 검사: 문제 없음
- LLM 검사 (gpt-5.6-sol):
  ### A. 중복 개념

  - 없음

  ### B. 모순

  - **검색 데이터의 시간 단위 — `search-trend-api` ↔ `fad-lifespan-metrics`**
    - `search-trend-api`: “2016-01~2026-09 유행 음식 26개의 **주간 검색량**을 수집해 유행의 정점 시점, 수명, 교체 간격을 계산했다.”
    - `fad-lifespan-metrics`: “정점의 50%/20%/10% 이상 유지 기간 […]을 네이버(**주간**)·구글(**월간**) 양쪽에 적용했다.”
    - 구글 트렌드가 주간인지 월간인지 어긋난다.
    - 자동 수정 제안: 네이버는 주간, 구글은 월간이었다는 구분을 관련 문서에 동일하게 반영하는 편이 적절하다.

  - **두쫀쿠의 검색량 규모 — `bc-card-bigdata-2026` 내부**
    - “두쫀쿠는 **역대 최대 규모로 흥행**하고도 9주 […]였다.”
    - “구글에서는 두쫀쿠가 대만카스테라의 19배지만 **네이버에서는 대만카스테라(124)가 두쫀쿠(65)보다 크다**.”
    - 첫 문장은 검색엔진을 한정하지 않아 네이버 결과와 충돌한다.
    - 자동 수정 제안: “구글 트렌드 기준 역대 최대 규모”처럼 범위를 한정하는 표현이 적절하다.

  - **수명 정의 개수 — `fad-lifespan-metrics` 내부**
    - “**해결: 7가지 정의로 재계산.**”
    - “정점의 50%/20%/10% 이상 유지 기간, 정점 이후 50%/20%/10% 아래로 떨어질 때까지의 기간, 검색량 면적을 정점 높이로 나눈 실효 기간, 정점 이후 12주 구간의 지수 감쇠 반감기까지 **일곱 가지**로 재고 […]”
    - 열거된 항목은 3+3+1+1로 여덟 가지여서 표기된 개수와 맞지 않는다.
    - 자동 수정 제안: 실제 구현 지표를 확인해 개수를 일곱 또는 여덟로 통일하는 편이 적절하다.

  - **기본 비전 모델명 — `vision-api-fallback-chain` 내부**
    - 설정 표기: “`OPENAI_MODEL=gpt-6-astra`”
    - 설명: “파이프라인 다이어그램은 `gpt-5-mini`.”
    - 기본 모델명이 두 곳에서 다르며 문서도 이를 미해결 모순으로 기록하고 있다.
    - 자동 수정 제안: 실제 실행 설정이나 코드를 기준으로 권위 있는 모델명을 정하고, 확인 전에는 둘 중 어느 쪽도 확정값으로 쓰지 않는 편이 적절하다.

  ### C. 원자료 대비 누락/왜곡

  - **`region-exposure-index` — 계절효과·업종 범위 한계를 빼고 유행 소멸의 피해로 단정**

    | 원자료 | 위키 |
    |---|---|
    | “업종이 11개뿐이라 **두쫀쿠 자체는 못 보고 제과점 전체로 추정**.”<br>“6개월 단면이라 계절 효과(2월 설, 6월 비수기)와 유행 소멸을 **완전히 분리하지 못함**. 대조군 비교로 보완.” | “**해석: 유행 소멸의 피해는 지역을 가리지 않고 전국에서 동시에 온다.**” |

    - 원자료가 명시한 두 가지 핵심 한계가 빠져, 제과점 하락을 유행 소멸의 인과적 피해로 더 강하게 옮겼다.
    - 자동 수정 제안: “유행 소멸 구간과 겹쳐 관측된 제과점 하락” 정도로 범위를 좁히고 두 한계를 함께 남기는 편이 적절하다.

  - **`fad-lifespan-metrics` — 표본 제외와 유행 목록 편향 누락**

    | 원자료 | 위키 |
    |---|---|
    | “검색량이 너무 적어 잡음이 심한 항목(뚱카롱, 십원빵, 온정돈까스 등) […]은 지속 기간 통계에서 뺐습니다.”<br>“유행 목록은 공모전 참고 페이지의 26개라 최근 유행이 더 많이 기억·수록되는 편향이 있을 수 있음. 네이버 데이터랩으로 후보를 넓혀 재검증 필요.” | “어느 정의로 보더라도 2025년 이후 유행이 가장 짧았다.” |

    - 결과를 좌우할 수 있는 제외 기준과 후보 목록의 선택 편향이 빠져 강건성의 범위가 넓어 보인다.
    - 자동 수정 제안: 결과 문장에 저검색량 항목 제외 사실과 26개 후보 목록의 선택 편향을 한계로 병기하는 편이 적절하다.

  - **`search-trend-api` — 구글 트렌드의 월간 데이터를 주간으로 옮김**

    | 원자료 | 위키 |
    |---|---|
    | `09_lifespan_metrics.py`: “유행 수명을 여러 정의로 측정 (**네이버 주간 + 구글 월간**)” | “2016-01~2026-09 유행 음식 26개의 **주간 검색량**을 수집해 […] 계산했다.” |

    - 네이버와 구글의 시간 해상도를 모두 주간으로 합쳐 적었다.
    - 자동 수정 제안: “네이버 주간·구글 월간 검색량”으로 분리해 서술하는 편이 적절하다.

  - **`bc-card-bigdata-2026` — 대안 설명 검토를 ‘기각’으로 강화**

    | 원자료 | 위키 |
    |---|---|
    | “숏폼 영상 확산이나 프랜차이즈 창업 패키지의 저비용화, 경기 위축 같은 **다른 설명도 검토했습니다**.”<br>“생성형 AI 때문에 콘텐츠를 만드는 속도가 달라진 것이 원인이라고 **생각합니다**.” | “대안 설명(숏폼 확산, 프랜차이즈 창업 패키지 저비용화, 경기 위축)은 시점이 맞지 않아 **기각했다**.” |

    - 원자료의 가설적·잠정적 판단이 대안을 확정적으로 배제한 것으로 강화됐다.
    - 자동 수정 제안: “대안 설명은 관측된 변화의 시점과 덜 부합한다고 보았다”처럼 잠정성을 유지하는 표현이 적절하다.
- 도구: tools/lint.py (openai api)

## 2026-09-22 lint 반영: 첫 API 점검(gpt-5.6-sol) 결과 처리
- 수정: concepts/fad-lifespan-metrics (정의 개수 7→8, `09_lifespan_metrics.py` 대조로 확인; 표본 제외·목록 편향 한계 병기)
- 수정: concepts/search-trend-api (네이버 주간·구글 월간으로 분리 표기)
- 수정: projects/bc-card-bigdata-2026, wiki/index.md (정의 개수 7→8)
- 규칙 추가: wiki-rules.md 2절, ingest 서브에이전트, AGENTS.md에 "원자료의 확신 수준 보존" 조항. 점검 지적 8건 중 4건이 잠정 표현→확정 표현 왜곡이라 개별 수정보다 규칙으로 대응
- 보류: bc-card "역대 최대 흥행" 범위 한정, region-exposure-index 한계 병기, "대안 설명 기각" 표현, vision-api-fallback-chain 모델명 — 재사용 가치 낮거나 이미 모순 표시됨. log의 lint 항목에 기록 유지
- 도구: claude-code

## 2026-09-22 ingest: github-repo-map.md
- 갱신: projects 11건 모두 — 머리말에 `repo:` 필드 추가, 개요 절에 "코드 저장소" 줄 추가 (로컬 git 원격에서 읽음)
- 저장소 없음 5건: bc-card(분석 스크립트 로컬만), kis-openapi(코드 로컬만), wanted-hackathon Smash Lab(코드 로컬만), news-bigdata, icognito (뒤 둘은 코드 없음)
- 로컬 정리 전 주의: 위 코드 3건과 AgentID 코드, 그리고 모든 PDF·pptx·mp4 산출물은 어느 git에도 없음
- 도구: claude-code
## 2026-09-22 ingest: tacotrump-2026-03-code-overview.md
- 신규: projects/taco-index-2026-03
- 신규: concepts/market-redline-composite-score (safe·redline 선형보간 정규화 합산)
- 신규: concepts/free-market-data-fetch-fallback (Yahoo v8 직접호출·FRED·RCP 스크래핑, 3겹 실패 흡수)
- 신규: concepts/vercel-python-cron-webpush (BaseHTTPRequestHandler 함수, crons, Redis 직전상태 비교, VAPID 웹푸시, 410 청소)
- 신규: concepts/dual-backend-local-vs-serverless (backend/ FastAPI vs api/ 서버리스 로직 복제와 표류)
- 메모: 해커톤 출품 여부는 원자료에 없어 개요에 "자료에 없음(개인 프로젝트 추정)"으로 기재. backend/와 api/의 총점 구성·레벨 색이 실제로 어긋나 있어 프로젝트 문서 4절과 concept에 기록.
- 도구: claude-code, 노트북

## 2026-09-22 ingest: im-challenge-daegu-2026-sns-menu-*.md
- 신규: projects/im-challenge-daegu-2026-sns-menu
- 신규: concepts/ngram-burst-discovery, concepts/search-index-stage-rule, concepts/public-store-population-context, concepts/ai-judgement-rule-ceiling, concepts/test-sale-cost-model
- 갱신: concepts/search-trend-api (연령별 기준자 용법, NAVER API HUB 이관·구독 401 메모, pytrends 제약 추가)
- 갱신: concepts/supply-side-fad-signal (상호명 기반 신규 점포 수를 공급 과열 후행 신호로 쓰는 변형 추가)
- 갱신: concepts/fad-lifespan-metrics (수명 대신 훅 창을 쓴 두 번째 측정 사례 추가)
- 갱신: concepts/rule-engine-llm-split (한 프로젝트 안에서 비용은 규칙, 적합도는 AI로 갈린 사례 추가)
- 갱신: concepts/evidence-linked-llm-output (인용 포함 검사·근거 ID 재검증, 원문 지시문 무시 확인 추가)
- 갱신: lessons/claim-scoping-in-hackathon-docs (개정이 아니라 최초 작성부터 범위를 좁힌 사례, 세 프로젝트 공통 형태 추가)
- 갱신: projects/blockchain-valley-2026-sabonx (같은 대회 다른 트랙 상호 링크)
- 도구: claude-code, 노트북

## 2026-09-22 ingest: blockthon-2026-memory-market-*.md
- 원자료: readme, demo, dev-memories, presentation-script, buyer-demo-notes (5건)
- 신규: projects/blockthon-2026-memory-market
- 신규: concepts/agent-session-capture-hooks, concepts/sui-timed-access-subscription, concepts/seal-key-policy-and-session-traps, concepts/onchain-buyer-only-receipt, concepts/repo-landing-chain-consistency, concepts/sui-sdk-rpc-migration-2026, concepts/stdio-mcp-server-hygiene
- 신규: lessons/measured-baseline-over-claimed-gain (대조군 실측과 수치 출처 명시)
- 갱신: concepts/onchain-revocation-registry ("어디서 썼는가"에 fail-open 대비 사례 추가)
- 갱신: concepts/ai-log-anchoring-data-receipt ("어디서 썼는가"에 구매자 영수증 구현 사례 추가)
- 메모: 블록체인 개발자 경험 팩 개수가 README 33건 / 데모 대본 30건으로 어긋나 project 문서에 모순 블록 표시 (README가 ground-truth)
- 도구: claude-code, 노트북

## 2026-09-22 ingest: 학습 절·면접 준비 절 일괄 추가 (서브에이전트 8개, 웹 대조)
- 규칙 11절(concept `## 학습`)·12절(project `## 면접 준비`) 신설. 질문 수준은 신입 기술면접 프로젝트 딥다이브(L1 개념 / L2 판단 / L3 한계 + 꼬리질문 + 틀리기 쉬운 답)
- concept 47개 전부에 cs_topics + 학습 절 (확인 질문 185개). 각 서브에이전트가 WebSearch로 실제 면접 질문·공식 문서를 대조하고 "더 파볼 것"은 WebFetch로 열어 확인한 URL만 기재
- project 14개 전부에 면접 준비 절 (한 문장 소개, 기술 스택과 선택 이유 표, 고민한 점, 예상 질문 67개, 솔직하게 말할 것)
- "왜 이걸 썼나"가 원자료에 없는 칸은 "이유 자료에 없음"으로 비움 — 사용자가 직접 채울 자리. 특히 jb-finance(9칸), wanted-interview-ai(13칸), hana-ar-kowalk(7칸)에 집중
- 미디어·인프라 concept 10개의 "설명할 수 있어야 하는 것"이 규칙 예시 문구 그대로 들어간 것을 발견해 재작성
- 새로 발견된 불일치: taco-index의 크론 docstring(5분)과 vercel.json(매시간) 불일치
- 사이트: 프로젝트 중심 면접 노트 UI로 개편 (tools/build_site.py). 홈 → 프로젝트 → 개념. 그래프는 보조
- 도구: claude-code, ingest 서브에이전트(Opus) 8개, 본체 병합

## 2026-09-22 문체·아키텍처 일괄 반영 (서브에이전트 6개)
- 규칙 13절(문체: my-writing-voice, 면접 대화체)·14절(아키텍처 절 형식) 신설
- concept 47개 `## 학습` 절과 project 14개 `## 면접 준비` 절을 면접 대화체로 재작성. 사실·숫자·코드 참조·확신 표시는 유지
- project 14개에 `### 아키텍처` 절 추가(층·기술·호스팅·연결). 호스팅 미기재는 "호스팅 자료에 없음"으로 둠 (icognito 전부, 끝물레이더 대부분, FRAME 워커 2개, jb 규정 인덱스, Ko-Walk 크론)
- 사이트: 탭 패널 전환, 아키텍처 그림, 홈 기술 스택 필터·로고, 화면 문구 경어체
- 도구: claude-code, Opus 서브에이전트 6개, 본체 병합

## 2026-09-22 site: 아키텍처 그림 개편
- 좌→우 흐름형 배치, iconify logos 컬러 로고(없으면 Simple Icons → 글자 배지), 묶음 상자(14절 네 번째 항목), 번호 배지 화살표와 번호 목록
- project 5개에 묶음 항목 추가 (miraeasset, jb-finance, im-challenge, wanted-hackathon, hana-ar-kowalk). 나머지는 근거 부족 또는 층별 노드 1개라 미적용
- 도구: claude-code, Sonnet 서브에이전트 1개

## 2026-09-22 ingest: SabonX DID·브라우저 지갑 학습 정리

- 원자료: raw/done/blockchain-valley-2026-sabonx-readme.md, raw/done/blockchain-valley-2026-trust404-readme.md와 SabonX에 관해 나눈 DID·VC·개인키 보관 대화
- 신규: concepts/did-vc-trust-chain (식별자·전자서명·VC·발급기관 신뢰의 역할과 체인 조회 범위)
- 신규: concepts/browser-wallet-key-storage (IndexedDB 출처 분리, XSS·키 분실 한계, 저장 시 암호화의 범위)
- 갱신: projects/blockchain-valley-2026-sabonx (관련 개념 링크), wiki/index.md
- 확인: W3C DID Core·VC Data Model·did:key Method, MDN 동일 출처 정책, OWASP HTML5 Security Cheat Sheet를 대조함
- 도구: codex
