---
title: 한국어 전사와 화자 구분 (speaker diarization)
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/wanted-interview-ai-2026-readme.md, raw/done/wanted-interview-ai-2026-development.md]
tags: [음성인식, 전사, 화자구분, AssemblyAI, 한국어]
---

## 1. 한 줄 정의

음성을 텍스트로 옮기면서(전사) 동시에 "누가 말했는가"로 발언을 나누는 것. 대화형 영상에서는 전사만으로는 부족하고, 발언 주체가 붙어야 근거로 쓸 수 있다.

## 2. 어디서 썼는가

- [[wanted-interview-ai-2026]] — FRAME. AssemblyAI(`universal-2` 기본값)로 한국어 전사와 화자 구분을 수행한다.

## 3. 실제로 겪은 문제와 해결

녹화 면접 영상에는 면접관과 지원자의 말이 섞여 있다. 전사문만 있으면 "협업 경험을 말해달라"는 질문과 그에 대한 답변이 구분되지 않아, 기준별 근거를 뽑을 때 면접관의 말이 지원자의 근거로 잡힐 수 있다.

FRAME의 처리 방식은 **자동 화자 구분 + 사람의 역할 지정**의 2단계다. AssemblyAI가 화자를 분리해 주면, 사용자가 전사된 발언을 보고 어느 화자가 지원자이고 어느 쪽이 면접관인지 직접 지정한다. 화자 지정이 끝나야 근거 분석 단계로 넘어간다. 즉 모델은 "화자 A/B"까지만 책임지고, "A가 지원자"라는 역할 매핑은 사람이 확정한다. 이렇게 확정된 역할이 [[evidence-linked-llm-output]]의 전제가 된다.

운영상 기록된 것:

- 전사는 [[background-job-pipeline]]의 백그라운드 작업으로 돌린다. 영상 업로드 후 전사 완료 → 화자 지정 → 분석이라는 순서가 강제된다.
- 전사 모델은 `ASSEMBLYAI_MODEL` 환경변수로 바꿀 수 있지만, 바꿀 때 **한국어 전사와 화자 구분을 지원하는지** 확인해야 한다고 문서에 못박아 두었다.
- 전사를 위해 영상 자체가 AssemblyAI로 전달된다. 삭제 요청 시 저장된 영상뿐 아니라 **외부 전사도 함께 삭제**하고, 실패하면 정리 작업에서 재시도한다.
- 입력은 한국어 MP4 최대 50MB·15분으로 제한했다.

## 4. 참고 자료

- FRAME README "핵심 기능"·"기술 구성" 절 (raw/done/wanted-interview-ai-2026-readme.md)
- FRAME 개발 안내 "실제 분석 연결"·"데이터 처리" 절 (raw/done/wanted-interview-ai-2026-development.md)
