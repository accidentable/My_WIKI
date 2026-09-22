---
title: 백그라운드 작업 파이프라인과 만료 데이터 정리 (Trigger.dev)
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/wanted-interview-ai-2026-readme.md, raw/done/wanted-interview-ai-2026-development.md]
tags: [Trigger.dev, 백그라운드작업, Supabase, Vercel, 데이터보관]
---

## 1. 한 줄 정의

웹 요청 안에서 끝낼 수 없는 긴 작업(전사, LLM 분석, 삭제)을 별도 워커로 빼고, 여기에 만료·정리 스케줄을 함께 붙여 데이터 보관 기간을 코드로 보장하는 구조.

## 2. 어디서 썼는가

- [[wanted-interview-ai-2026]] — FRAME. Trigger.dev로 전사·분석·삭제·만료 정리를 실행하고, 웹 앱은 Vercel에 배포한다.

## 3. 실제로 겪은 문제와 해결

### 왜 필요했나

영상 전사와 LLM 분석은 수 분이 걸릴 수 있어 서버리스 HTTP 요청 수명 안에서 끝나지 않는다. FRAME은 업로드 직후 Supabase 비공개 버킷에 저장만 하고, 이후 전사([[speaker-diarization]]) → 사용자 화자 확인 → 근거 분석([[evidence-linked-llm-output]])을 백그라운드 작업으로 이어 붙였다.

### 웹과 워커를 따로 배포한다

웹 앱(Vercel)과 백그라운드 작업(Trigger.dev)은 별개로 배포되고 환경변수도 각각 등록해야 한다. 자료에 기록된 함정 세 가지:

- Vercel에 등록하는 서버 비밀키에 `NEXT_PUBLIC_` 접두사를 붙이면 안 된다.
- Trigger.dev CLI의 `--env-file`은 **원격 작업의 환경변수를 자동 등록하지 않는다.** Production 환경에 Supabase·AssemblyAI·OpenAI 키와 모델 변수를 직접 등록해야 한다.
- `TRIGGER_SECRET_KEY`는 실행 환경에 맞는 키를 쓴다. 로컬은 Development, Vercel은 같은 프로젝트의 Production 키.

로컬에서는 웹과 별도 터미널에서 `npm run worker:dev`를 띄우고, 배포는 `npm run worker:deploy` + `npm run build`.

### 삭제를 작업으로 만든다

보관 기간을 문서로만 약속하지 않고 스케줄 작업으로 강제했다.

- 영상은 24시간 후 만료. `cleanup-expired-reviews` 스케줄이 **15분 주기**로 정리한다.
- 삭제 요청 시 저장된 영상과 외부(AssemblyAI) 전사를 함께 지우고, **실패한 삭제는 정리 작업에서 재시도**한다.
- 업로드 URL의 유효기간 동안 삭제 표식을 유지해, 삭제 이후 뒤늦게 올라오는 업로드도 정리한다.
- 배포 후 이 스케줄이 활성화되어 있는지 확인하라고 문서에 별도로 적어 두었다.

### 사용량 제한도 여기에 건다

한도는 Supabase 마이그레이션(`001_initial.sql`)이 만드는 사용량 제한 함수로 관리한다. 동시 보관 전체 15건, 최근 24시간 전체 업로드 예약 20건(`DAILY_UPLOAD_LIMIT`), 세션별 3건(`DAILY_SESSION_UPLOAD_LIMIT`). **업로드 예약은 실패해도 사용량에 포함**되며, 앱의 사용량 제한은 API 제공자의 결제 한도를 대체하지 않는다고 명시했다.

소유자 구분은 계정 없이 서명된 HttpOnly 쿠키로 한다. 쿠키를 지우거나 다른 브라우저를 쓰면 기존 영상에 접근할 수 없다.

## 4. 참고 자료

- FRAME 개발 안내 "배포"·"데이터 처리" 절 (raw/done/wanted-interview-ai-2026-development.md)
- FRAME README "기술 구성" 절 (raw/done/wanted-interview-ai-2026-readme.md)
