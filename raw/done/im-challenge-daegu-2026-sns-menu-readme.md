# SNS 신메뉴 AI 컨설팅

**2026 AI Blockchain Challenge in Daegu** 참가를 위해 기획한, 대구 소상공인의 신메뉴 시험 판매를 돕는 서비스입니다.

> SNS에서 유행하는 신메뉴를 발견하고, 우리 가게의 재료·장비·예산에 맞는 작은 판매 실험으로 연결합니다.

이 저장소는 **대화 맥락·기획·구현 명세·데이터**와, 그 명세대로 구현한 **웹 프로토타입(`sns-menu-consultant/`)**을 담고 있습니다. 자료 검증·가공 스크립트와 앱 모두 실행할 수 있습니다.

## 앱 구현 상태 (2026-09-14)

- `sns-menu-consultant/`에 Next.js 16 + TypeScript + SQLite/Prisma 로 실행계획 단계 1~6(F01~F09)을 구현했습니다. 실행 방법은 [sns-menu-consultant/README.md](sns-menu-consultant/README.md), 완료·미완료 기능과 검증 결과는 [구현 보고](sns-menu-consultant/docs/구현_보고.md)와 [검수 기록](sns-menu-consultant/docs/검수_기록.md)에 있습니다.
- 실제 AI는 OpenAI(`gpt-5.6-terra`, `AI_PROVIDER=openai`)로 연결 테스트·추출·적용안 생성까지 확인했습니다. Anthropic 어댑터도 있으나 Anthropic 키로는 미검증입니다. `.env`의 `AI_API_KEY`가 비어 있으면 명시적 데모 어댑터만 동작합니다.
- 공공 상가 118,357행과 대구 법정동 인구 383행은 앱의 가져오기 명령/화면으로 적재해 검증했습니다. 가상 카페·가상 SNS 자료·데모 후보·시연 시험은 `dataMode=demo`로 분리되어 있습니다.
- 대회 접수(붙임1~4)와 제출 ZIP 업로드는 아직 하지 않았습니다. ZIP은 `node sns-menu-consultant/scripts/prepare-submission-zip.mjs`로 만듭니다.
- **GitHub에서 바로 띄우기:** `Code → Codespaces → Create codespace on main`을 누르면 자동으로 설치·적재·실행되어 포트 3000에서 앱이 열립니다(GitHub Pages는 서버·DB가 필요해 사용 불가). Docker는 저장소 루트에서 `docker compose up --build`. 자세한 절차는 [sns-menu-consultant/README.md](sns-menu-consultant/README.md#1-1-github에서-바로-띄우기). 푸시마다 GitHub Actions가 lint·테스트·빌드·기동·Docker 이미지를 검사합니다.

## 처음 읽는 순서

1. [대화 맥락과 대회 배경](기획서/대화맥락과_대회배경.md): 어떤 대회에서 왜 이 아이디어가 나왔고, 사용자가 어떤 방향을 정했는지.
2. [서비스 상세기획서](기획서/SNS_신메뉴_AI컨설팅_상세기획서.md): F01~F09, 화면·DB·API·AI 출력, 비용 산식, 오류·완료 조건.
3. [데이터 상세명세](기획서/데이터_상세명세.md): 실제 확보 파일, 39개 상가 열·231개 인구 열 구조, 활용 목적·결합·한계.
4. [AI 코딩 실행계획](기획서/AI코딩_실행계획.md): 처음 전달할 지시문, 단계별 구현·검수 순서.
5. [유행 감지·추적 조사](기획서/유행_감지_추적_조사.md): P1 자동 수집의 데이터 소스, 단계 판정 규칙, 2026-09-14 실험 결과. 결과 파일은 `data/derived/trend_radar/`.
5. [파일 목록과 해시](data/manifest.json), [데이터 출처·상태](data/source_catalog.json): 무엇이 실제 포함됐는지 확인.

## 대회와 핵심 결정

- 대회 공모 분야의 **소상공인·골목상권 디지털 금융 → 골목상권 데이터 기반 AI 컨설팅**에 연결합니다. [공식 공고](대회%20제출자료/공고문.pdf), [홈페이지](https://www.im-challenge.com/).
- 예선 접수 마감 확인 기록은 **2026-09-20 23:59**입니다. 이 저장소를 올린 것과 대회 접수는 별개입니다.
- 외부 서비스 표현은 ‘SNS에서 유행하는 신메뉴’입니다. 서울 중심 전국 SNS 관찰은 내부 수집 전략이며 초기 이용자는 대구 사장님입니다.
- 전국 인기 순위를 정밀 예측하는 것보다 ‘우리 가게에서 시도할 만한 후보와 실행안’을 우선합니다.
- P0는 수동 근거 등록+AI 추출·검토, 가게별 적용안, 공공데이터 맥락, 시험 비용과 결과 기록입니다.
- 첫 업종은 개인 카페를 기본 제안으로 두었습니다. 공공 CSV의 카페 분류에는 체인점도 포함될 수 있습니다.
- 자동 SNS 수집은 P1, 무료 소비자 먹거리 지도와 사장님 유료 구독은 P2입니다. 현재 결제·지도 운영 기능이 없습니다.
- API·브라우저 에이전트 사용을 장기적으로 배제하지 않습니다. 아직 접근 계약이나 실제 관찰 계정 목록은 확정하지 않았습니다.
- 블록체인은 초기 필수 기능으로 정하지 않았습니다. 시험 예산·구매 현금·원가·비용 회수 계산으로 금융 맥락을 구체화합니다.

## 포함된 데이터와 파일

| 묶음 | 포함 내용 |
|---|---|
| 대구 상가 원본 | 2026.06, **118,357행·39열**, 약 63.3MB, UTF-8 |
| 카페·디저트 추출 | 카페 5,513 + 빵/도넛 1,509 + 떡/한과 485 = **7,507행**, UTF-8 BOM |
| 주민등록 인구 원본 | 2026.08.31, 전국 **18,624행·231열**, 약 10.1MB, CP949 |
| 대구 인구 추출 | **383개 법정동/리**, CSV·JSON, 원본 성·연령 합계 검증 |
| 개발 입력 예시 | 빈 SNS 자료 양식, 명시적인 가상 카페, 비용 계산 기대값 |
| 공식 자료 | 대회 공고 PDF·빈 제출 양식 HWPX, DIP 2026.09 설명서 PDF·검색용 텍스트 |
| 재현 자료 | 데이터 가공·검증 스크립트, 품질 보고서, 출처·해시 |

상가 전체와 카페 전체의 법정동코드가 인구 원본 코드와 일치함을 확인했습니다. 거주 인구를 실제 방문객이나 특정 메뉴 수요로 해석하지 않습니다. 상가 CSV에 메뉴·가격·매출은 없습니다.

**아직 없는 자료:** 실제 SNS 관찰 게시물, 실제 사장님 운영·원가 입력, 시험 판매 결과, DIP 카드·생활인구·주문 원본. DIP는 설명서만 확보했으며 승인된 분석 결과를 얻은 뒤 연결합니다. 2021년 먹거리골목 자료는 최신 메뉴·가격 입력에 쓰지 않아 필수 파일에서 제외했습니다.

## 다른 환경에서 시작하기

GitHub 저장소 접근 권한이 있는 환경에서 복제합니다. 포함한 CSV는 일반 Git 파일이며 Git LFS나 별도 데이터 다운로드가 필요하지 않습니다.

```sh
git clone https://github.com/IM-hack-TH/my_project.git
cd my_project
python tools/verify_bundle.py
```

Python 3.10 이상, 표준 라이브러리만 필요합니다. Windows에서는 `py -3`으로 실행할 수 있습니다. 아래 명령은 원본에서 파생 데이터를 다시 만들고 해시가 동일한지 검사합니다.

```sh
python tools/prepare_data.py
python data/raw/population/prepare_population.py
python tools/verify_bundle.py
```

파일을 의도적으로 수정했다면 내용 검토 후 `python tools/update_manifest.py`로 인계 파일 목록을 갱신합니다. 새 원본 스냅샷은 예상 행수·기간·문서도 함께 갱신해야 합니다.

앱은 `sns-menu-consultant/`에 있습니다 (Node.js 22 이상).

```sh
cd sns-menu-consultant
npm install
cp .env.example .env
npm run db:migrate
npm run db:seed:reset
npx tsx scripts/import-public-data.ts stores-full-202606 population-daegu-202608
npm run dev
```

의존성은 `package-lock.json`에 고정되어 있습니다. 실제 AI를 쓰려면 `.env`의 `AI_PROVIDER`(openai|anthropic)와 `AI_API_KEY`를 채웁니다. 자세한 내용은 [sns-menu-consultant/README.md](sns-menu-consultant/README.md)를 봅니다.

## 파일 구조

```text
README.md / AGENTS.md
기획서/                         # 맥락, 상세기획, 데이터 명세, 코딩 실행계획
대회 제출자료/                  # 공식 공고·빈 양식
references/                     # DIP 설명서 PDF와 추출 텍스트
data/
  raw/                          # 대구 상가 원본
    population/                 # 전국 인구 원본·출처·검증·재생성 코드
      derived/                  # 대구 인구 CSV/JSON
  derived/                      # 카페·디저트 CSV, 상가 품질·매핑 예시
  schemas/                      # 상가 원본 필드 순서·형식
  templates/                    # 신규 수집 양식·명시적 가상 예시
  source_catalog.json           # 확보/미확보 구분·출처
  manifest.json                 # 파일별 크기·SHA-256
tools/                          # 가공·무결성 확인·목록 갱신
sns-menu-consultant/            # 웹 프로토타입 (Next.js·Prisma·SQLite), README·docs·tests 포함
```

`data/manifest.json`은 인계 문서·데이터·도구만 추적하며 앱 소스는 추적하지 않습니다.

기준일은 2026-09-13입니다. 공식 일정·API·데이터가 갱신될 수 있으므로 실제 대회 제출·외부 연동 직전 다시 확인합니다. 문서의 기능 계획을 이미 구현된 기능이나 검증된 사업 성과로 읽지 않습니다.
