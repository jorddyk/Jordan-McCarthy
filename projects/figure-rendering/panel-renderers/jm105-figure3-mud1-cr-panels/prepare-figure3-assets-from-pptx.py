#!/usr/bin/env python3
"""Extract the current Figure 3 A-H assets from the source PowerPoint.

Source mapping used for the successful 2026-07-20 Figure 3 bundle:
A=image1.png, B=image2.png, C=image3.svg, D=image4.svg,
E=image5.svg, F=image6.svg, G=image7.svg, H=image8.png.

The script writes source SVG/PDF files and raster PNGs expected by
render-figure3-improved-composite.py. It does not modify the PowerPoint.
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

import cairosvg
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pptx", required=True, help="Path to Fig3_McCarthy.pptx")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pptx = Path(args.pptx).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not pptx.is_file():
        raise FileNotFoundError(f"Figure 3 PowerPoint not found: {pptx}")

    output_dir.mkdir(parents=True, exist_ok=False)

    with tempfile.TemporaryDirectory(prefix="figure3-pptx-") as temp_name:
        temp_root = Path(temp_name)
        with zipfile.ZipFile(pptx, "r") as archive:
            archive.extractall(temp_root)

        media_root = temp_root / "ppt" / "media"
        panel_sources = {
            "A": media_root / "image1.png",
            "B": media_root / "image2.png",
            "C": media_root / "image3.svg",
            "D": media_root / "image4.svg",
            "E": media_root / "image5.svg",
            "F": media_root / "image6.svg",
            "G": media_root / "image7.svg",
            "H": media_root / "image8.png",
        }

        for panel, source in panel_sources.items():
            if not source.is_file():
                raise FileNotFoundError(
                    f"Expected PowerPoint media for Panel {panel} is missing: {source}"
                )

            if source.suffix.lower() == ".svg":
                shutil.copy2(source, output_dir / f"panel_{panel}.source.svg")
                cairosvg.svg2png(
                    url=str(source),
                    write_to=str(output_dir / f"panel_{panel}.png"),
                    output_width=2400,
                )
                cairosvg.svg2pdf(
                    url=str(source),
                    write_to=str(output_dir / f"panel_{panel}.source.pdf"),
                )
            else:
                shutil.copy2(source, output_dir / f"panel_{panel}.png")
                with Image.open(source) as image:
                    image.convert("RGB").save(
                        output_dir / f"panel_{panel}.source.pdf",
                        "PDF",
                        resolution=300.0,
                    )

    print(f"ASSETS_DIR={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
