"""Property-based tests for spears.scanner.

The scanner's correctness has two failure modes that matter:
  - Missing an anchor: produces a false positive in audit (claims a Complete
    REQ has no implementation when it does).
  - Visiting pruned dirs: blows up the runtime on real projects.

Both are covered here.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from spears.scanner import (
    DEFAULT_PRUNE_DIRS,
    find_mentions,
    is_anchor_path,
    iter_text_files,
)
from tests.strategies import req_ids


safe_segments = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_",
    min_size=1,
    max_size=8,
)


@given(
    st.lists(safe_segments, min_size=0, max_size=4),
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_.", min_size=1, max_size=12),
)
def test_paths_outside_specs_are_anchors(tmp_path_factory, segments, filename):
    assume(filename and not filename.startswith("."))
    assume("specs" not in segments)
    root = tmp_path_factory.mktemp("root")
    target_dir = root.joinpath(*segments) if segments else root
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / filename
    file_path.write_text("hello", encoding="utf-8")
    assert is_anchor_path(file_path, root) is True


@given(
    st.lists(safe_segments, min_size=0, max_size=3),
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_.", min_size=1, max_size=12),
)
def test_paths_inside_specs_are_never_anchors(tmp_path_factory, segments, filename):
    assume(filename and not filename.startswith("."))
    root = tmp_path_factory.mktemp("root")
    target_dir = root / "specs"
    for seg in segments:
        target_dir = target_dir / seg
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / filename
    file_path.write_text("hello", encoding="utf-8")
    assert is_anchor_path(file_path, root) is False


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(st.sets(st.sampled_from(sorted(DEFAULT_PRUNE_DIRS)), min_size=1, max_size=4))
def test_iter_text_files_skips_pruned_dirs(tmp_path_factory, pruned):
    root = tmp_path_factory.mktemp("root")
    # Sentinel file in a normal dir, must be visited.
    (root / "src").mkdir()
    sentinel = root / "src" / "keep.py"
    sentinel.write_text("# keep", encoding="utf-8")
    # A file under each pruned dir, must NOT be visited.
    forbidden_files = []
    for name in pruned:
        d = root / name / "deep"
        d.mkdir(parents=True)
        f = d / "skip.py"
        f.write_text("# skip", encoding="utf-8")
        forbidden_files.append(f.resolve())
    visited = {p.resolve() for p in iter_text_files(root)}
    assert sentinel.resolve() in visited
    for forbidden in forbidden_files:
        assert forbidden not in visited, forbidden


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(req_ids, min_size=1, max_size=6, unique=True),
)
def test_find_mentions_recovers_every_embedded_id(tmp_path_factory, ids):
    root = tmp_path_factory.mktemp("root")
    code_dir = root / "src"
    code_dir.mkdir()
    body = "\n".join(f"// {rid}: code anchor" for rid in ids)
    (code_dir / "anchors.py").write_text(body, encoding="utf-8")
    mentions = find_mentions(root)
    for rid in ids:
        assert rid in mentions, (rid, list(mentions))
        assert any(m.path.name == "anchors.py" for m in mentions[rid])
