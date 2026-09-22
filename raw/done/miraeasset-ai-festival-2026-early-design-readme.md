# 공시 Agent — 미래에셋증권 AI Festival

DART 공시 코퍼스(70개사 / 4,204문서 / 2023.01~2026.03)를 근거로
자연어 질의에 답하는 Agent. LLM 은 HyperCLOVA X 만 사용한다.

## 설계 요지

코퍼스는 유한하고 고정돼 있다. 그래서 **질의 시점에 검색하지 않고, 미리 구조화한다.**

| 층 | 대상 | 방식 |
|---|---|---|
| 구조화 (Day 1 ✅) | 거래소·지분·주요사항 3,150건 | 서식이 정해져 있어 결정론적 파싱 → SQL |
| 검색 (Day 2) | 정기공시 1,054건 | 목차 기반 섹션 분할 → 임베딩 → 리랭킹 |
| 오케스트레이션 (Day 2) | — | function calling 으로 위 두 층을 호출 |
| 정책 (Day 3) | — | PII·투자의견·역질문·인젝션 방어 |

계약금액 비교나 "해지된 계약이 있는가" 같은 질의는 유사도 검색이 아니라
**SQL JOIN 으로 정확히** 답한다. 수치 정확도를 임베딩에 맡기지 않는 것이 핵심.

## 구조

```
src/
  parse/          공시 원문 파서
    common.py       XForms HTML + DART XML 양쪽을 (라벨→값) 으로 환원
    periodic.py     연결 손익계산서의 당기 누적 매출 → financial_facts
    sections.py     목차 기반 정기공시 계층형 청크 → document_sections
    exchange.py     거래소공시 4종 → contracts/terminations/investments/material_events
    holding.py      지분공시 → holdings (개인정보는 파싱 단계에서 폐기)
    major.py        주요사항보고서 25종 → major_events
  build_db.py     원문 → db/disclosure.db (정정 체인 연결 포함)
  agent/tools.py  에이전트 툴 11종 + function calling 스키마
  retrieval/      FTS5 정기공시 검색 인덱스·조회
                  CLOVA bge-m3 임베딩 배치·SQLite 벡터 저장·하이브리드 재정렬
  goldenset/generate.py   골든셋 자동 생성 (정답 → 질문 역생성)
  evalkit/
    score.py        채점기 (정확성·근거완전성·할루시네이션)
    runner.py       회귀 스위트
db/disclosure.db  구조화 DB
goldenset/        평가 문항
runs/             실행별 점수판 (회귀 비교용)
```

## 실행

```bash
python src/build_db.py                    # 원문 → DB
python -m unittest discover -s tests -v  # 파서·조회 회귀 테스트
python src/evalkit/financial_coverage.py  # 재무 fact Coverage·무결성 리포트
python src/evalkit/section_coverage.py    # 정기공시 섹션 Coverage·무결성 리포트
python -m src.retrieval.build_fts          # 섹션 키워드 검색 인덱스만 재생성
python -m src.retrieval.embed_sections --dry-run --limit 100
$env:CLOVASTUDIO_API_KEY="<CLOVA-STUDIO-API-KEY>"  # PowerShell, 코드/저장소에 키 저장 금지
python -m src.retrieval.embed_sections --limit 100 --batch-size 1  # 소량 파일럿
python -m src.retrieval.embed_sections --batch-size 1              # 전체/재개
python src/evalkit/embedding_coverage.py       # 임베딩 적재 진행률
python src/goldenset/generate.py          # 골든셋 생성
python src/evalkit/runner.py --agent null --tag baseline-null
python src/evalkit/runner.py --agent http --endpoint http://localhost:8000/answer \
       --tag v1 --compare baseline-null   # 이전 실행 대비 증감 표시
```

## Windows 노트북에서 이어서 작업하기

코드는 GitHub를 기준으로 이동한다. `.env`, 원본 `data/`, `db/*.db`는 보안과
용량 문제로 Git에서 제외되어 있으므로 별도로 준비해야 한다.

### 1. 기존 데스크톱에서 런타임 DB를 Ncloud에 한 번 업로드

서버 ACG의 TCP 22 접근 소스에 현재 데스크톱의 공인 IP `/32`가 등록되어
있어야 한다. PowerShell에서 다음을 실행하고 SSH 비밀번호를 입력한다.

```powershell
.\scripts\upload_runtime_db.ps1 -ServerAddress "<NCLOUD_SERVER_PUBLIC_IP>"
```

기본 업로드 위치는 `/opt/disclosure-ai/db`다. CLOVA 키가 저장된 서버의
`/etc/disclosure-ai.env`는 변경하거나 내려받지 않는다.

### 2. 노트북에서 복제 및 자동 설정

Git, Python 3.10 이상, Windows OpenSSH Client가 필요하다. 노트북의 공인
IP가 데스크톱과 다르면 먼저 Ncloud ACG의 TCP 22 접근 소스에 노트북 IP
`/32`를 추가한다.

```powershell
git clone https://github.com/accidentable/AI_miraeasset.git
cd AI_miraeasset
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_laptop.ps1 -ServerAddress "<NCLOUD_SERVER_PUBLIC_IP>"
```

설치 스크립트는 `.venv` 생성, 의존성 설치, CLOVA 키 숨김 입력, 서버 DB
다운로드, 전체 테스트를 순서대로 수행한다. API 키는 노트북의 `.env`에만
저장되고 Git에 포함되지 않는다.

새 PowerShell 세션에서는 프로젝트 폴더에서 환경변수를 다시 불러온다.

```powershell
. .\scripts\load_env.ps1
```

원본 6GB 코퍼스로 DB를 다시 빌드해야 할 때만 `data/`를 별도로 복사한다.
일반 개발·검색·평가에는 `disclosure.db`와 `embeddings.db`만 있으면 된다.

## 데이터 규칙 (평가 직결 — 반드시 준수)

- LLM 은 **HyperCLOVA X 만**. 다른 모델 사용 시 평가 대상 제외.
- 제공 코퍼스 외 데이터 사용 금지 (뉴스·리포트·위키·OpenDART 실시간 호출).
- 모든 답변에 **근거 공시(접수번호) 표시**.
- 확인 불가 시 "공시에서 확인되지 않음" 명시. 추측 금지.
- 공시에 근거 없는 미래 예측·투자의견 생성 금지.

## 판단 기준 (골든셋 정답의 근거)

- **매출액** = 연결 기준. 금융사는 공시에 직접 표시된 영업수익·총영업수익·
  보험 및 투자서비스 수익만 사용한다. 은행지주의 순이자이익·순수수료이익을
  임의 합산해 매출로 만들지 않는다.
- **설비투자** = 현금흐름표 유형자산 취득 + 신규시설투자 공시 병기.
- **개인정보** = 지분공시의 생년월일·주소·연락처·이메일은 적재하지 않는다.
  성명·보유비율·발행회사와의 관계 등 공적 정보만 보존.
- **정정공시** = 본문 표가 정정후 최신값. 원본은 `superseded_by` 로 무효화 표시.
