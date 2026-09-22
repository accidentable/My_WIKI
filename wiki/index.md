# 해커톤 지식 위키 — 인덱스

모든 문서는 여기 한 줄로 등록된다. 형식은 wiki-rules.md 7절.

## projects
- [[bc-card-bigdata-2026]] — BC카드 빅데이터 해커톤, 검색 트렌드 + 카드결제로 만든 유행 리스크 조기경보 서비스 제안 (2026-09)
- [[blockchain-valley-2026-sabonx]] — SabonX, 신분증 사본 없이 DID·VC로 월급 확인·소득 신고를 잇는 블록체인 프로토타입 (AI Blockchain Challenge in Daegu / TRUST404 Track 02)
- [[miraeasset-ai-festival-2026]] — 미래에셋증권 AI Festival 공시 Agent, DART 공시 4,204건 구조화 + 결정론 경로·근거 검증으로 접수번호 붙은 답 생성 (2026-09)
- [[finance-ai-2026-subscription-cut]] — 2026 금융 AI Challenge, 해외 구독·클라우드 이상청구 대응 에이전트 "구독컷" (2026-09)
- [[wanted-interview-ai-2026]] — 원티드 AI Championship 2026, 채용 영상에서 검토 기준별 지원자 발언을 원문·타임스탬프로 연결하는 FRAME (2026)
- [[kis-openapi-invest-2026-09]] — 한국투자증권 OpenAPI 실전투자대회, KOSPI100 5일선 돌파 역발상 자동매매 봇 (2026-09)
- [[wanted-hackathon-2026]] — 원티드 해커톤, 사진 속 물건을 AI로 잘라내 소재별로 부수는 모바일 웹 3D 데모 Smash Lab (2026-09 추정)
- [[jb-finance-compliance-lens-2026]] — JB금융 Fin:AI Challenge, 금융 광고 콘텐츠를 게시 전 자동 사전심의하는 준법 AI Agent 제안 (2026)
- [[news-bigdata-2026-kkeutmul-radar]] — 2026 뉴스빅데이터 해커톤, 뉴스 공급신호로 디저트 유행 단계를 판정하는 포화 경보 서비스 "끝물레이더" 기획서 (2026-09)
- [[hana-ar-kowalk-2026]] — 하나금융 AR 해커톤, 상장기업 본사를 걸어서 방문해 AR로 주식 토큰을 수집하는 앱 기획 (2026)
- [[im-challenge-daegu-2026-sns-menu]] — SNS 신메뉴 AI 컨설팅, SNS 유행 신메뉴를 대구 개인 카페의 재료·장비·예산에 맞춰 시험 판매로 잇는 Next.js 프로토타입 (2026-09)
- [[blockthon-2026-memory-market]] — Blockthon 2026 Memory Market, AI와 일한 대화 기록을 Sui에서 기간 한정으로 파는 시장 (Claude Code 플러그인 + Move 컨트랙트, 2026-09)
- [[icognito-2026-trustseal]] — AI TrustSeal, AI 개인정보 처리 로그를 체인에 앵커링하고 사용자에게 '데이터 영수증'을 발급하는 SDK 플랫폼 기획 (기간 자료에 없음)
- [[taco-index-2026-03]] — TACO Index(타코알리미), 시장지표 6개로 트럼프 대이란 강경책 번복 가능성을 점수화한 대시보드 (2026-03, 해커톤 여부 자료에 없음)

## concepts

### 데이터 분석 · 트렌드
- [[search-trend-api]] — 네이버 데이터랩·구글 트렌드 검색량을 기준 검색어로 스케일 통일해 관심도 시계열 만들기
- [[fad-lifespan-metrics]] — 유행 수명을 8가지 정의로 재어 결론의 강건성 확인하기
- [[region-exposure-index]] — 충격이 전국 동시에 올 때 지역 지수를 하락폭 대신 노출도로 세우기
- [[supply-side-fad-signal]] — 관심의 크기 대신 공급 측 사건의 순서로 유행의 포화·쇠퇴 단계 판정하기
- [[ngram-burst-discovery]] — 이름 없는 유행 후보를 사전 없이 n-gram 버스트로 찾고 LLM·교차확인으로 거르기
- [[search-index-stage-rule]] — 일별 검색지수 7일 이동평균으로 감지·정점·하락 단계와 행동 가능 기간(훅 창) 판정하기
- [[bigkinds-api]] — 빅카인즈 API로 기사량·연관어·기관 개체명을 뽑아 뉴스 신호 시계열 만들기
- [[market-redline-composite-score]] — 단위가 다른 시장지표를 safe·redline 사이 선형 보간으로 0~1 정규화해 합산하기
- [[free-market-data-fetch-fallback]] — Yahoo·FRED·스크래핑 무료 데이터를 직접 호출하고 실패를 fallback과 엣지 캐시로 덮기

### LLM 에이전트 설계
- [[rule-engine-llm-split]] — 추출·작문은 LLM, 날짜 산술과 범위 검사는 결정적 코드로 갈라 놓기
- [[deterministic-rule-path]] — 확정 가능한 사실은 SQL 규칙이 꺼내고, 게이트로 규칙이 덮은 범위를 재기
- [[grounded-answer-verification]] — 모델이 쓴 숫자·접수번호를 근거와 기계 대조해 뒷받침 안 되는 값 지우기
- [[citation-grounding-verification]] — 인용한 규정 조항이 실재하는지 인덱스와 대조해 가짜면 폐기·재판정하기
- [[evidence-linked-llm-output]] — LLM에 판정을 맡기지 않고 원본 구간을 근거로 가리키게 해 사람이 확인·수정하게 하기
- [[fixed-graph-hitl-agent]] — 그래프를 고정하고 사람 앞에서 멈춰 최종 책임을 사람에게 남기기
- [[vision-api-fallback-chain]] — 비전 LLM을 기본→대체모델→휴리스틱 3단 폴백으로 감싸 데모가 안 멈추게 하기
- [[llm-quiz-from-disclosure]] — DART 공시를 배치로 긁어 LLM으로 4지선다 퀴즈 JSON 미리 생성하기
- [[ai-judgement-rule-ceiling]] — 점수 판단을 AI에 넘기고 규칙은 검증 상태별 상한선·사실 대조로만 개입하기
- [[agent-session-capture-hooks]] — 훅으로 코딩 에이전트의 턴을 프롬프트·diff·화면·교훈 한 덩어리로 포집하고 해시 사슬로 묶기
- [[disclosure-correction-chain]] — 정정공시를 원공시와 체인으로 묶어 최신 유효 판과 정정 전후 값을 함께 보존하기

### 금융 도메인
- [[chargeback-deadline-and-reason-codes]] — 차지백 기한·사유코드를 일괄 계산하지 않고 검증된 조합에서만 계산하기
- [[merchant-descriptor-decoding]] — 카드 명세서 축약 표기를 실제 사업자와 공식 창구로 연결하기
- [[pii-masking-before-send]] — 전송 전 브라우저 마스킹과 사진·정규식의 한계
- [[test-sale-cost-model]] — 신메뉴 시험 판매를 사전 현금과 사용 원가로 갈라 계산하고 이중 차감 막기
- [[public-store-population-context]] — 공공 상가정보와 법정동 인구를 법정동코드로만 결합해 가게 주변 맥락 만들기
- [[ma5-intraday-breakout]] — 당일 종가 없이 직전 4일 종가 평균만으로 5일선 돌파를 장중 판정하기
- [[kis-openapi-2025-spec]] — 2025년 이후 한투 OpenAPI 주문 TR·필수 필드·호가단위·토큰 제한 변경점
- [[kis-master-file-universe]] — 한투 종목마스터 고정폭 파싱으로 외부 라이브러리 없이 KOSPI100 유니버스 만들기

### 블록체인 · 신원
- [[sd-jwt-selective-disclosure-jwe]] — SD-JWT는 공개 범위, JWE는 전달값 기밀성. 한 제출 묶음에 역할을 나눠 쓰기
- [[vc-key-binding-approval-jwt]] — KB-JWT로 소유자 제시를, 별도 승인 JWT로 특정 금액·월 동의를 증명하기
- [[onchain-revocation-registry]] — VC 폐기를 인덱스 번호만 온체인에 남기고 조회 실패 시에도 거절하는 fail-closed 검증
- [[testnet-reward-token]] — 테스트넷 ERC-20 + 서버 onlyOwner mint로 리워드 토큰 지급하기
- [[sui-timed-access-subscription]] — Sui 소유 객체와 Clock으로 결제·구독권·만료를 한 트랜잭션에 담아 기간 한정 접근권 만들기
- [[seal-key-policy-and-session-traps]] — Seal 열쇠 ID 접두사로 접근 단위를 정하고, 세션 키 시계 오차·키 캐시 함정 피하기
- [[onchain-buyer-only-receipt]] — 후기 권한을 구독권 객체에 묶어 산 사람만 1회 남기게 하고 증거 파일을 가리키기
- [[sui-sdk-rpc-migration-2026]] — 공개 풀노드 JSON-RPC 폐기 후 gRPC·GraphQL로 갈아타며 걸린 자리
- [[ai-log-anchoring-data-receipt]] — AI 처리 로그 해시를 앵커링하고 사용자에게 영수증 토큰을 줘 기업 로그 변조를 대조로 잡기

### 미디어 · 프론트 · 인프라
- [[on-device-segmentation]] — MediaPipe로 브라우저 안에서 사진 물체를 잘라내고 윤곽 폴리곤까지 뽑기
- [[photo-proxy-destruction]] — 사진을 컷아웃 격자 평면으로 바꿔 3D 물체처럼 찌그러뜨리고 조각내기
- [[gps-ar-object-anchoring]] — GPS 좌표 차이를 미터 x/z로 환산해 AR 월드에 3D 오브젝트 고정하기
- [[speaker-diarization]] — 한국어 전사와 화자 구분, 화자 역할 매핑은 사람이 확정하는 2단계
- [[background-job-pipeline]] — Trigger.dev로 전사·분석·삭제를 분리하고 만료 정리를 스케줄로 강제하기
- [[stdio-mcp-server-hygiene]] — stdio MCP 서버의 stdout 오염·Windows 실행·신뢰 대화상자 함정과 외부 텍스트 격리
- [[repo-landing-chain-consistency]] — 저장소·랜딩·체인의 수치를 실제 상태에서 다시 읽어 대조하고 어긋나면 실패시키기
- [[telegram-longpolling-ops]] — 롱폴링으로 공개 엔드포인트 없이 텔레그램 봇 운영하고 웹훅 409 피하기
- [[vercel-python-cron-webpush]] — Vercel 파이썬 서버리스 + 크론 + Redis 직전상태 비교로 변화 시에만 웹푸시 보내기
- [[dual-backend-local-vs-serverless]] — FastAPI 로컬판과 서버리스 배포판에 로직을 복제했을 때 생기는 표류

## lessons
- [[claim-scoping-in-hackathon-docs]] — 기획서 개정은 주장을 키우지 말고 근거가 받쳐 주는 범위까지 좁혀라
- [[measured-baseline-over-claimed-gain]] — 효과는 대조군을 직접 돌려 말하고, 어느 실험의 수치인지 붙여 말하라
- [[self-authored-eval-overfitting]] — 내가 만든 평가는 내가 아는 실패만 잡는다. 질의 선택·정답·채점기 중 하나는 손에서 떼기
