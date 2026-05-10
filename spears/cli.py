"""argparse-driven CLI entry point for the spears tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spears import __version__
from spears import audit as audit_mod
from spears import lint as lint_mod
from spears.audit import ALL_STATUSES


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
            "comma-separated list of statuses to report on. "
            "Allowed: " + ",".join(sorted(ALL_STATUSES))
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


class UsageError(ValueError):
    """Raised by argument parsing helpers; caller maps to exit code 2."""


def _parse_status_arg(value: str | None) -> set[str] | None:
    """Parse, normalise, and validate a --status value.

    Returns None when no value was given. Raises UsageError when any token
    is unknown so the CLI can exit with code 2 rather than silently
    producing an empty report.
    """
    if not value:
        return None
    tokens = {s.strip().lower() for s in value.split(",") if s.strip()}
    unknown = tokens - ALL_STATUSES
    if unknown:
        raise UsageError(
            f"unknown status(es): {','.join(sorted(unknown))}. "
            f"Allowed: {','.join(sorted(ALL_STATUSES))}"
        )
    return tokens


def _validate_root(root: Path) -> str | None:
    """Return an error message if ``root`` isn't a directory, else None."""
    if not root.exists():
        return f"root {root} does not exist"
    if not root.is_dir():
        return f"root {root} is not a directory"
    return None


def _cmd_audit(args: argparse.Namespace) -> int:
    root: Path = args.root
    err = _validate_root(root)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    try:
        statuses = _parse_status_arg(args.status)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
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
    err = _validate_root(root)
    if err:
        print(f"error: {err}", file=sys.stderr)
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
