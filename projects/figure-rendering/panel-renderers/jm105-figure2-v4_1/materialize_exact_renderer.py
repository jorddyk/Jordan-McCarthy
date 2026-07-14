#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

EXPECTED_SHA256 = "167ac8ffd306ce5e6fb234a4ed3c35eea5b8f2be7205b0df46c1b4f5b28ec593"
PART_GLOB = "exact_renderer_parts/render_JM105_Figure2_v4_1_no_overlap.py.part*"
OUTPUT_NAME = "render_JM105_Figure2_v4_1_no_overlap.py"


def main() -> int:
    root = Path(__file__).resolve().parent
    parts = sorted(root.glob(PART_GLOB))
    if len(parts) != 6:
        raise RuntimeError(f"Expected 6 exact renderer parts, found {len(parts)}: {parts}")
    payload = b"".join(path.read_bytes() for path in parts)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Renderer SHA256 mismatch: expected {EXPECTED_SHA256}, observed {digest}")
    output = root / OUTPUT_NAME
    output.write_bytes(payload)
    print(f"Wrote {output}")
    print(f"SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
