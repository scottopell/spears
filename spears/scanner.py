"""Walk a project tree and collect REQ-* mentions.

Uses os.walk with in-place dirname pruning: skipping large noise directories
(``.git``, ``node_modules`` and friends) at the dir level avoids stat/read
work on tens of thousands of files. The v1 prototype's 0.2s runtime depended
on this -- without pruning, a typical Node project crawl is dominated by
``node_modules``.
"""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from spears.parser import REQ_ID_RE

# Directories pruned at walk time. Names compared exactly; hidden dirs are
# pruned by a separate rule so we don't have to enumerate every `.foo` dir.
DEFAULT_PRUNE_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        "target",
        "out",
        "coverage",
        "venv",
        "env",
        "site-packages",
        "vendor",
    }
)

# Hidden directories we *do* want to traverse. Everything else starting with
# `.` is skipped.
ALLOW_HIDDEN: frozenset[str] = frozenset({".github"})

# File extensions skipped wholesale: binary or generated formats that would
# never carry a REQ anchor.
SKIP_EXTS: frozenset[str] = frozenset(
    {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
        ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
        ".so", ".o", ".a", ".dylib", ".dll", ".exe", ".bin", ".class", ".pyc", ".pyo",
        ".jar", ".war", ".ear",
        ".mp3", ".mp4", ".mov", ".avi", ".webm", ".ogg", ".wav", ".flac",
        ".lock",  # package lockfiles -- noisy and never carry anchors
    }
)

# Files larger than this are skipped to keep the scan bounded.
MAX_FILE_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class Mention:
    req_id: str
    path: Path
    line: int


def iter_text_files(
    root: Path,
    prune_dirs: Iterable[str] = DEFAULT_PRUNE_DIRS,
    extra_skip_paths: Iterable[Path] = (),
) -> Iterable[Path]:
    """Yield candidate text files under ``root``.

    Pruning happens in-place via ``dirnames[:] = ...`` so os.walk does not
    descend into noise directories.
    """
    prune = set(prune_dirs)
    skip_abs = {p.resolve() for p in extra_skip_paths}
    root_abs = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in prune
            and (not d.startswith(".") or d in ALLOW_HIDDEN)
        ]
        dir_abs = Path(dirpath)
        if dir_abs in skip_abs:
            dirnames[:] = []
            continue
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in SKIP_EXTS:
                continue
            path = dir_abs / name
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def find_mentions(
    root: Path,
    prune_dirs: Iterable[str] = DEFAULT_PRUNE_DIRS,
) -> dict[str, list[Mention]]:
    """Return REQ-id -> list of Mentions found anywhere under ``root``.

    Includes mentions inside spec markdown files; callers that want
    code-only anchors should filter with :func:`is_anchor_path`.
    """
    mentions: dict[str, list[Mention]] = defaultdict(list)
    for path in iter_text_files(root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, start=1):
                    for m in REQ_ID_RE.finditer(line):
                        mentions[m.group(0)].append(
                            Mention(req_id=m.group(0), path=path, line=lineno)
                        )
        except OSError:
            continue
    return dict(mentions)


def is_anchor_path(path: Path, root: Path) -> bool:
    """An anchor is any mention NOT inside <root>/specs/.

    Spec cross-references between specs are not anchors -- they are still
    "the spec system talking about itself". A real anchor is code, tests,
    docs, commit messages (via .git/COMMIT_EDITMSG, but .git is pruned),
    config -- anything outside the specs/ tree.
    """
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    parts = rel.parts
    return not (parts and parts[0] == "specs")
