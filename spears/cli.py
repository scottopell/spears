"""argparse-driven CLI entry point for the spears tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spears import __version__
from spears import audit as audit_mod
from spears import lint as lint_mod


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="spears",
        description="spEARS specification CLI: audit and lint requirements specs.",
    )
    p.add_argument("--version", action="version", version=f"spears {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    audit_p = sub.add_parser(
        "audit",
        help="find REQs declared in specs but not anchored in code",
        description=(
            "Status-aware unanchored detector. By default reports only ✅ "
            "Complete REQs that have no mention outside specs/. Pass "
            "--all-statuses for the full unanchored set, or --status "
            "complete,in-progress to filter explicitly."
        ),
    )
    audit_p.add_argument("--root", type=Path, default=Path.cwd())
    audit_p.add_argument(
        "--spec",
        action="append",
        dest="specs",
        help="restrict to a spec directory name; repeatable",
    )
    audit_p.add_argument(
        "--all-statuses",
        action="store_true",
        help="report unanchored REQs regardless of status (verbose)",
    )
    audit_p.add_argument(
        "--status",
        help=(
            "comma-separated list of statuses to report on "
            "(complete,in-progress,planned,not-started,manual,unknown)"
        ),
    )

    lint_p = sub.add_parser(
        "lint",
        help="check spec quality rules",
        description=(
            "Lint specs for: R1 user-verb titles, R2 Rationale presence, "
            "R3 status-table column shape, R4 Transparency Contract 1:1."
        ),
    )
    lint_p.add_argument("--root", type=Path, default=Path.cwd())
    lint_p.add_argument(
        "--spec",
        action="append",
        dest="specs",
        help="restrict to a spec directory name; repeatable",
    )

    return p


def _parse_status_arg(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {s.strip() for s in value.split(",") if s.strip()}


def _cmd_audit(args: argparse.Namespace) -> int:
    root: Path = args.root
    if not root.exists():
        print(f"error: root {root} does not exist", file=sys.stderr)
        return 2
    statuses = _parse_status_arg(args.status)
    result = audit_mod.audit(
        root=root,
        spec_filter=args.specs,
        all_statuses=args.all_statuses,
        statuses=statuses,
    )
    sys.stdout.write(audit_mod.format_report(result, root))
    return 0 if result.ok else 1


def _cmd_lint(args: argparse.Namespace) -> int:
    root: Path = args.root
    if not root.exists():
        print(f"error: root {root} does not exist", file=sys.stderr)
        return 2
    result = lint_mod.lint(root=root, spec_filter=args.specs)
    sys.stdout.write(lint_mod.format_report(result, root))
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "audit":
        return _cmd_audit(args)
    if args.command == "lint":
        return _cmd_lint(args)
    parser.print_help()
    return 2
