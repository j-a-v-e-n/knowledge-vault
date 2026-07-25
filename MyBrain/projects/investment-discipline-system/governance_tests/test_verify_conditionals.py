from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_SOURCE = PROJECT_ROOT / "scripts" / "verify_conditionals.py"
CONTRACT_SOURCE = PROJECT_ROOT / "governance" / "ACCEPTANCE_CONTRACT_V1.json"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
ZERO_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class ConditionalGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "governance").mkdir()
        (self.root / "scripts").mkdir()
        shutil.copy2(
            CONTRACT_SOURCE,
            self.root / "governance" / "ACCEPTANCE_CONTRACT_V1.json",
        )
        shutil.copy2(
            VERIFIER_SOURCE,
            self.root / "scripts" / "verify_conditionals.py",
        )
        self.contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        self.write_json(
            BUNDLE_RELATIVE,
            {
                "schema_version": 1,
                "status": "frozen",
                "contract_id": self.contract["contract_id"],
            },
        )
        self.run_git("init", "--initial-branch=main")
        self.run_git("config", "user.name", "Conditional Trust Test")
        self.run_git(
            "config", "user.email", "conditional-trust@example.invalid"
        )
        self.run_git("add", "governance", "scripts")
        self.run_git("commit", "-m", "trusted conditional fixture")
        self.candidate_commit = self.git_text("rev-parse", "HEAD")
        self.candidate_tree = self.git_text("rev-parse", "HEAD^{tree}")
        self.bundle_sha256 = hashlib.sha256(
            (self.root / BUNDLE_RELATIVE).read_bytes()
        ).hexdigest()
        self.verifier = VERIFIER_SOURCE
        self.runtime_root = self.root / "private-runtime"
        self.runtime_root.mkdir()
        self.runtime_config = self.write_json(
            "private-runtime/runtime-authority.json",
            {
                "schema_version": 1,
                "mode": "fixture",
                "runtime_database_relative_path": "runtime.sqlite3",
                "anchor_relative_path": "anchors.jsonl",
            },
        )
        self.authoritative_runtime_db = self.runtime_root / "runtime.sqlite3"
        self.authoritative_anchor = self.runtime_root / "anchors.jsonl"
        self.base_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            self.fail(
                f"git command failed ({result.returncode}): "
                f"{' '.join(args)}\n{result.stdout}"
            )
        return result

    def git_text(self, *args: str) -> str:
        return self.run_git(*args).stdout.strip()

    def read_json(self, relative: str) -> dict[str, Any]:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict[str, Any]) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    @staticmethod
    def timestamp(value: dt.datetime) -> str:
        return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")

    def gate(self, gate_id: str) -> dict[str, Any]:
        return next(
            item
            for item in self.contract["conditional_gates"]
            if item["id"] == gate_id
        )

    def catalog(self, gate_id: str) -> dict[str, Any]:
        mandatory = self.gate(gate_id)["mandatory_gate_when_ready"]
        return next(
            item
            for item in self.contract["conditional_gate_catalog"]
            if item["id"] == mandatory
        )

    def run_gate(
        self,
        gate_id: str,
        *,
        token: str | None = None,
        runtime_db: Path | None = None,
        target_verdict: str = "core_release_candidate",
        expected_commit: str | None = None,
        expected_tree: str | None = None,
        expected_bundle_path: str | None = None,
        expected_bundle_sha256: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        env["IDS_CONDITIONAL_FIXTURE_MODE"] = "1"
        env["IDS_RUNTIME_AUTHORITY_CONFIG"] = str(self.runtime_config)
        if token is None:
            env.pop("TIINGO_API_TOKEN", None)
        else:
            env["TIINGO_API_TOKEN"] = token
        command = [
            sys.executable,
            str(self.verifier),
            "--gate",
            gate_id,
            "--target-verdict",
            target_verdict,
            "--json",
        ]
        if runtime_db is not None:
            command.extend(["--runtime-db", str(runtime_db)])
        for flag, value in (
            ("--candidate-commit", expected_commit),
            ("--candidate-tree", expected_tree),
            ("--frozen-bundle-path", expected_bundle_path),
            ("--frozen-bundle-sha256", expected_bundle_sha256),
        ):
            if value is not None:
                command.extend([flag, value])
        return subprocess.run(
            command,
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def create_runtime_schema(
        self,
        connection: sqlite3.Connection,
        *,
        trigger_escape: str | None = None,
        unique_run_id: bool = True,
    ) -> None:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "CREATE TABLE events ("
            "sequence INTEGER PRIMARY KEY, "
            "event_type TEXT NOT NULL, "
            "producer_id TEXT NOT NULL, "
            "occurred_at TEXT NOT NULL, "
            "payload_json TEXT NOT NULL, "
            "prev_hash TEXT NOT NULL, "
            "event_hash TEXT NOT NULL UNIQUE)"
        )
        connection.execute(
            "CREATE TABLE condition_observations ("
            "source_event_seq INTEGER PRIMARY KEY, "
            "condition_id TEXT NOT NULL, "
            "stage TEXT NOT NULL, "
            "ready INTEGER NOT NULL CHECK (ready IN (0, 1)), "
            "source_event_hash TEXT NOT NULL UNIQUE, "
            "source_state_hash TEXT NOT NULL, "
            "source_anchor_hash TEXT NOT NULL, "
            "observed_at TEXT NOT NULL, "
            "producer_id TEXT NOT NULL, "
            "FOREIGN KEY (source_event_seq) REFERENCES events(sequence))"
        )
        run_id_constraint = " UNIQUE" if unique_run_id else ""
        connection.execute(
            "CREATE TABLE conditional_gate_runs ("
            "run_event_seq INTEGER PRIMARY KEY, "
            f"run_id TEXT NOT NULL{run_id_constraint}, "
            "condition_id TEXT NOT NULL, "
            "gate_id TEXT NOT NULL, "
            "gate_stage TEXT NOT NULL, "
            "state TEXT NOT NULL, "
            "source_event_seq INTEGER NOT NULL, "
            "source_event_hash TEXT NOT NULL, "
            "source_state_hash TEXT NOT NULL, "
            "source_anchor_hash TEXT NOT NULL, "
            "raw_result_path TEXT NOT NULL, "
            "raw_result_sha256 TEXT NOT NULL, "
            "completed_at TEXT NOT NULL, "
            "producer_id TEXT NOT NULL, "
            "run_event_hash TEXT NOT NULL, "
            "run_anchor_hash TEXT NOT NULL, "
            "FOREIGN KEY (run_event_seq) REFERENCES events(sequence))"
        )
        for name, table, operation in (
            ("events_no_update", "events", "UPDATE"),
            ("events_no_delete", "events", "DELETE"),
            (
                "condition_observations_no_update",
                "condition_observations",
                "UPDATE",
            ),
            (
                "condition_observations_no_delete",
                "condition_observations",
                "DELETE",
            ),
            (
                "conditional_gate_runs_no_update",
                "conditional_gate_runs",
                "UPDATE",
            ),
            (
                "conditional_gate_runs_no_delete",
                "conditional_gate_runs",
                "DELETE",
            ),
        ):
            if name == "events_no_update" and trigger_escape == "when_zero":
                trigger_sql = (
                    f"CREATE TRIGGER {name} BEFORE {operation} ON {table} "
                    "WHEN 0 BEGIN SELECT RAISE(ABORT, 'append_only'); END"
                )
            elif (
                name == "events_no_update"
                and trigger_escape == "unreachable_raise"
            ):
                trigger_sql = (
                    f"CREATE TRIGGER {name} BEFORE {operation} ON {table} "
                    "BEGIN SELECT CASE WHEN 0 THEN "
                    "RAISE(ABORT, 'append_only') ELSE 1 END; END"
                )
            elif (
                name == "conditional_gate_runs_no_update"
                and trigger_escape == "gate_run_when_zero"
            ):
                trigger_sql = (
                    f"CREATE TRIGGER {name} BEFORE {operation} ON {table} "
                    "WHEN 0 BEGIN SELECT RAISE(ABORT, 'append_only'); END"
                )
            else:
                trigger_sql = (
                    f"CREATE TRIGGER {name} BEFORE {operation} ON {table} "
                    "BEGIN SELECT RAISE(ABORT, 'append_only'); END"
                )
            connection.execute(trigger_sql)

    def event_payload(
        self,
        gate_id: str,
        stage: str,
        *,
        ready: bool,
        observed_at: str,
        producer_id: str,
    ) -> dict[str, Any]:
        return {
            "condition_id": gate_id,
            "stage": stage,
            "ready": ready,
            "observed_at": observed_at,
            "producer_id": producer_id,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": BUNDLE_RELATIVE,
            "frozen_bundle_sha256": self.bundle_sha256,
        }

    def presence_observation(
        self,
        gate_id: str = "COND-TIINGO-LIVE-PROBE",
        *,
        present: bool = True,
    ) -> dict[str, Any]:
        material = {
            "authority": "process_environment_presence",
            "condition_id": gate_id,
            "present": present,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": BUNDLE_RELATIVE,
            "frozen_bundle_sha256": self.bundle_sha256,
        }
        fingerprint = sha256_bytes(
            canonical_json(material).encode("utf-8")
        )
        return {
            "authority": "process_environment_presence",
            "condition_id": gate_id,
            "source_event_seq": 0,
            "source_event_hash": fingerprint,
            "source_state_hash": fingerprint,
            "source_anchor_hash": fingerprint,
            "observed_at": None,
        }

    def create_runtime_chain(
        self,
        gate_id: str = "COND-JAVEN-FIELD-USE",
        stage: str = "human_onboarding_ready",
        *,
        ready: bool = True,
        broken_event_hash: bool = False,
        producer_id: str | None = None,
        observed_at: dt.datetime | None = None,
        runtime_db: Path | None = None,
        anchor_path: Path | None = None,
        trigger_escape: str | None = None,
        unique_run_id: bool = True,
    ) -> tuple[Path, dict[str, Any]]:
        runtime_db = runtime_db or self.authoritative_runtime_db
        anchor_path = anchor_path or self.authoritative_anchor
        runtime_db.parent.mkdir(parents=True, exist_ok=True)
        anchor_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(runtime_db)
        try:
            self.create_runtime_schema(
                connection,
                trigger_escape=trigger_escape,
                unique_run_id=unique_run_id,
            )
            producer = (
                producer_id
                if producer_id is not None
                else self.gate(gate_id)["prerequisite_probe"]["producer_id"]
            )
            observed = self.timestamp(
                observed_at or (self.base_time - dt.timedelta(seconds=60))
            )
            payload = self.event_payload(
                gate_id,
                stage,
                ready=ready,
                observed_at=observed,
                producer_id=producer,
            )
            payload_json = canonical_json(payload)
            envelope = {
                "sequence": 1,
                "event_type": "condition_observation",
                "producer_id": producer,
                "occurred_at": observed,
                "payload": payload,
                "prev_hash": ZERO_HASH,
            }
            computed_hash = sha256_bytes(
                canonical_json(envelope).encode("utf-8")
            )
            event_hash = "f" * 64 if broken_event_hash else computed_hash
            state_hash = sha256_bytes(
                canonical_json(
                    {
                        "through_sequence": 1,
                        "through_event_hash": event_hash,
                        "condition_states": [payload],
                    }
                ).encode("utf-8")
            )
            anchored = self.timestamp(
                dt.datetime.fromisoformat(observed.replace("Z", "+00:00"))
                + dt.timedelta(seconds=1)
            )
            anchor_material = {
                "schema_version": 1,
                "sequence": 1,
                "event_hash": event_hash,
                "anchored_at": anchored,
                "previous_anchor_hash": ZERO_HASH,
            }
            anchor_hash = sha256_bytes(
                canonical_json(anchor_material).encode("utf-8")
            )
            anchor_record = dict(anchor_material)
            anchor_record["anchor_hash"] = anchor_hash
            connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    1,
                    "condition_observation",
                    producer,
                    observed,
                    payload_json,
                    ZERO_HASH,
                    event_hash,
                ),
            )
            connection.execute(
                "INSERT INTO condition_observations "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    1,
                    gate_id,
                    stage,
                    int(ready),
                    event_hash,
                    state_hash,
                    anchor_hash,
                    observed,
                    producer,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        anchor_path.write_text(
            canonical_json(anchor_record) + "\n",
            encoding="utf-8",
        )
        observation = {
            "authority": "runtime_sqlite_event_chain",
            "condition_id": gate_id,
            "source_event_seq": 1,
            "source_event_hash": event_hash,
            "source_state_hash": state_hash,
            "source_anchor_hash": anchor_hash,
            "observed_at": observed,
        }
        return runtime_db, observation

    def append_runtime_observation(
        self,
        runtime_db: Path,
        gate_id: str = "COND-JAVEN-FIELD-USE",
        stage: str = "human_onboarding_ready",
    ) -> dict[str, Any]:
        connection = sqlite3.connect(runtime_db)
        try:
            sequence, prev_hash = connection.execute(
                "SELECT sequence, event_hash FROM events "
                "ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            next_sequence = sequence + 1
            producer = self.gate(gate_id)["prerequisite_probe"]["producer_id"]
            observed = self.timestamp(self.base_time - dt.timedelta(seconds=5))
            payload = self.event_payload(
                gate_id,
                stage,
                ready=True,
                observed_at=observed,
                producer_id=producer,
            )
            envelope = {
                "sequence": next_sequence,
                "event_type": "condition_observation",
                "producer_id": producer,
                "occurred_at": observed,
                "payload": payload,
                "prev_hash": prev_hash,
            }
            event_hash = sha256_bytes(
                canonical_json(envelope).encode("utf-8")
            )
            state_hash = sha256_bytes(
                canonical_json(
                    {
                        "through_sequence": next_sequence,
                        "through_event_hash": event_hash,
                        "condition_states": [payload],
                    }
                ).encode("utf-8")
            )
            previous_anchor = json.loads(
                self.authoritative_anchor.read_text(encoding="utf-8").splitlines()[-1]
            )["anchor_hash"]
            anchored = self.timestamp(
                dt.datetime.fromisoformat(observed.replace("Z", "+00:00"))
                + dt.timedelta(seconds=1)
            )
            anchor_material = {
                "schema_version": 1,
                "sequence": next_sequence,
                "event_hash": event_hash,
                "anchored_at": anchored,
                "previous_anchor_hash": previous_anchor,
            }
            anchor_hash = sha256_bytes(
                canonical_json(anchor_material).encode("utf-8")
            )
            anchor_record = dict(anchor_material)
            anchor_record["anchor_hash"] = anchor_hash
            connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    next_sequence,
                    "condition_observation",
                    producer,
                    observed,
                    canonical_json(payload),
                    prev_hash,
                    event_hash,
                ),
            )
            connection.execute(
                "INSERT INTO condition_observations "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    next_sequence,
                    gate_id,
                    stage,
                    1,
                    event_hash,
                    state_hash,
                    anchor_hash,
                    observed,
                    producer,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        with self.authoritative_anchor.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(anchor_record) + "\n")
        return {
            "authority": "runtime_sqlite_event_chain",
            "condition_id": gate_id,
            "source_event_seq": next_sequence,
            "source_event_hash": event_hash,
            "source_state_hash": state_hash,
            "source_anchor_hash": anchor_hash,
            "observed_at": observed,
        }

    def append_gate_run_receipt(
        self,
        payload: dict[str, Any],
        *,
        append_anchor: bool = True,
    ) -> dict[str, Any]:
        connection = sqlite3.connect(self.authoritative_runtime_db)
        try:
            tail = connection.execute(
                "SELECT sequence, event_hash FROM events "
                "ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            if tail is None:
                run_event_seq = 1
                prev_hash = ZERO_HASH
            else:
                sequence, prev_hash = tail
                run_event_seq = sequence + 1
            occurred_at = payload["completed_at"]
            envelope = {
                "sequence": run_event_seq,
                "event_type": "conditional_gate_run",
                "producer_id": payload["producer_id"],
                "occurred_at": occurred_at,
                "payload": payload,
                "prev_hash": prev_hash,
            }
            run_event_hash = sha256_bytes(
                canonical_json(envelope).encode("utf-8")
            )
            anchor_lines = (
                self.authoritative_anchor.read_text(
                    encoding="utf-8"
                ).splitlines()
                if self.authoritative_anchor.is_file()
                else []
            )
            previous_anchor = (
                json.loads(anchor_lines[-1])["anchor_hash"]
                if anchor_lines
                else ZERO_HASH
            )
            anchored_at = self.timestamp(
                dt.datetime.fromisoformat(
                    occurred_at.replace("Z", "+00:00")
                )
                + dt.timedelta(seconds=1)
            )
            anchor_material = {
                "schema_version": 1,
                "sequence": run_event_seq,
                "event_hash": run_event_hash,
                "anchored_at": anchored_at,
                "previous_anchor_hash": previous_anchor,
            }
            run_anchor_hash = sha256_bytes(
                canonical_json(anchor_material).encode("utf-8")
            )
            anchor_record = dict(anchor_material)
            anchor_record["anchor_hash"] = run_anchor_hash
            connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    run_event_seq,
                    "conditional_gate_run",
                    payload["producer_id"],
                    occurred_at,
                    canonical_json(payload),
                    prev_hash,
                    run_event_hash,
                ),
            )
            connection.execute(
                "INSERT INTO conditional_gate_runs VALUES "
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_event_seq,
                    payload["run_id"],
                    payload["condition_id"],
                    payload["gate_id"],
                    payload["gate_stage"],
                    payload["state"],
                    payload["source_event_seq"],
                    payload["source_event_hash"],
                    payload["source_state_hash"],
                    payload["source_anchor_hash"],
                    payload["raw_result_path"],
                    payload["raw_result_sha256"],
                    payload["completed_at"],
                    payload["producer_id"],
                    run_event_hash,
                    run_anchor_hash,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        if append_anchor:
            with self.authoritative_anchor.open("a", encoding="utf-8") as handle:
                handle.write(canonical_json(anchor_record) + "\n")
        return {
            "authority": "runtime_sqlite_gate_run_receipt",
            "run_event_seq": run_event_seq,
            "run_event_hash": run_event_hash,
            "run_anchor_hash": run_anchor_hash,
            "run_id": payload["run_id"],
            "condition_id": payload["condition_id"],
            "gate_id": payload["gate_id"],
            "gate_stage": payload["gate_stage"],
            "state": payload["state"],
            "source_event_seq": payload["source_event_seq"],
            "source_event_hash": payload["source_event_hash"],
            "source_state_hash": payload["source_state_hash"],
            "source_anchor_hash": payload["source_anchor_hash"],
            "raw_result_path": payload["raw_result_path"],
            "raw_result_sha256": payload["raw_result_sha256"],
            "completed_at": payload["completed_at"],
        }

    def create_one_row_forgery(self) -> tuple[Path, dict[str, Any]]:
        runtime_db = self.root / "attacker.sqlite3"
        observed = self.timestamp(self.base_time - dt.timedelta(seconds=60))
        event_hash = "a" * 64
        state_hash = "b" * 64
        anchor_hash = "c" * 64
        producer = self.gate("COND-JAVEN-FIELD-USE")["prerequisite_probe"][
            "producer_id"
        ]
        connection = sqlite3.connect(runtime_db)
        try:
            connection.execute(
                "CREATE TABLE condition_observations ("
                "source_event_seq INTEGER PRIMARY KEY, "
                "condition_id TEXT NOT NULL, "
                "stage TEXT NOT NULL, "
                "ready INTEGER NOT NULL, "
                "source_event_hash TEXT NOT NULL, "
                "source_state_hash TEXT NOT NULL, "
                "source_anchor_hash TEXT NOT NULL, "
                "observed_at TEXT NOT NULL, "
                "producer_id TEXT NOT NULL)"
            )
            connection.execute(
                "INSERT INTO condition_observations "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    1,
                    "COND-JAVEN-FIELD-USE",
                    "human_onboarding_ready",
                    1,
                    event_hash,
                    state_hash,
                    anchor_hash,
                    observed,
                    producer,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        return runtime_db, {
            "authority": "runtime_sqlite_event_chain",
            "condition_id": "COND-JAVEN-FIELD-USE",
            "source_event_seq": 1,
            "source_event_hash": event_hash,
            "source_state_hash": state_hash,
            "source_anchor_hash": anchor_hash,
            "observed_at": observed,
        }

    def build_evidence(
        self,
        observation: dict[str, Any],
        *,
        gate_id: str = "COND-JAVEN-FIELD-USE",
        gate_stage: str = "human_onboarding",
        state: str = "passed",
        run_id: str | None = None,
        raw_started: dt.datetime | None = None,
        raw_completed: dt.datetime | None = None,
        evidence_completed: dt.datetime | None = None,
        append_receipt: bool = True,
        append_receipt_anchor: bool = True,
        run_receipt: dict[str, Any] | None = None,
        run_payload_extra: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
        gate = self.gate(gate_id)
        catalog = self.catalog(gate_id)
        run_identifier = run_id or str(uuid.uuid4())
        cases = list(
            gate["required_acceptance_case_ids_by_stage"][gate_stage]
        )
        case_results: list[dict[str, Any]] = []
        for case_id in cases:
            input_relative = (
                f"{catalog['artifact_path_prefix']}{run_identifier}/"
                f"{case_id}.input.json"
            )
            raw_relative = (
                f"{catalog['artifact_path_prefix']}{run_identifier}/"
                f"{case_id}.raw.json"
            )
            input_path = self.write_json(
                input_relative,
                {"case_id": case_id, "kind": "input"},
            )
            raw_path = self.write_json(
                raw_relative,
                {"case_id": case_id, "kind": "raw_result"},
            )
            case_results.append(
                {
                    "case_id": case_id,
                    "status": "pass",
                    "input_hashes": {
                        input_relative: hashlib.sha256(
                            input_path.read_bytes()
                        ).hexdigest()
                    },
                    "raw_result_hashes": {
                        raw_relative: hashlib.sha256(
                            raw_path.read_bytes()
                        ).hexdigest()
                    },
                }
            )
        started = raw_started or (
            self.base_time - dt.timedelta(seconds=30)
        )
        raw_done = raw_completed or (
            self.base_time - dt.timedelta(seconds=20)
        )
        evidence_done = evidence_completed or (
            self.base_time - dt.timedelta(seconds=10)
        )
        raw = {
            "schema_version": 1,
            "condition_id": gate_id,
            "gate_id": gate["mandatory_gate_when_ready"],
            "gate_stage": gate_stage,
            "state": state,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": BUNDLE_RELATIVE,
            "frozen_bundle_sha256": self.bundle_sha256,
            "run_id": run_identifier,
            "producer_id": catalog["evidence_producer_id"],
            "executor_ids": list(catalog["executor_ids"]),
            "acceptance_case_ids": cases,
            "observation": dict(observation),
            "started_at": self.timestamp(started),
            "completed_at": self.timestamp(raw_done),
            "status": "pass",
            "actual_cases_run": len(cases),
            "case_results": case_results,
        }
        raw_relative = (
            f"{catalog['raw_result_path_prefix']}{run_identifier}.json"
        )
        raw_path = self.write_json(raw_relative, raw)
        raw_result_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        completed_at = self.timestamp(evidence_done)
        run_payload = {
            "run_id": run_identifier,
            "condition_id": gate_id,
            "gate_id": gate["mandatory_gate_when_ready"],
            "gate_stage": gate_stage,
            "state": state,
            "source_event_seq": observation["source_event_seq"],
            "source_event_hash": observation["source_event_hash"],
            "source_state_hash": observation["source_state_hash"],
            "source_anchor_hash": observation["source_anchor_hash"],
            "raw_result_path": raw_relative,
            "raw_result_sha256": raw_result_sha256,
            "completed_at": completed_at,
            "producer_id": catalog["evidence_producer_id"],
            "executor_ids": list(catalog["executor_ids"]),
            "acceptance_case_ids": cases,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": BUNDLE_RELATIVE,
            "frozen_bundle_sha256": self.bundle_sha256,
        }
        if run_payload_extra:
            run_payload.update(run_payload_extra)
        if append_receipt:
            receipt = self.append_gate_run_receipt(
                run_payload,
                append_anchor=append_receipt_anchor,
            )
        elif run_receipt is not None:
            receipt = dict(run_receipt)
        else:
            receipt = {
                "authority": "runtime_sqlite_gate_run_receipt",
                "run_event_seq": 1,
                "run_event_hash": ZERO_HASH,
                "run_anchor_hash": ZERO_HASH,
                "run_id": run_identifier,
                "condition_id": gate_id,
                "gate_id": gate["mandatory_gate_when_ready"],
                "gate_stage": gate_stage,
                "state": state,
                "source_event_seq": observation["source_event_seq"],
                "source_event_hash": observation["source_event_hash"],
                "source_state_hash": observation["source_state_hash"],
                "source_anchor_hash": observation["source_anchor_hash"],
                "raw_result_path": raw_relative,
                "raw_result_sha256": raw_result_sha256,
                "completed_at": completed_at,
            }
        evidence = {
            "schema_version": 2,
            "condition_id": gate_id,
            "gate_id": gate["mandatory_gate_when_ready"],
            "gate_stage": gate_stage,
            "state": state,
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": BUNDLE_RELATIVE,
            "frozen_bundle_sha256": self.bundle_sha256,
            "run_id": run_identifier,
            "producer_id": catalog["evidence_producer_id"],
            "executor_ids": list(catalog["executor_ids"]),
            "acceptance_case_ids": cases,
            "observation": dict(observation),
            "run_receipt": receipt,
            "raw_result_path": raw_relative,
            "raw_result_sha256": raw_result_sha256,
            "completed_at": completed_at,
        }
        evidence_path = self.write_json(gate["evidence_path"], evidence)
        return raw, evidence, raw_path, evidence_path

    def rewrite_raw_and_evidence(
        self,
        raw: dict[str, Any],
        evidence: dict[str, Any],
        raw_path: Path,
        evidence_path: Path,
    ) -> None:
        raw_path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        evidence["raw_result_sha256"] = hashlib.sha256(
            raw_path.read_bytes()
        ).hexdigest()
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def forged_receipt_view(
        evidence: dict[str, Any],
        anchored_receipt: dict[str, Any],
    ) -> dict[str, Any]:
        forged = dict(anchored_receipt)
        for field in (
            "run_id",
            "condition_id",
            "gate_id",
            "gate_stage",
            "state",
            "raw_result_path",
            "raw_result_sha256",
            "completed_at",
        ):
            forged[field] = evidence[field]
        for field in (
            "source_event_seq",
            "source_event_hash",
            "source_state_hash",
            "source_anchor_hash",
        ):
            forged[field] = evidence["observation"][field]
        return forged

    def test_missing_tiingo_token_is_unproved_not_failed(self) -> None:
        result = self.run_gate("COND-TIINGO-LIVE-PROBE")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(
            payload["aggregate_verdict"], "core_pass_with_unproven_conditions"
        )
        self.assertEqual(
            payload["results"][0]["effective_state"],
            "not_run_missing_user_credential",
        )

    def test_present_token_without_evidence_is_blocked_and_not_leaked(self) -> None:
        secret = "test-token-must-not-appear"
        result = self.run_gate("COND-TIINGO-LIVE-PROBE", token=secret)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertNotIn(secret, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["aggregate_verdict"], "blocked")
        self.assertEqual(payload["results"][0]["effective_state"], "mandatory_pending")
        self.assertIn(
            "prerequisite_ready_but_evidence_missing",
            payload["results"][0]["errors"],
        )
        self.assertFalse(
            payload["results"][0]["prerequisite_observation"]["secret_value_read"]
        )

    def test_unknown_gate_is_usage_error(self) -> None:
        result = self.run_gate("COND-NOT-REAL")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("unknown conditional gate", result.stdout)

    def test_evidence_cannot_self_report_field_use_readiness(self) -> None:
        self.write_json(
            "evidence/conditional/javen_field_use.json",
            {
                "condition_id": "COND-JAVEN-FIELD-USE",
                "prerequisite_ready": True,
                "state": "passed",
            },
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            target_verdict="human_onboarding_verified",
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        payload = json.loads(result.stdout)
        observation = payload["results"][0]
        self.assertFalse(observation["prerequisite_ready"])
        self.assertIn(
            "gate_evidence_present_without_authoritative_prerequisite",
            observation["errors"],
        )
        self.assertIn("target_verdict_requirements_not_met", observation["errors"])

    def test_authoritative_ready_state_requires_gate_evidence(self) -> None:
        runtime_db, _ = self.create_runtime_chain()
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        payload = json.loads(result.stdout)
        observation = payload["results"][0]
        self.assertTrue(observation["prerequisite_ready"])
        self.assertEqual(observation["effective_state"], "mandatory_pending")
        self.assertIn(
            "prerequisite_ready_but_evidence_missing", observation["errors"]
        )

    def test_trusted_event_raw_result_and_evidence_path_passes(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="core_release_candidate",
            expected_commit=self.candidate_commit,
            expected_tree=self.candidate_tree,
            expected_bundle_path=BUNDLE_RELATIVE,
            expected_bundle_sha256=self.bundle_sha256,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(
            payload["aggregate_verdict"], "all_selected_conditions_passed"
        )
        self.assertEqual(payload["results"][0]["effective_state"], "passed")
        self.assertEqual(payload["runtime_authority"]["mode"], "fixture")
        self.assertFalse(
            payload["runtime_authority"]["fixture_release_allowed"]
        )
        self.assertEqual(
            payload["authoritative_bindings"]["candidate_commit"],
            self.candidate_commit,
        )
        self.assertEqual(
            payload["authoritative_bindings"]["frozen_bundle_sha256"],
            self.bundle_sha256,
        )

    def test_environment_gate_receipt_can_be_first_main_event(self) -> None:
        connection = sqlite3.connect(self.authoritative_runtime_db)
        try:
            self.create_runtime_schema(connection)
            connection.commit()
        finally:
            connection.close()
        self.build_evidence(
            self.presence_observation(),
            gate_id="COND-TIINGO-LIVE-PROBE",
            gate_stage="live_probe",
        )
        result = self.run_gate(
            "COND-TIINGO-LIVE-PROBE",
            token="fixture-token",
            runtime_db=self.authoritative_runtime_db,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["results"][0]["effective_state"], "passed")

    def test_fixture_runtime_cannot_satisfy_human_release(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["aggregate_verdict"], "blocked")
        self.assertIn(
            "fixture_runtime_cannot_satisfy_release",
            payload["results"][0]["errors"],
        )

    def test_when_zero_append_only_trigger_escape_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            trigger_escape="when_zero"
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="core_release_candidate",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn(
            "runtime_append_only_trigger_invalid:events_no_update",
            errors,
        )
        self.assertIn("runtime_append_only_event_update_not_blocked", errors)

    def test_unreachable_raise_trigger_escape_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            trigger_escape="unreachable_raise"
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="core_release_candidate",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn(
            "runtime_append_only_trigger_invalid:events_no_update",
            errors,
        )
        self.assertIn("runtime_append_only_event_update_not_blocked", errors)

    def test_valid_caller_selected_runtime_path_cannot_replace_authority(
        self,
    ) -> None:
        alternate_root = self.root / "attacker-selected-runtime"
        alternate_db = alternate_root / "runtime.sqlite3"
        alternate_anchor = alternate_root / "anchors.jsonl"
        runtime_db, observation = self.create_runtime_chain(
            runtime_db=alternate_db,
            anchor_path=alternate_anchor,
        )
        self.build_evidence(observation, append_receipt=False)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="core_release_candidate",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("expected_runtime_db_mismatch", errors)
        self.assertIn(
            "gate_evidence_present_without_authoritative_prerequisite",
            errors,
        )

    def test_round3_original_self_attestation_counterexample_is_rejected(
        self,
    ) -> None:
        runtime_db, forged_observation = self.create_one_row_forgery()
        raw, evidence, raw_path, evidence_path = self.build_evidence(
            forged_observation,
            append_receipt=False,
        )
        raw["frozen_bundle_sha256"] = ZERO_HASH
        raw["actual_cases_run"] = 0
        evidence["frozen_bundle_sha256"] = ZERO_HASH
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
            expected_bundle_sha256=ZERO_HASH,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        errors = payload["results"][0]["errors"]
        self.assertIn("expected_runtime_db_mismatch", errors)
        self.assertIn(
            "gate_evidence_present_without_authoritative_prerequisite",
            errors,
        )
        self.assertIn("expected_frozen_bundle_sha256_mismatch", errors)

    def test_all_zero_bundle_hash_is_not_authoritative(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        raw["frozen_bundle_sha256"] = ZERO_HASH
        evidence["frozen_bundle_sha256"] = ZERO_HASH
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
            expected_bundle_sha256=ZERO_HASH,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("expected_frozen_bundle_sha256_mismatch", errors)
        self.assertIn("gate_evidence_frozen_bundle_sha256_mismatch", errors)
        self.assertIn("raw_result_frozen_bundle_sha256_mismatch", errors)

    def test_zero_actual_cases_run_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        raw["actual_cases_run"] = 0
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("raw_result_actual_cases_run_mismatch", errors)

    def test_extra_case_is_rejected_by_exact_set_equality(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        extra_case = "CASE-ATTACKER-EXTRA"
        evidence["acceptance_case_ids"].append(extra_case)
        raw["acceptance_case_ids"].append(extra_case)
        extra_result = dict(raw["case_results"][0])
        extra_result["case_id"] = extra_case
        raw["case_results"].append(extra_result)
        raw["actual_cases_run"] += 1
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_acceptance_case_binding_mismatch", errors)
        self.assertIn("raw_result_acceptance_case_binding_mismatch", errors)
        self.assertIn("raw_result_case_set_mismatch", errors)
        self.assertIn("gate_run_receipt_evidence_mismatch", errors)

    def test_nonpassing_per_case_status_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        raw["case_results"][0]["status"] = "fail"
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertTrue(
            any(error.startswith("raw_result_case_status_not_pass") for error in errors),
            errors,
        )

    def test_stale_raw_result_and_evidence_are_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        max_age = self.catalog("COND-JAVEN-FIELD-USE")[
            "max_evidence_age_seconds"
        ]
        stale_completed = self.base_time - dt.timedelta(seconds=max_age + 60)
        raw, evidence, raw_path, evidence_path = self.build_evidence(
            observation,
            raw_started=stale_completed - dt.timedelta(seconds=10),
            raw_completed=stale_completed,
            evidence_completed=stale_completed,
        )
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_evidence_stale", errors)
        self.assertIn("raw_result_stale", errors)

    def test_missing_gate_run_receipt_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        _, evidence, _, evidence_path = self.build_evidence(observation)
        evidence.pop("run_receipt")
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_evidence_missing_fields:run_receipt", errors)
        self.assertIn("gate_run_receipt_invalid", errors)

    def test_tampered_gate_run_receipt_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        _, evidence, _, evidence_path = self.build_evidence(observation)
        evidence["run_receipt"]["run_event_hash"] = "f" * 64
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_run_receipt_mismatch", errors)

    def test_unanchored_gate_run_receipt_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(
            observation,
            append_receipt_anchor=False,
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("authoritative_runtime_anchor_tail_mismatch", errors)
        self.assertIn("gate_run_receipt_unanchored", errors)
        self.assertIn("runtime_gate_run_projection_invalid:2", errors)

    def test_same_gate_run_id_reuse_after_overwrite_is_rejected(self) -> None:
        runtime_db, first_observation = self.create_runtime_chain()
        _, first_evidence, _, _ = self.build_evidence(first_observation)
        first_result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertEqual(first_result.returncode, 0, first_result.stdout)

        reused_run_id = first_evidence["run_id"]
        anchored_receipt = dict(first_evidence["run_receipt"])
        latest_observation = self.append_runtime_observation(runtime_db)
        _, overwritten_evidence, _, overwritten_evidence_path = (
            self.build_evidence(
                latest_observation,
                run_id=reused_run_id,
                append_receipt=False,
                run_receipt=anchored_receipt,
                raw_started=self.base_time - dt.timedelta(seconds=4),
                raw_completed=self.base_time - dt.timedelta(seconds=3),
                evidence_completed=self.base_time - dt.timedelta(seconds=2),
            )
        )
        overwritten_evidence["run_receipt"] = self.forged_receipt_view(
            overwritten_evidence,
            anchored_receipt,
        )
        overwritten_evidence_path.write_text(
            json.dumps(
                overwritten_evidence,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        replay_result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(replay_result.returncode, 0, replay_result.stdout)
        errors = json.loads(replay_result.stdout)["results"][0]["errors"]
        self.assertIn("gate_run_receipt_mismatch", errors)
        self.assertIn("gate_run_receipt_evidence_mismatch", errors)
        self.assertIn(
            "gate_run_receipt_replayed_against_latest_observation",
            errors,
        )

    def test_cross_gate_run_id_reuse_is_rejected_by_anchored_receipt(
        self,
    ) -> None:
        runtime_db, observation = self.create_runtime_chain()
        _, original_evidence, _, _ = self.build_evidence(observation)
        reused_run_id = original_evidence["run_id"]
        anchored_receipt = dict(original_evidence["run_receipt"])
        _, copied_evidence, _, copied_evidence_path = self.build_evidence(
            self.presence_observation(),
            gate_id="COND-TIINGO-LIVE-PROBE",
            gate_stage="live_probe",
            run_id=reused_run_id,
            append_receipt=False,
            run_receipt=anchored_receipt,
        )
        copied_evidence["run_receipt"] = self.forged_receipt_view(
            copied_evidence,
            anchored_receipt,
        )
        copied_evidence_path.write_text(
            json.dumps(copied_evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result = self.run_gate(
            "COND-TIINGO-LIVE-PROBE",
            token="fixture-token",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_run_id_replayed", errors)
        self.assertIn("gate_run_receipt_mismatch", errors)
        self.assertIn("gate_run_receipt_evidence_mismatch", errors)

    def test_gate_run_unique_run_id_schema_weakening_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            unique_run_id=False
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn(
            "runtime_gate_run_unique_constraint_invalid",
            errors,
        )

    def test_duplicate_run_id_in_anchored_history_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            unique_run_id=False
        )
        _, first_evidence, _, _ = self.build_evidence(observation)
        latest_observation = self.append_runtime_observation(runtime_db)
        self.build_evidence(
            latest_observation,
            run_id=first_evidence["run_id"],
            raw_started=self.base_time - dt.timedelta(seconds=4),
            raw_completed=self.base_time - dt.timedelta(seconds=3),
            evidence_completed=self.base_time - dt.timedelta(seconds=2),
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertTrue(
            any(
                error.startswith("runtime_gate_run_id_duplicate:")
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                error.startswith(
                    "runtime_gate_run_projection_duplicate_run_id:"
                )
                for error in errors
            ),
            errors,
        )

    def test_gate_run_append_only_trigger_escape_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            trigger_escape="gate_run_when_zero"
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn(
            (
                "runtime_append_only_trigger_invalid:"
                "conditional_gate_runs_no_update"
            ),
            errors,
        )
        self.assertIn(
            "runtime_append_only_gate_run_update_not_blocked",
            errors,
        )

    def test_gate_run_projection_tampering_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(observation)
        connection = sqlite3.connect(runtime_db)
        try:
            connection.execute(
                "DROP TRIGGER conditional_gate_runs_no_update"
            )
            connection.execute(
                "UPDATE conditional_gate_runs "
                "SET run_event_hash = ?",
                ("f" * 64,),
            )
            connection.execute(
                "CREATE TRIGGER conditional_gate_runs_no_update "
                "BEFORE UPDATE ON conditional_gate_runs "
                "BEGIN SELECT RAISE(ABORT, 'append_only'); END"
            )
            connection.commit()
        finally:
            connection.close()
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("runtime_gate_run_projection_invalid:2", errors)

    def test_gate_run_payload_extra_field_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(
            observation,
            run_payload_extra={"caller_assertion": "trusted"},
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn(
            "runtime_gate_run_payload_fields_invalid:2",
            errors,
        )
        self.assertIn("gate_run_receipt_evidence_mismatch", errors)

    def test_evidence_replay_after_new_observation_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        self.build_evidence(observation)
        self.append_runtime_observation(runtime_db)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_observation_binding_mismatch", errors)

    def test_run_id_reuse_across_gate_evidence_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        _, evidence, _, _ = self.build_evidence(observation)
        self.write_json(
            "evidence/conditional/longitudinal_edge.json", dict(evidence)
        )
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_run_id_replayed", errors)

    def test_cross_candidate_raw_and_evidence_are_rejected_even_if_cli_agrees(
        self,
    ) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        attacker_commit = "f" * 40
        raw["candidate_commit"] = attacker_commit
        evidence["candidate_commit"] = attacker_commit
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
            expected_commit=attacker_commit,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("expected_candidate_commit_mismatch", errors)
        self.assertIn("gate_evidence_candidate_commit_mismatch", errors)
        self.assertIn("raw_result_candidate_commit_mismatch", errors)
        self.assertIn("gate_run_receipt_evidence_mismatch", errors)

    def test_broken_runtime_event_hash_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            broken_event_hash=True
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("runtime_event_hash_invalid:1", errors)

    def test_caller_selected_runtime_producer_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain(
            producer_id="ATTACKER-SELECTED-PRODUCER"
        )
        self.build_evidence(observation)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("runtime_event_producer_not_authorized:1", errors)

    def test_caller_selected_evidence_producer_is_rejected(self) -> None:
        runtime_db, observation = self.create_runtime_chain()
        raw, evidence, raw_path, evidence_path = self.build_evidence(observation)
        raw["producer_id"] = "ATTACKER-SELECTED-PRODUCER"
        evidence["producer_id"] = "ATTACKER-SELECTED-PRODUCER"
        self.rewrite_raw_and_evidence(raw, evidence, raw_path, evidence_path)
        result = self.run_gate(
            "COND-JAVEN-FIELD-USE",
            runtime_db=runtime_db,
            target_verdict="human_onboarding_verified",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        errors = json.loads(result.stdout)["results"][0]["errors"]
        self.assertIn("gate_evidence_producer_not_authorized", errors)


if __name__ == "__main__":
    unittest.main()
