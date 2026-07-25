#!/usr/bin/env python3
"""Run one design-freeze mutation against an exact Git candidate.

The receipt is produced from the subprocesses this runner actually executes.
Callers must compare the process return code with ``runner_exit_code`` in the
receipt; a hand-written command or declared target exit is never authoritative.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
RUNNER_ID = "ids-design-freeze-attack-runner-v1"
RUNNER_RELATIVE = "scripts/run_design_freeze_attack.py"
VERIFIER_RELATIVE = "scripts/verify_governance.py"
SHA1 = re.compile(r"[0-9a-f]{40}")
PROBE_ID = re.compile(r"PROBE-[A-Z0-9][A-Z0-9-]{2,80}")

CANONICAL_ATTACKS: dict[str, dict[str, Any]] = {
    "ATTACK-PIT-ORACLE-INVERSION": {
        "target_path": "governance/ACCEPTANCE_CASES_V1.json",
        "json_pointer": "/cases/@id=CASE-PIT-LATE-RETRIEVAL/expected/accepted",
        "replacement": True,
        "expected_rejection_substring": (
            "CASE-PIT-LATE-RETRIEVAL freeze-critical semantics differ"
        ),
        "description": "invert the point-in-time late-retrieval rejection oracle",
    },
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE": {
        "target_path": "governance/MARKET_SIMULATION_POLICY_V1.json",
        "json_pointer": "/calendar_and_causality/same_bar_fill",
        "replacement": "allowed by default whenever the backtest requests it",
        "expected_rejection_substring": (
            "market calendar and causality semantics differ"
        ),
        "description": "permit same-bar fills and erase the causal boundary",
    },
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE": {
        "target_path": "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json",
        "json_pointer": (
            "/corporate_action_matrix/@id=ACTION-SPLIT/semantics/quantity_rule"
        ),
        "replacement": "leave_quantity_unchanged",
        "expected_rejection_substring": (
            "ACTION-SPLIT corporate action semantics differ"
        ),
        "description": "smuggle a split rule that leaves position quantity unchanged",
    },
    "ATTACK-CONDITIONAL-SELF-ATTESTATION": {
        "target_path": "governance/ACCEPTANCE_CONTRACT_V1.json",
        "json_pointer": (
            "/conditional_evidence_schema/raw_result_schema/required/"
            "@value=actual_cases_run"
        ),
        "operation": "remove",
        "expected_rejection_substring": "conditional evidence schema differs",
        "description": (
            "remove the raw executed-case field needed to reject self-attestation"
        ),
    },
}


class RunnerError(RuntimeError):
    """Fail-closed runner setup or mutation error."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def git_text(cwd: Path, *args: str) -> str:
    completed = run(["git", *args], cwd=cwd)
    if completed.returncode != 0:
        raise RunnerError(
            f"git {' '.join(args)} failed: "
            f"{completed.stdout.strip() or '<no output>'}"
        )
    return completed.stdout.strip()


def exact_candidate_context(candidate_commit: str) -> tuple[Path, str, str]:
    if SHA1.fullmatch(candidate_commit) is None:
        raise RunnerError("candidate commit must be an exact 40-character SHA-1")
    repository_root = Path(
        git_text(PROJECT_ROOT, "rev-parse", "--show-toplevel")
    ).resolve()
    project_prefix = git_text(PROJECT_ROOT, "rev-parse", "--show-prefix")
    resolved = git_text(
        repository_root,
        "rev-parse",
        "--verify",
        f"{candidate_commit}^{{commit}}",
    )
    if resolved != candidate_commit:
        raise RunnerError("candidate commit did not resolve exactly")
    candidate_tree = git_text(
        repository_root, "rev-parse", f"{candidate_commit}^{{tree}}"
    )
    candidate_runner = run(
        [
            "git",
            "show",
            f"{candidate_commit}:{project_prefix}{RUNNER_RELATIVE}",
        ],
        cwd=repository_root,
    )
    if candidate_runner.returncode != 0:
        raise RunnerError("the frozen attack runner is absent from the candidate")
    current_runner = Path(__file__).resolve().read_bytes()
    if candidate_runner.stdout.encode("utf-8") != current_runner:
        raise RunnerError(
            "the executing attack runner differs from the candidate runner"
        )
    return repository_root, project_prefix, candidate_tree


def decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_parent(document: Any, pointer: str) -> tuple[Any, str | int]:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise RunnerError("mutation json_pointer must be an absolute JSON pointer")
    tokens = [decode_pointer_token(item) for item in pointer[1:].split("/")]
    if not tokens or any(not token for token in tokens):
        raise RunnerError("mutation json_pointer contains an empty token")
    current = document
    for token in tokens[:-1]:
        if token.startswith("@id="):
            if not isinstance(current, list):
                raise RunnerError("@id selector requires a list")
            wanted = token.removeprefix("@id=")
            matches = [
                item
                for item in current
                if isinstance(item, dict) and item.get("id") == wanted
            ]
            if len(matches) != 1:
                raise RunnerError(f"@id selector did not resolve uniquely: {wanted}")
            current = matches[0]
        elif isinstance(current, dict):
            if token not in current:
                raise RunnerError(f"json_pointer key is absent: {token}")
            current = current[token]
        elif isinstance(current, list) and token.isdecimal():
            index = int(token)
            if index >= len(current):
                raise RunnerError(f"json_pointer index is out of range: {index}")
            current = current[index]
        else:
            raise RunnerError(f"json_pointer cannot traverse token: {token}")

    final = tokens[-1]
    if final.startswith("@value="):
        if not isinstance(current, list):
            raise RunnerError("@value selector requires a list")
        wanted = final.removeprefix("@value=")
        indexes = [index for index, value in enumerate(current) if value == wanted]
        if len(indexes) != 1:
            raise RunnerError(
                f"@value selector did not resolve uniquely: {wanted}"
            )
        return current, indexes[0]
    if isinstance(current, dict):
        if final not in current:
            raise RunnerError(f"final json_pointer key is absent: {final}")
        return current, final
    if isinstance(current, list) and final.isdecimal():
        index = int(final)
        if index >= len(current):
            raise RunnerError(f"final json_pointer index is out of range: {index}")
        return current, index
    raise RunnerError(f"json_pointer cannot resolve final token: {final}")


def read_selected(parent: Any, key: str | int) -> Any:
    return parent[key]


def apply_mutation(project_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    target_relative = spec.get("target_path")
    if (
        not isinstance(target_relative, str)
        or not target_relative.startswith("governance/")
        or not target_relative.endswith(".json")
        or Path(target_relative).is_absolute()
        or ".." in Path(target_relative).parts
        or "\\" in target_relative
        or target_relative.endswith("FROZEN_BUNDLE_V1.json")
    ):
        raise RunnerError("mutation target_path is outside the allowed governance JSON")
    target = project_root / target_relative
    try:
        document = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot load mutation target: {exc}") from None

    pointer = spec.get("json_pointer")
    parent, key = resolve_parent(document, pointer)
    before = read_selected(parent, key)
    expected_before = spec.get("expected_before_sha256")
    before_hash = sha256_bytes(canonical_json(before))
    if expected_before is not None and expected_before != before_hash:
        raise RunnerError("novelty probe expected_before_sha256 differs")

    operation = spec.get("operation", "replace")
    if operation == "replace":
        if "replacement" not in spec:
            raise RunnerError("replace mutation has no replacement")
        parent[key] = spec["replacement"]
        after = parent[key]
    elif operation == "remove":
        if isinstance(parent, list) and isinstance(key, int):
            after = None
            parent.pop(key)
        elif isinstance(parent, dict) and isinstance(key, str):
            after = None
            del parent[key]
        else:
            raise RunnerError("remove mutation target is invalid")
    else:
        raise RunnerError(f"unsupported mutation operation: {operation}")

    target.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "target_path": target_relative,
        "json_pointer": pointer,
        "operation": operation,
        "before_sha256": before_hash,
        "after_sha256": sha256_bytes(canonical_json(after)),
    }


def load_novelty_spec(path: Path) -> dict[str, Any]:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot load novelty spec: {exc}") from None
    if not isinstance(spec, dict):
        raise RunnerError("novelty spec must be a JSON object")
    required = {
        "schema_version",
        "probe_id",
        "target_path",
        "json_pointer",
        "operation",
        "expected_before_sha256",
        "replacement",
        "expected_rejection_substring",
        "rationale",
    }
    if set(spec) != required:
        raise RunnerError(
            "novelty spec fields differ: "
            f"missing={sorted(required - set(spec))}, "
            f"extra={sorted(set(spec) - required)}"
        )
    if spec.get("schema_version") != 1:
        raise RunnerError("novelty spec schema_version differs")
    probe_id = spec.get("probe_id")
    if not isinstance(probe_id, str) or PROBE_ID.fullmatch(probe_id) is None:
        raise RunnerError("novelty probe_id is invalid")
    if spec.get("operation") != "replace":
        raise RunnerError("novelty probes may only replace an existing JSON value")
    expected_before = spec.get("expected_before_sha256")
    if (
        not isinstance(expected_before, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_before) is None
    ):
        raise RunnerError("novelty expected_before_sha256 is invalid")
    for field in ("expected_rejection_substring", "rationale"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise RunnerError(f"novelty {field} is missing")
    return spec


def normalized_verifier_command() -> list[str]:
    return ["PYTHON", VERIFIER_RELATIVE, "--allow-candidate"]


def run_verifier(project_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["IDS_PROJECT_ROOT"] = str(project_root)
    return run(
        [sys.executable, str(project_root / VERIFIER_RELATIVE), "--allow-candidate"],
        cwd=project_root,
        env=env,
    )


def receipt_fingerprint_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "runner_id": receipt["runner_id"],
        "runner_sha256": receipt["runner_sha256"],
        "candidate_commit": receipt["candidate_commit"],
        "candidate_tree": receipt["candidate_tree"],
        "project_prefix": receipt["project_prefix"],
        "mode": receipt["mode"],
        "probe_id": receipt["probe_id"],
        "mutation_spec_sha256": receipt["mutation_spec_sha256"],
        "mutation_observation": receipt["mutation_observation"],
        "baseline": receipt["baseline"],
        "target": receipt["target"],
        "expected_rejection_substring": receipt[
            "expected_rejection_substring"
        ],
        "result": receipt["result"],
        "runner_exit_code": receipt["runner_exit_code"],
    }


def build_receipt(
    *,
    candidate_commit: str,
    attack_id: str | None,
    novelty_spec_path: Path | None,
) -> tuple[dict[str, Any], int]:
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    repository_root, project_prefix, candidate_tree = exact_candidate_context(
        candidate_commit
    )
    if attack_id is not None:
        if attack_id not in CANONICAL_ATTACKS:
            raise RunnerError(f"unknown canonical attack_id: {attack_id}")
        mode = "canonical"
        probe_id = attack_id
        spec = dict(CANONICAL_ATTACKS[attack_id])
        spec["attack_id"] = attack_id
        spec.setdefault("operation", "replace")
    else:
        if novelty_spec_path is None:
            raise RunnerError("one canonical attack or novelty spec is required")
        mode = "novelty"
        spec = load_novelty_spec(novelty_spec_path)
        probe_id = spec["probe_id"]

    spec_hash = sha256_bytes(canonical_json(spec))
    expected_signal = spec.get("expected_rejection_substring")
    if not isinstance(expected_signal, str) or not expected_signal:
        raise RunnerError("mutation expected_rejection_substring is missing")

    with tempfile.TemporaryDirectory(prefix="ids-attack-runner-") as temp:
        clone_root = Path(temp) / "repository"
        cloned = run(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                str(repository_root),
                str(clone_root),
            ],
            cwd=repository_root,
        )
        if cloned.returncode != 0:
            raise RunnerError(
                f"isolated clone failed: {cloned.stdout.strip() or '<no output>'}"
            )
        source_origin = run(
            ["git", "remote", "get-url", "origin"], cwd=repository_root
        )
        if source_origin.returncode == 0 and source_origin.stdout.strip():
            restored = run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    source_origin.stdout.strip(),
                ],
                cwd=clone_root,
            )
            if restored.returncode != 0:
                raise RunnerError("cannot preserve the candidate source origin")
        checkout = run(
            ["git", "checkout", "--detach", candidate_commit], cwd=clone_root
        )
        if checkout.returncode != 0:
            raise RunnerError(
                f"candidate checkout failed: "
                f"{checkout.stdout.strip() or '<no output>'}"
            )
        isolated_project = (clone_root / project_prefix).resolve()
        baseline = run_verifier(isolated_project)
        baseline_record = {
            "argv": normalized_verifier_command(),
            "exit_code": baseline.returncode,
            "stdout": baseline.stdout,
            "stdout_sha256": sha256_bytes(baseline.stdout.encode("utf-8")),
        }
        if baseline.returncode != 0:
            receipt = {
                "schema_version": 2,
                "runner_id": RUNNER_ID,
                "runner_sha256": sha256_file(Path(__file__).resolve()),
                "candidate_commit": candidate_commit,
                "candidate_tree": candidate_tree,
                "project_prefix": project_prefix,
                "mode": mode,
                "probe_id": probe_id,
                "mutation_spec_sha256": spec_hash,
                "mutation_observation": None,
                "baseline": baseline_record,
                "target": None,
                "expected_rejection_substring": expected_signal,
                "result": "invalid_baseline",
                "runner_exit_code": 2,
                "started_at": started_at,
                "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            receipt["execution_fingerprint"] = sha256_bytes(
                canonical_json(receipt_fingerprint_payload(receipt))
            )
            return receipt, 2

        mutation_observation = apply_mutation(isolated_project, spec)
        target = run_verifier(isolated_project)
        target_record = {
            "argv": normalized_verifier_command(),
            "exit_code": target.returncode,
            "stdout": target.stdout,
            "stdout_sha256": sha256_bytes(target.stdout.encode("utf-8")),
        }
        rejected = target.returncode != 0 and expected_signal in target.stdout
        result_name = "rejected" if rejected else "escaped_or_wrong_failure"
        exit_code = 0 if rejected else 1
        receipt = {
            "schema_version": 2,
            "runner_id": RUNNER_ID,
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "candidate_commit": candidate_commit,
            "candidate_tree": candidate_tree,
            "project_prefix": project_prefix,
            "mode": mode,
            "probe_id": probe_id,
            "mutation_spec_sha256": spec_hash,
            "mutation_observation": mutation_observation,
            "baseline": baseline_record,
            "target": target_record,
            "expected_rejection_substring": expected_signal,
            "result": result_name,
            "runner_exit_code": exit_code,
            "started_at": started_at,
            "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        receipt["execution_fingerprint"] = sha256_bytes(
            canonical_json(receipt_fingerprint_payload(receipt))
        )
        return receipt, exit_code


def error_receipt(
    *,
    candidate_commit: str,
    probe_id: str,
    message: str,
) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "runner_id": RUNNER_ID,
        "candidate_commit": candidate_commit,
        "probe_id": probe_id,
        "result": "runner_error",
        "runner_exit_code": 2,
        "error": message,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-commit", required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--attack-id")
    choice.add_argument("--novelty-spec", type=Path)
    args = parser.parse_args()
    probe_id = args.attack_id or (
        args.novelty_spec.name if args.novelty_spec is not None else "<unknown>"
    )
    try:
        receipt, exit_code = build_receipt(
            candidate_commit=args.candidate_commit,
            attack_id=args.attack_id,
            novelty_spec_path=args.novelty_spec,
        )
    except (OSError, RunnerError) as exc:
        receipt = error_receipt(
            candidate_commit=args.candidate_commit,
            probe_id=probe_id,
            message=str(exc),
        )
        exit_code = 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
