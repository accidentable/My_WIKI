---
title: GPS 좌표를 AR 월드 좌표로 바꿔 오브젝트 고정하기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/hana-ar-kowalk-2026-plan.md]
tags: [AR, GPS, ViroReact, React Native]
cs_topics: [컴퓨터그래픽스, 알고리즘, 소프트웨어공학]
---

## 1. 한 줄 정의

유저의 현재 GPS와 목표 지점 GPS의 차이를 미터 단위 x/z 오프셋으로 환산해, AR 월드 좌표계의 그 자리에 3D 오브젝트를 놓는 기법.

## 2. 어디서 썼는가

- [[hana-ar-kowalk-2026]] — 기업 본사 위치에 주식 토큰 3D 오브젝트를 띄우는 데 사용 (계획 단계)

## 3. 실제로 겪은 문제와 해결

원자료는 계획 문서라 실행 중 겪은 문제는 없고, 사전에 정리된 방법과 제약만 있다.

변환식은 지구 반지름 R=6371000m를 쓰는 소각 근사다. 경도 차이에 `cos(위도)`를 곱해 동서 거리를, 위도 차이에 R을 곱해 남북 거리를 구하고, AR에서는 -z가 북쪽이므로 남북 성분에 부호를 뒤집는다. y는 1.5로 고정해 눈높이에 띄운다.

```javascript
function gpsToArPosition(userLat, userLng, targetLat, targetLng) {
  const R = 6371000; // 지구 반지름 (m)
  const dLat = toRad(targetLat - userLat);
  const dLng = toRad(targetLng - userLng);

  const x = dLng * Math.cos(toRad(userLat)) * R; // 동서 방향 (m)
  const z = -dLat * R; // 남북 방향 (m), AR에서 -z가 북쪽

  return { x, y: 1.5, z };
}
```

거리·방위각 자체는 Haversine 공식과 `atan2`로 계산한다. 반경 진입 판정(100m)에도 같은 거리 계산을 쓴다.

구현·테스트상 제약:

- ViroReact는 Expo Go에서 동작하지 않는다. `expo prebuild`로 bare workflow로 전환해 네이티브 빌드해야 한다.
- iOS AR은 시뮬레이터에서 안 되므로 실제 기기가 필요하다.
- GPS는 실외에서 테스트해야 정확하고, 실내에서는 mock location을 쓴다.

## 4. 참고 자료

- ViroReact v2.41+ (ARKit / ARCore)
- expo-location (GPS 추적, geofencing)
- 원자료: `raw/done/hana-ar-kowalk-2026-plan.md`

## 학습

### CS 주제
- 컴퓨터그래픽스: 좌표계 변환, 축 방향 규약(오른손/왼손, -z가 북쪽)
- 알고리즘: 구면 거리(Haversine)와 접평면 소각 근사, atan2 방위각
- 소프트웨어공학: 실기기·실외에서만 검증되는 기능의 테스트 전략

### 설명할 수 있어야 하는 것
- 왜 이 방법을 골랐는가 (문제 → 선택 → 결과)
- 대안은 무엇이었고 무엇을 포기했는가
- 어떤 조건에서 이 방법이 깨지는가

### 확인 질문
1. **Q:** (L1 개념) 위경도(구면 좌표)를 미터 단위 지역 평면 좌표로 바꾸는 근사는 무엇이고, 경도 차이에 왜 `cos(위도)`를 곱하는가?
   **A:** 좁은 범위에서는 지구를 그 지점에 붙인 평평한 접평면으로 봐도 오차가 작다는 소각 근사다. 위도 차이는 어디서나 같은 거리이므로 `dLat * R`(R=6371000m)로 남북 거리를 얻지만, 경선 사이의 실제 거리는 극으로 갈수록 줄어들기 때문에 `dLng * cos(위도) * R`로 보정해야 동서 거리가 나온다. 이 프로젝트의 `gpsToArPosition`이 정확히 그 식이며, 결과를 AR 월드 좌표의 x/z로 바로 쓴다.
   **꼬리:** 같은 위경도 차이라도 서울과 적도에서 동서 거리가 다른 이유를 식으로 설명해 보라.
   **틀리기 쉬운 답:** "위도 1도와 경도 1도는 같은 거리다." 경도 1도의 거리는 `cos(위도)`에 비례해 줄어든다.
2. **Q:** (L2 판단) 남북 성분에 왜 부호를 뒤집고, 왜 y를 1.5로 고정했는가? 거리 판정에는 왜 Haversine을 따로 쓰는가?
   **A:** AR 월드 좌표계에서는 **-z가 북쪽**이므로, 북쪽으로 dLat만큼 떨어진 목표는 `z = -dLat * R`이 되어야 한다. y(높이)는 계산하지 않고 1.5로 고정해 눈높이에 띄운다. 오브젝트를 놓는 데는 위의 평면 근사면 충분하지만, "기업 본사 반경 100m 진입" 같은 **판정용 거리**는 Haversine 공식으로, 방위각은 `atan2`로 계산한다. 다만 원자료는 계획 문서라 이 값들이 실행에서 검증된 값은 아니다.
   **꼬리:** AR 월드의 "북쪽"은 누가 정하며, 기기의 방위 추정이 틀어지면 오브젝트는 어떻게 보이는가?
   **틀리기 쉬운 답:** "y도 실제 해발고도로 계산해야 맞다." 이 설계는 높이를 쓰지 않고 눈높이 상수로 고정했고, 그 선택 자체가 단순화다.
3. **Q:** (L3 한계) 이 변환과 개발 방식은 어떤 조건에서 먼저 깨지는가?
   **A:** 세 방향으로 깨진다. (1) 소각 근사는 가까운 거리 전제이므로 목표가 멀어질수록 오차가 커진다. 이 서비스는 반경 100m 진입 후에야 AR을 켜므로 그 안에서만 쓰인다. (2) **환경 제약**: GPS는 실외에서 테스트해야 정확하고, 실내에서는 mock location을 써야 한다. (3) **빌드·검증 제약**: ViroReact는 Expo Go에서 동작하지 않아 `expo prebuild`로 bare workflow 전환 후 네이티브 빌드가 필요하고, iOS AR은 시뮬레이터에서 안 돼 실제 기기가 있어야 한다. 즉 "빨리 돌려보는" 경로가 막혀 있어 개발 속도가 제약된다.
   **꼬리:** mock location으로 검증할 수 있는 것과 절대 검증할 수 없는 것을 나눠 보라.
   **틀리기 쉬운 답:** "시뮬레이터로 AR 화면까지 확인하면 된다." iOS 시뮬레이터는 AR을 지원하지 않는다.

### 더 파볼 것
- [Calculate distance, bearing and more between Latitude/Longitude points](https://www.movable-type.co.uk/scripts/latlong.html) — Haversine 거리, `atan2` 방위각, 그리고 이 프로젝트가 쓴 것과 같은 등장방형(equirectangular) 근사 `x = Δλ·cos φm, y = Δφ, d = R·√(x²+y²)`
- [Local tangent plane coordinates](https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates) — 지역 ENU(동·북·상) 좌표계가 무엇이고, 기준점에서 멀어질수록 접평면 가정이 나빠지는 이유
