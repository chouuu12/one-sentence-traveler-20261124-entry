#!/usr/bin/env python3
"""Write one sentence explaining the modern internet to a traveler from 1800.

The sentence lives in line.txt next to this script (single source of truth).
This program reads it, checks it against the bounty gate (UTF-8 text of
1 to 200 characters, not only whitespace, a single sentence), and writes it
exactly -- no trailing newline -- to $MAKEFUN_OUTPUT_DIR/entry.txt
(or /output/entry.txt when that variable is not set), atomically via a
temporary file in the same directory.
"""

import os
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_sentence() -> str:
    text = (HERE / "line.txt").read_text(encoding="utf-8")
    if not text or text != text.strip() or text.endswith("\n"):
        raise ValueError("line.txt must hold exactly the sentence, no extra whitespace")
    if not 1 <= len(text) <= 200:
        raise ValueError(f"sentence must be 1-200 characters, got {len(text)}")
    if text.count(".") != 1 or not text.endswith("."):
        raise ValueError("sentence must be exactly one sentence ending in a period")
    return text


def main() -> None:
    sentence = load_sentence()
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.txt"
    fd, tmp_name = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(sentence)
        os.replace(tmp_name, out_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    text = out_path.read_text(encoding="utf-8")
    if text != sentence:
        raise ValueError("output does not match the sentence exactly")
    print(f"Wrote {len(text)} characters to {out_path}")


if __name__ == "__main__":
    main()
