from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = PROJECT_ROOT / "pilot" / "restaurant-web-repair"
CLI_PATH = PROJECT_ROOT / "src" / "opportunity_os.py"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from opportunity_os import (  # noqa: E402
    LEGACY_AUTHORITY_STATUS,
    LEGACY_QUARANTINE_REASON,
    LegacyQuarantineError,
    add_record,
    derive_opportunity_status,
    external_permission_for_probe,
    init_workspace,
    make_harness,
    status_report,
    validate_record,
    validate_workspace,
)


EXPECTED_REVOKED_ARTIFACTS = {
    "workspace/harnesses/opportunity-saffrono-public-page-repair/"
    "probe-5d37e36e25ea-TASK_CONTRACT.md": {
        "new_path": "quarantine/original/workspace/harnesses/"
        "opportunity-saffrono-public-page-repair/"
        "probe-5d37e36e25ea-TASK_CONTRACT.md",
        "sha256": "3c2229abd6a9ba52002c74570158814dc84b304a9a1f90fbc135be56df54318e",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "workspace/harnesses/opportunity-saffrono-public-page-repair/"
    "probe-5d37e36e25ea-manifest.json": {
        "new_path": "quarantine/original/workspace/harnesses/"
        "opportunity-saffrono-public-page-repair/"
        "probe-5d37e36e25ea-manifest.json",
        "sha256": "1304a486ecce792ebe15ed78442bf23cae8f8cce408f7888acb413106623e481",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "workspace/harnesses/opportunity-saffrono-public-page-repair/"
    "superseded/pre-input-binding/probe-TASK_CONTRACT.md": {
        "new_path": "quarantine/original/workspace/harnesses/"
        "opportunity-saffrono-public-page-repair/superseded/pre-input-binding/"
        "probe-TASK_CONTRACT.md",
        "sha256": "d1794df930e8b14dcc33b9460984c2c30ce765b3bbcc3f2569fe4137097417da",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "workspace/harnesses/opportunity-saffrono-public-page-repair/"
    "superseded/pre-input-binding/probe-manifest.json": {
        "new_path": "quarantine/original/workspace/harnesses/"
        "opportunity-saffrono-public-page-repair/superseded/pre-input-binding/"
        "probe-manifest.json",
        "sha256": "a34666c755f2ccad6ea1bbcdc7ba9cbc0465a1d53e7f181081dbec52e206cdeb",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "artifacts/preview/screenshots/desktop.png": {
        "new_path": "quarantine/original/artifacts/preview/screenshots/desktop.png",
        "sha256": "76e09ec013e9d5ecfc055307e0e6b0c0b44148586e6b88e9c9076ff5da4e306d",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "artifacts/preview/screenshots/mobile.png": {
        "new_path": "quarantine/original/artifacts/preview/screenshots/mobile.png",
        "sha256": "78b8a56f540e63be8583b4caccfa3031dcc2d3188163a598560ba51ab2c369e7",
        "former_path_disposition": "REMOVED_FROM_ACTIVE_TREE",
    },
    "artifacts/RUN_LOG.md": {
        "new_path": "quarantine/original/artifacts/RUN_LOG.md",
        "sha256": "a3dcf1f63f814a4823c4654df2515c0be3b12010565ad689afd03fe110138757",
        "former_path_disposition": "REPLACED_WITH_REVOCATION_NOTICE",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_tree(root: Path) -> tuple[tuple[str, str, bytes | None], ...]:
    if not root.exists():
        return (("missing", ".", None),)
    entries: list[tuple[str, str, bytes | None]] = [("directory", ".", None)]
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append(("symlink", relative, os.readlink(path).encode("utf-8")))
        elif path.is_dir():
            entries.append(("directory", relative, None))
        else:
            entries.append(("file", relative, path.read_bytes()))
    return tuple(entries)


class Untouchable:
    """Any attempted input inspection is a test failure."""

    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"legacy API inspected quarantined input attribute {name!r}")


class LegacyRuntimeTombstoneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp.name)
        self.original_workspace = self.temp_root / "legacy-workspace"
        screenings = self.original_workspace / "screenings"
        screenings.mkdir(parents=True)
        (self.original_workspace / "workspace.json").write_text(
            json.dumps({"workspace_version": "0.1"}) + "\n",
            encoding="utf-8",
        )
        (screenings / "screening-pass.json").write_text(
            json.dumps(
                {
                    "schema_version": "0.1",
                    "record_type": "screening",
                    "id": "screening-adversarial-pass",
                    "target_liveness": "active",
                    "payer_identified": True,
                    "native_feature_collision": "none",
                    "decision": "pass",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.original_workspace / ".legacy-quarantine-marker").write_text(
            "marker is not the authority boundary\n",
            encoding="utf-8",
        )

        self.copied_workspace = self.temp_root / "copied-under-new-path"
        shutil.copytree(self.original_workspace, self.copied_workspace)
        (self.copied_workspace / ".legacy-quarantine-marker").unlink()

        self.source_record = self.temp_root / "adversarial-record.json"
        self.source_record.write_text(
            json.dumps(
                {
                    "schema_version": "0.1",
                    "record_type": "screening",
                    "id": "later-screening-pass",
                    "decision": "pass",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.new_workspace = self.temp_root / "must-not-be-created"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def assert_quarantined(self, action: Callable[[], object]) -> None:
        with self.assertRaises(LegacyQuarantineError) as raised:
            action()
        self.assertEqual(LEGACY_QUARANTINE_REASON, str(raised.exception))

    def test_all_retained_apis_reject_before_inspecting_inputs(self) -> None:
        tripwire = Untouchable()
        actions = {
            "validate_record": lambda: validate_record(tripwire),
            "validate_workspace": lambda: validate_workspace(tripwire),
            "init_workspace": lambda: init_workspace(tripwire),
            "add_record": lambda: add_record(tripwire, tripwire),
            "status_report": lambda: status_report(tripwire),
            "derive_opportunity_status": lambda: derive_opportunity_status(
                tripwire, tripwire
            ),
            "external_permission_for_probe": lambda: external_permission_for_probe(
                tripwire
            ),
            "make_harness": lambda: make_harness(tripwire, tripwire, tripwire, tripwire),
        }
        for name, action in actions.items():
            with self.subTest(api=name):
                self.assert_quarantined(action)

    def test_direct_calls_cannot_mutate_filesystem_or_emit_authority(self) -> None:
        before = snapshot_tree(self.temp_root)
        actions = {
            "init": lambda: init_workspace(self.new_workspace),
            "add": lambda: add_record(self.copied_workspace, self.source_record),
            "validate": lambda: validate_workspace(self.copied_workspace),
            "status": lambda: status_report(self.copied_workspace),
            "derive": lambda: derive_opportunity_status(
                "opportunity-adversarial", {"screening-adversarial-pass": {"decision": "pass"}}
            ),
            "permission": lambda: external_permission_for_probe(
                {"external_action_policy": "scoped_authorization"}
            ),
            "probe mode": lambda: make_harness(
                self.copied_workspace,
                "opportunity-adversarial",
                "probe-adversarial",
                "probe",
            ),
            "delivery mode": lambda: make_harness(
                self.copied_workspace,
                "opportunity-adversarial",
                "probe-adversarial",
                "delivery",
            ),
        }
        for name, action in actions.items():
            with self.subTest(entry_point=name):
                self.assert_quarantined(action)
        self.assertEqual(before, snapshot_tree(self.temp_root))
        self.assertFalse(self.new_workspace.exists())

    def test_copy_marker_deletion_and_pass_screening_cannot_lift_quarantine(self) -> None:
        self.assertFalse((self.copied_workspace / ".legacy-quarantine-marker").exists())
        screening = json.loads(
            (self.copied_workspace / "screenings" / "screening-pass.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("pass", screening["decision"])
        before = snapshot_tree(self.copied_workspace)
        self.assert_quarantined(lambda: validate_workspace(self.copied_workspace))
        for mode in ("probe", "delivery"):
            with self.subTest(mode=mode):
                self.assert_quarantined(
                    lambda mode=mode: make_harness(
                        self.copied_workspace,
                        "opportunity-adversarial",
                        "probe-adversarial",
                        mode,
                    )
                )
        self.assertEqual(before, snapshot_tree(self.copied_workspace))

    def test_all_cli_commands_fail_with_same_reason_and_forbidden_stdout_is_empty(self) -> None:
        commands = {
            "no arguments": [],
            "former help": ["--help"],
            "init": ["init", str(self.new_workspace)],
            "init malformed": ["init"],
            "add": ["add", str(self.copied_workspace), str(self.source_record)],
            "validate": ["validate", str(self.copied_workspace)],
            "validate former help": ["validate", "--help"],
            "status": ["status", str(self.copied_workspace), "--json"],
            "make-harness probe": [
                "make-harness",
                str(self.copied_workspace),
                "--opportunity",
                "opportunity-adversarial",
                "--probe",
                "probe-adversarial",
                "--mode",
                "probe",
            ],
            "make-harness delivery": [
                "make-harness",
                str(self.copied_workspace),
                "--opportunity",
                "opportunity-adversarial",
                "--probe",
                "probe-adversarial",
                "--mode",
                "delivery",
            ],
            "make-harness invalid mode": [
                "make-harness",
                str(self.copied_workspace),
                "--mode",
                "not-a-mode",
            ],
        }
        forbidden_stdout_claims = (
            "VALID",
            "market_stage",
            "fulfillment_stage",
            "commitment",
            "paid",
            "per_action_approval",
            "scoped_authorization",
            "not_authorized",
            "manifest.json",
            "TASK_CONTRACT",
        )
        before = snapshot_tree(self.temp_root)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        for name, arguments in commands.items():
            with self.subTest(command=name):
                completed = subprocess.run(
                    [sys.executable, str(CLI_PATH), *arguments],
                    cwd=PROJECT_ROOT,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(0, completed.returncode)
                self.assertEqual("", completed.stdout)
                self.assertEqual(
                    f"ERROR {LEGACY_QUARANTINE_REASON}\n",
                    completed.stderr,
                )
                for forbidden in forbidden_stdout_claims:
                    self.assertNotIn(forbidden, completed.stdout)
        self.assertEqual(before, snapshot_tree(self.temp_root))
        self.assertFalse(self.new_workspace.exists())

    def test_persisted_artifacts_are_hash_bound_and_revoked(self) -> None:
        manifest_path = PILOT_ROOT / "quarantine" / "REVOCATION_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("REVOKED_LEGACY_ARTIFACT", manifest["authority_status"])
        self.assertEqual([], manifest["authoritative_for"])
        path_base = Path(manifest["path_base"])
        self.assertFalse(path_base.is_absolute())
        self.assertNotIn("..", path_base.parts)
        manifest_base = (PROJECT_ROOT / path_base).resolve()
        self.assertEqual(PILOT_ROOT.resolve(), manifest_base)
        quarantine_root = (PILOT_ROOT / "quarantine" / "original").resolve()
        entries = {item["former_path"]: item for item in manifest["artifacts"]}
        self.assertEqual(set(EXPECTED_REVOKED_ARTIFACTS), set(entries))

        for former_path, expected in EXPECTED_REVOKED_ARTIFACTS.items():
            with self.subTest(former_path=former_path):
                entry = entries[former_path]
                self.assertEqual(expected["new_path"], entry["new_path"])
                self.assertEqual(expected["sha256"], entry["sha256"])
                self.assertEqual(
                    expected["former_path_disposition"],
                    entry["former_path_disposition"],
                )
                self.assertEqual("REVOKED_LEGACY_ARTIFACT", entry["authority_status"])
                self.assertEqual([], entry["authoritative_for"])
                former_relative = Path(former_path)
                new_relative = Path(entry["new_path"])
                self.assertFalse(former_relative.is_absolute())
                self.assertFalse(new_relative.is_absolute())
                self.assertNotIn("..", former_relative.parts)
                self.assertNotIn("..", new_relative.parts)
                former_resolved = (manifest_base / former_relative).resolve()
                quarantined_path = (manifest_base / new_relative).resolve()
                try:
                    former_resolved.relative_to(manifest_base)
                    quarantined_path.relative_to(quarantine_root)
                except ValueError as exc:
                    self.fail(f"revocation path escapes declared roots: {exc}")
                self.assertTrue(quarantined_path.is_file())
                self.assertEqual(expected["sha256"], sha256(quarantined_path))
                if entry["former_path_disposition"] == "REMOVED_FROM_ACTIVE_TREE":
                    self.assertFalse(former_resolved.exists())
                else:
                    self.assertEqual(
                        "REPLACED_WITH_REVOCATION_NOTICE",
                        entry["former_path_disposition"],
                    )
                    self.assertTrue(former_resolved.is_file())

        active_harness_root = PILOT_ROOT / "workspace" / "harnesses"
        active_harness_files = [
            path for path in active_harness_root.rglob("*") if path.is_file()
        ]
        self.assertEqual([], active_harness_files)

        active_run_log = PILOT_ROOT / "artifacts" / "RUN_LOG.md"
        self.assertTrue(active_run_log.is_file())
        self.assertNotEqual(
            EXPECTED_REVOKED_ARTIFACTS["artifacts/RUN_LOG.md"]["sha256"],
            sha256(active_run_log),
        )
        run_log_text = active_run_log.read_text(encoding="utf-8")
        for forbidden_claim in (
            "Workspace validation:",
            "Market stage:",
            "Fulfillment stage:",
            "current Harness",
            "`VALID`",
        ):
            self.assertNotIn(forbidden_claim, run_log_text)

    def test_historical_labels_do_not_claim_a_current_runtime_or_pilot(self) -> None:
        self.assertEqual("LEGACY_UNQUALIFIED", LEGACY_AUTHORITY_STATUS)
        project_readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        pilot_readme = (PILOT_ROOT / "README.md").read_text(encoding="utf-8")
        for text in (project_readme, pilot_readme):
            self.assertIn("HISTORICAL", text)
            self.assertNotIn("当前 Probe", text)
            self.assertNotIn("python3 src/opportunity_os.py", text)

        standalone_artifacts = (
            PROJECT_ROOT / "STATE.md",
            PILOT_ROOT / "artifacts" / "audit.md",
            PILOT_ROOT / "artifacts" / "offer-draft.md",
            PILOT_ROOT / "artifacts" / "preview" / "index.html",
        )
        for artifact in standalone_artifacts:
            with self.subTest(standalone_artifact=artifact.name):
                text = artifact.read_text(encoding="utf-8")
                self.assertIn("HISTORICAL", text)
                self.assertIn("REVOKED", text)


if __name__ == "__main__":
    unittest.main()
