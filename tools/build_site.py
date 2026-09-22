"""위키를 한 장짜리 그래프 페이지(site/index.html)로 만든다.

- wiki/**/*.md 의 머리말과 [[링크]]를 읽어 노드·간선을 뽑는다
- 문서 본문도 함께 담아 노드를 누르면 옆 패널에서 읽을 수 있다
- 결과는 파일 하나라 더블클릭으로 열리고, GitHub Pages에 그대로 올릴 수 있다

사용: python tools/build_site.py   →  site/index.html
"""
from __future__ import annotations

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


def index_summaries() -> dict[str, str]:
    out: dict[str, str] = {}
    idx = WIKI / "index.md"
    if not idx.exists():
        return out
    for line in idx.read_text(encoding="utf-8").splitlines():
        m = re.match(r"- \[\[([^\]]+)\]\]\s*[—-]\s*(.+)", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def build() -> dict:
    summaries = index_summaries()
    nodes, links = [], []
    ids: set[str] = set()
    docs: dict[str, dict] = {}
    for folder in FOLDERS:
        for p in sorted((WIKI / folder).glob("*.md")):
            text = p.read_text(encoding="utf-8")
            fm, body = frontmatter(text)
            docs[p.stem] = {"folder": folder, "fm": fm, "body": body}
            ids.add(p.stem)
    for stem, d in docs.items():
        fm, body = d["fm"], d["body"]
        outgoing = sorted({l for l in LINK_RE.findall(body) if l in ids and l != stem})
        nodes.append({
            "id": stem,
            "type": fm.get("type", d["folder"][:-1]),
            "title": fm.get("title", stem),
            "summary": summaries.get(stem, ""),
            "tags": parse_list(fm.get("tags", "")),
            "updated": fm.get("updated", ""),
            "repo": fm.get("repo", ""),
            "url": f"{REPO_URL}wiki/{d['folder']}/{stem}.md",
            "body": body,
        })
        for t in outgoing:
            links.append({"source": stem, "target": t})
    # 양방향 중복 제거
    seen, uniq = set(), []
    for l in links:
        key = tuple(sorted((l["source"], l["target"])))
        if key not in seen:
            seen.add(key)
            uniq.append(l)
    return {"nodes": nodes, "links": uniq}


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>해커톤 지식 위키</title>
<style>
:root{
  color-scheme:light;
  --surface:#fcfcfb; --panel:#ffffff; --border:#e4e3df;
  --text:#0b0b0b; --text-2:#52514e; --muted:#8a8984;
  --project:#2a78d6; --concept:#1baf7a; --lesson:#eb6834;
  --edge:#c9c8c2; --edge-hi:#6d6c68; --focus:#0b0b0b;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --surface:#1a1a19; --panel:#232322; --border:#3a3936;
    --text:#ffffff; --text-2:#c3c2b7; --muted:#8f8e88;
    --project:#3987e5; --concept:#199e70; --lesson:#d95926;
    --edge:#3f3e3a; --edge-hi:#b5b4ad; --focus:#ffffff;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --surface:#1a1a19; --panel:#232322; --border:#3a3936;
  --text:#ffffff; --text-2:#c3c2b7; --muted:#8f8e88;
  --project:#3987e5; --concept:#199e70; --lesson:#d95926;
  --edge:#3f3e3a; --edge-hi:#b5b4ad; --focus:#ffffff;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{background:var(--surface);color:var(--text);font:14px/1.5 -apple-system,"Segoe UI","Pretendard","Noto Sans KR",sans-serif;display:flex;flex-direction:column}
header{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border);background:var(--panel)}
header h1{font-size:16px;margin:0 8px 0 0;font-weight:600}
header .count{color:var(--muted);font-size:12px}
input[type=search]{padding:6px 10px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);min-width:200px}
.toggles{display:flex;gap:6px}
.toggles button{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border:1px solid var(--border);border-radius:999px;background:var(--surface);color:var(--text-2);cursor:pointer;font-size:13px}
.toggles button[aria-pressed="true"]{color:var(--text);border-color:var(--text-2)}
.toggles button .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.toggles button[aria-pressed="false"] .dot{opacity:.25}
main{flex:1;display:flex;min-height:0}
#graph{flex:1;min-width:0;position:relative}
svg{width:100%;height:100%;display:block;cursor:grab}
svg:active{cursor:grabbing}
.link{stroke:var(--edge);stroke-width:1.2px}
.link.hi{stroke:var(--edge-hi);stroke-width:2px}
.node circle{stroke:var(--surface);stroke-width:2px;cursor:pointer}
.node.dim{opacity:.15}
.link.dim{opacity:.08}
.node text{font-size:11px;fill:var(--text-2);pointer-events:none;paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.node.hi text,.node.sel text{fill:var(--text);font-weight:600}
.node.sel circle{stroke:var(--focus);stroke-width:3px}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 10px;max-width:320px;font-size:12px;color:var(--text-2);box-shadow:0 4px 16px rgba(0,0,0,.12);display:none}
#tip b{color:var(--text);display:block;margin-bottom:2px;font-size:13px}
aside{width:min(460px,45vw);border-left:1px solid var(--border);background:var(--panel);overflow:auto;padding:16px 20px 40px;display:none}
aside.open{display:block}
aside .kind{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
aside h2{margin:4px 0 6px;font-size:18px;line-height:1.3}
aside .meta{color:var(--muted);font-size:12px;margin-bottom:12px}
aside .meta a{color:var(--text-2)}
aside .close{float:right;border:0;background:none;color:var(--muted);font-size:20px;cursor:pointer;line-height:1}
aside .nb{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 16px}
aside .nb button{border:1px solid var(--border);border-radius:999px;background:var(--surface);color:var(--text-2);padding:2px 10px;font-size:12px;cursor:pointer}
.md{font-size:14px;color:var(--text)}
.md h1,.md h2,.md h3{line-height:1.3;margin:20px 0 8px}
.md h1{font-size:17px}.md h2{font-size:15px}.md h3{font-size:14px}
.md p,.md li{color:var(--text-2)}
.md code{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:0 4px;font-size:12px}
.md pre{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px;overflow:auto;font-size:12px}
.md table{border-collapse:collapse;font-size:12px;margin:8px 0}
.md th,.md td{border:1px solid var(--border);padding:4px 8px;text-align:left;vertical-align:top}
.md blockquote{border-left:3px solid var(--border);margin:8px 0;padding:2px 12px;color:var(--text-2)}
.md a.wiki{color:var(--project);text-decoration:none;border-bottom:1px dotted currentColor;cursor:pointer}
footer{padding:6px 16px;border-top:1px solid var(--border);color:var(--muted);font-size:12px;background:var(--panel)}
@media (max-width:760px){
  main{flex-direction:column}
  aside{width:100%;border-left:0;border-top:1px solid var(--border);max-height:55vh}
}
</style>
</head>
<body>
<header>
  <h1>해커톤 지식 위키</h1>
  <span class="count" id="count"></span>
  <input type="search" id="q" placeholder="문서 검색 (제목, 태그, 요약)" aria-label="문서 검색">
  <div class="toggles" role="group" aria-label="문서 종류 필터">
    <button data-type="project" aria-pressed="true"><span class="dot" style="background:var(--project)"></span>프로젝트</button>
    <button data-type="concept" aria-pressed="true"><span class="dot" style="background:var(--concept)"></span>개념</button>
    <button data-type="lesson" aria-pressed="true"><span class="dot" style="background:var(--lesson)"></span>교훈</button>
  </div>
</header>
<main>
  <div id="graph"><svg aria-label="문서 관계 그래프"></svg><div id="tip"></div></div>
  <aside id="panel" aria-live="polite"></aside>
</main>
<footer>노드를 누르면 문서가 열립니다. 드래그로 이동, 휠로 확대. 원의 크기는 연결 수. 생성: __BUILT__</footer>

<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const byId = new Map(DATA.nodes.map(n => [n.id, n]));
const degree = new Map(DATA.nodes.map(n => [n.id, 0]));
DATA.links.forEach(l => { degree.set(l.source, degree.get(l.source)+1); degree.set(l.target, degree.get(l.target)+1); });
const neighbors = new Map(DATA.nodes.map(n => [n.id, new Set()]));
DATA.links.forEach(l => { neighbors.get(l.source).add(l.target); neighbors.get(l.target).add(l.source); });
const color = t => getComputedStyle(document.documentElement).getPropertyValue('--'+t).trim();
const KIND = {project:'프로젝트', concept:'개념', lesson:'교훈'};
document.getElementById('count').textContent =
  `프로젝트 ${DATA.nodes.filter(n=>n.type==='project').length} · 개념 ${DATA.nodes.filter(n=>n.type==='concept').length} · 교훈 ${DATA.nodes.filter(n=>n.type==='lesson').length} · 링크 ${DATA.links.length}`;

const svg = d3.select('svg');
const g = svg.append('g');
const box = document.getElementById('graph');
let W = box.clientWidth, H = box.clientHeight;

const linkSel = g.append('g').selectAll('line').data(DATA.links).join('line').attr('class','link');
const nodeSel = g.append('g').selectAll('g').data(DATA.nodes).join('g').attr('class','node')
  .call(d3.drag().clickDistance(6)
                 .on('start',(e,d)=>{d.fx=d.x;d.fy=d.y;})
                 .on('drag',(e,d)=>{if(!e.active&&sim.alpha()<.1)sim.alphaTarget(.2).restart();d.fx=e.x;d.fy=e.y;})
                 .on('end',(e,d)=>{sim.alphaTarget(0);d.fx=null;d.fy=null;}));
const r = d => 5 + Math.sqrt(degree.get(d.id)) * 3;
nodeSel.append('circle').attr('r', r).attr('fill', d => color(d.type));
nodeSel.append('text').attr('dy', d => r(d) + 12).attr('text-anchor','middle').text(d => d.title.length > 22 ? d.title.slice(0,21)+'…' : d.title);

const sim = d3.forceSimulation(DATA.nodes)
  .force('link', d3.forceLink(DATA.links).id(d=>d.id).distance(70).strength(.6))
  .force('charge', d3.forceManyBody().strength(-220))
  .force('center', d3.forceCenter(W/2, H/2))
  .force('collide', d3.forceCollide(d => r(d) + 14))
  .force('x', d3.forceX(W/2).strength(.06))
  .force('y', d3.forceY(H/2).strength(.08))
  .on('tick', () => {
    linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
  });
const zoom = d3.zoom().scaleExtent([.2, 4]).on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);
function fit(duration = 600) {
  const xs = DATA.nodes.map(n=>n.x), ys = DATA.nodes.map(n=>n.y);
  const x0 = Math.min(...xs)-60, x1 = Math.max(...xs)+60, y0 = Math.min(...ys)-40, y1 = Math.max(...ys)+40;
  const k = Math.max(.55, Math.min(1.5, .92 / Math.max((x1-x0)/W, (y1-y0)/H)));
  const t = d3.zoomIdentity.translate(W/2 - k*(x0+x1)/2, H/2 - k*(y0+y1)/2).scale(k);
  svg.transition().duration(duration).call(zoom.transform, t);
}
let fitted = false;
sim.on('end', () => { if (!fitted) { fitted = true; fit(); } });
const fitWatch = setInterval(() => { if (sim.alpha() < 0.03 && !fitted) { fitted = true; fit(); } if (fitted) clearInterval(fitWatch); }, 300);
new ResizeObserver(() => { const nw = box.clientWidth, nh = box.clientHeight; if (nw === W && nh === H) return; W = nw; H = nh; sim.force('center', d3.forceCenter(W/2, H/2)).force('x', d3.forceX(W/2).strength(.06)).force('y', d3.forceY(H/2).strength(.08)); if (fitted) fit(200); }).observe(box);

// 강조 / 흐리기
let selected = null;
function paint() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  const on = new Set([...document.querySelectorAll('.toggles button[aria-pressed="true"]')].map(b=>b.dataset.type));
  const match = n => on.has(n.type) && (!q || (n.title+' '+n.summary+' '+n.tags.join(' ')+' '+n.id).toLowerCase().includes(q));
  const focus = selected ? new Set([selected, ...neighbors.get(selected)]) : null;
  nodeSel.classed('dim', n => !match(n) || (focus && !focus.has(n.id)))
         .classed('sel', n => n.id === selected)
         .classed('hi', n => focus && focus.has(n.id) && n.id !== selected);
  linkSel.classed('dim', l => !(match(l.source) && match(l.target)) || (focus && !(focus.has(l.source.id) && focus.has(l.target.id))))
         .classed('hi', l => focus && (l.source.id === selected || l.target.id === selected));
}
document.getElementById('q').addEventListener('input', paint);
document.querySelectorAll('.toggles button').forEach(b => b.addEventListener('click', () => { b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true'); paint(); }));

// 툴팁
const tip = document.getElementById('tip');
nodeSel.on('mouseenter', (e,d) => { tip.style.display='block'; tip.innerHTML = `<b>${esc(d.title)}</b>${esc(d.summary || KIND[d.type])}<br><span style="color:var(--muted)">${KIND[d.type]} · 연결 ${degree.get(d.id)}</span>`; })
       .on('mousemove', e => { const p = box.getBoundingClientRect(); tip.style.left = (e.clientX - p.left + 14)+'px'; tip.style.top = (e.clientY - p.top + 14)+'px'; })
       .on('mouseleave', () => tip.style.display='none')
       .on('click', (e,d) => { e.stopPropagation(); openDoc(d.id); });
svg.on('click', () => { selected = null; paint(); });

// 패널
const panel = document.getElementById('panel');
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function render(md) {
  const withLinks = md.replace(/\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]/g, (m, id) => byId.has(id) ? `<a class="wiki" data-id="${id}">${esc(byId.get(id).title)}</a>` : `<span style="color:var(--muted)">[[${esc(id)}]]</span>`);
  if (window.marked) { marked.setOptions({gfm:true, breaks:false}); return marked.parse(withLinks); }
  return `<pre style="white-space:pre-wrap">${esc(md)}</pre>`;
}
function openDoc(id) {
  const n = byId.get(id); if (!n) return;
  selected = id; paint();
  const nb = [...neighbors.get(id)].map(x => byId.get(x)).sort((a,b)=>a.type.localeCompare(b.type)||a.title.localeCompare(b.title));
  panel.innerHTML = `
    <button class="close" aria-label="닫기" onclick="closePanel()">×</button>
    <div class="kind">${KIND[n.type]}</div>
    <h2>${esc(n.title)}</h2>
    <div class="meta">갱신 ${esc(n.updated)} · <a href="${n.url}" target="_blank" rel="noopener">GitHub에서 열기</a>${n.repo && n.repo !== '없음' ? ` · <a href="${esc(n.repo)}" target="_blank" rel="noopener">코드 저장소</a>` : ''}${n.tags.length ? `<br>${n.tags.map(t=>'#'+esc(t)).join(' ')}` : ''}</div>
    ${nb.length ? `<div class="nb">${nb.map(x => `<button data-id="${x.id}"><span class="dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--${x.type});margin-right:6px"></span>${esc(x.title)}</button>`).join('')}</div>` : ''}
    <div class="md">${render(n.body)}</div>`;
  panel.classList.add('open');
  panel.scrollTop = 0;
  panel.querySelectorAll('[data-id]').forEach(el => el.addEventListener('click', () => openDoc(el.dataset.id)));
  const node = DATA.nodes.find(x => x.id === id);
  if (node && node.x != null) { const k = Math.max(1, d3.zoomTransform(svg.node()).k); svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(W/2 - node.x*k, H/2 - node.y*k).scale(k)); }
  location.hash = id;
}
function closePanel(){ panel.classList.remove('open'); selected = null; paint(); history.replaceState(null,'',' '); }
window.closePanel = closePanel;
if (location.hash && byId.has(location.hash.slice(1))) setTimeout(() => openDoc(location.hash.slice(1)), 800);
paint();
</script>
</body>
</html>
"""


def main() -> int:
    import datetime as dt
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__BUILT__", dt.datetime.now().strftime("%Y-%m-%d %H:%M")))
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: 노드 {len(data['nodes'])}, 링크 {len(data['links'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
