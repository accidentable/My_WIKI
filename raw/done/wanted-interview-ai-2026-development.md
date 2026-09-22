# 개발 안내

프로젝트 소개와 사용 흐름은 [README](../README.md)를 참고하세요.

## 샘플 실행

Node.js 24와 npm이 필요합니다.

```bash
npm ci
npm run dev
```

http://127.0.0.1:3000 에서 샘플을 실행합니다. 샘플 모드는 외부 API를 호출하지 않습니다.

## 실제 분석 연결

1. 루트의 `.env.example`을 `.env.local`로 복사합니다. 기존 설정 파일이 있다면 필요한 값만 수정합니다.
2. Supabase SQL Editor에서 [`001_initial.sql`](../supabase/migrations/001_initial.sql)을 실행합니다. 검토 데이터 테이블, 사용량 제한 함수와 비공개 영상 버킷을 생성합니다.
3. 아래 환경변수를 설정합니다.

| 변수 | 설명 |
| --- | --- |
| `SUPABASE_URL` | 프로젝트 기본 URL. `/rest/v1` 경로는 포함하지 않음 |
| `SUPABASE_SERVICE_ROLE_KEY` | 서버 전용 Supabase secret 또는 service-role 키 |
| `ASSEMBLYAI_API_KEY` | 전사 API 키 |
| `OPENAI_API_KEY` | 근거 분석 API 키 |
| `TRIGGER_PROJECT_REF` | Trigger.dev 프로젝트 ID |
| `TRIGGER_SECRET_KEY` | 실행 환경에 맞는 Trigger.dev 키. 로컬 개발은 Development |
| `SESSION_SECRET` | 세션 서명용 임의 문자열, 32자 이상 |
| `OPENAI_MODEL` | 기본값 `gpt-4.1-mini` |
| `ASSEMBLYAI_MODEL` | 기본값 `universal-2` |
| `DAILY_UPLOAD_LIMIT` | 최근 24시간 전체 업로드 예약 한도. 기본 20건 |
| `DAILY_SESSION_UPLOAD_LIMIT` | 최근 24시간 세션별 업로드 예약 한도. 기본 3건 |

세션 비밀값 생성:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

4. 별도 터미널에서 백그라운드 작업을 실행합니다.

```bash
npm run worker:dev
```

5. 웹 앱을 재시작하고 영상을 업로드합니다. 전사 완료 후 지원자 화자를 지정하면 근거 분석을 진행할 수 있습니다.

실제 키는 `.env.local`에만 보관하며 Git에 포함하지 않습니다. 모델 변경 시 한국어 전사·화자 구분 및 구조화된 응답 지원을 확인하세요.

## 배포

웹 앱과 백그라운드 작업을 각각 배포합니다.

- **Vercel:** 웹 앱에 필요한 환경변수를 등록합니다. 서버 비밀키에 `NEXT_PUBLIC_` 접두사를 붙이지 않습니다. `TRIGGER_SECRET_KEY`에는 같은 프로젝트의 Production 키를 사용합니다.
- **Trigger.dev:** Production 환경에 Supabase·AssemblyAI·OpenAI 키와 모델 환경변수를 등록합니다. CLI의 `--env-file`은 원격 작업의 환경변수를 자동 등록하지 않습니다.

```bash
npm run worker:deploy
npm run build
```

Trigger.dev의 `cleanup-expired-reviews` 스케줄이 활성화되어 있는지 확인합니다. 만료 데이터 정리는 15분 주기로 실행됩니다.

## 데이터 처리

영상은 Supabase 비공개 버킷에 저장하고 서명 URL로 접근합니다. 서명된 HttpOnly 쿠키로 브라우저 세션별 소유자를 구분하므로, 쿠키를 삭제하거나 다른 브라우저를 사용하면 기존 영상에 접근할 수 없습니다.

전사를 위해 영상이 AssemblyAI에, 근거 분석을 위해 전사 내용이 OpenAI에 전달됩니다. OpenAI 요청은 `store: false`를 사용합니다. 앱의 보관 기간과 외부 제공자의 데이터 처리 정책은 구분됩니다.

영상은 24시간 후 만료됩니다. 삭제 요청 시 영상 파일과 외부 전사를 삭제하고, 실패한 삭제는 정리 작업에서 재시도합니다. 업로드 URL의 유효기간 동안 삭제 표식을 유지해 지연 업로드도 정리합니다.

동시 보관은 전체 15건으로 제한됩니다. 업로드 예약은 실패하더라도 사용량에 포함되며, 앱의 사용량 제한은 API 제공자의 결제 한도를 대체하지 않습니다.

## 검증

```bash
npm run typecheck
npm test
npm run build
npm run test:e2e
```

브라우저 테스트는 설치된 Microsoft Edge를 사용합니다. 샘플 재생·탐색, 근거 편집, 화자 변경, 업로드 제한과 모바일 레이아웃을 검사합니다. 실제 서비스 연결은 별도로 업로드 → 전사 → 화자 확인 → 분석 → 삭제 흐름을 확인합니다.

## 샘플 영상

`public/demo`에는 직접 제작한 가상 인터뷰 영상과 포스터가 포함되어 있습니다. 별도 영상 제작 도구 없이 샘플을 실행할 수 있습니다.
