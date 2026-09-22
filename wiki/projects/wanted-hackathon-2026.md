---
title: 원티드 해커톤 2026 — Smash Lab (사진 속 물건 부수기 데모)
type: project
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/wanted-hackathon-2026-readme.md]
tags: [원티드, 해커톤, 3d, web, mediapipe, openai, three-js]
---

> ⚠️ 모순: 소재 판단에 쓰는 OpenAI 모델 이름이 원자료 안에서 갈린다.
> - "소재 판단 (OpenAI 비전 API)" 절: 기본 모델 `gpt-6-astra`, 폴백 `gpt-5.6-sol`, `gpt-5.6-terra`, 경량 대안 `gpt-5.6-luna`.
> - "사진 파이프라인" 절 다이어그램: `/api/analyze (OpenAI 비전, gpt-5-mini)`.
> 출처는 둘 다 `raw/done/wanted-hackathon-2026-readme.md`. 어느 쪽이 실제 코드값인지는 자료에 없음. 다이어그램 쪽이 갱신되지 않은 옛 값일 가능성 (추정).

## 1. 개요

- 대회명: 원티드 해커톤 (프로젝트 분류상. 원자료 본문에는 대회명 표기가 없음)
- 기간: 자료에 없음. 본문에 "2026-09 기준 최신 플래그십" 표현이 있어 2026년 9월 전후 작업 (추정)
- 주제: 사진을 찍으면 AI가 사물 영역과 소재를 판단하고, 그 자리에서 가상 방망이로 부수는 **모바일 대응 웹 3D 데모**. 네이티브 앱이 아니라 브라우저에서 실행.
- 결과(수상 여부): 자료에 없음
- 산출물 이름: Smash Lab

같은 원티드 회차에 [[wanted-interview-ai-2026]]도 있다. 다만 두 프로젝트가 같은 회차인지 다른 회차인지는 이 원자료에 근거가 없어 판단할 수 없다.

## 2. 문제 정의

원자료는 문제 정의를 별도 절로 쓰지 않았다. 읽어낼 수 있는 범위는 다음과 같다.

- 사진 한 장에서 "부술 대상"을 사용자가 지정하거나 수정하지 않고, **확인·수정 UI 없이** 바로 타격까지 가는 흐름을 만드는 것이 목표다.
- 소재(나무/금속/유리)에 따라 반응과 소리가 달라야 하므로, 사진 속 물체의 소재를 자동으로 판정해야 한다.
- 모바일 브라우저에서 돌아가야 하므로 모델 크기, 자동재생 정책, 저사양 기기 프레임이 제약이 된다.

## 3. 접근

### 기술 스택

- 3D: three.js (+ RoomEnvironment), importmap으로 `three`, `@mediapipe/tasks-vision` 로드
- 세그멘테이션: MediaPipe InteractiveSegmenter 온디바이스, 모델 `vendor/models/magic_touch.tflite` (약 16MB, 첫 로딩 수 초)
- 소재 판단: 서버 `POST /api/analyze` → OpenAI 비전 (모델명은 상단 모순 블록 참고), 실패 시 색상 통계 휴리스틱 폴백
- 서버: `serve.js` (정적 서버 + analyze 엔드포인트, 키 없으면 503)
- 오디오: Web Audio 합성 효과음
- 실행: `npm install` → `npm start`, PC `http://localhost:5173/`, 폰은 같은 Wi-Fi의 `phone : http://192.168.x.x:5173/`

### 사진 파이프라인

```
사진(≤1024px) → MediaPipe InteractiveSegmenter(중앙 점 시드) → 마스크
  → 시드 연결 성분만 남김 → 외곽선 추적 → RDP 단순화 → 윤곽 폴리곤 + bbox
  → 소재 판단: /api/analyze → 실패 시 색상 휴리스틱 → wood | metal | glass
  → 배경 구멍 채우기(양파껍질 채움 + 블러) 미리 계산
  → 프록시 메시: 사진 조각을 입힌 컷아웃 격자 평면 (배경 사진 평면 앞, 깊이 보정)
```

자세한 내용은 [[on-device-segmentation]], [[photo-proxy-destruction]] 참고.

### 소재별 반응

| 소재 | 위치 반응 | 파괴 |
|---|---|---|
| 나무 | 눌린 자국·쪼개짐 무늬, 안으로 밀렸다 튕김, 사진에서 뽑은 색의 가시·먼지 | 3타에 보로노이 5~8조각(두께 있음, 사진 텍스처 유지), 배경은 채워진 빈자리 노출 |
| 금속 | 격자 정점을 밀어 넣는 영구 찌그러짐 + 긁힌 자국, 불꽃, 페인트 조각, 섬광 | 부서지지 않음 |
| 유리 | 방사형 금(가산 오버레이), 반짝이는 조각 | 손상 누적/재타격 시 40~70개 얇은 조각으로 산산조각, 타격점에서 퍼지는 파동 |

### 모드

- 사진 모드: 촬영 / 앨범 / 샘플 사진 → 자동 분석 → 바로 타격
- 테스트 벤치: 나무 상자 / 금속 드럼통 / 유리 병 샘플 3D 물체로 소재별 반응·소리 확인
- `?material=glass` URL 파라미터로 개발용 소재 강제

### 비용

`gpt-6-astra` 기준 입력 $10 / 출력 $50 per 1M 토큰, 이미지는 `detail: low`로 보내 사진 한 장당 약 10원 안팎. 아끼려면 `OPENAI_MODEL=gpt-5.6-luna`.

## 4. 잘된 점 / 안된 점

### 잘된 점 (원자료에 성과로 서술된 것)

- 확인·수정 UI 없이 사진 → 분석 → 타격이 이어지는 흐름을 완성. 첫 로딩 이후 사진당 1초 내외.
- 소재별 반응 규칙을 테스트 벤치와 사진 프록시에 **같은 규칙으로** 적용.
- 키가 없거나 호출이 실패해도 색상 휴리스틱으로 자동 폴백되어 데모가 멈추지 않음 (힌트에 "간이 판단"/"OpenAI" 표시).
- 물체 인터페이스를 공통 규약으로 통일: `{ group, hittables(), hit(intersection, strength), update(dt), dispose(), stats(), statusText() }`.
- `npm run build:single`로 three.js만 CDN에서 받는 단일 HTML(`dist/index.html`) 배포 가능.

### 안된 점 / 알려진 제한

- **OpenAI 실제 응답 경로 미검증.** 작업 PC에 키가 없어 키 없을 때의 503 폴백만 확인했다.
- 단일 파일 빌드는 MediaPipe WASM·모델·샘플 사진을 담지 못해 **사진 탭 없이** 테스트 벤치로만 열린다. `dist/artifact.html`도 같은 제약.
- 세그먼트는 사진 중앙 물체를 자동 선택. 중앙에 없으면 직접 탭해야 한다.
- 배경 채우기는 진짜 인페인팅이 아니라 주변색 번짐이라 복잡한 배경에서 뭉개진다.
- 파편끼리 충돌하지 않고 바닥만 인식. 유리 파편 70개는 저사양 폰에서 프레임 저하.
- iOS Safari 진동 미지원. 모바일 자동재생 정책 때문에 첫 터치 이후에야 소리가 켜진다.
- 사내/카페 Wi-Fi는 기기 간 통신을 막을 수 있어 폰 테스트는 핫스팟이 확실하다.
- `samples/`의 `glass-bottle.jpg`, `metal-mokapot.jpg`, `ceramic-mug.jpg`, `wood-chair.jpg`는 출처 확인이 필요하다 (나머지는 Wikimedia Commons, `samples/CREDITS.md`).

## 5. 재사용 가능한 것

| 경로 | 내용 |
|---|---|
| `src/photo/segment.js` | MediaPipe 세그멘터 래퍼 |
| `src/photo/contour.js` | 마스크 정리·외곽선 추적·RDP 단순화 (`simplify(..., 1.2)`, `maskToPolygon` 최소 면적) |
| `src/photo/fracture.js` | 보로노이 셀 + 폴리곤 클리핑 |
| `src/photo/inpaint.js` | 배경 구멍 채우기(양파껍질 + 블러) |
| `src/photo/material.js` | 소재 판단 (API → 휴리스틱), `heuristicMaterial` 점수식 |
| `src/objects/photo.js` | 사진 프록시 물체 (컷아웃 평면, 찌그러짐, 보로노이 파편, 배경 교체) |
| `serve.js` | 정적 서버 + `POST /api/analyze`, 소재 접기 규칙은 `INSTRUCTIONS` 상수 (도자기→유리, 플라스틱→금속 등) |
| `tools/analyze.js` | `node tools/analyze.js samples/mug.jpg` 단건 테스트 CLI |
| `src/textures.js` | 절차적 텍스처 + 손상 페인터 |
| `src/audio.js` | Web Audio 합성 효과음 |
| `src/debris.js` | 파편 물리 |
| `build-single.js` | 단일 HTML 번들러 |
| `__demo.loadSample/strikeAt/step/stats` | 자동 검증 훅 (예: `__demo.strikeAt(0,-0.1); __demo.step(1/60,12); __demo.stats();`) |

손맛 튜닝 포인트: `src/bat.js`의 `SWING_TIME`(탭→타격 약 0.12초), `src/objects/photo.js`의 나무 `hp`(3)·금속 찌그러짐 반경/깊이·유리 `SHATTER_AT`·파편 `count`·파동 속도(`dist * 0.25`).

## 6. 다음 단계 (원자료 기준)

1. 실기기 손맛 튜닝 (진동 세기, 스윙 시간, 파편 수 vs. 프레임)
2. API 키 연결 후 비전 판단 경로 검증, 물체 이름 라벨 노출
3. 촬영 → 부수기 → 결과 영상 저장/공유 흐름, PWA 설치
4. 히트스톱, 스와이프 세기, 녹음 샘플 ASMR 레이어

## 7. 관련 문서

- [[on-device-segmentation]]
- [[vision-api-fallback-chain]]
- [[photo-proxy-destruction]]
- [[wanted-interview-ai-2026]] — 같은 원티드 프로젝트 (같은 회차 여부는 자료에 없음)
