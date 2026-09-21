"""Turn an official ComfyUI workflow template into a local, ready-to-run one.

Why this exists: official templates reference the *repackaged* checkpoint names
(often an int8/convrot variant) and example input images that are NOT bundled.
Handing such a template to a user produces a graph that loads fine and then
fails — a missing model file, or an error badge on LoadImage.

This script does three things:
  1. rewrites model filenames throughout the template (plain text replace, so
     properties.models[].url, widgets_values_named and the MarkdownNote
     documentation all stay consistent)
  2. optionally downloads the template's referenced example input images into
     <comfy>/input/, via jsdelivr (raw.githubusercontent.com is frequently
     unreachable from CN links)
  3. verifies the result: old names gone, new names present, layout intact,
     every downloaded image has valid PNG magic

Writes UI/save format (NOT API format) so the user gets a laid-out graph.

Usage::

    python localize_template.py \
        --template-json <path to template .json> \
        --out-dir  "D:/.../ComfyUI/user/default/workflows" \
        --out-name "My Local Workflow.json" \
        --rename old_int8.safetensors=new_bf16.safetensors \
        --rename old_te_int8.safetensors=new_te_bf16.safetensors \
        --fetch-images "D:/.../ComfyUI/input"

Get a template .json out of the installed wheel::

    python -c "import zipfile,glob,os; \
      w=glob.glob(os.path.expandvars(r'%LOCALAPPDATA%/../..')+'/**/comfyui_workflow_templates_json',recursive=True)" 

    # simpler: the package is importable from the ComfyUI python
    python -c "import comfyui_workflow_templates_json, os; \
      print(os.path.dirname(comfyui_workflow_templates_json.__file__))"
"""
import argparse
import json
import os
import re
import sys
import urllib.request

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# jsdelivr mirrors a GitHub repo; raw.githubusercontent.com is often blocked.
GITHUB_RAW = "https://raw.githubusercontent.com/{org}/{repo}/refs/heads/{branch}/{path}"
JSDELIVR = "https://cdn.jsdelivr.net/gh/{org}/{repo}@{branch}/{path}"


def find_image_urls(text):
    """Pull example-input-image URLs out of the template's markdown notes."""
    pat = r'https://raw\.githubusercontent\.com/Comfy-Org/([\w.-]+)/refs/heads/([\w.-]+)/([^"\')\s]+?\.(?:png|jpg|jpeg|webp))'
    return re.findall(pat, text)


def http_get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as r:
        return r.read()


def fetch_images(text, input_dir, force=False):
    """Download every referenced example image; verify PNG/JPG magic."""
    os.makedirs(input_dir, exist_ok=True)
    results = []
    seen = set()
    for repo, branch, path in find_image_urls(text):
        name = os.path.basename(path)
        if name in seen:
            continue
        seen.add(name)
        dest = os.path.join(input_dir, name)
        if os.path.exists(dest) and not force and os.path.getsize(dest) > 0:
            results.append((name, "exists", os.path.getsize(dest)))
            continue
        data = None
        urls = [JSDELIVR.format(org="Comfy-Org", repo=repo, branch=branch, path=path),
                GITHUB_RAW.format(org="Comfy-Org", repo=repo, branch=branch, path=path)]
        errs = []
        for u in urls:
            try:
                data = http_get(u)
                break
            except Exception as e:
                errs.append(f"{u.split('/')[2]}: {type(e).__name__}")
        if data is None:
            results.append((name, "FAIL " + "; ".join(errs), 0))
            continue
        # A blocked fetch can return an HTML error page that would silently
        # "succeed" as a file; reject anything without a real image signature.
        if not (data.startswith(PNG_MAGIC) or data[:2] == b"\xff\xd8"):
            results.append((name, "BAD-MAGIC (not an image)", len(data)))
            continue
        with open(dest, "wb") as f:
            f.write(data)
        results.append((name, "downloaded", len(data)))
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template-json", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--out-name", default=None)
    ap.add_argument("--rename", action="append", default=[],
                    metavar="OLD=NEW", help="repeatable; plain text replace")
    ap.add_argument("--fetch-images", metavar="INPUT_DIR", default=None,
                    help="download referenced example images into this dir")
    ap.add_argument("--force-images", action="store_true")
    args = ap.parse_args()

    raw = open(args.template_json, encoding="utf-8").read()

    renames = []
    for spec in args.rename:
        if "=" not in spec:
            print(f"[ERROR] --rename needs OLD=NEW, got {spec!r}", file=sys.stderr)
            return 2
        old, new = spec.split("=", 1)
        renames.append((old.strip(), new.strip()))

    # Replace on the raw text, not a walk of widgets_values: the filename also
    # occurs in properties.models[].url, widgets_values_named, and the notes.
    # Track which OLD names actually matched: a rename that hit nothing means the
    # template did not reference what the caller thought it did, and silently
    # reporting OK there would hand over a workflow still pointing at a missing
    # file. That is the exact failure this script exists to prevent.
    unmatched = []
    for old, new in renames:
        if old not in raw:
            unmatched.append(old)
            continue
        raw = raw.replace(old, new)

    try:
        wf = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] template did not survive replacement as JSON: {e}", file=sys.stderr)
        return 1

    has_layout = all(k in wf for k in ("nodes", "links", "version"))
    if not has_layout:
        print("[ERROR] template is API format (no nodes/links/version). Handing this "
              "to a user yields overlapping nodes; start from the save-format "
              "template instead.", file=sys.stderr)
        return 1

    os.makedirs(args.out_dir, exist_ok=True)
    out_name = args.out_name or os.path.basename(args.template_json)
    out_path = os.path.join(args.out_dir, out_name)
    json.dump(wf, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    final = open(out_path, encoding="utf-8").read()
    leftover = [o for o, _ in renames if o in final]
    present = [n for _, n in renames if n in final]

    print(f"wrote {out_path}")
    print(f"  layout intact : {has_layout}")
    print(f"  stale names   : {leftover if leftover else 'none'}")
    print(f"  new names in  : {present}")

    rc = 0
    if unmatched:
        for o in unmatched:
            print(f"[ERROR] rename source not found in template: {o}", file=sys.stderr)
        print("[ERROR] those --rename entries did nothing; the workflow still points "
              "at whatever the template originally used. Re-check the exact "
              "filename in the template before assuming it was rewritten.",
              file=sys.stderr)
        rc = 1
    if not renames:
        print("[WARN] no --rename given: model filenames are whatever the template "
              "shipped with, which is frequently NOT what is on this machine.",
              file=sys.stderr)
    if leftover:
        print("[ERROR] stale filename survived replacement", file=sys.stderr)
        rc = 1

    if args.fetch_images:
        print(f"fetching example images -> {args.fetch_images}")
        for name, status, size in fetch_images(raw, args.fetch_images, args.force_images):
            print(f"  {name:42s} {status:10s} {size}")
            if status.startswith(("FAIL", "BAD-MAGIC")):
                rc = 1

    print("OK" if rc == 0 else "COMPLETED WITH ERRORS")
    return rc


if __name__ == "__main__":
    sys.exit(main())
