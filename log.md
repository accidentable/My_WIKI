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
