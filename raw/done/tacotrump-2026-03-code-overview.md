# TACO Index (타코알리미) 코드 개요 (자동 추출, 2026-09-22)

원본 저장소: https://github.com/accidentable/tacotrump.git (로컬: Desktop/해커톤/tacotrump). 해커톤 출품 여부는 자료에 없음.

## index.html 메타
<title>TACO Index – Will Trump Chicken Out? | 타코알리미
<meta name="description" content="Real-time TACO Index tracking the probability of Trump backing down on Iran. Based on S&P 500, VIX, Treasury yields, oil prices, Dollar Index & approval ratings. 트럼프 대이란 강경책 번복 가능성을 실시간 추적하는 타코 지수." />

## git log (전체 43개 커밋, 오래된 순)
- 2026-03-25 18:45:55 +0900 TACO Dashboard - initial commit
- 2026-03-25 18:48:12 +0900 fix: TS errors for Vercel deploy
- 2026-03-25 23:31:08 +0900 UI 개선: 헤더 간소화, 리스크 카드 레이아웃 변경, 문구 개선
- 2026-03-26 01:05:54 +0900 OG 메타 추가, 타이틀 변경(타코알리미), Truth Social 제거, 푸터 정리
- 2026-03-26 01:30:23 +0900 OG 설명 간결화, 레벨별 설명 도움말 버튼 추가
- 2026-03-26 08:32:45 +0900 OG 이미지 변경, Vercel Analytics 추가, 방문자 카운터 표시, 푸터 수정
- 2026-03-26 08:36:27 +0900 fix: Redis 환경변수 다중 패턴 대응
- 2026-03-26 08:37:47 +0900 fix: ignoreCommand 제거 — Git 자동 배포 복구
- 2026-03-26 09:03:09 +0900 UI: 레벨 도움말을 풍선 팝오버로 변경
- 2026-03-26 09:06:27 +0900 fix: 팝오버 잘림 수정 — overflow-hidden 제거
- 2026-03-26 09:11:12 +0900 UI: 레벨 상관없이 전체 이미지 랜덤 표시
- 2026-03-27 07:30:48 +0900 UI: 애드센스 추가 및 레벨 팝오버에 점수 범위 표시
- 2026-03-27 07:41:23 +0900 SEO: sitemap.xml 및 robots.txt 추가
- 2026-03-27 07:42:42 +0900 SEO: Google Search Console 인증 파일 추가 및 도메인 수정
- 2026-03-27 07:51:29 +0900 SEO: 메타 태그 보강 및 이미지 최적화
- 2026-03-27 07:52:46 +0900 SEO: 메타 설명을 TACO 컨셉에 맞게 수정
- 2026-03-27 08:01:00 +0900 UI: 다크 모드 + 공유 버튼 추가
- 2026-03-27 08:22:05 +0900 feat: Push 알림 + 공유 버튼 이동 + 차트 Y축 조정
- 2026-03-27 08:24:51 +0900 fix: Cron 주기를 하루 1회로 변경 (Hobby 플랜 제한)
- 2026-03-27 14:06:31 +0900 feat: 공유 문구를 바이럴용으로 변경
- 2026-03-27 14:07:51 +0900 fix: 사용하지 않는 label prop 제거 (빌드 에러 수정)
- 2026-03-27 15:21:50 +0900 feat: S&P→E-mini 선물(ES=F) 변경 + VIX 공포지수 추가 + 이미지 업데이트
- 2026-03-27 15:26:13 +0900 fix: 모바일에서 레벨 기준 모달 짤림 수정
- 2026-03-27 17:33:34 +0900 feat: 토스 스타일 UI 리디자인
- 2026-03-27 17:44:46 +0900 feat: 알림 버튼 항상 표시 + 미지원 환경 안내 모달
- 2026-03-27 18:06:19 +0900 fix: 관세→이란-미국 전쟁 맥락으로 설명 전체 수정
- 2026-03-27 18:12:13 +0900 fix: 문구를 TACO 일반 개념(시장 압박→후퇴)으로 재수정
- 2026-03-29 23:05:08 +0900 security: CORS 제한, 에러 메시지 제거, 보안 헤더 등 일괄 보안 강화
- 2026-03-30 00:58:52 +0900 feat: 트럼프 이미지 print3~print10 추가
- 2026-03-30 01:13:27 +0900 feat: 히스토리 차트를 6개 지표 타코지수로 통일 + 라이브 점수 표시
- 2026-03-30 09:48:47 +0900 fix: 애드센스 승인을 위한 ads.txt 추가 및 크롤러용 정적 콘텐츠 삽입
- 2026-03-30 12:35:40 +0900 feat: 홈 위젯 기능 추가 (PWA + iOS Scriptable + Widget API)
- 2026-03-30 12:38:31 +0900 Revert "feat: 홈 위젯 기능 추가 (PWA + iOS Scriptable + Widget API)"
- 2026-03-30 12:39:17 +0900 feat: 공유 버튼 아래 알림 설정 CTA 배너 추가
- 2026-03-30 12:40:40 +0900 fix: 크론 주기를 하루 1회 → 매시간으로 변경
- 2026-03-30 12:43:33 +0900 fix: 알림 CTA를 VAPID 키 없어도 항상 표시
- 2026-03-30 12:49:39 +0900 fix: iOS 알림 안내 문구에 공유 아이콘(⬆) 설명 추가
- 2026-03-30 12:51:36 +0900 fix: 알림 CTA 배너를 메인 콘텐츠 최상단으로 이동
- 2026-03-30 13:30:28 +0900 feat: 한국어/영어 i18n 전체 구현
- 2026-03-30 13:32:44 +0900 fix: RiskCard 설명 텍스트를 API 응답 대신 t()로 번역 적용
- 2026-03-30 13:37:00 +0900 feat: 해외 SEO 최적화 — 영어 메타태그, JSON-LD, hreflang
- 2026-03-30 13:38:52 +0900 fix: SEO 맥락을 관세→미국-이란 강경책으로 수정
- 2026-03-30 15:58:26 +0900 fix: Oil label Brent → WTI 통일 및 영어 번역 수정

## 파일 구조
- .env.example
- .gitignore
- api/cron/check-level.py
- api/history.py
- api/indicators.py
- api/pageviews.py
- api/push-subscribe.py
- api/risk-level.py
- api/truths.py
- api/_shared.py
- backend/.env.example
- backend/app/db/database.py
- backend/app/db/__init__.py
- backend/app/main.py
- backend/app/models/schemas.py
- backend/app/models/__init__.py
- backend/app/routers/history.py
- backend/app/routers/indicators.py
- backend/app/routers/risk.py
- backend/app/routers/__init__.py
- backend/app/services/approval_scraper.py
- backend/app/services/data_collector.py
- backend/app/services/fred_fetcher.py
- backend/app/services/score_engine.py
- backend/app/services/yahoo_fetcher.py
- backend/app/services/__init__.py
- backend/app/websocket/handler.py
- backend/app/websocket/__init__.py
- backend/app/__init__.py
- backend/requirements.txt
- frontend/.gitignore
- frontend/eslint.config.js
- frontend/index.html
- frontend/package-lock.json
- frontend/package.json
- frontend/public/ads.txt
- frontend/public/favicon.svg
- frontend/public/google0d45b24a5af1c8f1.html
- frontend/public/icons.svg
- frontend/public/level1_1.png
- frontend/public/level1_2.png
- frontend/public/level2_2.png
- frontend/public/level3_1.png
- frontend/public/level3_2.png
- frontend/public/level4_1.png
- frontend/public/level4_2.png
- frontend/public/og.png
- frontend/public/print1.png
- frontend/public/print10.png
- frontend/public/print2.png
- frontend/public/print3.png
- frontend/public/print4.png
- frontend/public/print5.png
- frontend/public/print6.png
- frontend/public/print7.png
- frontend/public/print8.png
- frontend/public/print9.png
- frontend/public/robots.txt
- frontend/public/sitemap.xml
- frontend/public/sw.js
- frontend/README.md
- frontend/src/App.tsx
- frontend/src/assets/hero.png
- frontend/src/assets/react.svg
- frontend/src/assets/vite.svg
- frontend/src/components/ExtendedIndicators.tsx
- frontend/src/components/Footer.tsx
- frontend/src/components/GaugeBar.tsx
- frontend/src/components/Header.tsx
- frontend/src/components/HistoryTimeline.tsx
- frontend/src/components/IndicatorCard.tsx
- frontend/src/components/IndicatorGrid.tsx
- frontend/src/components/NotificationCTA.tsx
- frontend/src/components/RiskCard.tsx
- frontend/src/components/ShareButton.tsx
- frontend/src/components/TruthFeed.tsx
- frontend/src/hooks/useIndicators.ts
- frontend/src/hooks/usePageViews.ts
- frontend/src/hooks/useTruths.ts
- frontend/src/hooks/useWebSocket.ts
- frontend/src/i18n/en.ts
- frontend/src/i18n/index.ts
- frontend/src/i18n/ko.ts
- frontend/src/index.css
- frontend/src/main.tsx
- frontend/src/utils/constants.ts
- frontend/src/utils/indicatorDescriptions.ts
- frontend/src/utils/riskCalculator.ts
- frontend/tsconfig.app.json
- frontend/tsconfig.json
- frontend/tsconfig.node.json
- frontend/vite.config.ts
- google0d45b24a5af1c8f1.html
- package-lock.json
- package.json
- requirements.txt
- scripts/generate-vapid.py
- vercel.json

## vercel.json
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": null,
  "functions": {
    "api/truths.py": { "maxDuration": 60 }
  },
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" }
  ],
  "crons": [
    { "path": "/api/cron/check-level", "schedule": "0 * * * *" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ]
}
```

## backend/app/main.py
```python
import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

from app.db.database import init_db
from app.routers import indicators, risk, history
from app.websocket.handler import router as ws_router
from app.services.data_collector import collect_all_data


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    await init_db()
    # 데이터 수집을 백그라운드로 → 서버가 즉시 요청을 받을 수 있도록
    asyncio.create_task(collect_all_data())
    scheduler.add_job(collect_all_data, "interval", minutes=1, id="data_collector")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="TACO Dashboard API",
    description="Trump Administration Policy Change Odds Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tacotrump.space", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(indicators.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": "TACO Dashboard API", "version": "1.0.0"}
```

## backend/app/services/score_engine.py
```python
"""
TACO 점수 산정 엔진
핵심 6개 지표로 0~6점 산출 → 위험도 레벨 1~4 결정
(Vercel 배포 버전과 동기화)
"""

from app.models.schemas import RiskLevel

# 레드라인 기준값 (safe: 이 값 이하면 0점, value: 이 값 이상이면 1점)
REDLINES = {
    "sp500":           {"value": -15.0, "direction": "below", "safe": -3.0,  "label": "E-mini S&P 선물 고점 대비 하락률(%)"},
    "vix":             {"value": 35.0,  "direction": "above", "safe": 15.0,  "label": "VIX 공포지수"},
    "treasury_10y":    {"value": 4.5,   "direction": "above", "safe": 4.0,   "label": "미국 10년물 국채금리(%)"},
    "oil":             {"value": 100.0, "direction": "above", "safe": 75.0,  "label": "유가 (WTI, $/배럴)"},
    "dollar_index":    {"value": 110.0, "direction": "above", "safe": 97.0,  "label": "달러 인덱스"},
    "approval_rating": {"value": 35.0,  "direction": "below", "safe": 50.0,  "label": "대통령 지지율(%)"},
}

# 확장 지표 레드라인
EXTENDED_REDLINES = {
    "gasoline": {"value": 4.0, "direction": "above", "label": "전국 평균 휘발유 ($/갤런)"},
    "treasury_30y": {"value": 5.5, "direction": "above", "label": "미국 30년물 국채금리(%)"},
    "russell2000": {"value": -25.0, "direction": "below", "label": "Russell 2000 고점 대비 하락률(%)"},
}

CORE_KEYS = ["sp500", "vix", "treasury_10y", "oil", "dollar_index", "approval_rating"]


def calculate_indicator_score(key: str, value: float) -> float:
    """개별 지표의 레드라인 근접도를 0~1점으로 산출"""
    redline_info = REDLINES.get(key) or EXTENDED_REDLINES.get(key)
    if not redline_info:
        return 0.0

    rl = redline_info["value"]
    direction = redline_info["direction"]
    safe = redline_info.get("safe", 0.0)

    if direction == "above":
        if value <= safe:
            return 0.0
        if value >= rl:
            return 1.0
        return (value - safe) / (rl - safe)
    else:
        # below: S&P 500 (safe=-3, rl=-15) / 지지율 (safe=50, rl=35)
        if value >= safe:
            return 0.0
        if value <= rl:
            return 1.0
        return (safe - value) / (safe - rl)


def calculate_total_score(indicators: dict[str, float]) -> float:
    """핵심 6개 지표의 총점 산출 (0~6점)"""
    score = 0.0
    for key in CORE_KEYS:
        if key in indicators:
            score += calculate_indicator_score(key, indicators[key])
    return round(score, 2)


def get_risk_level(total_score: float) -> dict:
    """총점 → 위험도 레벨 결정 (max = 6.0)"""
    if total_score < 1.8:
        return {
            "level": RiskLevel.LEVEL_1,
            "label": "안전",
            "color": "#16A34A",
            "description": "시장 안정. 트럼프 자신감 충전 중. 강경 기조 유지 확률 높음.",
        }
    elif total_score < 3.0:
        return {
            "level": RiskLevel.LEVEL_2,
            "label": "주의",
            "color": "#FFC84C",
            "description": "시장이 흔들리기 시작. 추가 에스컬레이션 가능성.",
        }
    elif total_score < 4.2:
        return {
            "level": RiskLevel.LEVEL_3,
            "label": "경고",
            "color": "#F58737",
            "description": "시장 압박 거세지는 중. 슬슬 물러날 준비.",
        }
    else:
        return {
            "level": RiskLevel.LEVEL_4,
            "label": "위험",
            "color": "#F04452",
            "description": "시장 패닉. 트럼프 후퇴(타코) 임박.",
        }
```

## backend/app/services/data_collector.py
```python
"""통합 데이터 수집 서비스"""

import logging
from datetime import datetime

import aiosqlite

from app.db.database import DB_PATH
from app.services.yahoo_fetcher import fetch_yahoo_data, get_fallback_data
from app.services.fred_fetcher import fetch_gasoline_price
from app.services.approval_scraper import fetch_approval_rating
from app.services.score_engine import calculate_total_score, get_risk_level
from app.websocket.handler import broadcast

logger = logging.getLogger(__name__)

# 메모리 캐시
_latest_data: dict = {}
_last_updated: str = ""


def get_cached_data() -> tuple[dict, str]:
    return _latest_data, _last_updated


async def collect_all_data():
    """모든 데이터 소스에서 수집 후 DB 저장 + 브로드캐스트"""
    global _latest_data, _last_updated

    logger.info("Collecting data...")

    # Yahoo Finance 데이터 (스레드에서 실행)
    yahoo_data = {}
    try:
        yahoo_data = await fetch_yahoo_data()
    except Exception as e:
        logger.error(f"Yahoo fetch failed: {e}")

    # 데이터가 비었으면 fallback 사용
    if not yahoo_data:
        logger.warning("Using fallback market data")
        yahoo_data = get_fallback_data()

    # FRED 데이터
    try:
        gasoline = await fetch_gasoline_price()
    except Exception as e:
        logger.error(f"FRED fetch failed: {e}")
        gasoline = {"value": 3.45, "prev_value": 3.42}

    # 지지율 데이터
    try:
        approval = await fetch_approval_rating()
    except Exception as e:
        logger.error(f"Approval fetch failed: {e}")
        approval = {"value": 42.5, "prev_value": 43.0}

    # 통합
    all_data = {**yahoo_data}
    all_data["gasoline"] = gasoline
    all_data["approval_rating"] = approval

    # 핵심 지표로 점수 산출
    core_values = {}
    for key in ["sp500", "vix", "treasury_10y", "oil", "dollar_index"]:
        if key in all_data:
            core_values[key] = all_data[key]["value"]

    total_score = calculate_total_score(core_values)
    risk_info = get_risk_level(total_score)

    now = datetime.now().isoformat()

    # 캐시 업데이트 (DB 저장 전에 먼저 업데이트 — API가 바로 응답할 수 있도록)
    _latest_data = all_data
    _latest_data["_total_score"] = total_score
    _latest_data["_risk"] = risk_info
    _last_updated = now

    # DB 저장
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """INSERT INTO indicator_history
                   (timestamp, sp500, treasury_10y, oil, dollar_index,
                    gasoline, treasury_30y, russell2000, approval_rating,
                    total_score, risk_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    now,
                    all_data.get("sp500", {}).get("value"),
                    all_data.get("treasury_10y", {}).get("value"),
                    all_data.get("oil", {}).get("value"),
                    all_data.get("dollar_index", {}).get("value"),
                    all_data.get("gasoline", {}).get("value"),
                    all_data.get("treasury_30y", {}).get("value"),
                    all_data.get("russell2000", {}).get("value"),
                    all_data.get("approval_rating", {}).get("value"),
                    total_score,
                    risk_info["level"],
                ),
            )

            for key, data in all_data.items():
                if key.startswith("_"):
                    continue
                await db.execute(
                    """INSERT OR REPLACE INTO latest_indicators (key, value, prev_value, updated_at)
                       VALUES (?, ?, ?, ?)""",
                    (key, data["value"], data.get("prev_value"), now),
                )

            await db.commit()
    except Exception as e:
        logger.error(f"DB save error: {e}")

    # WebSocket 브로드캐스트
    try:
        await broadcast({
            "type": "update",
            "total_score": total_score,
            "risk_level": risk_info["level"],
            "timestamp": now,
        })
    except Exception as e:
        logger.error(f"Broadcast error: {e}")

    logger.info(f"Data collected. Score: {total_score}, Level: {risk_info['level']}")
```

## api/risk-level.py
```python
"""GET /api/risk-level — 종합 위험도 반환"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import BaseHTTPRequestHandler
import json
import asyncio
from _shared import fetch_all, send_cors_headers, send_error


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data, total, risk = asyncio.run(fetch_all())

            body = json.dumps({
                "total_score": total,
                "max_score": 6.0,
                "level": risk["level"],
                "label": risk["label"],
                "color": risk["color"],
                "description": risk["description"],
            }, ensure_ascii=False)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            send_cors_headers(self)
            self.send_header("Cache-Control", "s-maxage=30, stale-while-revalidate=60")
            self.end_headers()
            self.wfile.write(body.encode())
        except Exception:
            send_error(self)
```

## api/cron/check-level.py
```python
"""Vercel Cron Job — 5분마다 레벨 변화 감지 후 Push 알림 발송"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from http.server import BaseHTTPRequestHandler
import json
import asyncio
import redis as redis_lib
from pywebpush import webpush, WebPushException
from _shared import fetch_all

REDIS_URL = os.environ.get("REDIS_URL", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:admin@tacotrump.space")
CRON_SECRET = os.environ.get("CRON_SECRET", "")

PUSH_SUBS_KEY = "push_subs"
LAST_LEVEL_KEY = "push_last_level"

LEVEL_LABELS = {
    1: {"ko": "안전", "en": "Safe"},
    2: {"ko": "주의", "en": "Caution"},
    3: {"ko": "경고", "en": "Warning"},
    4: {"ko": "위험", "en": "Danger"},
}


def get_redis():
    return redis_lib.from_url(REDIS_URL, decode_responses=True)


def send_push(sub_json: str, payload: dict):
    """단일 구독에 push 발송. 410이면 삭제 대상 반환."""
    try:
        sub = json.loads(sub_json)
        webpush(
            subscription_info=sub,
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return None
    except WebPushException as e:
        if e.response and e.response.status_code == 410:
            return sub_json  # expired subscription
        return None
    except Exception:
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Verify CRON_SECRET
        if CRON_SECRET:
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {CRON_SECRET}":
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return

        try:
            r = get_redis()

            # 1) 현재 레벨 계산
            _data, _total, risk = asyncio.run(fetch_all())
            current_level = risk["level"]

            # 2) 이전 레벨 조회
            prev_raw = r.get(LAST_LEVEL_KEY)
            prev_level = int(prev_raw) if prev_raw else None

            # 3) 레벨 변경 시 push 발송
            sent = 0
            if prev_level is not None and current_level != prev_level:
                subs = r.smembers(PUSH_SUBS_KEY) or set()
                label = LEVEL_LABELS.get(current_level, {"ko": "", "en": ""})
                payload = {
                    "title": {
                        "ko": f"타코 레벨 변경! Lv.{current_level} {label['ko']}",
                        "en": f"TACO Level Changed! Lv.{current_level} {label['en']}",
                    },
                    "body": {
                        "ko": f"Lv.{prev_level} → Lv.{current_level} 으로 변경되었습니다.",
                        "en": f"Changed from Lv.{prev_level} to Lv.{current_level}.",
                    },
                }

                expired = []
                for sub_str in subs:
                    result = send_push(sub_str, payload)
                    if result:
                        expired.append(result)
                    else:
                        sent += 1

                # 만료된 구독 제거
                for exp in expired:
                    r.srem(PUSH_SUBS_KEY, exp)

            # 4) 현재 레벨 저장
            r.set(LAST_LEVEL_KEY, str(current_level))

            body = json.dumps({
                "level": current_level,
                "prev_level": prev_level,
                "changed": prev_level is not None and current_level != prev_level,
                "sent": sent,
            })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        except Exception:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
```

## api/truths.py
```python
"""GET /api/truths — 트럼프 Truth Social 최신 글 + OpenAI 한국어 번역"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import BaseHTTPRequestHandler
import json
import re
import defusedxml.ElementTree as ET
import httpx
from _shared import send_cors_headers

RSS_URL = "https://www.trumpstruth.org/feed"


def strip_html(html: str) -> str:
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>[^<]*</a>', r' \1', html)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&quot;', '"')
    return text.strip()


def fetch_truths(limit=10):
    try:
        r = httpx.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=8.0, follow_redirects=True)
        if r.status_code != 200:
            return []

        root = ET.fromstring(r.text)
        items = root.findall('.//item')

        posts = []
        for item in items[:limit]:
            title = item.findtext('title', '').strip()
            desc = item.findtext('description', '').strip()
            link = item.findtext('link', '').strip()
            pub_date = item.findtext('pubDate', '').strip()

            original_url = ''
            for child in item:
                if 'originalUrl' in child.tag:
                    original_url = (child.text or '').strip()

            content = strip_html(desc) if desc else title

            posts.append({
                "content": content,
                "title": title,
                "link": original_url or link,
                "published_at": pub_date,
            })

        return posts
    except Exception:
        return []


def translate_posts(posts):
    """OpenAI API로 게시글 일괄 번역"""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key or not posts:
        return posts

    # 번역할 텍스트를 번호 매겨서 하나의 프롬프트로 묶기 (API 호출 최소화)
    numbered = []
    for i, p in enumerate(posts):
        text = p["content"][:300]  # 너무 긴 글 제한
        if text:
            numbered.append(f"[{i}] {text}")

    if not numbered:
        return posts

    batch_text = "\n".join(numbered)

    try:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "트럼프의 Truth Social 게시글을 한국어 뉴스 헤드라인으로 요약해주세요. "
                            "각 게시글은 [번호]로 시작합니다. 결과도 동일한 [번호] 형식으로 출력하세요. "
                            "각 게시글을 15자~30자 내외의 짧은 한줄 헤드라인으로 요약하세요. "
                            "URL은 출력하지 마세요. 핵심 내용만 담아주세요."
                        ),
                    },
                    {"role": "user", "content": batch_text},
                ],
                "temperature": 0.3,
                "max_tokens": 3000,
            },
            timeout=25.0,
        )

        if resp.status_code != 200:
            return posts

        result_text = resp.json()["choices"][0]["message"]["content"]

        # [번호] 패턴으로 파싱
        translations = {}
        for m in re.finditer(r'\[(\d+)\]\s*(.+?)(?=\n\[|\Z)', result_text, re.DOTALL):
            idx = int(m.group(1))
            translations[idx] = m.group(2).strip()

        # 번역 결과 매핑
        for i, p in enumerate(posts):
            if i in translations:
                p["translated"] = translations[i]

    except Exception:
        pass

    return posts


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        posts = fetch_truths()
        posts = translate_posts(posts)
        body = json.dumps(posts, ensure_ascii=False)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        send_cors_headers(self)
        self.send_header("Cache-Control", "s-maxage=120, stale-while-revalidate=300")
        self.end_headers()
        self.wfile.write(body.encode())
```

## backend/requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
apscheduler==3.10.4
websockets==13.0
pydantic==2.9.2
aiosqlite==0.20.0
httpx==0.27.2
python-dotenv==1.0.1

## frontend/package.json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vercel/analytics": "^2.0.1",
    "lucide-react": "^1.6.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "recharts": "^3.8.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.4",
    "@tailwindcss/vite": "^4.2.2",
    "@types/node": "^24.12.0",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^9.39.4",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.4.0",
    "tailwindcss": "^4.2.2",
    "typescript": "~5.9.3",
    "typescript-eslint": "^8.57.0",
    "vite": "^8.0.1"
  }
}
