"""위키를 학습용 한 장짜리 사이트(site/index.html)로 만든다.

- wiki/**/*.md 의 머리말, [[링크]], `## 학습` 절을 읽어 구조화한다
- 화면: 학습(주제별 개념 + 이해도) / 프로젝트 보드 / 그래프
- 이해도 기록은 브라우저(localStorage)에 남고 JSON으로 내보내기·가져오기 가능
- 결과는 파일 하나라 더블클릭으로 열리고 GitHub Pages에 그대로 올라간다

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
    """index.md 에서 (요약, 소제목 그룹) 을 읽는다."""
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


def split_study(body: str) -> tuple[str, dict | None]:
    """본문에서 `## 학습` 절을 떼어 구조화한다. 없으면 (body, None)."""
    m = re.search(r"^## 학습\s*$", body, flags=re.M)
    if not m:
        return body, None
    main, study = body[:m.start()].rstrip(), body[m.end():]
    nxt = re.search(r"^## (?!#)", study, flags=re.M)
    tail = ""
    if nxt:
        tail = study[nxt.start():]
        study = study[:nxt.start()]
    sections: dict[str, str] = {}
    cur = None
    for line in study.splitlines():
        h = re.match(r"^### (.+)$", line)
        if h:
            cur = h.group(1).strip()
            sections[cur] = ""
        elif cur:
            sections[cur] += line + "\n"

    def bullets(key: str) -> list[str]:
        return [re.sub(r"^\s*[-*]\s*", "", l).strip() for l in sections.get(key, "").splitlines() if re.match(r"^\s*[-*]\s+", l)]

    questions = []
    qtext = sections.get("확인 질문", "")
    for block in re.split(r"^\s*\d+\.\s+", qtext, flags=re.M):
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
        questions.append({"level": level, "q": q, "a": grab("A"), "tail": grab("꼬리"), "wrong": grab("틀리기 쉬운 답")})
    further = []
    for b in bullets("더 파볼 것"):
        mm = re.match(r"\[([^\]]+)\]\(([^)]+)\)\s*[—-]?\s*(.*)", b)
        further.append({"title": mm.group(1), "url": mm.group(2), "note": mm.group(3)} if mm else {"title": b, "url": "", "note": ""})
    return (main + ("\n\n" + tail if tail else "")), {
        "cs": bullets("CS 주제"),
        "explain": bullets("설명할 수 있어야 하는 것"),
        "questions": questions,
        "further": further,
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
        main, study = split_study(body)
        nodes.append({
            "id": stem,
            "type": fm.get("type", d["folder"][:-1]),
            "title": fm.get("title", stem),
            "summary": summaries.get(stem, ""),
            "group": groups.get(stem, ""),
            "tags": parse_list(fm.get("tags", "")),
            "cs_topics": parse_list(fm.get("cs_topics", "")),
            "updated": fm.get("updated", ""),
            "repo": fm.get("repo", ""),
            "url": f"{REPO_URL}wiki/{d['folder']}/{stem}.md",
            "body": main,
            "study": study,
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


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>해커톤 학습 위키</title>
<style>
:root{
  color-scheme:light;
  --surface:#fcfcfb; --panel:#ffffff; --border:#e4e3df; --soft:#f3f2ef;
  --text:#0b0b0b; --text-2:#52514e; --muted:#8a8984;
  --project:#2a78d6; --concept:#1baf7a; --lesson:#eb6834;
  --edge:#c9c8c2; --edge-hi:#6d6c68; --focus:#0b0b0b;
  --know:#008300; --half:#eda100; --dunno:#e34948;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --surface:#1a1a19; --panel:#232322; --border:#3a3936; --soft:#2b2b29;
    --text:#ffffff; --text-2:#c3c2b7; --muted:#8f8e88;
    --project:#3987e5; --concept:#199e70; --lesson:#d95926;
    --edge:#3f3e3a; --edge-hi:#b5b4ad; --focus:#ffffff;
    --know:#3fae3f; --half:#c98500; --dunno:#e66767;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --surface:#1a1a19; --panel:#232322; --border:#3a3936; --soft:#2b2b29;
  --text:#ffffff; --text-2:#c3c2b7; --muted:#8f8e88;
  --project:#3987e5; --concept:#199e70; --lesson:#d95926;
  --edge:#3f3e3a; --edge-hi:#b5b4ad; --focus:#ffffff;
  --know:#3fae3f; --half:#c98500; --dunno:#e66767;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{background:var(--surface);color:var(--text);font:14px/1.55 -apple-system,"Segoe UI","Pretendard","Noto Sans KR",sans-serif;display:flex;flex-direction:column}
a{color:var(--project)}
button{font:inherit}
header{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border);background:var(--panel)}
header h1{font-size:16px;margin:0 6px 0 0;font-weight:600}
nav.tabs{display:flex;gap:4px}
nav.tabs button{padding:6px 12px;border:1px solid transparent;border-radius:8px;background:none;color:var(--text-2);cursor:pointer}
nav.tabs button[aria-selected="true"]{background:var(--soft);color:var(--text);border-color:var(--border)}
header .spacer,footer .spacer{flex:1}
input[type=search]{padding:6px 10px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);min-width:220px}
.small{font-size:12px;color:var(--muted)}
main{flex:1;display:flex;min-height:0}
#view{flex:1;min-width:0;overflow:auto;padding:16px 20px 60px}
#view.graph{padding:0;overflow:hidden;position:relative}
aside{width:min(520px,48vw);border-left:1px solid var(--border);background:var(--panel);overflow:auto;padding:16px 20px 60px;display:none}
aside.open{display:block}
@media (max-width:820px){ main{flex-direction:column} aside{width:100%;border-left:0;border-top:1px solid var(--border);max-height:60vh} }

.stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:10px 14px;min-width:130px}
.stat b{display:block;font-size:20px;font-weight:600}
.stat span{font-size:12px;color:var(--muted)}
.bar{height:6px;border-radius:3px;background:var(--soft);overflow:hidden;display:flex;margin-top:6px}
.bar i{display:block;height:100%}
.today{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-bottom:18px}
.today h3{margin:0 0 6px;font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--border);border-radius:999px;padding:3px 10px;font-size:12px;background:var(--surface);color:var(--text-2);cursor:pointer;max-width:100%;text-align:left}
.chip:hover{border-color:var(--text-2);color:var(--text)}
.chip .dot{width:8px;height:8px;border-radius:50%;flex:none}
.st{width:8px;height:8px;border-radius:2px;flex:none;background:var(--soft);display:inline-block}
.st.know{background:var(--know)} .st.half{background:var(--half)} .st.dunno{background:var(--dunno)}
.group{margin-bottom:22px}
.group h2{font-size:15px;margin:0 0 8px;display:flex;align-items:baseline;gap:8px}
.group h2 .small{font-weight:400}
.rows{display:grid;gap:6px}
.row{display:grid;grid-template-columns:14px 1fr auto;gap:10px;align-items:center;background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:8px 12px;cursor:pointer}
.row:hover{border-color:var(--text-2)}
.row .t{font-weight:500}
.row .s{font-size:12px;color:var(--muted);display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .from{display:flex;gap:4px;align-items:center}
.row .from i{width:8px;height:8px;border-radius:50%;background:var(--project);display:inline-block}
.row .q{font-size:11px;color:var(--muted);white-space:nowrap;margin-left:4px}
.row .st{width:10px;height:10px;border-radius:3px}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.card h3{margin:0 0 4px;font-size:15px;cursor:pointer}
.card h3:hover{text-decoration:underline}
.card .sum{font-size:12px;color:var(--muted);margin-bottom:10px}
.card .learn{font-size:12px;color:var(--text-2);margin:8px 0 6px}

aside .kind{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
aside h2{margin:4px 0 6px;font-size:19px;line-height:1.3}
aside .meta{color:var(--muted);font-size:12px;margin-bottom:12px}
aside .meta a{color:var(--text-2)}
aside .close{float:right;border:0;background:none;color:var(--muted);font-size:22px;cursor:pointer;line-height:1}
aside .nb{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}
.box{border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:10px 0;background:var(--surface)}
.box h4{margin:0 0 8px;font-size:13px;color:var(--text-2)}
.box ul{margin:0;padding-left:18px;color:var(--text-2)}
.qcard{border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:8px 0;background:var(--panel)}
.qcard .lv{font-size:11px;color:var(--muted);margin-right:6px;border:1px solid var(--border);border-radius:4px;padding:0 5px}
.qcard .qq{font-weight:500;margin:4px 0 8px}
.qcard .ans{display:none;color:var(--text-2);border-top:1px dashed var(--border);padding-top:8px;margin-top:8px}
.qcard.open .ans{display:block}
.qcard .ans p{margin:4px 0}
.qcard .ans .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.qcard .reveal{border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text-2);padding:4px 10px;cursor:pointer;font-size:12px}
.rate{display:flex;gap:6px;margin-top:10px}
.rate button{flex:1;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text-2);padding:6px;cursor:pointer;font-size:12px}
.rate button[aria-pressed="true"].know{border-color:var(--know);color:var(--know)}
.rate button[aria-pressed="true"].half{border-color:var(--half);color:var(--half)}
.rate button[aria-pressed="true"].dunno{border-color:var(--dunno);color:var(--dunno)}
details.body{margin-top:14px}
details.body summary{cursor:pointer;color:var(--text-2);font-size:13px}
.md{font-size:14px;color:var(--text)}
.md h1,.md h2,.md h3{line-height:1.3;margin:20px 0 8px}
.md h1{font-size:17px}.md h2{font-size:15px}.md h3{font-size:14px}
.md p,.md li{color:var(--text-2)}
.md code{background:var(--soft);border:1px solid var(--border);border-radius:4px;padding:0 4px;font-size:12px}
.md pre{background:var(--soft);border:1px solid var(--border);border-radius:8px;padding:10px;overflow:auto;font-size:12px}
.md table{border-collapse:collapse;font-size:12px;margin:8px 0;display:block;overflow:auto}
.md th,.md td{border:1px solid var(--border);padding:4px 8px;text-align:left;vertical-align:top}
.md blockquote{border-left:3px solid var(--border);margin:8px 0;padding:2px 12px;color:var(--text-2)}
.md a.wiki{color:var(--project);text-decoration:none;border-bottom:1px dotted currentColor;cursor:pointer}

svg{width:100%;height:100%;display:block;cursor:grab}
svg:active{cursor:grabbing}
.link{stroke:var(--edge);stroke-width:1.2px}
.link.hi{stroke:var(--edge-hi);stroke-width:2px}
.node circle{stroke:var(--surface);stroke-width:2px;cursor:pointer}
.node.dim{opacity:.15} .link.dim{opacity:.08}
.node text{font-size:11px;fill:var(--text-2);pointer-events:none;paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.node.minor text{display:none}
.node.hi text,.node.sel text{display:block;fill:var(--text);font-weight:600}
.node.sel circle{stroke:var(--focus);stroke-width:3px}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 10px;max-width:320px;font-size:12px;color:var(--text-2);box-shadow:0 4px 16px rgba(0,0,0,.12);display:none}
#tip b{color:var(--text);display:block;margin-bottom:2px;font-size:13px}
.legend{position:absolute;left:12px;bottom:12px;display:flex;gap:10px;font-size:12px;color:var(--text-2);background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:6px 10px;flex-wrap:wrap}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}
footer{padding:6px 16px;border-top:1px solid var(--border);color:var(--muted);font-size:12px;background:var(--panel);display:flex;gap:14px;flex-wrap:wrap}
footer button{border:0;background:none;color:var(--text-2);cursor:pointer;text-decoration:underline;padding:0;font-size:12px}
</style>
</head>
<body>
<header>
  <h1>해커톤 학습 위키</h1>
  <nav class="tabs" role="tablist">
    <button role="tab" aria-selected="true" data-view="study">학습</button>
    <button role="tab" aria-selected="false" data-view="projects">프로젝트</button>
    <button role="tab" aria-selected="false" data-view="graph">그래프</button>
  </nav>
  <span class="spacer"></span>
  <input type="search" id="q" placeholder="검색 (제목, 태그, CS 주제, 요약)" aria-label="검색">
</header>
<main>
  <div id="view"></div>
  <aside id="panel" aria-live="polite"></aside>
</main>
<footer>
  <span>이해도 기록은 이 브라우저에만 저장됩니다.</span>
  <button id="export">기록 내보내기</button>
  <button id="import">가져오기</button>
  <input type="file" id="importFile" accept="application/json" hidden>
  <span class="spacer"></span>
  <span>생성 __BUILT__</span>
</footer>

<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const byId = new Map(DATA.nodes.map(n => [n.id, n]));
const KIND = {project:'프로젝트', concept:'개념', lesson:'교훈'};
const nb = new Map(DATA.nodes.map(n => [n.id, new Set()]));
DATA.links.forEach(l => { nb.get(l.source).add(l.target); nb.get(l.target).add(l.source); });
const projectsOf = id => [...nb.get(id)].map(x => byId.get(x)).filter(n => n && n.type === 'project');
const conceptsOf = pid => [...nb.get(pid)].map(x => byId.get(x)).filter(n => n && n.type !== 'project');
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const STATE_LABEL = {know:'설명 가능', half:'애매함', dunno:'모름'};

const KEY = 'wiki-progress-v1';
let progress = {};
try { progress = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { progress = {}; }
function save() { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) {} }
function stateOf(id) { return (progress[id] || {}).state || ''; }
function setState(id, st) { progress[id] = {state: st, at: new Date().toISOString().slice(0,10)}; save(); }
function dueIds() {
  const gap = {dunno:1, half:3, know:14};
  const today = new Date();
  return DATA.nodes.filter(n => n.type === 'concept' && n.study && n.study.questions.length).filter(n => {
    const p = progress[n.id]; if (!p) return false;
    return (today - new Date(p.at)) / 86400000 >= (gap[p.state] || 1);
  }).map(n => n.id);
}
document.getElementById('export').onclick = () => {
  const blob = new Blob([JSON.stringify(progress, null, 2)], {type:'application/json'});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'wiki-progress.json'; a.click();
};
document.getElementById('import').onclick = () => document.getElementById('importFile').click();
document.getElementById('importFile').onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  f.text().then(t => { try { Object.assign(progress, JSON.parse(t)); save(); render(); } catch (err) { alert('JSON을 읽지 못했습니다'); } });
};

let view = 'study';
const viewEl = document.getElementById('view');
document.querySelectorAll('nav.tabs button').forEach(b => b.onclick = () => { view = b.dataset.view; document.querySelectorAll('nav.tabs button').forEach(x => x.setAttribute('aria-selected', x === b)); render(); });
document.getElementById('q').addEventListener('input', () => view === 'graph' ? paintGraph() : render());
const query = () => document.getElementById('q').value.trim().toLowerCase();
const matches = n => { const q = query(); if (!q) return true; return (n.title+' '+n.summary+' '+n.tags.join(' ')+' '+n.cs_topics.join(' ')+' '+n.id).toLowerCase().includes(q); };

function render() {
  viewEl.className = view === 'graph' ? 'graph' : '';
  if (view === 'study') renderStudy();
  else if (view === 'projects') renderProjects();
  else renderGraph();
}

function renderStudy() {
  const concepts = DATA.nodes.filter(n => n.type === 'concept');
  const withQ = concepts.filter(n => n.study && n.study.questions.length);
  const cnt = {know:0, half:0, dunno:0, none:0};
  concepts.forEach(n => cnt[stateOf(n.id) || 'none']++);
  const due = dueIds();
  const fresh = withQ.filter(n => !stateOf(n.id)).slice(0, 5);
  const groups = new Map();
  concepts.filter(matches).forEach(n => { const g = n.group || '기타'; if (!groups.has(g)) groups.set(g, []); groups.get(g).push(n); });
  const total = concepts.length || 1;
  viewEl.innerHTML = `
    <div class="stats">
      <div class="stat"><b>${concepts.length}</b><span>개념 문서</span></div>
      <div class="stat"><b>${withQ.reduce((s,n)=>s+n.study.questions.length,0)}</b><span>확인 질문</span></div>
      <div class="stat" style="min-width:280px"><b>${Math.round(cnt.know/total*100)}%</b><span>설명 가능 · 애매 ${cnt.half} · 모름 ${cnt.dunno} · 아직 안 봄 ${cnt.none}</span>
        <div class="bar"><i style="width:${cnt.know/total*100}%;background:var(--know)"></i><i style="width:${cnt.half/total*100}%;background:var(--half)"></i><i style="width:${cnt.dunno/total*100}%;background:var(--dunno)"></i></div></div>
    </div>
    <div class="today">
      <h3>오늘 볼 것 <span class="small">복습 ${due.length} · 새로 ${fresh.length}</span></h3>
      <div class="chips">
        ${[...due.map(id=>byId.get(id)), ...fresh].map(n => `<button class="chip" data-id="${n.id}"><span class="st ${stateOf(n.id)}"></span>${esc(n.title)}</button>`).join('') || '<span class="small">확인 질문이 있는 개념이 아직 없습니다.</span>'}
      </div>
    </div>
    ${[...groups.entries()].map(([g, list]) => `
      <section class="group">
        <h2>${esc(g)} <span class="small">${list.length}개 · 설명 가능 ${list.filter(n=>stateOf(n.id)==='know').length}</span></h2>
        <div class="rows">
          ${list.map(n => `
            <div class="row" data-id="${n.id}">
              <span class="st ${stateOf(n.id)}" title="${STATE_LABEL[stateOf(n.id)]||'기록 없음'}"></span>
              <div><span class="t">${esc(n.title)}</span><span class="s">${esc(n.summary)}${n.cs_topics.length ? ' · ' + n.cs_topics.map(esc).join(', ') : ''}</span></div>
              <div class="from" title="${esc(projectsOf(n.id).map(p=>p.title).join(', '))}">${projectsOf(n.id).map(()=>'<i></i>').join('')}<span class="q">${n.study ? n.study.questions.length + '문' : '학습 절 없음'}</span></div>
            </div>`).join('')}
        </div>
      </section>`).join('')}`;
  viewEl.querySelectorAll('[data-id]').forEach(el => el.onclick = () => openDoc(el.dataset.id));
}

function renderProjects() {
  const ps = DATA.nodes.filter(n => n.type === 'project' && matches(n)).sort((a,b) => (b.updated||'').localeCompare(a.updated||''));
  viewEl.innerHTML = `<div class="cards">${ps.map(p => {
    const cs = conceptsOf(p.id);
    const known = cs.filter(c => stateOf(c.id) === 'know').length;
    return `<div class="card">
      <h3 data-id="${p.id}">${esc(p.title)}</h3>
      <div class="sum">${esc(p.summary)}</div>
      <div class="learn">여기서 배울 것 ${cs.length} · 설명 가능 ${known}</div>
      <div class="bar" style="margin:0 0 10px"><i style="width:${cs.length?known/cs.length*100:0}%;background:var(--know)"></i></div>
      <div class="chips">${cs.map(c => `<button class="chip" data-id="${c.id}"><span class="dot" style="background:var(--${c.type})"></span><span class="st ${stateOf(c.id)}"></span>${esc(c.title)}</button>`).join('')}</div>
    </div>`; }).join('')}</div>`;
  viewEl.querySelectorAll('[data-id]').forEach(el => el.onclick = () => openDoc(el.dataset.id));
}

const panel = document.getElementById('panel');
let selected = null;
function md(text) {
  const withLinks = text.replace(/\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]/g, (m, id) => byId.has(id) ? `<a class="wiki" data-id="${id}">${esc(byId.get(id).title)}</a>` : `<span style="color:var(--muted)">[[${esc(id)}]]</span>`);
  if (window.marked) { marked.setOptions({gfm:true}); return marked.parse(withLinks); }
  return `<pre style="white-space:pre-wrap">${esc(text)}</pre>`;
}
const inline = t => md(t).replace(/^<p>|<\/p>\s*$/g, '');
function openDoc(id) {
  const n = byId.get(id); if (!n) return;
  selected = id;
  const neigh = [...nb.get(id)].map(x => byId.get(x)).sort((a,b)=>a.type.localeCompare(b.type)||a.title.localeCompare(b.title));
  const s = n.study;
  const st = stateOf(id);
  panel.innerHTML = `
    <button class="close" aria-label="닫기">×</button>
    <div class="kind">${KIND[n.type]}${n.group ? ' · ' + esc(n.group) : ''}</div>
    <h2>${esc(n.title)}</h2>
    <div class="meta">갱신 ${esc(n.updated)} · <a href="${n.url}" target="_blank" rel="noopener">GitHub</a>${n.repo && n.repo !== '없음' ? ` · <a href="${esc(n.repo)}" target="_blank" rel="noopener">코드 저장소</a>` : ''}${n.cs_topics.length ? `<br>CS: ${n.cs_topics.map(esc).join(', ')}` : ''}${n.tags.length ? `<br>${n.tags.map(t=>'#'+esc(t)).join(' ')}` : ''}</div>
    ${neigh.length ? `<div class="nb">${neigh.map(x => `<button class="chip" data-id="${x.id}"><span class="dot" style="background:var(--${x.type})"></span>${esc(x.title)}</button>`).join('')}</div>` : ''}
    ${s ? `
      ${s.explain.length ? `<div class="box"><h4>설명할 수 있어야 하는 것</h4><ul>${s.explain.map(x=>`<li>${inline(x)}</li>`).join('')}</ul></div>` : ''}
      ${s.cs.length ? `<div class="box"><h4>바탕이 되는 CS 주제</h4><ul>${s.cs.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>` : ''}
      ${s.questions.map((q,i) => `
        <div class="qcard">
          <div><span class="lv">${esc(q.level||'Q')}</span><span class="small">${i+1} / ${s.questions.length}</span></div>
          <div class="qq">${inline(q.q)}</div>
          <button class="reveal">답 보기</button>
          <div class="ans">
            <p>${inline(q.a)}</p>
            ${q.tail ? `<p><span class="lbl">꼬리질문</span><br>${inline(q.tail)}</p>` : ''}
            ${q.wrong ? `<p><span class="lbl">틀리기 쉬운 답</span><br>${inline(q.wrong)}</p>` : ''}
          </div>
        </div>`).join('')}
      ${s.questions.length ? `<div class="box"><h4>이 개념, 지금 면접에서 설명할 수 있나?</h4>
        <div class="rate">
          <button class="dunno" data-st="dunno" aria-pressed="${st==='dunno'}">모름</button>
          <button class="half" data-st="half" aria-pressed="${st==='half'}">애매함</button>
          <button class="know" data-st="know" aria-pressed="${st==='know'}">설명 가능</button>
        </div></div>` : ''}
      ${s.further.length ? `<div class="box"><h4>더 파볼 것</h4><ul>${s.further.map(f=>`<li>${f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.title)}</a>` : esc(f.title)}${f.note ? ' — ' + esc(f.note) : ''}</li>`).join('')}</ul></div>` : ''}
      <details class="body"><summary>문서 본문 보기</summary><div class="md">${md(n.body)}</div></details>
    ` : `<div class="md">${md(n.body)}</div>`}`;
  panel.classList.add('open');
  panel.scrollTop = 0;
  panel.querySelector('.close').onclick = closePanel;
  panel.querySelectorAll('[data-id]').forEach(el => el.onclick = () => openDoc(el.dataset.id));
  panel.querySelectorAll('.reveal').forEach(b => b.onclick = () => { const c = b.closest('.qcard'); c.classList.toggle('open'); b.textContent = c.classList.contains('open') ? '답 숨기기' : '답 보기'; });
  panel.querySelectorAll('.rate button').forEach(b => b.onclick = () => { setState(id, b.dataset.st); openDoc(id); if (view !== 'graph') render(); });
  history.replaceState(null, '', '#' + id);
  if (view === 'graph') paintGraph();
}
function closePanel(){ panel.classList.remove('open'); selected = null; history.replaceState(null,'',' '); if (view === 'graph') paintGraph(); }

let sim = null, nodeSel = null, linkSel = null;
const degree = new Map(DATA.nodes.map(n => [n.id, nb.get(n.id).size]));
function renderGraph() {
  viewEl.innerHTML = `<svg aria-label="문서 관계 그래프"></svg><div id="tip"></div>
    <div class="legend"><span><i style="background:var(--project)"></i>프로젝트</span><span><i style="background:var(--concept)"></i>개념</span><span><i style="background:var(--lesson)"></i>교훈</span><span class="small">연결 3개 미만은 마우스를 올리면 이름이 보입니다</span></div>`;
  const svg = d3.select(viewEl).select('svg');
  const gW = viewEl.clientWidth, gH = viewEl.clientHeight;
  const nodes = DATA.nodes.map(n => Object.assign({}, n));
  const links = DATA.links.map(l => ({source: l.source, target: l.target}));
  const g = svg.append('g');
  const r = d => 5 + Math.sqrt(degree.get(d.id)) * 3;
  linkSel = g.append('g').selectAll('line').data(links).join('line').attr('class','link');
  nodeSel = g.append('g').selectAll('g').data(nodes).join('g').attr('class', d => 'node' + (degree.get(d.id) < 3 ? ' minor' : ''))
    .call(d3.drag().clickDistance(6)
      .on('start',(e,d)=>{d.fx=d.x;d.fy=d.y;})
      .on('drag',(e,d)=>{if(!e.active&&sim.alpha()<.1)sim.alphaTarget(.2).restart();d.fx=e.x;d.fy=e.y;})
      .on('end',(e,d)=>{sim.alphaTarget(0);d.fx=null;d.fy=null;}));
  nodeSel.append('circle').attr('r', r).attr('fill', d => `var(--${d.type})`);
  nodeSel.append('text').attr('dy', d => r(d) + 12).attr('text-anchor','middle').text(d => d.title.length > 22 ? d.title.slice(0,21)+'…' : d.title);
  const tip = viewEl.querySelector('#tip');
  nodeSel.on('mouseenter', (e,d) => { tip.style.display='block'; tip.innerHTML = `<b>${esc(d.title)}</b>${esc(d.summary || KIND[d.type])}<br><span class="small">${KIND[d.type]} · 연결 ${degree.get(d.id)}${d.type==='concept' ? ' · ' + (STATE_LABEL[stateOf(d.id)] || '기록 없음') : ''}</span>`; })
         .on('mousemove', e => { const p = viewEl.getBoundingClientRect(); tip.style.left = (e.clientX - p.left + 14)+'px'; tip.style.top = (e.clientY - p.top + 14)+'px'; })
         .on('mouseleave', () => tip.style.display='none')
         .on('click', (e,d) => { e.stopPropagation(); openDoc(d.id); });
  svg.on('click', () => { selected = null; paintGraph(); });
  sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(70).strength(.6))
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(gW/2, gH/2))
    .force('collide', d3.forceCollide(d => r(d) + 12))
    .force('x', d3.forceX(gW/2).strength(.06)).force('y', d3.forceY(gH/2).strength(.08))
    .on('tick', () => { linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y); nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`); });
  const zoom = d3.zoom().scaleExtent([.2, 4]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom);
  let fitted = false;
  const fit = () => { const xs = nodes.map(n=>n.x), ys = nodes.map(n=>n.y); const x0=Math.min(...xs)-60,x1=Math.max(...xs)+60,y0=Math.min(...ys)-40,y1=Math.max(...ys)+40; const k=Math.max(.55,Math.min(1.5,.92/Math.max((x1-x0)/gW,(y1-y0)/gH))); svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(gW/2-k*(x0+x1)/2, gH/2-k*(y0+y1)/2).scale(k)); };
  const w = setInterval(() => { if (view !== 'graph') { clearInterval(w); return; } if (sim.alpha() < .03 && !fitted) { fitted = true; fit(); clearInterval(w); } }, 300);
  paintGraph();
}
function paintGraph() {
  if (!nodeSel || view !== 'graph') return;
  const focus = selected ? new Set([selected, ...nb.get(selected)]) : null;
  nodeSel.classed('dim', n => !matches(n) || (focus && !focus.has(n.id)))
         .classed('sel', n => n.id === selected)
         .classed('hi', n => focus && focus.has(n.id) && n.id !== selected);
  linkSel.classed('dim', l => !(matches(l.source) && matches(l.target)) || (focus && !(focus.has(l.source.id) && focus.has(l.target.id))))
         .classed('hi', l => focus && (l.source.id === selected || l.target.id === selected));
}

render();
if (location.hash && byId.has(location.hash.slice(1))) openDoc(location.hash.slice(1));
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
    nq = sum(len(n["study"]["questions"]) for n in data["nodes"] if n["study"])
    ns = sum(1 for n in data["nodes"] if n["study"])
    print(f"{OUT.relative_to(ROOT)}: 문서 {len(data['nodes'])}, 링크 {len(data['links'])}, 학습 절 {ns}, 질문 {nq}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
