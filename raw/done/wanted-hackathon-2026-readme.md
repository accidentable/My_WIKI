# Smash Lab — 사진 속 물건 부수기 데모

사진 → AI가 사물 영역·소재 판단 → 가상 방망이로 **그 자리에서** 부수기. 해커톤용 **모바일 대응 웹 3D 데모**입니다 (네이티브 앱 아님, 브라우저에서 실행).

- 📷 **사진 모드**: 촬영/앨범/샘플 사진 → 온디바이스 AI가 중앙의 물체를 잘라내고 → 소재(나무/금속/유리)를 판단 → 바로 때립니다. 확인·수정 UI 없음.
- 🪵🛢️🍾 **테스트 벤치**: 나무 상자 / 금속 드럼통 / 유리 병 샘플 3D 물체로 소재별 반응·소리를 빠르게 확인.
- 터치한 **그 위치**에 반응(자국·찌그러짐·금), 소재별 소리는 같은 프레임에 재생, ↺ 초기화로 복구.

## 실행 방법

```bash
npm install
npm start
```

- PC: http://localhost:5173/
- 스마트폰: 같은 Wi-Fi에서 `npm start`가 출력하는 `phone : http://192.168.x.x:5173/` 주소를 열기 (Windows 방화벽 허용 필요, 회사/카페 Wi-Fi는 기기 간 통신을 막을 수 있어 핫스팟이 확실함)
- 첫 터치 이후 소리가 켜집니다 (모바일 자동재생 정책). 안드로이드는 진동도 옵니다.
- 사진 모드는 처음에 AI 모델(약 16MB)을 받느라 몇 초 걸립니다. 이후엔 사진당 1초 내외.

### 소재 판단 (OpenAI 비전 API)

`/api/analyze`가 잘라낸 물체 사진을 OpenAI에 보내 물체 이름과 소재를 JSON으로 받습니다. 키가 없거나 호출이 실패하면 색상 통계 기반 간이 판단으로 자동 폴백됩니다 (힌트에 "간이 판단"으로 표시, 키가 있으면 "OpenAI").

프로젝트 루트의 `.env` 파일에 키를 적고 서버를 켭니다 (`.env`는 git에 올라가지 않음, 예시는 `.env.example`).

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-astra
OPENAI_MODEL_FALLBACKS=gpt-5.6-sol,gpt-5.6-terra
```

```bash
npm start
```

터미널 환경변수(`$env:OPENAI_API_KEY=...`)로 넣어도 되고, 둘 다 있으면 터미널 값이 우선입니다.

- 모델 기본값은 2026-09 기준 최신 플래그십 `gpt-6-astra`입니다. 계정에 권한이 없으면(404/403) `OPENAI_MODEL_FALLBACKS`의 모델을 순서대로 시도하고, 어떤 모델이 답했는지 서버 로그에 찍힙니다.
- 이미지는 `detail: low`(저해상도 토큰)로 보내고 응답은 JSON 스키마로 고정합니다. `gpt-6-astra`는 입력 $10/출력 $50 per 1M 토큰이라 사진 한 장당 약 10원 안팎이고, 비용을 아끼려면 `OPENAI_MODEL=gpt-5.6-luna`(경량)로 바꾸면 됩니다.
- 소재 접기 규칙(도자기→유리, 플라스틱→금속 등)은 `serve.js`의 `INSTRUCTIONS`에 있습니다.
- 서버를 켠 상태에서 `node tools/analyze.js samples/mug.jpg`로 한 장씩 시험할 수 있습니다.
- 이 PC에는 키가 없어 **실제 응답 경로는 미검증**이고, 키 없을 때의 503 폴백만 확인했습니다. 키를 넣은 뒤 위 명령으로 한 번 확인하세요.

### 파일 하나로 공유하기 (테스트 벤치만)

```bash
npm run build:single
```

`dist/index.html`은 three.js만 cdnjs에서 받는 단일 파일입니다. MediaPipe WASM·모델·샘플 사진은 못 담으므로 이 빌드는 **사진 탭 없이** 테스트 벤치로 열립니다. `dist/artifact.html`은 Claude 아티팩트용 변형입니다.

## 조작

| 동작 | 결과 |
|---|---|
| 물체 탭 | 방망이 스윙 → 약 0.12초 뒤 타격 (효과·소리·진동 동시) |
| 사진 모드에서 물체 밖 탭 | 그 자리의 다른 물체를 새로 잘라내어 대상 변경 (스윙 안 함) |
| 📷 촬영 / 🖼 앨범 / 🎲 샘플 사진 | 새 사진 불러오기 → 자동 분석 |
| 드래그 (테스트 벤치) | 물체 회전 |
| ↺ 초기화 | 사진 모드: 같은 사진 다시 분석 / 벤치: 물체 새로 놓기 |
| `?material=glass` URL 파라미터 | 개발용 소재 강제 |

## 사진 파이프라인

```
사진(≤1024px) ──► MediaPipe InteractiveSegmenter (온디바이스, 중앙 점 시드) ──► 마스크
   ──► 시드 연결 성분만 남김 → 외곽선 추적 → RDP 단순화 ──► 윤곽 폴리곤 + bbox
   ──► 소재 판단: /api/analyze (OpenAI 비전, gpt-5-mini) → 실패 시 색상 휴리스틱 ──► wood | metal | glass
   ──► 배경 구멍 채우기(양파껍질 채움+블러, 물건 사라진 자리용) 미리 계산
   ──► 프록시 메시: 사진 조각을 입힌 컷아웃 격자 평면 (배경 사진 평면 앞, 깊이 보정으로 정합 유지)
```

소재별 반응은 벤치와 같은 규칙을 사진 프록시에 그대로 적용합니다.

| 소재 | 위치 반응 | 파괴 |
|---|---|---|
| 나무 | 사진 위에 눌린 자국·쪼개짐 무늬, 안으로 밀렸다 튕김, 사진에서 뽑은 색의 가시·먼지 | 3타에 보로노이 5~8조각(두께 있음, 각 조각이 사진 텍스처 유지)으로 부서짐, 배경은 채워진 빈자리 노출 |
| 금속 | 격자 정점을 밀어 넣는 영구 찌그러짐 + 긁힌 자국, 불꽃, 사진색 페인트 조각, 섬광 | 부서지지 않음 |
| 유리 | 방사형 금(가산 오버레이), 반짝이는 조각 | 손상 누적/같은 곳 재타격 시 40~70개 얇은 조각으로 산산조각, 타격점에서 퍼지는 파동 |

## 코드 구조

```
index.html               UI 셸, importmap (three, @mediapipe/tasks-vision)
serve.js                 정적 서버 + POST /api/analyze (OpenAI SDK, 키 없으면 503)
tools/analyze.js         /api/analyze 단건 테스트 CLI
src/main.js              씬·카메라(사진 모드는 정면 cover-fit)·입력·HUD·모드 전환·사진 흐름
src/bat.js               방망이 스윙/타격 콜백
src/audio.js             Web Audio 합성 효과음
src/debris.js            파편 물리
src/textures.js          절차적 텍스처 + 손상 페인터(나무/금속/유리)
src/objects/wood|metal|glass.js   테스트 벤치 물체
src/objects/photo.js     사진 프록시 물체 (컷아웃 평면, 찌그러짐, 보로노이 파편, 배경 교체)
src/photo/segment.js     MediaPipe 세그멘터 래퍼
src/photo/contour.js     마스크 정리·외곽선 추적·단순화
src/photo/fracture.js    보로노이 셀 + 폴리곤 클리핑
src/photo/inpaint.js     배경 구멍 채우기
src/photo/material.js    소재 판단 (API → 휴리스틱)
samples/                 샘플 사진 + manifest.json + CREDITS.md
vendor/                  three.js, RoomEnvironment, models/magic_touch.tflite
build-single.js          단일 HTML 번들러
```

물체 인터페이스는 공통입니다: `{ group, hittables(), hit(intersection, strength), update(dt), dispose(), stats(), statusText() }`.

## 손맛 튜닝 포인트

- 스윙: `src/bat.js` `SWING_TIME`(탭→타격 지연)
- 사진 물체: `src/objects/photo.js` — 나무 `hp`(3), 금속 찌그러짐 반경/깊이(`objSize * ...`), 유리 `SHATTER_AT`, 파편 개수(`count`), 파동 속도(`dist * 0.25`)
- 세그먼트 품질: `src/photo/contour.js` `simplify(..., 1.2)`(윤곽 단순화 정도), `maskToPolygon` 최소 면적
- 휴리스틱 소재 판단: `src/photo/material.js` `heuristicMaterial` 점수식
- 소리: `src/audio.js`

## 자동 검증 훅

```js
__demo.loadSample(1); // 샘플 전환
__demo.strikeAt(0, -0.1); __demo.step(1/60, 12); __demo.stats();
```

## 다음 단계

1. 실기기에서 손맛 튜닝 (진동 세기, 스윙 시간, 파편 수 vs. 프레임)
2. API 키 연결 후 비전 판단 경로 검증, 물체 이름 라벨 노출
3. 촬영 → 부수기 → 결과 영상 저장/공유 흐름, PWA(홈 화면 설치)
4. 히트스톱, 스와이프 세기, 녹음 샘플 ASMR 레이어

## 알려진 제한

- 세그먼트는 사진 중앙의 물체를 자동 선택합니다. 물체가 중앙에 없으면 물체를 직접 탭하면 됩니다.
- 배경 채우기는 진짜 인페인팅이 아니라 주변색 번짐이라, 복잡한 배경에선 뭉개져 보입니다.
- 파편끼리 충돌하지 않고 바닥(화면 아래)만 인식합니다. 유리 파편 70개는 저사양 폰에서 잠깐 프레임이 떨어질 수 있습니다.
- iOS Safari는 진동 미지원. 단일 파일 빌드/아티팩트에는 사진 모드가 없습니다.
- `samples/`의 `glass-bottle.jpg`, `metal-mokapot.jpg`, `ceramic-mug.jpg`, `wood-chair.jpg`는 폴더에 있던 파일이라 출처 확인이 필요합니다 (나머지는 Wikimedia Commons, `samples/CREDITS.md`).
