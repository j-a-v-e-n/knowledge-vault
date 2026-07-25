#!/usr/bin/env python3
"""Refresh hashes for the already-declared ground-truth artifact set.

This command never adds or removes review scope. It only updates hashes after
an intentional candidate edit, so scope changes remain explicit reviewable
patches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "governance" / "GROUND_TRUTH_MANIFEST_V1.json"


def repository_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"cannot resolve repository root: {completed.stdout.strip()}"
        )
    return Path(completed.stdout.strip()).resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when a declared hash is stale; do not rewrite the manifest.",
    )
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = document.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SystemExit("ground-truth artifacts must be a nonempty list")
    repo_root = repository_root()
    changed: list[str] = []
    seen: set[tuple[str, str]] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise SystemExit("ground-truth artifact must be an object")
        relative = artifact.get("path")
        scope = artifact.get("scope", "project")
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or scope not in {"project", "repository"}
        ):
            raise SystemExit(f"unsafe ground-truth artifact: {artifact!r}")
        identity = (scope, relative)
        if identity in seen:
            raise SystemExit(f"duplicate ground-truth artifact: {identity}")
        seen.add(identity)
        path = (repo_root if scope == "repository" else PROJECT_ROOT) / relative
        if not path.is_file():
            raise SystemExit(f"missing ground-truth artifact: {scope}:{relative}")
        observed = sha256(path)
        if artifact.get("sha256") != observed:
            changed.append(f"{scope}:{relative}")
            artifact["sha256"] = observed
    expected_order = sorted(
        artifacts,
        key=lambda item: (item.get("scope", "project"), item["path"]),
    )
    if artifacts != expected_order:
        raise SystemExit("ground-truth artifacts are not stably sorted")
    if args.check:
        if changed:
            raise SystemExit(
                "stale ground-truth hashes: " + ", ".join(changed)
            )
        print("ground-truth manifest: PASS")
        return 0
    MANIFEST.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ground-truth manifest refreshed: {len(changed)} hash(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
