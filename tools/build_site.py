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


def parse_interview(body: str) -> tuple[str, dict | None]:
    main, parts = cut_section(body, "면접 준비")
    if parts is None:
        return body, None
    intro = " ".join(l.strip() for l in parts.get("한 문장 소개", "").splitlines() if l.strip() and not l.strip().startswith("("))
    stack = []
    for row in table(parts.get("기술 스택과 선택 이유", "")):
        row = (row + ["", "", "", ""])[:4]
        stack.append({"tech": row[0], "role": row[1], "why": row[2], "alt": row[3]})
    return main, {
        "intro": intro,
        "stack": stack,
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
<style>
:root{
  color-scheme:light;
  --bg:#f6f7f9; --card:#ffffff; --line:#e6e8ec; --soft:#f0f2f5;
  --ink:#111318; --ink-2:#4b5160; --mute:#8b92a1;
  --accent:#4f5df0; --accent-soft:#eef0ff;
  --know:#1f8f3a; --half:#d98a00; --dunno:#d7423a;
  --project:#4f5df0; --concept:#1baf7a; --lesson:#eb6834;
  --shadow:0 1px 2px rgba(16,24,40,.04), 0 8px 24px -12px rgba(16,24,40,.12);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#121417; --card:#1b1e23; --line:#2a2f37; --soft:#232830;
    --ink:#f2f4f7; --ink-2:#c2c8d2; --mute:#8a919e;
    --accent:#7c88ff; --accent-soft:#232a4d;
    --know:#3fae3f; --half:#e0a030; --dunno:#e66767;
    --project:#7c88ff; --concept:#2dbf8a; --lesson:#f07a4a;
    --shadow:none;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#121417; --card:#1b1e23; --line:#2a2f37; --soft:#232830;
  --ink:#f2f4f7; --ink-2:#c2c8d2; --mute:#8a919e;
  --accent:#7c88ff; --accent-soft:#232a4d;
  --know:#3fae3f; --half:#e0a030; --dunno:#e66767;
  --project:#7c88ff; --concept:#2dbf8a; --lesson:#f07a4a;
  --shadow:none;
}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,"Segoe UI","Pretendard","Noto Sans KR",sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
button{font:inherit;cursor:pointer}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}
header.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;gap:14px;height:56px}
.brand{font-weight:700;letter-spacing:-.01em;color:var(--ink)}
.brand small{font-weight:400;color:var(--mute);margin-left:8px;font-size:12px}
.top .sp{flex:1}
.top input{padding:7px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);width:220px}
.top a.gh{font-size:12px;color:var(--mute)}
main{padding:28px 0 80px}
h1{font-size:26px;letter-spacing:-.02em;margin:0 0 6px;line-height:1.3}
h2{font-size:18px;letter-spacing:-.01em;margin:36px 0 12px}
h2 .n{color:var(--mute);font-weight:500;font-size:13px;margin-left:8px}
.lead{color:var(--ink-2);margin:0 0 18px;font-size:16px}
.crumb{font-size:13px;color:var(--mute);margin-bottom:14px}
.crumb a{color:var(--mute)} .crumb a:hover{color:var(--ink)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.pcard{display:block;color:inherit;transition:transform .12s, border-color .12s}
.pcard:hover{transform:translateY(-1px);border-color:var(--accent)}
.pcard .when{font-size:12px;color:var(--mute)}
.pcard h3{margin:4px 0 6px;font-size:16px;line-height:1.35}
.pcard p{margin:0 0 12px;color:var(--ink-2);font-size:13px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12px;color:var(--ink-2);background:var(--soft)}
.chip.link{background:var(--card);cursor:pointer;color:var(--ink)} .chip.link:hover{border-color:var(--accent)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
.st{width:8px;height:8px;border-radius:2px;display:inline-block;flex:none;background:var(--line)}
.st.know{background:var(--know)} .st.half{background:var(--half)} .st.dunno{background:var(--dunno)}
.prog{display:flex;align-items:center;gap:10px;margin-top:12px;font-size:12px;color:var(--mute)}
.bar{flex:1;height:6px;border-radius:3px;background:var(--soft);overflow:hidden;display:flex}
.bar i{display:block;height:100%}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 26px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;min-width:140px}
.stat b{display:block;font-size:22px;font-weight:600;letter-spacing:-.02em}
.stat span{font-size:12px;color:var(--mute)}
.empty{color:var(--mute);font-size:13px;background:var(--soft);border-radius:10px;padding:12px 14px}
.hero{display:flex;gap:18px;align-items:flex-start;flex-wrap:wrap}
.hero .meta{font-size:13px;color:var(--mute);margin:6px 0 12px}
.hero .meta a{color:var(--ink-2)}
.hero .intro{font-size:16px;color:var(--ink);background:var(--accent-soft);border-radius:12px;padding:14px 16px;margin:14px 0 0;border-left:3px solid var(--accent)}
table.stack{width:100%;border-collapse:collapse;font-size:13.5px;table-layout:fixed}
table.stack col.c1{width:20%} table.stack col.c2{width:15%} table.stack col.c3{width:38%} table.stack col.c4{width:27%}
table.stack td,table.stack th{word-break:keep-all;overflow-wrap:anywhere}
table.stack code{font-size:12px;word-break:break-all}
table.stack th{text-align:left;font-weight:600;color:var(--mute);font-size:12px;padding:8px 10px;border-bottom:1px solid var(--line)}
table.stack td{padding:10px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink-2)}
table.stack td:first-child{color:var(--ink);font-weight:600}
table.stack tr:last-child td{border-bottom:0}
.tblwrap{overflow:auto}
.missing{color:var(--mute);font-style:italic}
ul.clean{margin:0;padding-left:0;list-style:none;display:grid;gap:10px}
ul.clean li{padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card);color:var(--ink-2)}
ul.clean li b,ul.clean li strong{color:var(--ink)}
.q{border:1px solid var(--line);border-radius:12px;background:var(--card);margin-bottom:10px;overflow:hidden}
.q .qh{display:flex;gap:10px;align-items:flex-start;padding:14px 16px;cursor:pointer}
.q .lv{flex:none;font-size:11px;font-weight:600;color:var(--accent);background:var(--accent-soft);border-radius:6px;padding:2px 7px;margin-top:3px}
.q .qt{flex:1;font-weight:500;line-height:1.5}
.q .tg{flex:none;color:var(--mute);font-size:12px;margin-top:3px}
.q .qa{display:none;padding:0 16px 16px 16px;color:var(--ink-2);font-size:14px}
.q.open .qa{display:block}
.q .qa .lbl{display:block;font-size:11px;color:var(--mute);letter-spacing:.05em;text-transform:uppercase;margin:12px 0 2px}
.q .qa p{margin:0}
.rate{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.rate span{font-size:13px;color:var(--ink-2);margin-right:4px}
.rate button{border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink-2);padding:7px 14px;font-size:13px}
.rate button[aria-pressed="true"].know{border-color:var(--know);color:var(--know);background:color-mix(in srgb,var(--know) 10%,transparent)}
.rate button[aria-pressed="true"].half{border-color:var(--half);color:var(--half);background:color-mix(in srgb,var(--half) 10%,transparent)}
.rate button[aria-pressed="true"].dunno{border-color:var(--dunno);color:var(--dunno);background:color-mix(in srgb,var(--dunno) 10%,transparent)}
.ccard{display:block;color:inherit;padding:14px 16px}
.ccard:hover{border-color:var(--accent)}
.ccard .t{font-weight:600;display:flex;gap:8px;align-items:center}
.ccard .s{font-size:13px;color:var(--ink-2);margin-top:4px}
.ccard .m{font-size:12px;color:var(--mute);margin-top:6px}
details.raw{margin-top:28px}
details.raw summary{cursor:pointer;color:var(--mute);font-size:13px}
.md{font-size:14.5px;color:var(--ink-2)}
.md h1,.md h2,.md h3{color:var(--ink);line-height:1.3;margin:22px 0 8px}
.md h1{font-size:18px}.md h2{font-size:16px}.md h3{font-size:15px}
.md code{background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:0 4px;font-size:12.5px}
.md pre{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;font-size:12.5px}
.md table{border-collapse:collapse;font-size:13px;margin:8px 0;display:block;overflow:auto}
.md th,.md td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
.md blockquote{border-left:3px solid var(--line);margin:8px 0;padding:2px 12px}
.md a.wiki{color:var(--accent);border-bottom:1px dotted currentColor}
footer{border-top:1px solid var(--line);padding:16px 0;color:var(--mute);font-size:12px}
footer .wrap{display:flex;gap:14px;flex-wrap:wrap;align-items:center}
footer button{border:0;background:none;color:var(--ink-2);text-decoration:underline;padding:0;font-size:12px}
footer .sp{flex:1}
#graphbox{height:70vh;position:relative;border:1px solid var(--line);border-radius:14px;background:var(--card);overflow:hidden}
svg{width:100%;height:100%;display:block;cursor:grab}
.link{stroke:var(--line);stroke-width:1.2px}.link.hi{stroke:var(--ink-2);stroke-width:2px}
.node circle{stroke:var(--card);stroke-width:2px;cursor:pointer}
.node.dim{opacity:.15}.link.dim{opacity:.08}
.node text{font-size:11px;fill:var(--ink-2);pointer-events:none;paint-order:stroke;stroke:var(--card);stroke-width:3px}
.node.minor text{display:none}.node.hi text,.node.sel text{display:block;fill:var(--ink);font-weight:600}
.node.sel circle{stroke:var(--ink);stroke-width:3px}
#tip{position:absolute;pointer-events:none;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;max-width:300px;font-size:12px;color:var(--ink-2);box-shadow:var(--shadow);display:none}
@media (max-width:640px){ .top input{width:140px} h1{font-size:22px} table.stack{font-size:12.5px} table.stack col.c2{width:0} table.stack td:nth-child(2),table.stack th:nth-child(2){display:none} }
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="#/">해커톤 면접 노트<small>프로젝트로 배우는 CS</small></a>
  <span class="sp"></span>
  <input type="search" id="q" placeholder="검색" aria-label="검색">
  <a class="gh" href="#/graph">관계도</a>
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
const conceptsOf = pid => [...nb.get(pid)].map(x => byId.get(x)).filter(n => n && n.type !== 'project').sort((a,b)=>a.type.localeCompare(b.type));
const projectsOf = id => [...nb.get(id)].map(x => byId.get(x)).filter(n => n && n.type === 'project');
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const STATE = {know:'설명 가능', half:'애매함', dunno:'모름'};
const KIND = {project:'프로젝트', concept:'개념', lesson:'교훈'};
function md(t){ const w=String(t??'').replace(/\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]/g,(m,id)=>byId.has(id)?`<a class="wiki" href="#/${byId.get(id).type==='project'?'p':'c'}/${id}">${esc(byId.get(id).title)}</a>`:esc(id)); if(window.marked){marked.setOptions({gfm:true});return marked.parse(w);} return `<pre style="white-space:pre-wrap">${esc(t)}</pre>`; }
const inline = t => md(t).replace(/^<p>|<\/p>\s*$/g,'');

// 이해도
const KEY='wiki-progress-v1'; let progress={};
try{progress=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(progress))}catch(e){}};
const stateOf=id=>(progress[id]||{}).state||'';
const setState=(id,st)=>{progress[id]={state:st,at:new Date().toISOString().slice(0,10)};save();};
document.getElementById('export').onclick=()=>{const b=new Blob([JSON.stringify(progress,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='wiki-progress.json';a.click();};
document.getElementById('import').onclick=()=>document.getElementById('importFile').click();
document.getElementById('importFile').onchange=e=>{const f=e.target.files[0];if(!f)return;f.text().then(t=>{try{Object.assign(progress,JSON.parse(t));save();route();}catch(err){alert('JSON을 읽지 못했습니다')}});};
function readiness(p){ const cs=conceptsOf(p.id).filter(c=>c.type==='concept'); const items=[...cs.map(c=>stateOf(c.id)), stateOf('p:'+p.id)]; const w={know:1,half:.5,dunno:0,'':0}; return {pct:Math.round(items.reduce((s,x)=>s+w[x],0)/items.length*100), known:cs.filter(c=>stateOf(c.id)==='know').length, total:cs.length}; }

// 라우팅
const app=document.getElementById('app');
const q=document.getElementById('q'); q.addEventListener('input',()=>{ if(location.hash.startsWith('#/graph')) paintGraph(); else if(!location.hash||location.hash==='#/') home(); });
const query=()=>q.value.trim().toLowerCase();
const matches=n=>{const s=query(); if(!s) return true; return (n.title+' '+n.summary+' '+n.tags.join(' ')+' '+n.cs_topics.join(' ')+' '+(n.interview?n.interview.stack.map(x=>x.tech).join(' '):'')).toLowerCase().includes(s);};
window.addEventListener('hashchange',route);
function route(){ const h=location.hash||'#/'; window.scrollTo(0,0);
  let m; if((m=h.match(/^#\/p\/(.+)$/))) return project(decodeURIComponent(m[1]));
  if((m=h.match(/^#\/c\/(.+)$/))) return concept(decodeURIComponent(m[1]));
  if(h.startsWith('#/graph')) return graph();
  home(); }

// 홈
function home(){
  const list=projects.filter(matches);
  const cs=DATA.nodes.filter(n=>n.type==='concept');
  const known=cs.filter(c=>stateOf(c.id)==='know').length;
  const nq=DATA.nodes.reduce((s,n)=>s+((n.study&&n.study.questions.length)||0)+((n.interview&&n.interview.questions.length)||0),0);
  app.innerHTML=`
    <h1>내가 한 해커톤, 면접에서 설명할 수 있나</h1>
    <p class="lead">프로젝트를 고르면 기술 스택을 왜 썼는지, 무엇을 고민했는지, 어떤 질문이 나올지 순서대로 보입니다.</p>
    <div class="stats">
      <div class="stat"><b>${projects.length}</b><span>프로젝트</span></div>
      <div class="stat"><b>${cs.length}</b><span>배운 개념</span></div>
      <div class="stat"><b>${nq}</b><span>예상 질문</span></div>
      <div class="stat"><b>${cs.length?Math.round(known/cs.length*100):0}%</b><span>설명 가능한 개념</span></div>
    </div>
    <div class="grid">${list.map(p=>{const r=readiness(p); const stack=(p.interview?p.interview.stack.map(s=>s.tech):[]).slice(0,5);
      return `<a class="card pcard" href="#/p/${p.id}">
        <div class="when">${esc((p.created||'').slice(0,7))}${p.interview?'':' · 면접 준비 절 없음'}</div>
        <h3>${esc(p.title)}</h3>
        <p>${esc(p.interview&&p.interview.intro||p.summary)}</p>
        <div class="chips">${stack.map(s=>`<span class="chip">${esc(s)}</span>`).join('')}</div>
        <div class="prog"><div class="bar"><i style="width:${r.pct}%;background:var(--know)"></i></div><span>준비도 ${r.pct}% · 개념 ${r.known}/${r.total}</span></div>
      </a>`;}).join('')}</div>
    ${list.length?'':'<div class="empty">검색 결과가 없습니다.</div>'}`;
}

// 질문 카드
function qcards(list, prefix){ return list.map((x,i)=>`
  <div class="q" id="${prefix}${i}">
    <div class="qh" onclick="this.parentElement.classList.toggle('open')"><span class="lv">${esc(x.level||'Q')}</span><span class="qt">${inline(x.q)}</span><span class="tg">답 보기</span></div>
    <div class="qa"><span class="lbl">답</span><p>${inline(x.a)}</p>
      ${x.tail?`<span class="lbl">꼬리질문</span><p>${inline(x.tail)}</p>`:''}
      ${x.wrong?`<span class="lbl">틀리기 쉬운 답</span><p>${inline(x.wrong)}</p>`:''}</div>
  </div>`).join(''); }
function rateBox(key, label){ const st=stateOf(key); return `<div class="card rate" data-key="${key}"><span>${label}</span>
  <button class="dunno" data-st="dunno" aria-pressed="${st==='dunno'}">모름</button>
  <button class="half" data-st="half" aria-pressed="${st==='half'}">애매함</button>
  <button class="know" data-st="know" aria-pressed="${st==='know'}">설명 가능</button></div>`; }
function bindRate(){ app.querySelectorAll('.rate button').forEach(b=>b.onclick=()=>{ setState(b.parentElement.dataset.key,b.dataset.st); route(); }); }

// 프로젝트
function project(id){
  const p=byId.get(id); if(!p||p.type!=='project'){home();return;}
  const iv=p.interview; const cs=conceptsOf(id); const r=readiness(p);
  app.innerHTML=`
    <div class="crumb"><a href="#/">프로젝트</a> › ${esc(p.title)}</div>
    <div class="hero"><div style="flex:1;min-width:260px">
      <h1>${esc(p.title)}</h1>
      <div class="meta">${esc(p.created||'')} · <a href="${p.url}" target="_blank" rel="noopener">위키 원문</a>${p.repo&&p.repo!=='없음'?` · <a href="${esc(p.repo)}" target="_blank" rel="noopener">코드 저장소</a>`:''}${p.tags.length?` · ${p.tags.map(t=>'#'+esc(t)).join(' ')}`:''}</div>
      <div class="prog"><div class="bar"><i style="width:${r.pct}%;background:var(--know)"></i></div><span>준비도 ${r.pct}%</span></div>
      ${iv&&iv.intro?`<div class="intro">${inline(iv.intro)}</div>`:`<p class="lead" style="margin-top:12px">${esc(p.summary)}</p>`}
    </div></div>
    ${iv?`
    <h2>기술 스택, 왜 썼나<span class="n">${iv.stack.length}</span></h2>
    <div class="card tblwrap"><table class="stack"><colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"></colgroup><thead><tr><th>기술</th><th>역할</th><th>왜 이걸 썼나</th><th>대안과 포기한 것</th></tr></thead><tbody>
      ${iv.stack.map(s=>`<tr><td>${inline(s.tech)}</td><td>${inline(s.role)}</td><td>${/자료에 없음/.test(s.why)?`<span class="missing">${esc(s.why)} — 직접 채울 것</span>`:inline(s.why)}</td><td>${inline(s.alt)}</td></tr>`).join('')}
    </tbody></table></div>
    <h2>고민한 점<span class="n">${iv.concerns.length}</span></h2>
    <ul class="clean">${iv.concerns.map(c=>`<li>${inline(c)}</li>`).join('')}</ul>
    <h2>예상 질문<span class="n">프로젝트 전체 ${iv.questions.length}</span></h2>
    ${qcards(iv.questions,'pq')}
    ${rateBox('p:'+id,'이 프로젝트, 지금 면접에서 5분 설명할 수 있나?')}
    ${iv.honest.length?`<h2>솔직하게 말할 것</h2><ul class="clean">${iv.honest.map(c=>`<li>${inline(c)}</li>`).join('')}</ul>`:''}
    `:`<div class="empty" style="margin-top:20px">이 프로젝트에는 아직 면접 준비 절이 없습니다. 위키 문서에 <code>## 면접 준비</code> 절을 채우면 여기에 표시됩니다.</div>`}
    <h2>이 프로젝트에서 배운 개념<span class="n">${cs.length}</span></h2>
    <div class="grid">${cs.map(c=>`<a class="card ccard" href="#/c/${c.id}">
      <div class="t"><span class="dot" style="background:var(--${c.type})"></span>${esc(c.title)}<span class="st ${stateOf(c.id)}" title="${STATE[stateOf(c.id)]||'기록 없음'}" style="margin-left:auto"></span></div>
      <div class="s">${esc(c.summary)}</div>
      <div class="m">${c.cs_topics.length?c.cs_topics.map(esc).join(' · ')+' · ':''}${c.study?c.study.questions.length+'문':''}${c.type==='lesson'?'교훈':''}</div>
    </a>`).join('')}</div>
    <details class="raw"><summary>위키 문서 전문 보기</summary><div class="md card" style="margin-top:10px">${md(p.body)}</div></details>`;
  bindRate();
}

// 개념
function concept(id){
  const c=byId.get(id); if(!c||c.type==='project'){home();return;}
  const s=c.study; const from=projectsOf(id); const st=stateOf(id);
  const back=from[0];
  app.innerHTML=`
    <div class="crumb"><a href="#/">프로젝트</a>${back?` › <a href="#/p/${back.id}">${esc(back.title)}</a>`:''} › ${esc(c.title)}</div>
    <h1>${esc(c.title)}</h1>
    <div class="hero"><div class="meta" style="margin:0 0 14px">${KIND[c.type]}${c.group?' · '+esc(c.group):''}${c.cs_topics.length?' · CS: '+c.cs_topics.map(esc).join(', '):''} · <a href="${c.url}" target="_blank" rel="noopener">위키 원문</a></div></div>
    ${from.length?`<div class="chips" style="margin-bottom:18px">${from.map(p=>`<a class="chip link" href="#/p/${p.id}"><span class="dot" style="background:var(--project)"></span>${esc(p.title)}</a>`).join('')}</div>`:''}
    ${s?`
      ${s.explain.length?`<h2>설명할 수 있어야 하는 것</h2><ul class="clean">${s.explain.map(x=>`<li>${inline(x)}</li>`).join('')}</ul>`:''}
      ${s.cs.length?`<h2>바탕이 되는 CS</h2><ul class="clean">${s.cs.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}
      <h2>확인 질문<span class="n">${s.questions.length}</span></h2>
      ${qcards(s.questions,'cq')}
      ${rateBox(id,'이 개념, 면접에서 설명할 수 있나?')}
      ${s.further.length?`<h2>더 파볼 것</h2><ul class="clean">${s.further.map(f=>`<li>${f.url?`<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.title)}</a>`:esc(f.title)}${f.note?' — '+esc(f.note):''}</li>`).join('')}</ul>`:''}
      <details class="raw"><summary>위키 문서 전문 보기</summary><div class="md card" style="margin-top:10px">${md(c.body)}</div></details>
    `:`<div class="md card">${md(c.body)}</div>`}`;
  bindRate();
}

// 관계도
let nodeSel=null, linkSel=null, selected=null;
function graph(){
  app.innerHTML=`<div class="crumb"><a href="#/">프로젝트</a> › 관계도</div><h1>문서 관계도</h1><p class="lead">프로젝트(파랑)와 개념(초록), 교훈(주황)이 어떻게 이어지는지. 노드를 누르면 해당 페이지로 갑니다.</p><div id="graphbox"><svg></svg><div id="tip"></div></div>`;
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
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__BUILT__", data["built"]))
    OUT.write_text(html, encoding="utf-8")
    ns = sum(1 for n in data["nodes"] if n["study"])
    ni = sum(1 for n in data["nodes"] if n["interview"])
    nq = sum(len(n["study"]["questions"]) for n in data["nodes"] if n["study"]) + sum(len(n["interview"]["questions"]) for n in data["nodes"] if n["interview"])
    print(f"{OUT.relative_to(ROOT)}: 문서 {len(data['nodes'])}, 링크 {len(data['links'])}, 학습 절 {ns}, 면접 준비 절 {ni}, 질문 {nq}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
