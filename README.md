<div align="center">

# My_WIKI

해커톤 출전 자료를 LLM이 규칙대로 위키로 정리하고, 면접 노트 사이트로 만드는 저장소

[사이트](https://hackathon-wiki-rho.vercel.app/) · [규칙](wiki-rules.md) · [인덱스](wiki/index.md) · [로그](log.md)

</div>

## About

해커톤에서 AI가 대신 짜고 넘어간 것을 나중에 제 말로 설명할 수 있게 만드는 교재입니다. 틀은 Karpathy의 [LLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595)에서 가져왔고, 목적은 구현을 LLM에 지나치게 기대던 습관을 떨쳐내는 데 두었습니다. 사람은 원자료를 넣고 질문만 하고, 문서를 쓰는 일은 Claude Code와 Codex가 맡습니다.

현재 프로젝트 문서 14개, 개념 문서 49개, 교훈 문서 4개, 처리한 원자료 35건 (2026-09-22).

### Built With

Markdown 위키 · Python 점검·빌드 스크립트 · GitHub Actions · Vercel · OpenAI API (판단 검사) · Claude Code / Codex 에이전트 규칙

## Structure

```
raw/            사람이 넣는 원자료. LLM은 읽기만 함
raw/done/       처리 끝난 원자료
wiki/index.md   전체 목차. 모든 작업은 여기서 시작
wiki/projects/  프로젝트당 문서 하나 (면접 준비 절 포함)
wiki/concepts/  기술·도메인 개념 (학습 절 포함)
wiki/lessons/   여러 프로젝트에 걸친 교훈
log.md          작업 기록. 추가만 함
wiki-rules.md   운영 규칙 14절
tools/lint.py   점검: 결정적 검사 + LLM 판단 검사
tools/build_site.py  위키 → 한 장짜리 사이트
```

## Rules That Matter

- 원자료에 없는 사실은 쓰지 않고, 추론은 "(추정)"으로 표시
- 원자료의 확신 수준을 보존. "검토했다"를 "기각했다"로 바꾸지 않음
- 모순은 지우지 않고 두 서술과 출처를 남긴 채 표시
- 기술 선택 이유가 원자료에 없으면 "이유 자료에 없음"으로 비워 둠
- 모든 문서는 `sources:`로 근거 원자료를 가리키고, 점검이 경로를 확인

## Workflow

1. 넣기: `raw/`에 파일을 두고 "반영해". 에이전트가 인덱스를 읽고 관련 문서 1~4개만 갱신
2. 묻기: 인덱스에서 관련 문서만 열어 답하고, 위키에 없으면 "위키에 없음"
3. 점검: push마다 결정적 검사, 주 1회 LLM 판단 검사. 지적만 하고 자동 수정 없음

## Example: 타코 트럼프

코드 개요 한 장을 넣자 프로젝트 문서 1개와 개념 문서 4개가 생겼고, 그 과정에서 두 백엔드의 점수 로직이 어긋난 것, 주석과 상수가 다른 것, 크론 설명과 설정이 다른 것이 드러났습니다. 프로젝트 문서에는 예상 질문과 "솔직하게 말할 것" 일곱 항목이, 개념 문서에는 "다음에 어떻게 할 것인가"가 남았습니다. [문서 보기](wiki/projects/taco-index-2026-03.md)

## Getting Started

```bash
python tools/lint.py          # 결정적 검사
python tools/lint.py --llm    # + 판단 검사 (OPENAI_API_KEY, LINT_MODEL)
python tools/build_site.py    # site/index.html
```

## Roadmap

- [ ] 새 프로젝트 시작 시 위키의 "다음에 어떻게 할 것인가"를 자동으로 꺼내 보기
- [ ] 프로젝트가 끝날 때 회고를 `raw/`에 넣는 흐름을 도구로 강제
- [ ] 점검이 지적한 보류 항목 처리

## Limitations

- 문서 대부분이 하루에 만들어져 사람이 한 건씩 검토한 밀도가 낮음
- 원자료가 부풀려 썼다면 위키도 그대로 옮김
- 판단 검사는 실행마다 결과가 달라질 수 있어 CI 실패 조건으로 쓰지 않음
- 다음 프로젝트에 실제로 참고한 기록은 아직 없음
