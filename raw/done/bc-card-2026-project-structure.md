# BC카드 빅데이터 해커톤 프로젝트 파일 구조

원본 위치: C:\Users\pc\Desktop\해커톤\BC카드 빅데이터 해커톤

## analysis/ (실행 순서대로 번호가 붙은 스크립트)

### 01_preprocess.py
# -*- coding: utf-8 -*-
"""제공 데이터 전처리: 업종 정리, 그룹 태그, 완전 패널 필터, 시군구 x 업종 x 월 집계"""
import pandas as pd, numpy as np, os
# 갈비전문점/한정식은 거의 비어 있어 일반한식에 합산
# 완전 패널: region x 업종 x seg 가 6개월 모두 있는 조합만

### 02_index.py
# -*- coding: utf-8 -*-
"""시군구별 유행 취약 상권 지수 (제과점 중심, v2)"""
import pandas as pd, numpy as np, os

### 03_charts.py
# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, os, matplotlib
import matplotlib.pyplot as plt
# 1. 업종별 변화율 (1~3월 평균 대비 6월)

### 04_naver_trend.py
# -*- coding: utf-8 -*-
"""네이버 클라우드 API 허브(검색어트렌드)로 유행 음식 26개의 정점 시점과 반감기 계산
"""
import json, os, time, urllib.request, pandas as pd, numpy as np
# 네이버 클라우드 플랫폼 API 허브(naverapihub) 키: X-NCP-APIGW-API-KEY-ID / X-NCP-APIGW-API-KEY

### 05_google_trends_save.py
# -*- coding: utf-8 -*-
"""구글 트렌드(크롬 내부 API로 수집, 2026-09-21)를 CSV로 저장
"""
import pandas as pd, os

### 06_trend_cycle_chart.py
# -*- coding: utf-8 -*-
"""유행 주기 단축 그래프 (구글 트렌드)"""
import pandas as pd, numpy as np, os, matplotlib
# 제외: 검색 범위(2016~) 이전 유행, 데이터 거의 없음, 일반 단어와 겹침, 아직 진행 중

### 07_fad_interval.py
# -*- coding: utf-8 -*-
"""유행 교체 주기: 유행 정점 사이 간격과 연간 유행 개수"""
import pandas as pd, numpy as np, os, matplotlib
# 정점이 관측 범위 안에 있고 실제 '단기 유행'인 것 (정착 품목·일반 단어·범위 밖 제외)
# 3년 구간 평균 간격

### 08_naver_vs_google.py
# -*- coding: utf-8 -*-
"""네이버 주간 검색량으로 지속기간·진폭·교체간격 계산, 구글과 비교"""
import pandas as pd, numpy as np, os, matplotlib

### 09_lifespan_metrics.py
# -*- coding: utf-8 -*-
"""유행 수명을 여러 정의로 측정 (네이버 주간 + 구글 월간)"""
import pandas as pd, numpy as np, os
    """s: 평활된 시계열. 반환: 여러 수명 정의(단위: 주)"""
    # 상승 시작: 정점 전 마지막으로 10% 미만

### 10_lifespan_charts.py
# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, os, matplotlib
# 그림 16: 정점 → 10% 이하(소멸)까지 걸린 주, 네이버 vs 구글, 음식별

### 11_content_density.py
# -*- coding: utf-8 -*-
"""유행별 콘텐츠 양: 네이버 블로그·카페·뉴스 총 게시물 수 (API 허브 검색 API)"""
import json, os, time, urllib.request, urllib.parse, pandas as pd

### 12_charts_v2.py
# -*- coding: utf-8 -*-
"""보고서용 차트 재설계: 한 장에 메시지 하나, 강조색 하나 + 회색, 직접 라벨, Pretendard"""
import pandas as pd, numpy as np, os, glob, matplotlib
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt

## output/ 산출물
attention_share_dominance.csv
clean_rows.parquet
content_density.csv
fig10_유행_진폭.png
fig11_유행_교체주기.png
fig12_유행_타임라인.png
fig13_지속기간_구글vs네이버.png
fig14_네이버_시기별지표.png
fig15_네이버_유행곡선.png
fig16_소멸까지_기간.png
fig17_시기별_수명_3지표.png
fig18_관심점유율.png
fig1_업종별_변화율.png
fig2_제과점_월별추이.png
fig3_시도별_제과점하락.png
fig4_노출도_vs_하락_산점도.png
fig5_노출도_상위지역.png
fig6_대표지역_사례.png
fig7_유행주기_단축.png
fig8_시기별_평균주기.png
fig9_유행곡선_비교.png
google_trends
lifespan_metrics_all.csv
my-writing-voice.skill
naver_fad_table.csv
naver_trend_summary.csv
naver_trend_weekly.csv
panel_region_buz_seg_month.parquet
r1_업종별_변화율.png
r2_제과점_월별지수.png
r3_시도별_제과점.png
r4_노출도.png
r5_시기별_3지표.png
r6_1위_타임라인.png
region_exposure.csv
region_risk_index.csv
service_mockup.png
~$이디어요약서.docx
분석결과_요약.md
아이디어요약서.docx
아이디어요약서_v2.docx
아이디어요약서_초안.md
