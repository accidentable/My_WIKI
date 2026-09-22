---
title: 비전 API 폴백 체인 — 모델 대체와 비(非)LLM 최후 수단
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/wanted-hackathon-2026-readme.md]
tags: [openai, vision, fallback, 비용, 데모안정성]
---

## 1. 한 줄 정의

LLM 비전 호출을 기본값 모델 → 대체 모델 목록 → 휴리스틱의 3단 폴백으로 감싸서, 권한 문제(404/403)나 키 부재로도 데모가 멈추지 않게 하는 구성.

## 2. 어디서 썼는가

- [[wanted-hackathon-2026]] — 사진 속 물체의 소재(나무/금속/유리) 판단. 서버는 `serve.js`의 `POST /api/analyze`, 클라이언트 쪽 판단 로직과 휴리스틱은 `src/photo/material.js`.

## 3. 실제로 겪은 문제와 해결

**모델 권한을 미리 알 수 없다.** 기본값을 그 시점 최신 플래그십으로 두되, 계정에 권한이 없으면(404/403) 환경변수의 대체 목록을 순서대로 시도한다.

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-astra
OPENAI_MODEL_FALLBACKS=gpt-5.6-sol,gpt-5.6-terra
```

어떤 모델이 실제로 답했는지는 서버 로그에 남긴다. `.env`와 터미널 환경변수를 모두 지원하고, 둘 다 있으면 터미널 값이 우선이다.

> 주의: 원자료 안에서 모델명이 갈린다. 설정 절은 `gpt-6-astra`, 파이프라인 다이어그램은 `gpt-5-mini`. 자세한 내용은 [[wanted-hackathon-2026]] 상단의 모순 블록.

**LLM이 아예 없는 경우까지 대비.** 키가 없거나 호출이 실패하면 색상 통계 기반 간이 판단(`heuristicMaterial` 점수식)으로 자동 폴백한다. 사용자에게는 힌트 문구로 "간이 판단" / "OpenAI" 중 어느 경로였는지 보여준다. 폴백을 숨기지 않고 표시한 점이 데모 신뢰에 중요했다.

**출력 안정화와 비용.** 이미지는 `detail: low`로 보내고 응답은 JSON 스키마로 고정한다. `gpt-6-astra` 기준 입력 $10 / 출력 $50 per 1M 토큰, 사진 한 장당 약 10원 안팎. 더 아끼려면 경량 모델(`gpt-5.6-luna`)로 바꾼다.

**출력 범주를 좁히기.** 모델이 내놓는 임의의 소재명을 세 가지로 접는 규칙(도자기→유리, 플라스틱→금속 등)을 `serve.js`의 `INSTRUCTIONS`에 둔다. 렌더러가 다룰 수 있는 범주가 3개뿐이므로 매핑을 프롬프트 쪽에서 강제한 것이다.

**검증 공백.** 작업 PC에 키가 없어 **실제 응답 경로는 미검증**이고 키 없을 때의 503 폴백만 확인됐다. 단건 확인용 CLI로 `node tools/analyze.js samples/mug.jpg`가 준비돼 있다. 폴백이 너무 잘 동작하면 주 경로가 죽은 것을 모른 채 지나갈 수 있다는 점이 위험이다.

## 4. 참고 자료

- `raw/done/wanted-hackathon-2026-readme.md`
