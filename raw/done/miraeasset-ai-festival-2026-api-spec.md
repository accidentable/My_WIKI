# 평가용 API 명세

공시 Agent는 `GET /answer`와 `POST /answer`를 제공하며 두 방식의 응답 스키마는 동일합니다.
모든 정상 답변은 근거 공시를 `[접수번호: 14자리]` 형식으로 표시합니다.

## Endpoint

| 용도 | URL |
|---|---|
| 평가 API | `http://49.50.137.93:8000/answer` |
| 상태 확인 | `GET http://49.50.137.93:8000/health` |
| 로컬·Docker | `http://localhost:8000/answer` |

## GET /answer

| 쿼리 파라미터 | 형식 | 필수 | 설명 |
|---|---|---:|---|
| `question_id` | string | 예 | 호출자가 부여한 문항 식별자 |
| `question` | string | 예 | 공시 코퍼스에 관한 자연어 질문 |

```bash
curl --get 'http://49.50.137.93:8000/answer' \
  --data-urlencode 'question_id=Q-001' \
  --data-urlencode 'question=삼성전자의 2023년 연결기준 매출액은?'
```

```python
import requests
resp = requests.get("http://49.50.137.93:8000/answer",
                    params={"question_id": "Q-001", "question": "삼성전자의 2023년 연결기준 매출액은?"})
result = resp.json()
```

## POST /answer

Header: `Content-Type: application/json`

```json
{"question_id": "Q-001", "question": "삼성전자의 2023년 연결기준 매출액은?"}
```

```bash
curl -X POST 'http://49.50.137.93:8000/answer' \
  -H 'Content-Type: application/json' \
  -d '{"question_id":"Q-001","question":"삼성전자의 2023년 연결기준 매출액은?"}'
```

## 응답 (HTTP 200)

```json
{
  "question_id": "Q-001",
  "question": "삼성전자의 2023년 연결기준 매출액은?",
  "retrieved_context": "[{\"tool\": \"get_financial_metric\", \"result\": {\"rows\": [...]}}]",
  "think_trace": "도구 사용: get_financial_metric (기간 매출 결정론적 경로)",
  "answer": "삼성전자의 2023년 연간 연결 매출액은 258,935,494,000,000원입니다. [접수번호: 20240312000736]"
}
```

| 필드 | 형식 | 설명 |
|---|---|---|
| `question_id` | string | 요청에서 받은 문항 식별자 |
| `question` | string | 요청 원문 |
| `retrieved_context` | string(JSON) | 도구가 돌려준 근거 목록(`[{"tool": 이름, "result": {...}}, ...]`)을 JSON 문자열로 직렬화 |
| `think_trace` | string | 사용한 도구와 경로의 공개 기록(결정론 경로, 질문 분해, 확정 사실표, 사전 검색). 모델의 비공개 추론이 아님 |
| `answer` | string | 근거 접수번호가 포함된 최종 답변 |

JSON Schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["question_id", "question", "retrieved_context", "think_trace", "answer"],
  "properties": {
    "question_id": {"type": "string", "minLength": 1},
    "question": {"type": "string", "minLength": 1},
    "retrieved_context": {"type": "string"},
    "think_trace": {"type": "string"},
    "answer": {"type": "string", "minLength": 1}
  },
  "additionalProperties": false
}
```

## 오류와 한계 응답

`/answer`는 **항상 HTTP 200과 위 5필드**로 응답합니다. 평가 하네스가 JSON 파싱에 실패해 문항이
무응답으로 처리되지 않도록 내부 예외·모델 호출 실패·시간 초과를 모두 한계 응답으로 되돌립니다.
부재의 종류에 따라 문장이 다릅니다.

| 상황 | `answer` | `think_trace` |
|---|---|---|
| 필수 파라미터 누락·빈 문자열 | 필요한 파라미터 안내 | `입력 오류` |
| 공시에 해당 사실이 없음 | "…기재되어 있지 않습니다" 또는 "확인되지 않습니다" + 확인한 공시의 접수번호 | 사용 도구 |
| 항목이 공시유보 | 유보 사유·유보기한과 함께 "기재되어 있지 않습니다" | 사용 도구 |
| 근거 없이 수치를 말할 상황 | "제공된 공시에서 확인되지 않습니다. 기업명·연도·공시 유형을 구체적으로 지정해 주시면 다시 확인하겠습니다." | 사용 도구 |
| 시간 예산(80초) 초과 | "시간 예산 안에 근거를 다 확인하지 못해 답하지 못했습니다. 공시에 없다는 뜻은 아니니 질문을 나누어 다시 물어봐 주세요." (확정 사실표가 있으면 그 사실표 + 안내) | `… \| 중단: 시간 예산 초과` |
| 모델 호출 실패·빈 응답 | "일시적인 모델 응답 오류로 답하지 못했습니다. …다시 보내 주세요." | `… \| 중단: 모델 호출 실패(…)` |
| 정책 차단(개인정보·투자 권유·전망·프롬프트 공격) | 거절 사유 안내 | `정책 차단` |
| 코퍼스 범위 밖(70개사, 2023.01~2026.03 외) | 범위를 명시한 정보한계 안내 | `범위 판정` |

근거가 없는 한계 응답에는 접수번호를 붙이지 않습니다. 한 문항의 전체 처리 시간은 `ANSWER_BUDGET_SECONDS`(기본 80초)로 제한되며,
예산을 넘기면 그때까지 확보한 근거로 답변을 만들어 반환합니다. 평가는 문항을 순차로 보내는 것을 전제로 합니다.

## 재현 절차

```bash
cp .env.example .env          # CLOVASTUDIO_API_KEY 입력
# db/disclosure.db (필수), db/title_vectors.db (선택) 를 db/ 에 배치
docker compose up --build -d
curl http://localhost:8000/health
docker compose down
```

`.env`, SSH 키, 관리자 비밀번호, 원본 공시 데이터와 런타임 DB는 Git에 커밋하지 않습니다.
