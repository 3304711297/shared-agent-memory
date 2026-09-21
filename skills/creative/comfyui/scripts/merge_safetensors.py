"""Merge sharded safetensors into one file, byte-level, low memory.

Why this exists: HF diffusers repos ship weights as
``transformer/diffusion_pytorch_model-0000N-of-0000M.safetensors`` plus a
``*.safetensors.index.json``. ComfyUI has no index/weight_map support
anywhere, and ``comfy/diffusers_load.py`` only looks for ``unet/`` +
``text_encoder/model.safetensors``, so neither the single-file loaders nor
``DiffusersLoader`` can read such a folder. Merging locally avoids
re-downloading tens of GB of weights that are already on disk.

Reads each shard's JSON header, rebuilds one header with re-based
(8-byte aligned) data_offsets, then streams the data blocks with a fixed
buffer. Peak RSS is the buffer size (~64 MB), not the file size, so it
handles 14 GB shards on a normal machine.

Safety: refuses duplicate tensor keys across shards, verifies the final file
size equals 8 + header + data, and writes to ``.part`` before ``os.replace``.

Usage::

    # plan file: [{"out": "<dest.safetensors>", "shards": ["<a>", "<b>"]}, ...]
    python merge_safetensors.py plan.json

Afterwards, verify ComfyUI actually accepts the result before relying on it.
Dump the new header and confirm the detectors agree, using the portable
python from the ComfyUI root (header-only, loads no weights)::

    from safetensors import safe_open
    import comfy.model_detection as mdet

    class T:
        def __init__(s, shape, dtype): s.shape = shape; s.dtype = dtype

    with safe_open(path, framework="pt", device="cpu") as f:
        sd = {k: T(tuple(f.get_slice(k).get_shape()), torch.bfloat16) for k in f.keys()}
    print(mdet.detect_unet_config(sd, "", metadata={"format": "pt"}))

For a text encoder use ``comfy.sd.detect_te_model(proxy)`` instead. Both take
shape-only proxies, so this costs no GPU RAM. Confirm ``image_model`` matches
the expected architecture, then check the VAE separately: diffusers VAE naming
(``decoder.conv_in``) can be misdetected as a HunyuanVideo VAE, so the VAE
usually must come from the official ComfyUI repack rather than the diffusers
folder.
"""
import json
import os
import struct
import sys

BUF = 64 << 20


def read_header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        hdr = json.loads(f.read(n))
    return hdr, 8 + n


def merge(shard_paths, out_path, keep_metadata=True, progress=True):
    entries = []
    meta = None
    for p in shard_paths:
        hdr, base = read_header(p)
        if keep_metadata and meta is None and isinstance(hdr.get("__metadata__"), dict):
            meta = hdr["__metadata__"]
        for k, info in hdr.items():
            if k == "__metadata__":
                continue
            entries.append((k, info, p, base))

    keys = [e[0] for e in entries]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        raise ValueError("duplicate tensor keys across shards: %s" % sorted(dupes)[:5])

    new = {}
    if meta:
        new["__metadata__"] = meta
    offset = 0
    for k, info, _p, _b in entries:
        start, end = info["data_offsets"]
        size = end - start
        offset += (-offset) % 8
        new[k] = {
            "dtype": info["dtype"],
            "shape": info["shape"],
            "data_offsets": [offset, offset + size],
        }
        offset += size

    blob = json.dumps(new, separators=(",", ":")).encode("utf-8")
    blob += b" " * ((-len(blob)) % 8)
    data_total = offset

    tmp = out_path + ".part"
    written = 0
    with open(tmp, "wb") as out:
        out.write(struct.pack("<Q", len(blob)))
        out.write(blob)
        for k, info, p, base in entries:
            start, end = info["data_offsets"]
            size = end - start
            dst = new[k]["data_offsets"][0]
            if dst > written:
                out.write(b"\0" * (dst - written))
                written = dst
            with open(p, "rb") as f:
                f.seek(base + start)
                remaining = size
                while remaining:
                    chunk = f.read(min(BUF, remaining))
                    if not chunk:
                        raise IOError("short read in %s for %s" % (p, k))
                    out.write(chunk)
                    remaining -= len(chunk)
            written += size

    expect = 8 + len(blob) + data_total
    actual = os.path.getsize(tmp)
    if actual != expect:
        raise IOError("size mismatch: wrote %d expected %d" % (actual, expect))
    os.replace(tmp, out_path)
    if progress:
        print("  %-46s %d tensors  %.2f GB  OK"
              % (os.path.basename(out_path), len(entries), actual / 1e9), flush=True)
    return len(entries), actual


if __name__ == "__main__":
    plan = json.load(open(sys.argv[1]))
    for item in plan:
        print("merging ->", item["out"], flush=True)
        merge(item["shards"], item["out"])
