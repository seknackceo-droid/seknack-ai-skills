#!/usr/bin/env python3
"""Validate numbered 16:9 PNG pages and build a metadata-minimized PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


PAGE_RE = re.compile(r"^(\d+)(?:[-_].*)?\.png$", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="AIエージェント導入提案")
    parser.add_argument("--expected-pages", type=int)
    return parser.parse_args()


def numbered_pages(page_dir: Path) -> list[tuple[int, Path]]:
    if not page_dir.is_dir():
        raise SystemExit(f"pages directory not found: {page_dir}")
    pages: list[tuple[int, Path]] = []
    for path in page_dir.iterdir():
        match = PAGE_RE.match(path.name)
        if match:
            pages.append((int(match.group(1)), path))
    pages.sort(key=lambda item: item[0])
    if not pages:
        raise SystemExit("no numbered PNG pages found")
    expected = list(range(1, len(pages) + 1))
    actual = [number for number, _ in pages]
    if actual != expected:
        raise SystemExit(f"page numbers must be contiguous from 1: {actual}")
    return pages


def main() -> None:
    args = parse_args()
    try:
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise SystemExit(
            "Pillow, reportlab and pypdf are required. Use the bundled Codex "
            "workspace Python or install these packages in the active environment."
        ) from exc

    pages = numbered_pages(args.pages.resolve())
    if args.expected_pages is not None and len(pages) != args.expected_pages:
        raise SystemExit(
            f"expected {args.expected_pages} pages, found {len(pages)}"
        )

    image_hashes: set[str] = set()
    page_records: list[dict[str, object]] = []
    width = height = None
    temp_root = Path(tempfile.mkdtemp(prefix="aisetup-proposal-"))
    clean_pages: list[Path] = []

    try:
        for number, source in pages:
            source_hash = sha256(source)
            if source_hash in image_hashes:
                raise SystemExit(f"duplicate page image detected: {source.name}")
            image_hashes.add(source_hash)

            with Image.open(source) as image:
                if image.format != "PNG":
                    raise SystemExit(f"not a PNG image: {source.name}")
                current_width, current_height = image.size
                if current_width * 9 != current_height * 16:
                    raise SystemExit(
                        f"page is not exact 16:9: {source.name} "
                        f"({current_width}x{current_height})"
                    )
                if width is None:
                    width, height = current_width, current_height
                elif (current_width, current_height) != (width, height):
                    raise SystemExit(
                        f"page dimensions differ: {source.name} "
                        f"({current_width}x{current_height}) != ({width}x{height})"
                    )
                clean = temp_root / f"{number:02d}.png"
                image.convert("RGB").save(clean, format="PNG", optimize=True)
                clean_pages.append(clean)
                page_records.append(
                    {
                        "page": number,
                        "file": source.name,
                        "width": current_width,
                        "height": current_height,
                        "sha256": source_hash,
                    }
                )

        args.output = args.output.resolve()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        draft_pdf = temp_root / "draft.pdf"
        pdf_width, pdf_height = 960, 540
        pdf = canvas.Canvas(
            str(draft_pdf), pagesize=(pdf_width, pdf_height), pageCompression=1
        )
        for clean in clean_pages:
            pdf.drawImage(
                ImageReader(str(clean)),
                0,
                0,
                width=pdf_width,
                height=pdf_height,
                preserveAspectRatio=True,
                anchor="c",
            )
            pdf.showPage()
        pdf.save()

        reader = PdfReader(str(draft_pdf))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({"/Title": args.title})
        with args.output.open("wb") as stream:
            writer.write(stream)

        final_reader = PdfReader(str(args.output))
        if len(final_reader.pages) != len(pages):
            raise SystemExit(
                f"PDF page mismatch: {len(final_reader.pages)} != {len(pages)}"
            )
        metadata = final_reader.metadata or {}
        sensitive = {
            key: str(value)
            for key, value in metadata.items()
            if key in {"/Author", "/Creator", "/Subject", "/Keywords"}
            and str(value).strip()
        }
        if sensitive:
            raise SystemExit(f"sensitive PDF metadata remains: {sensitive}")

        manifest = {
            "title": args.title,
            "page_count": len(pages),
            "dimensions": {"width": width, "height": height, "ratio": "16:9"},
            "pages": page_records,
            "pdf": {
                "file": args.output.name,
                "sha256": sha256(args.output),
                "bytes": args.output.stat().st_size,
            },
        }
        manifest_path = args.output.with_suffix(".manifest.json")
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
