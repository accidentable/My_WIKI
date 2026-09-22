# Ko-Walk: 코스피와 걷다

## 프로젝트 개요

코스피 상장기업 본사를 직접 걸어서 방문하고, AR로 해당 기업의 토큰화된 주식을 수집하는 위치 기반 투자 플랫폼.

### 핵심 플로우

1. 유저가 앱 실행하고 지도에서 주변 상장기업 본사 위치 확인
2. 도보로 기업 본사 반경 100m 이내 진입
3. 앱이 GPS로 위치 감지 → AR 모드 활성화
4. AR 카메라 화면에 해당 기업의 주식 토큰 3D 오브젝트 렌더링
5. 유저가 토큰 탭 → 퀴즈 화면으로 전환
6. AI가 기업 IR 자료/공시 기반으로 자동 생성한 퀴즈 3문제 출제
7. 2문제 이상 정답 → 토큰 수집 성공 → 유저 지갑으로 토큰 전송
8. 포트폴리오에 추가, 다음 기업으로 이동

---

## 기술 스택

### 프론트엔드 (모바일)

- **React Native + Expo** (SDK 51+)
  - 크로스 플랫폼 iOS/Android 동시 개발
  - Expo Go로 빠른 테스트 가능
- **ViroReact** (v2.41+)
  - React Native 위에서 AR 구현
  - ARKit (iOS) / ARCore (Android) 둘 다 지원
  - JS로 AR 씬, 3D 오브젝트, 인터랙션 처리
  - 주의: Expo managed workflow와 호환 안 됨 → `expo prebuild`로 bare workflow 전환 필요
- **react-native-maps**
  - 기업 본사 위치 지도 표시
  - 마커 클릭 시 기업 정보 표시
- **expo-location**
  - GPS 좌표 실시간 추적
  - geofencing으로 기업 반경 진입 감지

### AR 구현 상세

```
AR 씬 구조:

ViroARSceneNavigator
└── ViroARScene
    └── ViroNode (GPS 좌표 기반 위치)
        └── Viro3DObject (주식 토큰 3D 모델)
            ├── ViroAnimations (회전, 부유 애니메이션)
            └── onClick → 퀴즈 화면 전환
```

- **3D 토큰 모델**: .glb 형식. Blender로 제작하거나 Sketchfab 무료 에셋 활용
  - 기업별로 색상/로고 다르게 적용
  - 금색 코인 형태 기본, 기업 로고 텍스처 매핑
- **GPS → AR 좌표 변환**:
  - 유저 현재 GPS와 기업 본사 GPS 간 거리/방위각 계산
  - Haversine 공식으로 거리, atan2로 방위각
  - AR 월드 좌표에서 해당 방향/거리에 오브젝트 배치
- **수집 인터랙션**:
  - 토큰 탭 → 파티클 이펙트 + 사운드 → 퀴즈 모달

```javascript
// GPS → AR 좌표 변환 예시
function gpsToArPosition(userLat, userLng, targetLat, targetLng) {
  const R = 6371000; // 지구 반지름 (m)
  const dLat = toRad(targetLat - userLat);
  const dLng = toRad(targetLng - userLng);
  
  const x = dLng * Math.cos(toRad(userLat)) * R; // 동서 방향 (m)
  const z = -dLat * R; // 남북 방향 (m), AR에서 -z가 북쪽
  
  return { x, y: 1.5, z }; // y는 높이 (눈높이 정도)
}
```

### 백엔드

- **Node.js + Express**
  - REST API 서버
  - 엔드포인트: 기업 목록, 퀴즈 생성, 방문 기록, 포트폴리오 조회
- **Supabase (PostgreSQL)**
  - 유저 관리 (Supabase Auth)
  - 기업 데이터 (본사 좌표, 기본 정보)
  - 방문 기록 (유저ID, 기업ID, 타임스탬프, 퀴즈 결과)
  - 포트폴리오 (유저별 수집한 토큰 목록, 수량)
- **배포**: Vercel (API) + Supabase (DB)

### AI 퀴즈 자동 생성

- **OpenAI API (GPT-4o)**
- **데이터 소스**: DART 전자공시 API (https://opendart.fss.or.kr)
  - 기업별 최신 공시 문서 자동 수집
  - 사업보고서, 반기보고서, 주요사항보고서
- **퀴즈 생성 플로우**:
  1. 크론잡으로 DART에서 코스피 100 기업 공시 일 1회 수집
  2. 공시 텍스트를 GPT-4o에 전달
  3. 프롬프트: "다음 기업 공시를 바탕으로 4지선다 퀴즈 3문제를 JSON으로 생성해줘"
  4. 응답 JSON을 DB에 저장
  5. 유저가 기업 방문 시 해당 퀴즈를 앱에서 로드

```json
// 퀴즈 JSON 형식
{
  "company_id": "005930",
  "company_name": "삼성전자",
  "generated_at": "2026-04-01",
  "questions": [
    {
      "question": "삼성전자의 2025년 4분기 영업이익은 약 얼마입니까?",
      "options": ["6.5조 원", "8.1조 원", "10.2조 원", "12.7조 원"],
      "answer": 2,
      "explanation": "삼성전자는 2025년 4분기 잠정 영업이익 10.2조 원을 발표했습니다."
    }
  ]
}
```

### 블록체인 (토큰)

- **네트워크**: Base Sepolia 테스트넷
  - Ray가 Base 해커톤 수상 경험 있어서 익숙
  - 가스비 무료 (테스트넷)
  - 추후 Base 메인넷으로 마이그레이션 가능
- **스마트 컨트랙트**: Solidity
  - ERC-20 기반 토큰 컨트랙트
  - 기업별 개별 토큰 (예: KO_005930 = 삼성전자 토큰)
  - mint 함수: 퀴즈 통과 시 서버에서 호출하여 유저 지갑에 토큰 전송
- **프론트 연동**: ethers.js v6
  - 유저 지갑: 앱 내 내장 지갑 (privateKey를 Secure Storage에 저장)
  - 토큰 잔액 조회, 포트폴리오 표시

```solidity
// 간소화된 토큰 컨트랙트 예시
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract KoWalkToken is ERC20, Ownable {
    constructor(string memory name, string memory symbol) 
        ERC20(name, symbol) 
        Ownable(msg.sender) {}

    // 서버에서 퀴즈 통과 확인 후 호출
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```

---

## 데이터베이스 스키마

```sql
-- 유저
create table users (
  id uuid primary key default gen_random_uuid(),
  wallet_address text not null,
  nickname text,
  created_at timestamptz default now()
);

-- 기업 (코스피 100)
create table companies (
  id text primary key, -- 종목코드 (예: 005930)
  name text not null, -- 삼성전자
  latitude double precision not null,
  longitude double precision not null,
  address text,
  sector text, -- 업종
  description text, -- 기업 소개
  token_contract_address text, -- 배포된 토큰 컨트랙트 주소
  logo_url text
);

-- 퀴즈
create table quizzes (
  id uuid primary key default gen_random_uuid(),
  company_id text references companies(id),
  questions jsonb not null, -- 위의 퀴즈 JSON 형식
  generated_at date not null,
  source text -- DART 공시 번호
);

-- 방문 기록
create table visits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  company_id text references companies(id),
  visited_at timestamptz default now(),
  quiz_score int, -- 맞춘 문제 수
  quiz_passed boolean, -- 2문제 이상 맞추면 true
  token_amount decimal, -- 지급된 토큰 수량
  tx_hash text -- 블록체인 트랜잭션 해시
);

-- 테마 루트
create table routes (
  id uuid primary key default gen_random_uuid(),
  name text not null, -- "여의도 금융 코스"
  description text,
  company_ids text[] -- 포함된 기업 종목코드 배열
);
```

---

## 프로토타입 범위 (MVP)

### 반드시 구현

- [ ] 지도 화면에 기업 본사 위치 마커 표시 (10~20개)
- [ ] GPS 기반 기업 반경 100m 진입 감지
- [ ] AR 카메라에 주식 토큰 3D 오브젝트 렌더링
- [ ] 토큰 탭 → 퀴즈 화면 전환
- [ ] AI 퀴즈 3문제 출제 및 채점
- [ ] 퀴즈 통과 시 토큰 수집 성공 화면
- [ ] 탐방 포트폴리오 화면 (수집한 기업 토큰 목록)
- [ ] Base Sepolia 테스트넷 토큰 발행/전송

### 있으면 좋음

- [ ] 테마별 루트 추천 (여의도 금융 코스 등)
- [ ] 기업 상세 정보 화면 (사업 구조, 재무 요약)
- [ ] 수집한 기업 도감 (방문 완료/미방문 표시)
- [ ] 걸음 수 트래킹 + 일일 통계
- [ ] 랭킹 (가장 많은 기업 방문한 유저)

### 프로토타입에서 가짜 데이터로 처리

- 토큰 = 실제 주식이 아닌 테스트넷 ERC-20 토큰
- 기업 IR 데이터 = DART 실제 공시 활용하되, 퀴즈 품질은 데모 수준
- 토큰 가치 환산 = 화면에 "만원 상당" 등으로 표기만

---

## 화면 구성

```
1. 스플래시 / 온보딩
   - Ko-Walk 로고
   - 간단한 서비스 설명 3단계 슬라이드
   - 지갑 생성 (자동)

2. 홈 (지도)
   - 전체 화면 지도
   - 기업 본사 마커 (수집완료=초록, 미수집=금색)
   - 하단에 가까운 기업 카드 슬라이더
   - 카드: 기업명, 거리, 업종, 토큰 리워드 금액
   - 상단에 "수집한 기업 N개 / 100개"

3. AR 수집 화면
   - 전체 화면 카메라
   - AR 오버레이: 주식 토큰 3D 오브젝트 (회전 + 부유)
   - 하단에 기업명, "탭하여 수집하기"
   - 탭 시 → 퀴즈 모달

4. 퀴즈 화면
   - 상단: 기업 로고 + 기업명
   - "이 기업을 알아보세요"
   - 4지선다 퀴즈 3문제
   - 문제별 정답/오답 즉시 표시 + 해설
   - 결과: 3/3, 2/3 → 성공 / 1/3, 0/3 → 실패

5. 수집 성공 화면
   - 축하 애니메이션 (파티클, 코인 떨어지는 효과)
   - "삼성전자 토큰 10,000원 상당 수집!"
   - 트랜잭션 해시 (블록체인 기록)
   - "포트폴리오 보기" / "다음 기업 찾기" 버튼

6. 포트폴리오
   - 총 수집 토큰 가치 (합산)
   - 기업별 토큰 카드 리스트
   - 카드: 기업명, 로고, 수집 일시, 토큰 수량, 현재 환산 가치
   - 섹터별 분포 파이차트

7. 루트 탐색 (있으면 좋음)
   - 테마별 추천 루트 리스트
   - "여의도 금융 코스" → 하나금융, KB금융, 신한금융...
   - 지도에 루트 폴리라인 표시
   - 예상 소요 시간, 총 거리, 방문 기업 수

8. 프로필
   - 닉네임, 지갑 주소
   - 총 방문 기업 수, 총 걸은 거리
   - 최근 방문 기록
```

---

## 초기 기업 데이터 (서울 주요 기업 샘플)

```json
[
  {"id": "005930", "name": "삼성전자", "lat": 37.4953, "lng": 127.0627, "sector": "반도체", "address": "서울 서초구 서초대로74길 11"},
  {"id": "000660", "name": "SK하이닉스", "lat": 37.5013, "lng": 127.0396, "sector": "반도체", "address": "서울 종로구 종로1"},
  {"id": "005380", "name": "현대자동차", "lat": 37.5066, "lng": 127.0436, "sector": "자동차", "address": "서울 서초구 헌릉로 12"},
  {"id": "086790", "name": "하나금융지주", "lat": 37.5227, "lng": 126.9246, "sector": "금융", "address": "서울 중구 을지로 35"},
  {"id": "105560", "name": "KB금융", "lat": 37.5147, "lng": 126.9268, "sector": "금융", "address": "서울 영등포구 국제금융로8길 26"},
  {"id": "055550", "name": "신한금융지주", "lat": 37.5094, "lng": 126.9313, "sector": "금융", "address": "서울 중구 세종대로9길 20"},
  {"id": "035420", "name": "NAVER", "lat": 37.3595, "lng": 127.1052, "sector": "IT", "address": "경기 성남시 분당구 불정로 6"},
  {"id": "035720", "name": "카카오", "lat": 37.3948, "lng": 127.1108, "sector": "IT", "address": "경기 성남시 분당구 판교역로 166"},
  {"id": "006400", "name": "삼성SDI", "lat": 37.4713, "lng": 127.0393, "sector": "배터리", "address": "서울 강남구 봉은사로 150"},
  {"id": "051910", "name": "LG화학", "lat": 37.5217, "lng": 126.9408, "sector": "화학", "address": "서울 영등포구 여의대로 128"}
]
```

---

## API 엔드포인트

```
GET  /api/companies              → 전체 기업 목록
GET  /api/companies/:id          → 기업 상세 정보
GET  /api/companies/:id/quiz     → 해당 기업 오늘의 퀴즈
POST /api/visits                 → 방문 기록 생성 (퀴즈 결과 포함)
GET  /api/users/:id/portfolio    → 유저 포트폴리오
GET  /api/users/:id/visits       → 유저 방문 기록
GET  /api/routes                 → 테마 루트 목록
POST /api/quiz/generate/:id      → 특정 기업 퀴즈 수동 생성 (어드민)
POST /api/token/mint             → 토큰 발행 (서버 내부 호출)
```

---

## 개발 순서

### Week 1: 기초 세팅 + 지도
1. React Native + Expo 프로젝트 생성
2. Supabase 프로젝트 생성 + DB 스키마 설정
3. 기업 본사 좌표 데이터 DB에 삽입
4. react-native-maps로 지도 화면 구현
5. 기업 마커 표시 + 하단 카드 슬라이더

### Week 2: GPS + AR
1. expo-location으로 GPS 추적
2. Haversine 거리 계산 → 반경 진입 감지
3. expo prebuild → ViroReact 설치
4. AR 씬 세팅 + 3D 토큰 오브젝트 렌더링
5. GPS→AR 좌표 변환 구현
6. 토큰 탭 인터랙션

### Week 3: AI 퀴즈 + 블록체인
1. DART API 연동 → 기업 공시 수집
2. OpenAI API로 퀴즈 자동 생성
3. 퀴즈 화면 UI 구현
4. Base Sepolia에 토큰 컨트랙트 배포
5. ethers.js로 토큰 발행/전송 연동
6. 퀴즈 통과 → 토큰 민트 플로우 완성

### Week 4: 포트폴리오 + 마무리
1. 포트폴리오 화면 구현
2. 수집 성공 애니메이션
3. 테마 루트 (있으면)
4. UI 폴리싱
5. 데모 영상 촬영
6. PPT 최종 정리

---

## 참고 사항

- ViroReact는 Expo Go에서 안 돌아감. 반드시 expo prebuild 후 네이티브 빌드 필요
- iOS에서 AR 테스트하려면 실제 기기 필요 (시뮬레이터 AR 미지원)
- GPS 테스트는 실외에서 해야 정확. 실내에서는 mock location 사용
- DART API 키는 https://opendart.fss.or.kr 에서 무료 발급
- OpenAI API 키 필요 (유료, 하지만 퀴즈 생성 정도는 비용 미미)
- Base Sepolia 테스트넷 ETH는 faucet에서 무료 수급
