---
title: GPS 좌표를 AR 월드 좌표로 바꿔 오브젝트 고정하기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/hana-ar-kowalk-2026-plan.md]
tags: [AR, GPS, ViroReact, React Native]
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
