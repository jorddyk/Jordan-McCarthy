from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

OUT = Path("sealed_output/truth/tracings")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "Barthel_Fa.png": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Barthel_Fa.png",
    "Rongorongo_F-a.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Rongorongo_F-a_-_Stephen-Chauvet_fragment.jpg",
    "Rongorongo_F-b.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/82/Rongorongo_F-b_-_Stephen-Chauvet_fragment.jpg",
}

manifest: dict[str, dict[str, str | int]] = {}
for name, url in SOURCES.items():
    req = urllib.request.Request(url, headers={"User-Agent": "RongorongoBlindTest/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
    path = OUT / name
    path.write_bytes(data)
    manifest[name] = {
        "url": url,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }

(OUT / "manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
)
print(json.dumps({"status": "tracings_fetched", "files": len(manifest)}, sort_keys=True))
