---
title: 한투 종목마스터 파일로 유니버스 뽑기
type: concept
created: 2026-09-22
updated: 2026-09-22
sources: [raw/done/kis-openapi-invest-2026-09-readme.md]
tags: [한국투자증권, 데이터수집, 의존성]
---

## 한 줄 정의

한투가 공개하는 `kospi_code.mst` 안에 KOSPI100 편입 플래그와 각종 위험 플래그가 들어 있어,
지수 구성종목 스크래핑이나 외부 시세 라이브러리 없이 매매 유니버스를 만들 수 있다.

## 어디서 썼는가

- [[kis-openapi-invest-2026-09]] — `core/universe.py`

## 실제로 겪은 문제와 해결

- 마스터파일에 KOSPI100 편입 플래그뿐 아니라 관리종목·거래정지·정리매매·시장경고·
  단기과열·공매도과열·우선주 플래그도 같이 들어 있다. 매매 제외 필터를 한 파일로 끝낼 수 있다.
- 파싱은 고정폭 문자열 슬라이싱이라 pandas도 필요 없다. 그 결과 런타임 의존성이
  `requests` 하나로 줄고, AWS 람다 배포 패키지가 몇 MB에 그친다.
- 스크래핑이나 FinanceDataReader 같은 외부 라이브러리에 의존하지 않으므로
  외부 사이트 구조 변경으로 유니버스가 깨질 일이 없다.

## 참고 자료

- raw/done/kis-openapi-invest-2026-09-readme.md
