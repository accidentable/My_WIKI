---
title: 공시 문서로 LLM 퀴즈 자동 생성하기 (DART + GPT-4o)
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/hana-ar-kowalk-2026-plan.md]
tags: [LLM, DART, 공시, 퀴즈, OpenAI]
---

## 1. 한 줄 정의

DART 전자공시에서 기업별 최신 공시를 배치로 긁어 LLM에 넣고, 정해진 JSON 스키마의 4지선다 퀴즈를 미리 생성해 DB에 쌓아 두는 방식.

## 2. 어디서 썼는가

- [[hana-ar-kowalk-2026]] — 기업 본사 방문 시 출제할 퀴즈 3문제를 자동 생성 (계획 단계)

## 3. 실제로 겪은 문제와 해결

파이프라인은 다음과 같다.

1. 크론잡으로 DART에서 코스피 100 기업 공시를 일 1회 수집 (사업보고서, 반기보고서, 주요사항보고서)
2. 공시 텍스트를 GPT-4o에 전달
3. 프롬프트: "다음 기업 공시를 바탕으로 4지선다 퀴즈 3문제를 JSON으로 생성해줘"
4. 응답 JSON을 DB(`quizzes.questions` jsonb)에 저장. `source` 컬럼에 DART 공시 번호를 남긴다.
5. 유저가 해당 기업에 도달하면 앱이 저장된 퀴즈를 로드

즉 **생성은 배치, 소비는 조회**로 분리한다. 유저 요청 시점에 LLM을 호출하지 않으므로 응답 지연과 비용 변동이 없다.

JSON 스키마는 문항마다 `question`, `options`(4개), `answer`(정답 인덱스), `explanation`을 강제한다. 해설을 필수 필드로 둔 덕에 오답 시에도 바로 학습 화면을 보여줄 수 있다.

```json
{
  "company_id": "005930",
  "company_name": "삼성전자",
  "generated_at": "2026-04-01",
  "questions": [
    {
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "answer": 2,
      "explanation": "..."
    }
  ]
}
```

품질에 대한 판단: 원자료는 프로토타입 단계에서 "실제 DART 공시를 쓰되 퀴즈 품질은 데모 수준"이라고 명시적으로 범위를 낮춰 잡았다. 품질 검증 절차는 자료에 없음.

비용: DART API 키는 무료 발급, OpenAI API는 유료지만 퀴즈 생성 정도는 비용이 미미하다고 판단.

## 4. 참고 자료

- DART 전자공시 OpenAPI — https://opendart.fss.or.kr
- OpenAI GPT-4o
- 원자료: `raw/done/hana-ar-kowalk-2026-plan.md`
- 관련: [[miraeasset-ai-festival-2026]] — 같은 DART 전자공시를 LLM에 물린 다른 프로젝트. 이쪽은 퀴즈 생성, 저쪽은 근거 기반 QA라 검증 요구 수준이 다르다. 대비되는 설계는 [[grounded-answer-verification]], [[disclosure-correction-chain]].
