#!/usr/bin/env python3
"""Permanent fail-closed tombstone for the legacy opportunity runtime.

Schema/workspace ``0.1`` is historical and globally quarantined.  This module
keeps the former public entry-point names only so callers receive one stable,
machine-checkable refusal instead of accidentally running the retired state,
permission, or artifact-generation semantics.

There is deliberately no path-based marker, screening override, structural
"valid" result, commercial status view, permission view, or successor runtime
in this module.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, NoReturn


SCHEMA_VERSION = "0.1"
WORKSPACE_VERSION = "0.1"
LEGACY_AUTHORITY_STATUS = "LEGACY_UNQUALIFIED"
LEGACY_QUARANTINE_CODE = "LEGACY_SCHEMA_WORKSPACE_0_1_QUARANTINED"
LEGACY_QUARANTINE_REASON = (
    f"{LEGACY_QUARANTINE_CODE}: legacy schema/workspace 0.1 is globally "
    "tombstoned and has no current authority"
)


class LegacyQuarantineError(RuntimeError):
    """Stable refusal raised by every retained legacy runtime entry point."""


def _raise_legacy_quarantine() -> NoReturn:
    raise LegacyQuarantineError(LEGACY_QUARANTINE_REASON)


def validate_record(record: Any, location: str = "record") -> NoReturn:
    """Retired validator entry point; no structural qualification is emitted."""

    _raise_legacy_quarantine()


def validate_workspace(workspace: Path) -> NoReturn:
    """Retired workspace validator; it refuses before inspecting ``workspace``."""

    _raise_legacy_quarantine()


def init_workspace(workspace: Path) -> NoReturn:
    """Retired initializer; it refuses before inspecting or creating a path."""

    _raise_legacy_quarantine()


def add_record(workspace: Path, source_path: Path) -> NoReturn:
    """Retired mutation API; it refuses before reading either path."""

    _raise_legacy_quarantine()


def status_report(workspace: Path) -> NoReturn:
    """Retired status API; legacy records cannot emit commercial state."""

    _raise_legacy_quarantine()


def derive_opportunity_status(
    opportunity_id: str,
    index: dict[str, dict[str, Any]],
) -> NoReturn:
    """Retired derivation API; caller-supplied records cannot lift quarantine."""

    _raise_legacy_quarantine()


def external_permission_for_probe(probe: dict[str, Any]) -> NoReturn:
    """Retired permission API; legacy fields cannot confer authority."""

    _raise_legacy_quarantine()


def make_harness(
    workspace: Path,
    opportunity_id: str,
    probe_id: str,
    mode: str,
) -> NoReturn:
    """Retired artifact API; both former modes are permanently quarantined."""

    _raise_legacy_quarantine()


def main(argv: list[str] | None = None) -> int:
    # The legacy executable is a tombstone, not a parser-backed runtime.  Even
    # malformed arguments and former help paths receive the same refusal before
    # argv is inspected.
    try:
        _raise_legacy_quarantine()
    except LegacyQuarantineError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
