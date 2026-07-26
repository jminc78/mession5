"""소설 목록·본문 로드 (로컬 MongoDB)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from settings import NOVELS_DIR


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def clean_novel_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def infer_title_from_stem(stem: str) -> str:
    title = re.sub(r"\([^)]*\)", "", stem).strip()
    return title or stem


@dataclass
class NovelDoc:
    file_stem: str
    title: str
    text: str
    author: str | None = None

    @property
    def char_count(self) -> int:
        return len(self.text)


def _from_inbox() -> list[NovelDoc]:
    docs: list[NovelDoc] = []
    if not NOVELS_DIR.exists():
        return docs
    for path in sorted(NOVELS_DIR.glob("*.txt")):
        text = clean_novel_text(path.read_text(encoding="utf-8", errors="ignore"))
        if len(text) < 100:
            continue
        stem = nfc(path.stem)
        docs.append(
            NovelDoc(
                file_stem=stem,
                title=infer_title_from_stem(stem),
                text=text,
            )
        )
    return docs


def load_novel_docs() -> list[NovelDoc]:
    try:
        from db import fetch_novels

        rows = fetch_novels()
        docs = []
        for row in rows:
            text = row.get("content") or ""
            if len(text) < 100:
                continue
            docs.append(
                NovelDoc(
                    file_stem=nfc(str(row["file_stem"])),
                    title=nfc(str(row["title"])),
                    text=text,
                    author=row.get("author"),
                )
            )
        if docs:
            return docs
    except Exception:
        pass
    return _from_inbox()


def find_novel(title: str) -> NovelDoc | None:
    docs = load_novel_docs()
    return next(
        (
            d
            for d in docs
            if title == d.title
            or title == d.file_stem
            or title in d.title
            or title in d.file_stem
        ),
        None,
    )
