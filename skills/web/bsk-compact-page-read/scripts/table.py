#!/usr/bin/env python
"""jev snapshot.js 元素表 —— 给 bsk 用的紧凑页面读取层。

场景：用 jev 的 snapshot.js 把页面压成「编号控件表 + 可见文本」，代替（或先用它筛查）
`bsk observe` 的长文本树。实测体积比 0.14x–0.35x（见 SKILL.md 表格）。

依赖：bsk daemon 在跑、session 活跃、页面已加载。

用法：
    python table.py --session <id> --selectors
    python table.py --session <id> --no-text
    python table.py --session <id> --json --selectors
"""

import argparse
import json
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
SNAPSHOT_JS = HERE / "snapshot.js"
SELECTORS_JS = HERE / "selectors.js"


def action_space(actions):
    """One index per observed element; each operation has its own valid targets.

    Port of jev_ultrafast/model.py::action_space (MIT, browser-use).
    """
    elements, indices, targets, controls = [], {}, {}, {}
    operations = {"click": "CLICK", "fill": "TYPE_TEXT", "select": "SELECT"}
    for action in actions:
        kind = action["kind"]
        if kind not in operations:
            controls[action["id"].upper()] = action
            continue
        node = action["node"]
        if node not in indices:
            index = str(len(elements) + 1)
            indices[node] = index
            element = {k: action[k] for k in ("role", "value", "checked", "selected", "expanded") if k in action}
            element.update(index=index, label=action["label"].split(" \u2192 ")[0], operations=[])
            if kind == "select":
                element["value"] = action.get("current_value", "")
                element["options"] = []
            elements.append(element)
        index = indices[node]
        operation = operations[kind]
        group = targets.setdefault(operation, {})
        element = elements[int(index) - 1]
        if operation not in element["operations"]:
            element["operations"].append(operation)
        target = index
        if kind == "select":
            target = f"{index}:{len(element['options']) + 1}"
            element["options"].append({"index": target, "label": action["label"], "value": action["value"]})
        group[target] = action
    return elements, targets, controls


def _env():
    return {**os.environ.copy(), "BSK_AUTO_START": "0"}


def evaluate(session, expression, timeout=180):
    """Run JS in the active tab. argv list (no shell) => size/quoting safe."""
    p = subprocess.run(["bsk", "evaluate", "--session", session, expression],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=_env(), timeout=timeout)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    if p.returncode != 0:
        raise RuntimeError(f"bsk evaluate failed (exit {p.returncode}): {out[:400]}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def read_page(session, with_selectors=False):
    """Returns the compact table dict for the session's current page."""
    snap = evaluate(session, SNAPSHOT_JS.read_text(encoding="utf-8"))
    if not isinstance(snap, dict) or "actions" not in snap:
        raise RuntimeError(f"snapshot.js returned no page state: {str(snap)[:300]}")
    elements, targets, controls = action_space(snap["actions"])
    if with_selectors:
        probe = evaluate(session, SELECTORS_JS.read_text(encoding="utf-8"))
        smap = {str(k): v for k, v in (probe or {}).get("map", {}).items()}
        for e in elements:
            e["selector"] = smap.get(e["index"])
    return {
        "url": snap["url"],
        "title": snap["title"],
        "scroll": snap["scroll"],
        "text": snap["text"],
        "elements": elements,
        "targets": {k: sorted(v, key=lambda x: (len(x), x)) for k, v in targets.items()},
        "controls": sorted(controls),
        "omitted_actions": snap.get("omitted_actions", 0),
    }


def render(table, with_selectors=False, text_limit=1400):
    """Compact text rendering: what you actually hand to a model."""
    out = [f"URL {table['url']}", f"TITLE {table['title']}"]
    out.append(f"SCROLL y={table['scroll']['y']} h={table['scroll']['height']}")
    if table.get("omitted_actions"):
        out.append(f"NOTE {table['omitted_actions']} candidates truncated")
    for e in table["elements"]:
        ops = ",".join(e.get("operations", []))
        val = str(e.get("value", ""))[:24]
        out.append(f"[{e['index']}] {e.get('role','')} {e['label'][:60]} ={val} {{{ops}}}")
        if with_selectors and e.get("selector"):
            out.append(f"    SEL {e['selector']}")
    for op in sorted(table["targets"]):
        out.append(f"{op}: {' '.join(table['targets'][op])}")
    out.append(f"CONTROLS: {' '.join(table['controls'])}")
    text = table["text"]
    if text_limit and len(text) > text_limit:
        text = text[:text_limit] + f"... [+{len(table['text']) - text_limit} chars]"
    out.append("TEXT:")
    out.append(text)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True)
    ap.add_argument("--selectors", action="store_true",
                    help="attach CSS selectors usable by `bsk click --selector`")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--text-limit", type=int, default=1400)
    ap.add_argument("--no-text", action="store_true", help="drop the visible text")
    args = ap.parse_args()

    table = read_page(args.session, with_selectors=args.selectors)
    if args.no_text:
        table["text"] = ""
    if args.json:
        print(json.dumps(table, ensure_ascii=False, indent=1))
    else:
        print(render(table, args.selectors, args.text_limit))


if __name__ == "__main__":
    main()
