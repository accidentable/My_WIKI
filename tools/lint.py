"""해커톤 지식 위키 점검 스크립트.

1층: 결정적 검사 (LLM 없음) — 링크, 인덱스, 머리말, sources 경로
2층: 판단 검사 (OpenAI API) — 중복 개념, 모순 서술, 원자료 대비 누락

사용:
    python tools/lint.py            # 1층만
    python tools/lint.py --llm      # 1층 + 2층
    python tools/lint.py --llm --commit   # 결과를 log.md에 붙이고 git commit/push

환경변수:
    OPENAI_API_KEY   필수(--llm 사용 시)
    LINT_MODEL       기본 gpt-5 (사용 가능한 최신 추론 모델로 바꿔 쓸 것)
    LINT_EFFORT      기본 high
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW_DONE = ROOT / "raw" / "done"
LOG = ROOT / "log.md"
INDEX = WIKI / "index.md"
FOLDERS = {"projects": "project", "concepts": "concept", "lessons": "lesson"}
FM_REQUIRED = ["title", "type", "created", "updated", "sources", "tags"]
LINK_RE = re.compile(r"\[\[([^\]|#]+)")


# ---------- 공통 ----------

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def all_docs() -> list[Path]:
    return sorted(p for f in FOLDERS for p in (WIKI / f).glob("*.md"))


def frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def parse_list(v: str) -> list[str]:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


# ---------- 1층: 결정적 검사 ----------

def deterministic() -> list[str]:
    issues: list[str] = []
    docs = all_docs()
    names = {p.stem for p in docs}
    index_text = read(INDEX) if INDEX.exists() else ""
    indexed = set(LINK_RE.findall(index_text))

    for p in docs:
        rel = p.relative_to(ROOT).as_posix()
        text = read(p)
        fm = frontmatter(text)
        if fm is None:
            issues.append(f"머리말 없음: {rel}")
        else:
            for k in FM_REQUIRED:
                if k not in fm or not fm[k]:
                    issues.append(f"머리말 필드 누락 [{k}]: {rel}")
            expected = FOLDERS[p.parent.name]
            if fm.get("type") != expected:
                issues.append(f"type 불일치 (기대 {expected}, 실제 {fm.get('type')}): {rel}")
            for src in parse_list(fm.get("sources", "")):
                if not (ROOT / src).exists():
                    issues.append(f"sources 경로 없음 [{src}]: {rel}")
        for link in set(LINK_RE.findall(text)):
            if link not in names:
                issues.append(f"끊어진 링크 [[{link}]]: {rel}")
        if p.stem not in indexed:
            issues.append(f"인덱스 미등록: {rel}")

    for link in indexed - names:
        issues.append(f"인덱스에 있으나 파일 없음: [[{link}]]")
    return issues


# ---------- 2층: LLM 판단 검사 ----------

def _recent_ingested(n: int = 8) -> list[Path]:
    """log.md 의 최근 ingest 항목에서 '신규:' 문서를 뽑는다."""
    if not LOG.exists():
        return []
    picked: list[Path] = []
    for line in reversed(read(LOG).splitlines()):
        m = re.search(r"신규:\s*(projects|concepts|lessons)/([\w-]+)", line)
        if m:
            p = WIKI / m.group(1) / f"{m.group(2)}.md"
            if p.exists() and p not in picked:
                picked.append(p)
        if len(picked) >= n:
            break
    return picked


def llm_review(model: str, effort: str) -> str:
    from openai import OpenAI  # 지연 임포트: --llm 없을 땐 필요 없음

    client = OpenAI()
    index_text = read(INDEX)
    concepts = sorted((WIKI / "concepts").glob("*.md"))
    concept_heads = []
    for p in concepts:
        t = read(p)
        fm = frontmatter(t) or {}
        body = t[t.find("\n---", 3) + 4:] if fm else t
        concept_heads.append(f"### {p.stem}\ntitle: {fm.get('title','')}\n{body[:700].strip()}\n")

    recent = _recent_ingested()
    recent_blocks = []
    for p in recent:
        t = read(p)
        fm = frontmatter(t) or {}
        srcs = []
        for s in parse_list(fm.get("sources", ""))[:3]:
            sp = ROOT / s
            if sp.exists():
                srcs.append(f"--- 원자료 {s} (앞 6000자) ---\n{read(sp)[:6000]}")
        recent_blocks.append(
            f"## 문서 {p.relative_to(ROOT).as_posix()}\n{t[:8000]}\n\n" + "\n".join(srcs)
        )

    prompt = f"""너는 개인 지식 위키의 점검자다. 아래 자료를 읽고 다음 세 가지만 보고하라. 없는 문제를 만들지 마라.

A. 중복 개념: concept 문서들 중 같은 개념을 다루어 병합해야 할 쌍. 서로 다른 개념이면 보고하지 않는다. 각 쌍마다 "왜 같은가" 한 문장.
B. 모순: 위키 문서들 사이, 또는 한 문서 안에서 서로 어긋나는 사실 서술. 문서명과 어긋나는 두 문장을 인용.
C. 원자료 대비 누락/왜곡: 최근 넣은 문서가 원자료의 중요한 사실을 빠뜨렸거나 다르게 옮긴 곳. 원자료 문장과 위키 문장을 나란히.

출력은 한국어 마크다운 불릿. 항목이 없으면 "없음"이라고만 쓴다. 자동 수정 제안은 하되, 수정 자체를 지시하지 마라.

# 인덱스
{index_text}

# concept 문서 요약 (각 앞부분)
{chr(10).join(concept_heads)}

# 최근 넣은 문서와 그 원자료
{chr(10).join(recent_blocks)}
"""
    resp = client.responses.create(
        model=model,
        reasoning={"effort": effort},
        input=prompt,
    )
    return resp.output_text.strip()


# ---------- 출력 / 커밋 ----------

def append_log(det: list[str], llm: str | None, model: str | None) -> None:
    today = dt.date.today().isoformat()
    lines = [f"\n## {today} lint: tools/lint.py"]
    lines.append(f"- 결정적 검사: {'문제 없음' if not det else f'{len(det)}건'}")
    lines += [f"  - {i}" for i in det]
    if llm is not None:
        lines.append(f"- LLM 검사 ({model}):")
        lines += ["  " + l if l else "" for l in llm.splitlines()]
    lines.append("- 도구: tools/lint.py (openai api)")
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="OpenAI API로 2층 검사 실행")
    ap.add_argument("--commit", action="store_true", help="log.md 갱신 후 git commit/push")
    args = ap.parse_args()

    det = deterministic()
    print("== 결정적 검사 ==")
    print("문제 없음" if not det else "\n".join(det))

    llm_out = None
    model = None
    if args.llm:
        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY 가 없습니다.", file=sys.stderr)
            return 2
        model = os.environ.get("LINT_MODEL", "gpt-5")
        effort = os.environ.get("LINT_EFFORT", "high")
        print(f"\n== LLM 검사 ({model}, effort={effort}) ==")
        llm_out = llm_review(model, effort)
        print(llm_out)

    if args.commit:
        git("pull", "-q")
        append_log(det, llm_out, model)
        git("add", "log.md")
        git("commit", "-q", "-m", f"lint: {dt.date.today().isoformat()} [tools/lint.py]")
        git("push", "-q")
        print("\nlog.md 갱신 및 push 완료")
    return 1 if det else 0


if __name__ == "__main__":
    sys.exit(main())
