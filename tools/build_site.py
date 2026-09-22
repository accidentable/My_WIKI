"""위키를 면접 준비용 한 장짜리 사이트(site/index.html)로 만든다.

구조: 홈(프로젝트 목록) → 프로젝트 페이지(기술 스택·이유, 고민, 예상 질문, 배운 개념)
      → 개념 페이지(확인 질문 카드). 그래프는 보조.
- project 문서의 `## 면접 준비`(규칙 12절), concept 문서의 `## 학습`(11절)을 파싱한다
- 이해도 기록은 브라우저(localStorage), JSON 내보내기·가져오기
- 결과는 파일 하나. 더블클릭으로 열리고 Vercel/Pages에 그대로 올라간다

사용: python tools/build_site.py   →  site/index.html
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
OUT = ROOT / "site" / "index.html"
FOLDERS = ["projects", "concepts", "lessons"]
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
REPO_URL = "https://github.com/accidentable/My_WIKI/blob/main/"


# ---------------- 공통 파서 ----------------

def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:].lstrip("\n")


def parse_list(v: str) -> list[str]:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def index_groups() -> tuple[dict[str, str], dict[str, str]]:
    summaries: dict[str, str] = {}
    groups: dict[str, str] = {}
    idx = WIKI / "index.md"
    if not idx.exists():
        return summaries, groups
    section, sub = "", ""
    for line in idx.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section, sub = line[3:].strip(), ""
        elif line.startswith("### "):
            sub = line[4:].strip()
        m = re.match(r"- \[\[([^\]]+)\]\]\s*[—-]\s*(.+)", line)
        if m:
            summaries[m.group(1)] = m.group(2).strip()
            groups[m.group(1)] = sub or section
    return summaries, groups


def cut_section(body: str, heading: str) -> tuple[str, dict[str, str] | None]:
    """`## heading` 절을 떼어 {소제목: 내용} 으로 돌려준다."""
    m = re.search(rf"^## {re.escape(heading)}\s*$", body, flags=re.M)
    if not m:
        return body, None
    main, sec = body[:m.start()].rstrip(), body[m.end():]
    nxt = re.search(r"^## (?!#)", sec, flags=re.M)
    tail = ""
    if nxt:
        tail, sec = sec[nxt.start():], sec[:nxt.start()]
    parts: dict[str, str] = {}
    cur = None
    for line in sec.splitlines():
        h = re.match(r"^### (.+)$", line)
        if h:
            cur = h.group(1).strip()
            parts[cur] = ""
        elif cur:
            parts[cur] += line + "\n"
    return main + ("\n\n" + tail if tail else ""), parts


def bullets(text: str) -> list[str]:
    return [re.sub(r"^\s*[-*]\s*", "", l).strip() for l in text.splitlines() if re.match(r"^\s*[-*]\s+", l)]


def questions(text: str) -> list[dict]:
    out = []
    for block in re.split(r"^\s*\d+\.\s+", text, flags=re.M):
        if "**Q:**" not in block:
            continue

        def grab(label: str) -> str:
            mm = re.search(r"\*\*" + label + r":\*\*\s*(.*?)(?=\n\s*\*\*[^*]+:\*\*|\Z)", block, flags=re.S)
            return re.sub(r"\s*\n\s*", " ", mm.group(1)).strip() if mm else ""

        q = grab("Q")
        level = ""
        lv = re.match(r"\((L[123])[^)]*\)\s*(.*)", q)
        if lv:
            level, q = lv.group(1), lv.group(2)
        out.append({"level": level, "q": q, "a": grab("A"), "tail": grab("꼬리"), "wrong": grab("틀리기 쉬운 답")})
    return out


def table(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows[1:] if rows else []  # 머리 행 제외


def parse_study(body: str) -> tuple[str, dict | None]:
    main, parts = cut_section(body, "학습")
    if parts is None:
        return body, None
    further = []
    for b in bullets(parts.get("더 파볼 것", "")):
        mm = re.match(r"\[([^\]]+)\]\(([^)]+)\)\s*[—-]?\s*(.*)", b)
        further.append({"title": mm.group(1), "url": mm.group(2), "note": mm.group(3)} if mm else {"title": b, "url": "", "note": ""})
    return main, {
        "cs": bullets(parts.get("CS 주제", "")),
        "explain": bullets(parts.get("설명할 수 있어야 하는 것", "")),
        "questions": questions(parts.get("확인 질문", "")),
        "further": further,
    }



def parse_arch(text: str) -> dict:
    """14절 형식: '- [층] 이름 :: 기술, 기술 :: 호스팅' / '- A -> B :: 라벨'"""
    nodes, edges, note = [], [], ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        if line.startswith("("):
            note = line.strip("()")
            continue
        if "->" in line and not line.startswith("["):
            left, _, label = line.partition("::")
            a, _, b = left.partition("->")
            edges.append({"from": a.strip(), "to": b.strip(), "label": label.strip()})
            continue
        m = re.match(r"\[(\w+)\]\s*(.+)", line)
        if not m:
            continue
        layer, rest = m.group(1).lower(), m.group(2)
        parts = [x.strip() for x in rest.split("::")]
        name = parts[0]
        tech = [t.strip() for t in re.split(r"[,，]", parts[1])] if len(parts) > 1 and parts[1] else []
        host = parts[2] if len(parts) > 2 else ""
        nodes.append({"layer": layer, "name": name, "tech": [t for t in tech if t], "host": host})
    names = {n["name"] for n in nodes}
    edges = [e for e in edges if e["from"] in names and e["to"] in names]
    return {"nodes": nodes, "edges": edges, "note": note}

def parse_interview(body: str) -> tuple[str, dict | None]:
    main, parts = cut_section(body, "면접 준비")
    if parts is None:
        return body, None
    intro = " ".join(l.strip() for l in parts.get("한 문장 소개", "").splitlines() if l.strip() and not l.strip().startswith("("))
    stack = []
    for row in table(parts.get("기술 스택과 선택 이유", "")):
        row = (row + ["", "", "", ""])[:4]
        stack.append({"tech": row[0], "role": row[1], "why": row[2], "alt": row[3]})
    arch = parse_arch(parts.get("아키텍처", ""))
    return main, {
        "intro": intro,
        "stack": stack,
        "arch": arch if arch["nodes"] else None,
        "concerns": bullets(parts.get("고민한 점", "")),
        "questions": questions(parts.get("예상 질문", "")),
        "honest": bullets(parts.get("솔직하게 말할 것", "")),
    }


def build() -> dict:
    summaries, groups = index_groups()
    docs: dict[str, dict] = {}
    for folder in FOLDERS:
        for p in sorted((WIKI / folder).glob("*.md")):
            fm, body = frontmatter(p.read_text(encoding="utf-8"))
            docs[p.stem] = {"folder": folder, "fm": fm, "body": body}
    ids = set(docs)
    nodes, links = [], []
    for stem, d in docs.items():
        fm, body = d["fm"], d["body"]
        outgoing = sorted({l for l in LINK_RE.findall(body) if l in ids and l != stem})
        typ = fm.get("type", d["folder"][:-1])
        study = interview = None
        if typ == "concept":
            body, study = parse_study(body)
        elif typ == "project":
            body, interview = parse_interview(body)
        nodes.append({
            "id": stem, "type": typ,
            "title": fm.get("title", stem),
            "summary": summaries.get(stem, ""),
            "group": groups.get(stem, ""),
            "tags": parse_list(fm.get("tags", "")),
            "cs_topics": parse_list(fm.get("cs_topics", "")),
            "created": fm.get("created", ""), "updated": fm.get("updated", ""),
            "repo": fm.get("repo", ""),
            "url": f"{REPO_URL}wiki/{d['folder']}/{stem}.md",
            "body": body, "study": study, "interview": interview,
        })
        for t in outgoing:
            links.append({"source": stem, "target": t})
    seen, uniq = set(), []
    for l in links:
        key = tuple(sorted((l["source"], l["target"])))
        if key not in seen:
            seen.add(key)
            uniq.append(l)
    return {"nodes": nodes, "links": uniq, "built": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}


# ---------------- 페이지 ----------------

TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>해커톤 면접 노트</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Manrope:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#ffffff; --ink:#202124; --muted:#666666; --line:#e5e5e5; --soft:#f7f7f8; --head:#2b2f3a;
  --accent:#5b5bd6; --accent-bg:#eeeefc;
  --know:#1a7f37; --half:#b7791f; --dunno:#c0392b;
  --project:#5b5bd6; --concept:#1baf7a; --lesson:#eb6834;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{margin:0;background:var(--bg);color:var(--ink)}
body{font:15px/1.8 "Noto Sans KR",-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
button{font:inherit;cursor:pointer;color:inherit}
:focus-visible{outline:2px solid #555;outline-offset:2px}
.wrap{max-width:1000px;margin:0 auto;padding:0 20px}
.num,.meta,.badge,.tabbar a,.kv dt{font-family:"Manrope","Noto Sans KR",sans-serif}

header.top{border-bottom:1px solid var(--line);background:#fff}
header.top .wrap{display:flex;align-items:center;gap:20px;height:60px}
.brand{font-weight:700;font-size:16px;letter-spacing:-.01em}
.brand small{font-weight:400;color:var(--muted);margin-left:10px;font-size:12px}
.top .sp{flex:1}
.top nav a{font-size:14px;color:var(--muted);margin-left:18px;padding:10px 0;display:inline-block}
.top nav a:hover,.top nav a.on{color:var(--ink);text-decoration:underline;text-underline-offset:6px}
.top input{padding:9px 12px;border:1px solid var(--line);border-radius:8px;width:200px;font:inherit;font-size:14px}
main{padding:32px 0 96px}

.page-title{font-size:24px;font-weight:700;letter-spacing:-.02em;margin:0 0 6px}
.page-sub{color:var(--muted);margin:0 0 28px;font-size:14px}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.filters button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:8px 16px;font-size:13px;color:var(--muted)}
.filters button[aria-pressed="true"]{border-color:var(--ink);color:var(--ink)}
.pgroup{margin:26px 0 6px}
.ghead{font-size:15px;font-weight:700;margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:baseline}
.ghead .n{color:var(--muted);font-weight:500;font-size:12px;font-family:"Manrope",sans-serif}
.list{display:grid;gap:8px}
.item{display:grid;grid-template-columns:72px 1fr;gap:16px;border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:#fff;align-items:center}
.item:hover{border-color:var(--ink)}
.thumb{border-radius:8px;height:56px;display:flex;align-items:center;justify-content:center;text-align:center;padding:6px;color:#fff;font-family:"Manrope","Noto Sans KR",sans-serif;font-weight:700;font-size:11px;line-height:1.25;background:linear-gradient(135deg,var(--c1),var(--c2));overflow:hidden}
.item h3{margin:0 0 4px;font-size:15.5px;font-weight:700;letter-spacing:-.01em;line-height:1.4}
.item .row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.item .when{font-family:"Manrope",sans-serif;font-size:12px;color:var(--muted);margin-right:4px}
.item p{margin:0 0 10px;color:var(--muted);font-size:13.5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.kv{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:0;font-size:13px}
.kv dt{color:var(--muted);font-weight:500}
.kv dd{margin:0}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:6px;background:var(--accent-bg);color:var(--accent);vertical-align:1px;margin-left:8px}
.badge.gray{background:var(--soft);color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:6px;padding:3px 10px;font-size:12px;color:var(--ink);background:#fff;min-height:28px}
.chip.link:hover{border-color:var(--ink)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
.st{width:9px;height:9px;border-radius:2px;display:inline-block;flex:none;background:var(--line)}
.st.know{background:var(--know)}.st.half{background:var(--half)}.st.dunno{background:var(--dunno)}
.prog{display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted);margin-top:8px}
.bar{flex:1;max-width:160px;height:5px;border-radius:3px;background:var(--soft);overflow:hidden}
.bar i{display:block;height:100%;background:var(--ink)}

.hero{border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-bottom:22px;background:#fff}
.banner{padding:34px 28px;color:#fff;background:linear-gradient(120deg,var(--c1),var(--c2));min-height:150px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px}
.banner .kind{font-family:"Manrope",sans-serif;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.85}
.banner h1{margin:0;font-size:26px;line-height:1.35;font-weight:700;letter-spacing:-.02em}
.hero .info{padding:20px 28px;display:grid;grid-template-columns:1fr auto;gap:14px 28px;align-items:center}
.hero .kv{font-size:14px;gap:6px 18px}
.hero .actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
.btn{border:1px solid var(--ink);border-radius:10px;padding:10px 18px;font-size:14px;font-weight:500;background:#fff;min-height:44px;display:inline-flex;align-items:center}
.btn.primary{background:var(--ink);color:#fff}
.btn:hover{opacity:.85}
.intro{padding:18px 28px;border-top:1px solid var(--line);font-size:15.5px;line-height:1.85}

.tabbar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:2px solid var(--line);margin:0 0 8px;display:flex;overflow:auto}
.tabbar a{flex:none;padding:14px 18px;font-size:14px;font-weight:700;color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-2px;white-space:nowrap}
.tabbar a.on{color:var(--ink);border-bottom-color:var(--ink)}
section.sec{padding:34px 0 10px;scroll-margin-top:60px}
section.sec h2{font-size:18px;font-weight:700;margin:0 0 6px;letter-spacing:-.01em;display:flex;align-items:baseline;gap:8px}
section.sec h2 .num{color:var(--accent)}
section.sec .desc{color:var(--muted);font-size:13.5px;margin:0 0 16px}
section.sec + section.sec{border-top:1px solid var(--line)}
.hint{font-size:13px;color:var(--muted);background:var(--soft);border-radius:8px;padding:10px 14px;margin:12px 0 0}

table.t{width:100%;border-collapse:collapse;font-size:14px;table-layout:fixed}
table.t th{background:var(--head);color:#fff;font-weight:500;text-align:left;padding:11px 14px;font-size:13px}
table.t th:first-child{border-radius:8px 0 0 0} table.t th:last-child{border-radius:0 8px 0 0}
table.t td{padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink);word-break:keep-all;overflow-wrap:anywhere;line-height:1.7}
table.t td:first-child{font-weight:700}
table.t code{font-size:12.5px;background:var(--soft);padding:0 4px;border-radius:4px;word-break:break-all}
.missing{color:var(--muted);font-style:italic}
.missing b{color:var(--dunno);font-style:normal;font-weight:500}

ol.plain,ul.plain{margin:0;padding:0;list-style:none;display:grid;gap:0}
ul.plain li,ol.plain li{padding:14px 4px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:32px 1fr;gap:10px;line-height:1.8}
ol.plain li:last-child,ul.plain li:last-child{border-bottom:0}
.plain .n{font-family:"Manrope",sans-serif;font-weight:700;color:var(--accent)}

.qlist{display:grid;gap:10px}
.q{border:1px solid var(--line);border-radius:12px;overflow:hidden}
.q .qh{display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:start;padding:16px 18px;cursor:pointer;background:#fff;min-height:44px}
.q .qh:hover{background:var(--soft)}
.q .lv{font-family:"Manrope",sans-serif;font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-bg);border-radius:6px;padding:2px 8px;margin-top:4px}
.q .qt{font-weight:500;line-height:1.7}
.q .tg{font-size:12px;color:var(--muted);margin-top:4px;white-space:nowrap}
.q .qa{display:none;padding:4px 18px 18px 18px;border-top:1px solid var(--line);background:#fff}
.q.open .qa{display:block}
.q.open .tg::after{content:" ▲"} .q .tg::after{content:" ▼"}
.q .qa .lbl{display:block;font-family:"Manrope",sans-serif;font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin:14px 0 4px}
.q .qa p{margin:0;color:var(--ink);line-height:1.8}
.q .qa .wrong{color:var(--dunno)}
.rate{display:flex;gap:10px;align-items:center;flex-wrap:wrap;border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-top:18px;background:var(--soft)}
.rate span{font-size:14px;font-weight:500;margin-right:auto}
.rate button{border:1px solid var(--line);border-radius:8px;background:#fff;padding:10px 16px;font-size:13px;color:var(--muted);min-height:44px}
.rate button[aria-pressed="true"]{color:#fff;border-color:transparent}
.rate button[aria-pressed="true"].know{background:var(--know)}
.rate button[aria-pressed="true"].half{background:var(--half)}
.rate button[aria-pressed="true"].dunno{background:var(--dunno)}

.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
.ccard{border:1px solid var(--line);border-radius:12px;padding:16px 18px;display:block}
.ccard:hover{border-color:var(--ink)}
.ccard .t{font-weight:700;display:flex;gap:8px;align-items:center;line-height:1.4}
.ccard .s{font-size:13px;color:var(--muted);margin-top:6px;line-height:1.6}
.ccard .m{font-size:12px;color:var(--muted);margin-top:8px;font-family:"Manrope","Noto Sans KR",sans-serif}

details.raw{margin-top:30px;border-top:1px solid var(--line);padding-top:16px}
details.raw summary{cursor:pointer;color:var(--muted);font-size:13px;padding:8px 0}
.md{font-size:14.5px;color:var(--ink);line-height:1.85}
.md h1,.md h2,.md h3{line-height:1.4;margin:26px 0 8px;font-weight:700}
.md h1{font-size:18px}.md h2{font-size:16px}.md h3{font-size:15px}
.md code{background:var(--soft);border-radius:4px;padding:0 4px;font-size:12.5px}
.md pre{background:var(--soft);border-radius:8px;padding:12px;overflow:auto;font-size:12.5px}
.md table{border-collapse:collapse;font-size:13px;margin:8px 0;display:block;overflow:auto}
.md th,.md td{border:1px solid var(--line);padding:5px 9px;text-align:left;vertical-align:top}
.md th{background:var(--soft)}
.md blockquote{border-left:3px solid var(--line);margin:8px 0;padding:2px 12px;color:var(--muted)}
.md a.wiki{color:var(--accent);text-decoration:underline;text-underline-offset:3px}


/* 기술 필터 */
.techbar{display:flex;flex-wrap:wrap;gap:6px;margin:-8px 0 22px}
.techbar button{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:#fff;border-radius:8px;padding:5px 10px;font-size:12px;color:var(--muted);min-height:32px}
.techbar button img{width:14px;height:14px}
.techbar button[aria-pressed="true"]{border-color:var(--ink);color:var(--ink);background:var(--soft)}
.techbar .more{color:var(--muted);border-style:dashed}
/* 탭 패널 */
section.sec{display:none;padding:26px 0 10px}
section.sec.on{display:block}
section.sec + section.sec{border-top:0}
.secnav{display:flex;justify-content:space-between;gap:10px;margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}
.secnav a{font-size:13px;color:var(--muted);padding:10px 0;display:inline-flex;align-items:center;gap:6px}
.secnav a:hover{color:var(--ink)}
/* 아키텍처 */
.arch{position:relative;border:1px solid var(--line);border-radius:12px;padding:18px 18px 10px;background:#fff;overflow:auto}
.arch svg.wires{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.arch .layer{display:grid;grid-template-columns:88px 1fr;gap:14px;align-items:center;padding:10px 0;position:relative;z-index:1}
.arch .layer + .layer{border-top:1px dashed var(--line)}
.arch .lname{font-family:"Manrope",sans-serif;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.arch .boxes{display:flex;flex-wrap:wrap;gap:12px}
.arch .box{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:#fff;min-width:170px;max-width:260px;position:relative;z-index:1}
.arch .box .bn{font-weight:700;font-size:14px;display:flex;align-items:center;gap:8px;line-height:1.3}
.arch .box .bn img{width:18px;height:18px;flex:none}
.arch .box .bn .ini{width:18px;height:18px;border-radius:4px;background:var(--soft);color:var(--muted);font-size:10px;display:inline-flex;align-items:center;justify-content:center;font-family:"Manrope",sans-serif;font-weight:700;flex:none}
.arch .box .bt{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.arch .box .bt span{font-size:11px;border:1px solid var(--line);border-radius:5px;padding:0 6px;color:var(--ink);display:inline-flex;align-items:center;gap:4px}
.arch .box .bt img{width:11px;height:11px}
.arch .box .bh{font-size:11px;color:var(--muted);margin-top:6px;font-family:"Manrope","Noto Sans KR",sans-serif}
.arch .box .bh.none{font-style:italic}
.arch .note{font-size:12px;color:var(--muted);margin:0 0 8px}
.edgelist{margin:10px 0 0;padding:0;list-style:none;font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 18px}
.edgelist li b{color:var(--ink);font-weight:500}
.hostrow{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}
.hostrow .chip img{width:13px;height:13px}
footer{border-top:1px solid var(--line);padding:18px 0;color:var(--muted);font-size:12px}
footer .wrap{display:flex;gap:16px;flex-wrap:wrap;align-items:center}
footer button{border:0;background:none;text-decoration:underline;padding:8px 0;font-size:12px;color:var(--muted)}
footer .sp{flex:1}
#graphbox{height:70vh;position:relative;border:1px solid var(--line);border-radius:14px;overflow:hidden}
svg{width:100%;height:100%;display:block;cursor:grab}
.link{stroke:var(--line);stroke-width:1.2px}.link.hi{stroke:var(--muted);stroke-width:2px}
.node circle{stroke:#fff;stroke-width:2px;cursor:pointer}
.node.dim{opacity:.15}.link.dim{opacity:.08}
.node text{font-size:11px;fill:var(--muted);pointer-events:none;paint-order:stroke;stroke:#fff;stroke-width:3px}
.node.minor text{display:none}.node.hi text,.node.sel text{display:block;fill:var(--ink);font-weight:700}
.node.sel circle{stroke:var(--ink);stroke-width:3px}
#tip{position:absolute;pointer-events:none;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 10px;max-width:300px;font-size:12px;color:var(--muted);display:none}
@media (prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }
@media (max-width:820px){ .brand small{display:none} header.top .wrap{gap:12px} }
@media (max-width:720px){
  .item{grid-template-columns:56px 1fr;gap:12px} .thumb{height:48px;font-size:10px}
  .hero .info{grid-template-columns:1fr} .hero .actions{justify-content:flex-start}
  .banner{padding:26px 20px} .banner h1{font-size:21px}
  .intro,.hero .info{padding-left:20px;padding-right:20px}
  .top input{width:130px} .top nav a{margin-left:12px}
  table.t th:nth-child(2),table.t td:nth-child(2){display:none}
}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="#/">해커톤 면접 노트<small>해커톤에서 배운 것을 면접 언어로</small></a>
  <span class="sp"></span>
  <input type="search" id="q" placeholder="프로젝트·기술 검색" aria-label="검색">
  <nav><a href="#/" data-nav="home">프로젝트</a><a href="#/graph" data-nav="graph">관계도</a></nav>
</div></header>
<main><div class="wrap" id="app"></div></main>
<footer><div class="wrap">
  <span>이해도 기록은 이 브라우저에 저장됩니다.</span>
  <button id="export">내보내기</button><button id="import">가져오기</button>
  <input type="file" id="importFile" accept="application/json" hidden>
  <span class="sp"></span><span>생성 __BUILT__</span>
</div></footer>

<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const byId = new Map(DATA.nodes.map(n => [n.id, n]));
const nb = new Map(DATA.nodes.map(n => [n.id, new Set()]));
DATA.links.forEach(l => { nb.get(l.source).add(l.target); nb.get(l.target).add(l.source); });
const projects = DATA.nodes.filter(n => n.type === 'project').sort((a,b) => (b.created||'').localeCompare(a.created||''));
const conceptsOf = pid => [...nb.get(pid)].map(x => byId.get(x)).filter(n => n && n.type !== 'project').sort((a,b)=>a.type.localeCompare(b.type)||a.title.localeCompare(b.title));
const projectsOf = id => [...nb.get(id)].map(x => byId.get(x)).filter(n => n && n.type === 'project');
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const STATE = {know:'설명 가능', half:'애매함', dunno:'모름'};
const KIND = {project:'프로젝트', concept:'개념', lesson:'교훈'};
const PALETTES = [['#3b4a8a','#6b7cc7'],['#2f6f5e','#5fb59b'],['#7a3e6a','#b76aa3'],['#3f5f7a','#6f9bc0'],['#7a5a2f','#c09a5f'],['#4a3f7a','#8a7ac7'],['#2f6a7a','#5fb0c0'],['#6a3f3f','#b07070']];
const pal = id => PALETTES[[...id].reduce((s,c)=>s+c.charCodeAt(0),0) % PALETTES.length];
function md(t){ const w=String(t??'').replace(/\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]/g,(m,id)=>byId.has(id)?`<a class="wiki" href="#/${byId.get(id).type==='project'?'p':'c'}/${id}">${esc(byId.get(id).title)}</a>`:esc(id)); if(window.marked){marked.setOptions({gfm:true});return marked.parse(w);} return `<pre style="white-space:pre-wrap">${esc(t)}</pre>`; }
const inline = t => md(t).replace(/^<p>|<\/p>\s*$/g,'');
const shortTitle = t => t.split(/\s[—-]\s/)[0];
function overview(body){ const parts=body.split(/\n(?=## )/); const first=parts.find(x=>/^## .*개요/.test(x)) || parts[1]; if(first) return first.replace(/^## [^\n]*\n?/,''); return body.replace(/^# [^\n]*\n?/,'').slice(0,600); }


// ---- 기술 로고 (Simple Icons CDN, 없으면 글자 배지) ----
const ICON_ALIAS = {'next.js':'nextdotjs','nextjs':'nextdotjs','next':'nextdotjs','node.js':'nodedotjs','node':'nodedotjs','three.js':'threedotjs','threejs':'threedotjs','tailwind css':'tailwindcss','tailwind':'tailwindcss','amazon web services':'amazonwebservices','aws':'amazonwebservices','aws lambda':'awslambda','lambda':'awslambda','api gateway':'amazonapigateway','amazon api gateway':'amazonapigateway','postgres':'postgresql','postgresql':'postgresql','sqlite':'sqlite','hyperclova x':'naver','hyperclova':'naver','hcx-005':'naver','clova':'naver','네이버':'naver','naver cloud':'naver','ncloud':'naver','openai':'openai','gpt':'openai','chatgpt':'openai','claude':'claude','claude code':'claude','anthropic':'anthropic','codex':'openai','react native':'react','expo':'expo','solidity':'solidity','ethereum':'ethereum','base sepolia':'ethereum','sepolia':'ethereum','erc-20':'ethereum','sui':'sui','move':'sui','walrus':'walrus','telegram':'telegram','python':'python','fastapi':'fastapi','docker':'docker','vercel':'vercel','supabase':'supabase','prisma':'prisma','redis':'redis','upstash':'upstash','github':'github','ubuntu':'ubuntu','linux':'linux','langgraph':'langgraph','langchain':'langchain','typescript':'typescript','javascript':'javascript','react':'react','vite':'vite','express':'express','mediapipe':'google','google trends':'google','구글 트렌드':'google','cloudflare':'cloudflare','vercel cron':'vercel','pandas':'pandas','numpy':'numpy','matplotlib':'python','pytorch':'pytorch','huggingface':'huggingface','chroma':'chromadb','chromadb':'chromadb','assemblyai':'assemblyai','trigger.dev':'triggerdotdev','systemd':'linux','apscheduler':'python','webrtc':'webrtc','pwa':'pwa','service worker':'pwa','web push':'pwa','dart':'opendart','opendart':'opendart','sqlite fts5':'sqlite','fts5':'sqlite','parquet':'apacheparquet','csv':'googlesheets'};
function iconSlug(tech){ let t=String(tech||'').replace(/`/g,'').toLowerCase().trim(); if(!t) return null; if(ICON_ALIAS[t]) return ICON_ALIAS[t]; const first=t.split(/[\s(·,/+]/)[0]; if(ICON_ALIAS[first]) return ICON_ALIAS[first]; for(const k in ICON_ALIAS){ if(t.startsWith(k+' ')||t.startsWith(k+'(')) return ICON_ALIAS[k]; } if(/^[a-z0-9.]+$/.test(first)) return first.replace(/\.js$/,'dotjs').replace(/[^a-z0-9]/g,''); return null; }
function iconImg(tech, size){ const slug=iconSlug(tech); const ini=`<span class="ini" title="${esc(tech)}">${esc(String(tech).replace(/`/g,'').trim().slice(0,2).toUpperCase())}</span>`; if(!slug) return ini; return `<img src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/${slug}.svg" alt="" width="${size||18}" height="${size||18}" loading="lazy" onerror="this.outerHTML=${JSON.stringify(ini).replace(/"/g,'&quot;')}">`; }
// ---- 기술 필터 ----
let techFilter = null; let techMore = false;
function techStats(){ const cnt=new Map(); projects.forEach(p=>{ new Set(techNames(p).map(shortTech)).forEach(t=>cnt.set(t,(cnt.get(t)||0)+1)); }); return [...cnt.entries()].filter(([t,c])=>c>=1).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])); }
function shortTech(t){ t=t.replace(/`/g,'').trim(); const m=t.match(/^(Next\.js|React Native|React|Vite|TypeScript|Python|FastAPI|SQLite|PostgreSQL|Redis|Docker|Vercel|Supabase|Prisma|Solidity|Sui|Move|Walrus|Seal|Telegram|OpenAI|Claude|HyperCLOVA X|LangGraph|Express|Expo|Three\.js|MediaPipe|pandas|numpy|AWS|Trigger\.dev|AssemblyAI|Tailwind CSS|Node\.js|Web Push|SD-JWT|JWE|DID|VC|ERC-20|Chroma|APScheduler|systemd|Upstash|KIS API|한국투자증권 OpenAPI|네이버 데이터랩|구글 트렌드|빅카인즈|DART)/i); return m? m[1] : t.split(/[\s(·,/+]/)[0]; }
const KEY='wiki-progress-v1'; let progress={};
try{progress=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(progress))}catch(e){}};
const stateOf=id=>(progress[id]||{}).state||'';
const setState=(id,st)=>{progress[id]={state:st,at:new Date().toISOString().slice(0,10)};save();};
document.getElementById('export').onclick=()=>{const b=new Blob([JSON.stringify(progress,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='wiki-progress.json';a.click();};
document.getElementById('import').onclick=()=>document.getElementById('importFile').click();
document.getElementById('importFile').onchange=e=>{const f=e.target.files[0];if(!f)return;f.text().then(t=>{try{Object.assign(progress,JSON.parse(t));save();route();}catch(err){alert('JSON을 읽지 못했습니다')}});};
function readiness(p){ const cs=conceptsOf(p.id).filter(c=>c.type==='concept'); const items=[...cs.map(c=>stateOf(c.id)), stateOf('p:'+p.id)]; const w={know:1,half:.5,dunno:0,'':0}; return {pct:Math.round(items.reduce((s,x)=>s+w[x],0)/items.length*100), known:cs.filter(c=>stateOf(c.id)==='know').length, total:cs.length}; }

const app=document.getElementById('app');
const q=document.getElementById('q'); q.addEventListener('input',()=>{ if(location.hash.startsWith('#/graph')) paintGraph(); else if(!location.hash||location.hash==='#/') home(); });
const query=()=>q.value.trim().toLowerCase();
const matches=n=>{const s=query(); if(!s) return true; return (n.title+' '+n.summary+' '+n.tags.join(' ')+' '+n.cs_topics.join(' ')+' '+(n.interview?n.interview.stack.map(x=>x.tech).join(' '):'')).toLowerCase().includes(s);};
window.addEventListener('hashchange',route);
let filter='all';
function route(){ const h=location.hash||'#/'; window.scrollTo(0,0);
  document.querySelectorAll('.top nav a').forEach(a=>a.classList.toggle('on', a.dataset.nav==='graph'?h.startsWith('#/graph'):!h.startsWith('#/graph')));
  let m; if((m=h.match(/^#\/p\/([^\/]+)(?:\/(\d+))?$/))) return project(decodeURIComponent(m[1]), +(m[2]||1));
  if((m=h.match(/^#\/c\/([^\/]+)(?:\/(\d+))?$/))) return concept(decodeURIComponent(m[1]), +(m[2]||1));
  if(h.startsWith('#/graph')) return graph();
  home(); }

// 기술 문자열 정리: 괄호·경로 제거, 구분자로 쪼개 짧은 이름만
function techNames(p){ if(!p.interview) return []; const out=[]; for(const s of p.interview.stack){ let t=s.tech.replace(/`/g,'').replace(/\([^)]*\)/g,'').replace(/\[[^\]]*\]/g,''); for(let x of t.split(/[·,+/]|\s{2,}| \+ /)){ x=x.trim(); if(!x||x.length>24||/^(및|등)$/.test(x)) continue; if(!out.includes(x)) out.push(x); } } return out; }
const TECH_CATS = [
  ['블록체인·신원', /solidity|sui|move|walrus|seal|viem|ethers|erc|did|vc\b|jwt|jose|sepolia|온체인|체인|지갑|wallet/i],
  ['LLM·에이전트', /gpt|openai|claude|hyperclova|hcx|clova|langgraph|langchain|llm|assemblyai|embedding|bge|prompt|agent|에이전트|structured/i],
  ['데이터 분석', /pandas|numpy|parquet|통계|trend|트렌드|bigkinds|빅카인즈|datalab|데이터랩|csv|matplotlib|공공데이터|dart|공시|api 허브|지수/i],
  ['웹·앱', /next|react|vite|typescript|fastapi|express|vercel|expo|native|node|trigger|supabase|prisma|postgres|sqlite|redis|three|mediapipe|web|tailwind|python/i],
];
function primaryCat(p){ const names=techNames(p).join(' '); let best=['기타',0]; for(const [c,re] of TECH_CATS){ const n=(names.match(new RegExp(re.source,'gi'))||[]).length; if(n>best[1]) best=[c,n]; } return best[0]; }
function home(){
  const cs=DATA.nodes.filter(n=>n.type==='concept'); const known=cs.filter(c=>stateOf(c.id)==='know').length;
  const list=projects.filter(matches).filter(p=>filter==='all'||(filter==='ready'?readiness(p).pct>=70:readiness(p).pct<70)).filter(p=>!techFilter||techNames(p).map(shortTech).includes(techFilter));
  const stats=techStats(); const shown=techMore?stats:stats.slice(0,10);
  const order=[...TECH_CATS.map(x=>x[0]),'기타'];
  const groups=new Map(); list.forEach(p=>{const c=primaryCat(p); if(!groups.has(c)) groups.set(c,[]); groups.get(c).push(p);});
  app.innerHTML=`
    <h1 class="page-title">프로젝트</h1>
    <p class="page-sub">해커톤 ${projects.length}개 · 설명 가능한 개념 ${known}/${cs.length}</p>
    <div class="filters">
      <button data-f="all" aria-pressed="${filter==='all'}">전체</button>
      <button data-f="todo" aria-pressed="${filter==='todo'}">아직 준비 안 됨</button>
      <button data-f="ready" aria-pressed="${filter==='ready'}">준비도 70% 이상</button>
    </div>
    <div class="techbar" aria-label="기술 스택 필터">
      ${shown.map(([t,c])=>`<button data-t="${esc(t)}" aria-pressed="${techFilter===t}">${iconImg(t,14)}${esc(t)}<span style="color:var(--muted)">${c}</span></button>`).join('')}
      ${stats.length>10?`<button class="more" data-more="1">${techMore?'접기':`+${stats.length-10}`}</button>`:''}
    </div>
    ${order.filter(c=>groups.has(c)).map(c=>`
      <section class="pgroup"><h2 class="ghead">${esc(c)}<span class="n">${groups.get(c).length}</span></h2>
      <div class="list">${groups.get(c).map(p=>{const r=readiness(p); const [c1,c2]=pal(p.id); const tech=techNames(p).slice(0,4);
        return `<a class="item" href="#/p/${p.id}">
          <div class="thumb" style="--c1:${c1};--c2:${c2}">${esc(shortTitle(p.title)).slice(0,14)}</div>
          <div>
            <h3>${esc(p.title)}${r.pct>=70?'<span class="badge">준비됨</span>':''}</h3>
            <div class="row"><span class="when">${esc((p.created||'').slice(0,7))}</span>${tech.map(t=>`<span class="chip">${esc(t)}</span>`).join('')}${tech.length?'':'<span class="chip">면접 준비 절 없음</span>'}</div>
            <div class="prog"><div class="bar"><i style="width:${r.pct}%"></i></div><span>${r.pct}%</span></div>
          </div></a>`;}).join('')}</div></section>`).join('')}
    ${list.length?'':'<p class="page-sub">조건에 맞는 프로젝트가 없습니다.</p>'}`;
  app.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{filter=b.dataset.f;home();});
  app.querySelectorAll('.techbar button[data-t]').forEach(b=>b.onclick=()=>{techFilter=techFilter===b.dataset.t?null:b.dataset.t;home();});
  const mb=app.querySelector('.techbar .more'); if(mb) mb.onclick=()=>{techMore=!techMore;home();};
}

function qcards(list){ return `<div class="qlist">${list.map((x,i)=>`
  <div class="q">
    <div class="qh" role="button" tabindex="0" onclick="this.parentElement.classList.toggle('open')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();this.click();}"><span class="lv">${esc(x.level||'Q')}</span><span class="qt">${inline(x.q)}</span><span class="tg">답</span></div>
    <div class="qa"><span class="lbl">답</span><p>${inline(x.a)}</p>
      ${x.tail?`<span class="lbl">꼬리질문</span><p>${inline(x.tail)}</p>`:''}
      ${x.wrong?`<span class="lbl">틀리기 쉬운 답</span><p class="wrong">${inline(x.wrong)}</p>`:''}</div>
  </div>`).join('')}</div>`; }
function rateBox(key, label){ const st=stateOf(key); return `<div class="rate" data-key="${key}"><span>${label}</span>
  <button class="dunno" data-st="dunno" aria-pressed="${st==='dunno'}">모름</button>
  <button class="half" data-st="half" aria-pressed="${st==='half'}">애매함</button>
  <button class="know" data-st="know" aria-pressed="${st==='know'}">설명 가능</button></div>`; }
function bindRate(){ app.querySelectorAll('.rate button').forEach(b=>b.onclick=()=>{ const y=window.scrollY; const keep=curSec; setState(b.parentElement.dataset.key,b.dataset.st); const base=location.hash.replace(/\/\d+$/,''); history.replaceState(null,'',`${base}/${keep}`); route(); window.scrollTo(0,y); }); }
function sec(n, title, desc, body){ return `<section class="sec" id="s${n}" data-n="${n}"><h2><span class="num">${n}.</span>${esc(title)}</h2>${desc?`<p class="desc">${desc}</p>`:''}${body}</section>`; }
function tabbar(items){ return `<nav class="tabbar" id="tabbar" aria-label="절 이동">${items.map(([n,t])=>`<a href="#" data-s="${n}">${n}. ${esc(t)}</a>`).join('')}</nav>`; }
let curSec = 1;
function showSec(n, push){ const secs=[...app.querySelectorAll('section.sec')]; if(!secs.length) return; const ns=secs.map(x=>+x.dataset.n); if(!ns.includes(n)) n=ns[0]; curSec=n;
  secs.forEach(x=>x.classList.toggle('on', +x.dataset.n===n));
  app.querySelectorAll('#tabbar a').forEach(a=>a.classList.toggle('on', +a.dataset.s===n));
  const i=ns.indexOf(n); const prev=ns[i-1], next=ns[i+1]; const nav=app.querySelector('.secnav');
  if(nav){ const t=x=>app.querySelector(`#tabbar a[data-s="${x}"]`).textContent; nav.innerHTML=`<a href="#" data-go="${prev??''}" ${prev?'':'style="visibility:hidden"'}>← ${prev?t(prev):''}</a><a href="#" data-go="${next??''}" ${next?'':'style="visibility:hidden"'}>${next?t(next):''} →</a>`; nav.querySelectorAll('a').forEach(a=>a.onclick=e=>{e.preventDefault(); if(a.dataset.go) showSec(+a.dataset.go,true);}); }
  if(push){ const base=location.hash.replace(/\/\d+$/,''); history.replaceState(null,'',`${base}/${n}`); }
  const box=app.querySelector('.arch'); if(box && box.closest('section.sec').classList.contains('on')) requestAnimationFrame(drawWires);
  window.scrollTo({top: Math.min(window.scrollY, (app.querySelector('#tabbar')||app).offsetTop-8)});
}
function spy(initial){ app.querySelectorAll('#tabbar a').forEach(a=>a.onclick=e=>{e.preventDefault(); showSec(+a.dataset.s,true);}); if(!app.querySelector('.secnav')) app.insertAdjacentHTML('beforeend','<div class="secnav"></div>'); const raw=app.querySelector('details.raw'); if(raw) app.appendChild(raw); showSec(initial||1,false); }

// ---- 아키텍처 그림 ----
const LAYERS=[['client','클라이언트'],['edge','엣지·CDN'],['server','서버'],['worker','워커·배치'],['data','데이터'],['chain','체인'],['external','외부 서비스'],['ops','운영']];
function archHtml(a){ if(!a) return ''; const by=new Map(); a.nodes.forEach(n=>{ if(!by.has(n.layer)) by.set(n.layer,[]); by.get(n.layer).push(n); });
  const hosts=[...new Set(a.nodes.map(n=>n.host).filter(h=>h&&!/자료에 없음/.test(h)))];
  return `${a.note?`<p class="note">${esc(a.note)}</p>`:''}
  ${hosts.length?`<div class="hostrow"><span class="small" style="align-self:center;color:var(--muted)">호스팅</span>${hosts.map(h=>`<span class="chip">${iconImg(h,13)}${esc(h)}</span>`).join('')}</div>`:''}
  <div class="arch"><svg class="wires"></svg>
  ${LAYERS.filter(([k])=>by.has(k)).map(([k,label])=>`<div class="layer"><div class="lname">${label}</div><div class="boxes">${by.get(k).map(n=>`<div class="box" data-node="${esc(n.name)}"><div class="bn">${iconImg(n.tech[0]||n.name,18)}${esc(n.name)}</div>${n.tech.length?`<div class="bt">${n.tech.map(t=>`<span>${iconImg(t,11)}${esc(t)}</span>`).join('')}</div>`:''}<div class="bh ${/자료에 없음/.test(n.host)?'none':''}">${esc(n.host||'')}</div></div>`).join('')}</div></div>`).join('')}
  </div>
  ${a.edges.length?`<ul class="edgelist">${a.edges.map(e=>`<li><b>${esc(e.from)}</b> → <b>${esc(e.to)}</b>${e.label?` · ${esc(e.label)}`:''}</li>`).join('')}</ul>`:''}`; }
function drawWires(){ const box=app.querySelector('.arch'); if(!box) return; const svg=box.querySelector('svg.wires'); const a=window.__arch; if(!a||!svg) return;
  const r0=box.getBoundingClientRect(); const pos=name=>{ const el=box.querySelector(`.box[data-node="${CSS.escape(name)}"]`); if(!el) return null; const r=el.getBoundingClientRect(); return {x:r.left-r0.left+box.scrollLeft+r.width/2, top:r.top-r0.top+box.scrollTop, bottom:r.bottom-r0.top+box.scrollTop, left:r.left-r0.left+box.scrollLeft, right:r.right-r0.left+box.scrollLeft, cy:r.top-r0.top+box.scrollTop+r.height/2}; };
  svg.setAttribute('viewBox',`0 0 ${box.scrollWidth} ${box.scrollHeight}`); svg.style.width=box.scrollWidth+'px'; svg.style.height=box.scrollHeight+'px';
  let d='<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#9aa0a6"/></marker></defs>';
  a.edges.forEach(e=>{ const A=pos(e.from), B=pos(e.to); if(!A||!B) return; let x1,y1,x2,y2; if(Math.abs(A.cy-B.cy)<4){ x1=A.right; y1=A.cy; x2=B.left; y2=B.cy; if(A.left>B.left){x1=A.left;x2=B.right;} d+=`<path d="M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}" fill="none" stroke="#9aa0a6" stroke-width="1.5" marker-end="url(#arr)"/>`; } else { const down=A.cy<B.cy; x1=A.x; y1=down?A.bottom:A.top; x2=B.x; y2=down?B.top:B.bottom; d+=`<path d="M${x1},${y1} C${x1},${(y1+y2)/2} ${x2},${(y1+y2)/2} ${x2},${y2}" fill="none" stroke="#9aa0a6" stroke-width="1.5" marker-end="url(#arr)"/>`; } });
  svg.innerHTML=d; }
window.addEventListener('resize',()=>requestAnimationFrame(drawWires));

function project(id, initial){
  const p=byId.get(id); if(!p||p.type!=='project'){home();return;}
  const iv=p.interview; const cs=conceptsOf(id); const r=readiness(p); const [c1,c2]=pal(id);
  const tabs=iv?[[1,'개요'],[2,'기술 스택'],[3,'아키텍처'],[4,'고민한 점'],[5,'예상 질문'],[6,'솔직하게'],[7,'배운 개념']]:[[1,'개요'],[2,'배운 개념']]; window.__arch = iv? iv.arch : null;
  app.innerHTML=`
    <div class="hero">
      <div class="banner" style="--c1:${c1};--c2:${c2}"><div class="kind">Hackathon · ${esc(p.created||'')}</div><h1>${esc(p.title)}</h1></div>
      <div class="info">
        <dl class="kv">
          <dt>시기</dt><dd>${esc(p.created||'자료에 없음')}</dd>
          <dt>준비도</dt><dd>${r.pct}%<span class="badge ${r.pct>=70?'':'gray'}">${r.pct>=70?'준비됨':'준비 중'}</span> <span style="color:var(--muted);font-size:13px">개념 ${r.known}/${r.total} 설명 가능</span></dd>
          ${p.tags.length?`<dt>태그</dt><dd style="color:var(--muted)">${p.tags.map(t=>'#'+esc(t)).join(' ')}</dd>`:''}
        </dl>
        <div class="actions">${p.repo&&p.repo!=='없음'?`<a class="btn" href="${esc(p.repo)}" target="_blank" rel="noopener">코드 저장소</a>`:''}<a class="btn primary" href="${p.url}" target="_blank" rel="noopener">위키 원문</a></div>
      </div>
      ${iv&&iv.intro?`<div class="intro">${inline(iv.intro)}</div>`:''}
    </div>
    ${tabbar(tabs)}
    ${sec(1,'개요','무엇을 만들었고 어떻게 끝났는지, 30초 안에 말할 수 있을 만큼만 다시 읽어 봅니다.', `<div class="md">${md(overview(p.body))}</div>`)}
    ${iv?`
    ${sec(2,'기술 스택과 선택 이유','면접에서는 어떤 기술을 썼는지보다 왜 그것을 골랐는지를 묻게 됩니다. 비어 있는 칸은 원자료에 이유가 남아 있지 않아 비워 둔 자리이니, 기억나는 대로 직접 채워 넣으면 됩니다.',
      `<table class="t"><colgroup><col style="width:22%"><col style="width:16%"><col style="width:36%"><col style="width:26%"></colgroup><thead><tr><th>기술</th><th>역할</th><th>왜 이걸 썼나</th><th>대안과 포기한 것</th></tr></thead><tbody>
      ${iv.stack.map(s=>`<tr><td>${inline(s.tech)}</td><td>${inline(s.role)}</td><td>${/자료에 없음/.test(s.why)?`<span class="missing"><b>비어 있음</b> · 직접 채울 것</span>`:inline(s.why)}</td><td>${/자료에 없음/.test(s.alt)?`<span class="missing">${esc(s.alt)}</span>`:inline(s.alt)}</td></tr>`).join('')}
      </tbody></table>`)}
    ${sec(3,'아키텍처','어디에 무엇을 올렸고 서로 어떻게 연결되는지 그림으로 봅니다. 호스팅이 비어 있는 상자는 자료에 기록이 없어 남겨 둔 것입니다.', iv.arch? archHtml(iv.arch) : '<div class="hint">이 프로젝트에는 아직 아키텍처 절이 없습니다. 위키 문서의 면접 준비 절에 <code>### 아키텍처</code>를 채우면 여기에 그려집니다.</div>')}
    ${sec(4,'고민한 점','다른 선택지가 있었고 나름의 근거로 골랐다는 것을 보여 주는 부분입니다. 꼬리질문이 대개 여기서 이어지므로, 각 항목마다 왜 그렇게 정했는지 한 번씩 말해 보면 좋습니다.', `<ol class="plain">${iv.concerns.map((c,i)=>`<li><span class="n">${i+1}</span><div>${inline(c)}</div></li>`).join('')}</ol>`)}
    ${sec(5,'예상 질문','개념을 묻는 질문(L1)에서 시작해 왜 그렇게 했는지(L2), 어디서 깨지는지(L3)로 내려갑니다. 답을 펼치기 전에 먼저 소리 내어 답해 보고, 아래에서 스스로 평가해 두면 다음에 복습할 때 도움이 됩니다.', qcards(iv.questions)+rateBox('p:'+id,'이 프로젝트를 지금 5분 동안 설명할 수 있을까요'))}
    ${sec(6,'솔직하게 말할 것','AI 도구가 대신 짠 부분이나 검증하지 못한 주장은 부풀려 말하면 꼬리질문에서 드러나기 쉽습니다. 먼저 인정하고 거기서 무엇을 배웠는지로 이어 가는 편이 오히려 좋은 인상을 남긴다고 생각합니다.', `<ul class="plain">${iv.honest.map((c,i)=>`<li><span class="n">!</span><div>${inline(c)}</div></li>`).join('')}</ul>`)}
    ${sec(7,'이 프로젝트에서 배운 개념','이 프로젝트에서 처음 써 본 기술과 개념입니다. 각 페이지에 확인 질문이 있고, 설명할 수 있다고 표시한 개념이 늘수록 프로젝트 준비도가 함께 올라갑니다.', conceptGrid(cs))}
    `:`
    <div class="hint">이 프로젝트에는 아직 <b>면접 준비</b> 절이 없습니다. 위키 문서에 <code>## 면접 준비</code>를 채우면 기술 스택·고민·예상 질문이 여기에 표시됩니다.</div>
    ${sec(2,'이 프로젝트에서 배운 개념','', conceptGrid(cs))}`}
    <details class="raw"><summary>위키 문서 전문 보기</summary><div class="md">${md(p.body)}</div></details>`;
  bindRate(); spy(initial);
}
function conceptGrid(cs){ return cs.length?`<div class="cgrid">${cs.map(c=>`<a class="ccard" href="#/c/${c.id}">
  <div class="t"><span class="dot" style="background:var(--${c.type})"></span>${esc(c.title)}<span class="st ${stateOf(c.id)}" title="${STATE[stateOf(c.id)]||'기록 없음'}" style="margin-left:auto"></span></div>
  <div class="s">${esc(c.summary)}</div>
  <div class="m">${c.cs_topics.length?c.cs_topics.map(esc).join(' · ')+' · ':''}${c.study?c.study.questions.length+'문항':''}${c.type==='lesson'?'교훈':''}</div>
</a>`).join('')}</div>`:'<p class="page-sub">연결된 개념 문서가 없습니다.</p>'; }

function concept(id, initial){
  const c=byId.get(id); if(!c||c.type==='project'){home();return;}
  const s=c.study; const from=projectsOf(id); const back=from[0]; const [c1,c2]=pal(back?back.id:id);
  const tabs=s?[[1,'설명할 것'],[2,'바탕 CS'],[3,'확인 질문'],[4,'더 파볼 것']]:[[1,'본문']];
  app.innerHTML=`
    <div class="hero">
      <div class="banner" style="--c1:${c1};--c2:${c2}"><div class="kind">${KIND[c.type]}${c.group?' · '+esc(c.group):''}</div><h1>${esc(c.title)}</h1></div>
      <div class="info">
        <dl class="kv">
          ${from.length?`<dt>출처 프로젝트</dt><dd><div class="chips">${from.map(p=>`<a class="chip link" href="#/p/${p.id}"><span class="dot" style="background:var(--project)"></span>${esc(shortTitle(p.title))}</a>`).join('')}</div></dd>`:''}
          ${c.cs_topics.length?`<dt>CS 과목</dt><dd>${c.cs_topics.map(esc).join(' · ')}</dd>`:''}
          <dt>이해도</dt><dd>${STATE[stateOf(id)]||'기록 없음'}</dd>
        </dl>
        <div class="actions"><a class="btn primary" href="${c.url}" target="_blank" rel="noopener">위키 원문</a></div>
      </div>
      ${c.summary?`<div class="intro">${esc(c.summary)}</div>`:''}
    </div>
    ${tabbar(tabs)}
    ${s?`
    ${sec(1,'설명할 수 있어야 하는 것','아래 문장들을 자기 말로 풀어 설명할 수 있는지 먼저 확인해 봅니다.', `<ol class="plain">${s.explain.map((x,i)=>`<li><span class="n">${i+1}</span><div>${inline(x)}</div></li>`).join('')}</ol>`)}
    ${sec(2,'바탕이 되는 CS','이 개념이 어느 과목의 어느 부분과 이어지는지 적어 두었습니다. 교과서로 돌아가 볼 때 참고하면 됩니다.', `<ul class="plain">${s.cs.map(x=>`<li><span class="n">·</span><div>${esc(x)}</div></li>`).join('')}</ul>`)}
    ${sec(3,'확인 질문','답을 펼치기 전에 먼저 답해 보고, 아래에서 이해도를 표시해 두면 복습 순서를 정하는 데 씁니다.', qcards(s.questions)+rateBox(id,'이 개념을 면접에서 설명할 수 있을까요'))}
    ${sec(4,'더 파볼 것','작성할 때 직접 열어 내용을 확인한 자료만 골라 두었습니다.', s.further.length?`<ul class="plain">${s.further.map(f=>`<li><span class="n">→</span><div>${f.url?`<a href="${esc(f.url)}" target="_blank" rel="noopener" style="text-decoration:underline;text-underline-offset:3px">${esc(f.title)}</a>`:esc(f.title)}${f.note?`<div style="color:var(--muted);font-size:13px">${esc(f.note)}</div>`:''}</div></li>`).join('')}</ul>`:'<p class="page-sub">없음</p>')}
    <details class="raw"><summary>위키 문서 전문 보기</summary><div class="md">${md(c.body)}</div></details>
    `:sec(1,'본문','', `<div class="md">${md(c.body)}</div>`)}`;
  bindRate(); spy(initial);
}

let nodeSel=null, linkSel=null, selected=null;
function graph(){
  app.innerHTML=`<h1 class="page-title">문서 관계도</h1><p class="page-sub">프로젝트(보라)와 개념(초록), 교훈(주황)이 어떻게 이어져 있는지 보여 줍니다. 노드를 누르면 해당 페이지로 이동합니다.</p><div id="graphbox"><svg></svg><div id="tip"></div></div>`;
  const box=document.getElementById('graphbox'), svg=d3.select(box).select('svg'); const W=box.clientWidth,H=box.clientHeight;
  const degree=new Map(DATA.nodes.map(n=>[n.id,nb.get(n.id).size]));
  const nodes=DATA.nodes.map(n=>({id:n.id,type:n.type,title:n.title,summary:n.summary})); const links=DATA.links.map(l=>({source:l.source,target:l.target}));
  const g=svg.append('g'); const r=d=>5+Math.sqrt(degree.get(d.id))*3;
  linkSel=g.append('g').selectAll('line').data(links).join('line').attr('class','link');
  nodeSel=g.append('g').selectAll('g').data(nodes).join('g').attr('class',d=>'node'+(degree.get(d.id)<3?' minor':''))
    .call(d3.drag().clickDistance(6).on('start',(e,d)=>{d.fx=d.x;d.fy=d.y;}).on('drag',(e,d)=>{if(!e.active&&sim.alpha()<.1)sim.alphaTarget(.2).restart();d.fx=e.x;d.fy=e.y;}).on('end',(e,d)=>{sim.alphaTarget(0);d.fx=null;d.fy=null;}));
  nodeSel.append('circle').attr('r',r).attr('fill',d=>`var(--${d.type})`);
  nodeSel.append('text').attr('dy',d=>r(d)+12).attr('text-anchor','middle').text(d=>d.title.length>22?d.title.slice(0,21)+'…':d.title);
  const tip=box.querySelector('#tip');
  nodeSel.on('mouseenter',(e,d)=>{tip.style.display='block';tip.innerHTML=`<b>${esc(d.title)}</b><br>${esc(d.summary||KIND[d.type])}`;})
    .on('mousemove',e=>{const p=box.getBoundingClientRect();tip.style.left=(e.clientX-p.left+14)+'px';tip.style.top=(e.clientY-p.top+14)+'px';})
    .on('mouseleave',()=>tip.style.display='none')
    .on('click',(e,d)=>{e.stopPropagation(); selected=d.id; paintGraph(); setTimeout(()=>{location.hash=`#/${d.type==='project'?'p':'c'}/${d.id}`;},250);});
  svg.on('click',()=>{selected=null;paintGraph();});
  const sim=d3.forceSimulation(nodes).force('link',d3.forceLink(links).id(d=>d.id).distance(70).strength(.6)).force('charge',d3.forceManyBody().strength(-220)).force('center',d3.forceCenter(W/2,H/2)).force('collide',d3.forceCollide(d=>r(d)+12)).force('x',d3.forceX(W/2).strength(.06)).force('y',d3.forceY(H/2).strength(.08))
    .on('tick',()=>{linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);nodeSel.attr('transform',d=>`translate(${d.x},${d.y})`);});
  const zoom=d3.zoom().scaleExtent([.2,4]).on('zoom',e=>g.attr('transform',e.transform)); svg.call(zoom);
  let fitted=false; const w=setInterval(()=>{ if(!document.getElementById('graphbox')){clearInterval(w);return;} if(sim.alpha()<.03&&!fitted){fitted=true;clearInterval(w);const xs=nodes.map(n=>n.x),ys=nodes.map(n=>n.y);const x0=Math.min(...xs)-60,x1=Math.max(...xs)+60,y0=Math.min(...ys)-40,y1=Math.max(...ys)+40;const k=Math.max(.55,Math.min(1.5,.92/Math.max((x1-x0)/W,(y1-y0)/H)));svg.transition().duration(500).call(zoom.transform,d3.zoomIdentity.translate(W/2-k*(x0+x1)/2,H/2-k*(y0+y1)/2).scale(k));} },300);
  paintGraph();
}
function paintGraph(){ if(!nodeSel||!document.getElementById('graphbox'))return; const focus=selected?new Set([selected,...nb.get(selected)]):null;
  nodeSel.classed('dim',n=>!matches(byId.get(n.id))||(focus&&!focus.has(n.id))).classed('sel',n=>n.id===selected).classed('hi',n=>focus&&focus.has(n.id)&&n.id!==selected);
  linkSel.classed('dim',l=>!(matches(byId.get(l.source.id))&&matches(byId.get(l.target.id)))||(focus&&!(focus.has(l.source.id)&&focus.has(l.target.id)))).classed('hi',l=>focus&&(l.source.id===selected||l.target.id===selected)); }

route();
</script>
</body>
</html>
"""


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("<", "\\u003c"))
            .replace("__BUILT__", data["built"]))
    OUT.write_text(html, encoding="utf-8")
    ns = sum(1 for n in data["nodes"] if n["study"])
    ni = sum(1 for n in data["nodes"] if n["interview"])
    nq = sum(len(n["study"]["questions"]) for n in data["nodes"] if n["study"]) + sum(len(n["interview"]["questions"]) for n in data["nodes"] if n["interview"])
    print(f"{OUT.relative_to(ROOT)}: 문서 {len(data['nodes'])}, 링크 {len(data['links'])}, 학습 절 {ns}, 면접 준비 절 {ni}, 질문 {nq}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
