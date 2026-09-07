#!/usr/bin/env python3
"""Split rpdd.zdd into publishable chunks, and verify them.

The whole file is 104,857,600 bytes — exactly 100 MiB, which is exactly
GitHub's hard limit for a single file, so it cannot be published whole
whatever anyone thinks of the licensing. It has to be chunked.

The chunk size is not arbitrary. Pavlicek's own tooling counts in 64K-deal
blocks ("160 = all deals"), and 65,536 deals is four of the deal generator's
16,384-deal seed groups. So a chunk boundary is also a seed boundary: a reader
that wants deals from chunk N can seed the generator from chunk N alone and
needs nothing before it. Any other size would force a reader to fetch a
neighbour to find where it stands.

    scripts/split-zdd.py split    # rpdd.zdd -> data/zdd/*.zdd + manifest
    scripts/split-zdd.py verify   # check the chunks against rpdd.zdd
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "rpdd.zdd"
OUT = ROOT / "data" / "zdd"
MANIFEST = ROOT / "data" / "manifest.json"

TABLE_LEN = 10          # bytes per .zdd record
DEALS_PER_GROUP = 16384  # the generator re-seeds here
GROUPS_PER_CHUNK = 4     # Pavlicek's 64K block
DEALS_PER_CHUNK = DEALS_PER_GROUP * GROUPS_PER_CHUNK
CHUNK_BYTES = DEALS_PER_CHUNK * TABLE_LEN
TOTAL_DEALS = 10_485_760


def chunks(data):
    for index in range(0, len(data), CHUNK_BYTES):
        yield index // CHUNK_BYTES, data[index:index + CHUNK_BYTES]


def split():
    if not SOURCE.exists():
        sys.exit(f"{SOURCE} not found. Unzip rpdd.zip from rpbridge.net here.")
    data = SOURCE.read_bytes()
    expected = TOTAL_DEALS * TABLE_LEN
    if len(data) != expected:
        sys.exit(f"{SOURCE} is {len(data):,} bytes, expected {expected:,}")

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for number, chunk in chunks(data):
        name = f"rpdd-{number:03d}.zdd"
        (OUT / name).write_bytes(chunk)
        entries.append({
            "file": name,
            "first_deal": number * DEALS_PER_CHUNK,
            "deals": len(chunk) // TABLE_LEN,
            "bytes": len(chunk),
            "sha256": hashlib.sha256(chunk).hexdigest(),
        })

    MANIFEST.write_text(json.dumps({
        "source": "rpdd.zdd from rpdd.zip, rpbridge.net, (c) 2007 Richard Pavlicek",
        "record_bytes": TABLE_LEN,
        "deals_per_chunk": DEALS_PER_CHUNK,
        "total_deals": TOTAL_DEALS,
        "note": ("A chunk holds four of the deal generator's 16,384-deal seed "
                 "groups, so its first deal is always a seed boundary."),
        "sha256_whole": hashlib.sha256(data).hexdigest(),
        "chunks": entries,
    }, indent=2) + "\n")
    print(f"wrote {len(entries)} chunks of {CHUNK_BYTES:,} bytes to "
          f"{OUT.relative_to(ROOT)}/ and data/manifest.json")


def verify():
    manifest = json.loads(MANIFEST.read_text())
    bad = 0
    for entry in manifest["chunks"]:
        path = OUT / entry["file"]
        if not path.exists():
            print(f"MISSING {entry['file']}")
            bad += 1
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            print(f"MISMATCH {entry['file']}")
            bad += 1
    if bad:
        sys.exit(f"{bad} chunk(s) wrong")
    joined = b"".join((OUT / e["file"]).read_bytes() for e in manifest["chunks"])
    whole = hashlib.sha256(joined).hexdigest()
    if whole != manifest["sha256_whole"]:
        sys.exit("chunks are individually right but do not rejoin correctly")
    print(f"{len(manifest['chunks'])} chunks verified, and they rejoin to the "
          f"whole file's digest")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "split"
    {"split": split, "verify": verify}[action]()
