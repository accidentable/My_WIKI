---
title: 온디바이스 세그멘테이션으로 사진 속 물체 잘라내기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/wanted-hackathon-2026-readme.md]
tags: [mediapipe, segmentation, webassembly, 모바일웹]
---

## 1. 한 줄 정의

서버로 사진을 보내지 않고 브라우저 안에서 MediaPipe InteractiveSegmenter로 마스크를 뽑아, 후처리를 거쳐 물체 윤곽 폴리곤과 bbox까지 만들어내는 방식.

## 2. 어디서 썼는가

- [[wanted-hackathon-2026]] — 사진 모드에서 부술 대상을 잘라낼 때. 래퍼는 `src/photo/segment.js`, 후처리는 `src/photo/contour.js`.

## 3. 실제로 겪은 문제와 해결

**시드 지정을 사용자에게 묻지 않기.** 확인·수정 UI를 없애는 것이 목표였기 때문에 사진 중앙 점을 시드로 넣어 자동 선택했다. 대신 물체가 중앙에 없을 때를 위해 "물체 밖을 탭하면 그 자리의 다른 물체를 새로 잘라내고 대상 변경(스윙은 하지 않음)"이라는 조작을 뒀다. 실패를 UI로 막지 않고 재시도 동작으로 흡수한 셈이다.

**마스크를 그대로 쓰지 않기.** 원시 마스크에는 시드와 무관한 영역이 섞이므로 시드 연결 성분만 남기고, 외곽선을 추적한 뒤 RDP로 단순화해 폴리곤을 만든다. 단순화 정도는 `contour.js`의 `simplify(..., 1.2)`, 잡티 제거는 `maskToPolygon`의 최소 면적으로 조절한다.

**모델 로딩 비용.** `vendor/models/magic_touch.tflite`가 약 16MB라 사진 모드 첫 진입에 몇 초가 걸린다. 이후에는 사진당 1초 내외. 입력 사진은 1024px 이하로 줄여 넣는다.

**번들 제약.** MediaPipe WASM과 모델, 샘플 사진은 단일 HTML 파일 빌드(`npm run build:single`)에 담기지 않는다. 그래서 단일 파일 배포본과 Claude 아티팩트용 변형(`dist/artifact.html`)은 사진 탭 없이 테스트 벤치만 열린다. 온디바이스 모델을 쓰면 "파일 하나로 공유" 경로를 포기하거나 기능을 이중화해야 한다는 교환이 그대로 드러난 사례다.

## 4. 참고 자료

- `raw/done/wanted-hackathon-2026-readme.md`
- 라이브러리: `@mediapipe/tasks-vision` (importmap으로 로드)
