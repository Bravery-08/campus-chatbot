"""
Merge indented continuation lines into the previous non-indented line.

Example:
    line one
        continued text
    line two

Becomes:
    line one continued text
    line two
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


INDENT_RE = re.compile(r"^[ \t]+")


def merge_indented_lines(text: str) -> str:
    merged_lines: list[str] = []
    current_line: str | None = None

    lines = text.splitlines()
    total = len(lines)
    i = 0

    while i < total:
        raw_line = lines[i]
        if not raw_line.strip():
            if current_line is None:
                i += 1
                continue

            j = i + 1
            while j < total and not lines[j].strip():
                j += 1

            if j < total and INDENT_RE.match(lines[j]):
                i += 1
                continue

            merged_lines.append(current_line)
            current_line = None
            i += 1
            continue

        is_indented = bool(INDENT_RE.match(raw_line))
        clean = raw_line.strip()

        if current_line is None:
            current_line = clean
            i += 1
            continue

        if is_indented:
            current_line = f"{current_line} {clean}"
        else:
            merged_lines.append(current_line)
            current_line = clean
        i += 1

    if current_line is not None:
        merged_lines.append(current_line)

    return "\n".join(merged_lines) + "\n"


def process_file(path: Path) -> tuple[int, int]:
    original = path.read_text(encoding="utf-8")
    merged = merge_indented_lines(original)

    before = len(original.splitlines())
    after = len(merged.splitlines())

    path.write_text(merged, encoding="utf-8")
    return before, after


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge indented continuation lines into previous lines."
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="data.txt",
        help="Path to text file (default: data.txt in current directory).",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    before, after = process_file(path)
    print(f"Processed: {path}")
    print(f"Lines before: {before}")
    print(f"Lines after:  {after}")


if __name__ == "__main__":
    main()
