#!/usr/bin/env python3
"""Adversarial tests for the closed declarative shadow runner."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_shadow_acceptance as rsa


HERE = Path(__file__).resolve().parent
POLICY = HERE / "SHADOW_CAPABILITY_POLICY.json"
RUNNER = HERE / "run_shadow_acceptance.py"


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: object) -> None:
    write_bytes(path, rsa.canonical_text(value).encode("utf-8"))


class ShadowAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otts-declarative-test-")
        self.root = Path(self.temporary.name) / "shadow"
        self.root.mkdir()
        self.program_path = self.root / "program.json"
        self.fixture_path = self.root / "fixture.json"
        self.program = {
            "schema_version": "otts.shadow-declarative-ir/1",
            "program_id": "SAFE-IR",
            "input_type": "JSON",
            "output_type": "JSON",
            "nodes": [
                {"id": "input", "op": "INPUT"},
                {"id": "value", "op": "JSON_POINTER", "source": "input", "pointer": "/value"},
                {"id": "result", "op": "BUILD_OBJECT", "entries": [{"key": "value", "ref": "value"}]},
            ],
            "result_ref": "result",
        }
        self.fixture = {"value": "safe fixture"}
        write_json(self.program_path, self.program)
        write_json(self.fixture_path, self.fixture)
        self.policy_snapshot = rsa.read_once_regular(POLICY, "policy", 524288)
        self.policy = rsa.load_policy_snapshot(self.policy_snapshot)
        self.runner_snapshot = rsa.read_once_regular(RUNNER, "runner", 2 * 1024 * 1024)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def snapshot(self, path: Path, label: str = "test") -> rsa.Snapshot:
        return rsa.read_once_regular(path, label, 2 * 1024 * 1024)

    def base_shadow(self) -> dict:
        result = {"value": "safe fixture"}
        return {
            "capability_policy_sha256": self.policy_snapshot.sha256,
            "program": "program.json",
            "acceptance_cases": [{
                "case_id": "SAFE-1",
                "fixture_path": "fixture.json",
                "expected_result_sha256": rsa.sha256_bytes(rsa.canonical_bytes(result)),
            }],
            "sbom": {"path": "SBOM.json", "sha256": "0" * 64},
            "capability_report": {"path": "CAPABILITY_REPORT.json", "sha256": "0" * 64},
            "acceptance_test_report": {"path": "ACCEPTANCE_TEST_REPORT.json", "sha256": "0" * 64},
            "snapshot_ledger": {"path": "SNAPSHOT_LEDGER.json", "sha256": "0" * 64},
            "entries": [
                {"path": "program.json", "sha256": self.snapshot(self.program_path).sha256, "role": "ir-program"},
                {"path": "fixture.json", "sha256": self.snapshot(self.fixture_path).sha256, "role": "fixture"},
            ],
        }

    def local_case_response(self) -> dict:
        with tempfile.TemporaryDirectory(prefix="otts-local-eval-") as temporary:
            output = Path(temporary) / "output"
            cas = output / "cas"
            cas.mkdir(parents=True)
            result, steps = rsa.evaluate_program(self.program, self.fixture, self.policy, cas)
            inventory = rsa._output_inventory(output, self.policy["limits"])
        result_bytes = rsa.canonical_bytes(result)
        module_path = rsa.TRUSTED_PYTHON_HOME / "lib/python3.9/json/__init__.py"
        module_snapshot = rsa._trusted_binary_snapshot(module_path, "test module")
        module_rows = [{
            "path": str(module_path), "sha256": module_snapshot.sha256,
            "byte_length": len(module_snapshot.data), "modules": ["json"],
        }]
        runtime_observation = {
            "python_version": "3.9.6 synthetic-test-binding",
            "python_implementation_cache_tag": "cpython-39",
            "python_executable": str(rsa.TRUSTED_PYTHON),
            "python_prefix": str(rsa.TRUSTED_PYTHON_HOME),
            "loaded_module_files": module_rows,
            "loaded_module_file_closure_digest_sha256": rsa.sha256_json(module_rows),
            "closure_scope": "ACTUALLY_LOADED_PYTHON_MODULE_FILES_AT_RESPONSE_MEASUREMENT",
            "full_dynamic_library_and_host_runtime_closure_proven": False,
        }
        return {
            "ok": True,
            "result_sha256": rsa.sha256_bytes(result_bytes),
            "result_type": rsa.json_type_name(result),
            "result_byte_length": len(result_bytes),
            "steps": steps,
            "output_inventory_digest_sha256": rsa.sha256_json(inventory),
            "runtime_observation": runtime_observation,
            "program_sha256": self.snapshot(self.program_path).sha256,
            "fixture_sha256": self.snapshot(self.fixture_path).sha256,
            "runner_sha256": self.runner_snapshot.sha256,
            "policy_sha256": self.policy_snapshot.sha256,
            "node_graph_digest_sha256": rsa.validate_program(self.program, self.policy)["node_graph_digest_sha256"],
            "sandbox_observed_enforcement": {
                "CHILD_PROCESS_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_READ_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_WRITE_DENIED": "OBSERVED_DENIED",
                "NETWORK_LOOPBACK_BIND_DENIED": "OBSERVED_DENIED",
            },
            "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
            "exact_opened_unlinked_snapshot_execution": True,
            "staged_target_controlled_pathname_reopen_count": 0,
            "same_uid_concurrent_mutation_resistance_proven": False,
            "host_level_universal_noninterference_proven": False,
            "sandbox_inherited_fd_boundary": "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_BOUNDED_UNLINKED_STDIO_FDS; POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED",
            "sandbox_same_runtime_reexec_residual": "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; CLOSED_IR_HAS_NO_EXEC_OPCODE",
            "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED",
        }

    def materialize_package(self) -> tuple[dict, dict]:
        shadow = self.base_shadow()
        sbom, capability, initial_entries = rsa.build_static_reports(
            shadow_root=self.root, shadow=shadow, policy_path=POLICY,
            policy_snapshot=self.policy_snapshot, runner_snapshot=self.runner_snapshot,
        )
        ledger = rsa.build_snapshot_ledger(
            entries=initial_entries, policy_snapshot=self.policy_snapshot,
            runner_snapshot=self.runner_snapshot,
        )
        ledger_path = self.root / "SNAPSHOT_LEDGER.json"
        write_json(ledger_path, ledger)
        shadow["entries"].append({
            "path": ledger_path.name, "sha256": self.snapshot(ledger_path).sha256,
            "role": "snapshot-ledger",
        })
        shadow["snapshot_ledger"]["sha256"] = self.snapshot(ledger_path).sha256
        sbom_path = self.root / "SBOM.json"
        write_json(sbom_path, sbom)
        capability["sbom_sha256"] = self.snapshot(sbom_path).sha256
        capability_path = self.root / "CAPABILITY_REPORT.json"
        write_json(capability_path, capability)
        for path, role in ((sbom_path, "sbom"), (capability_path, "capability-report")):
            shadow["entries"].append({"path": path.name, "sha256": self.snapshot(path).sha256, "role": role})
        shadow["sbom"]["sha256"] = self.snapshot(sbom_path).sha256
        shadow["capability_report"]["sha256"] = self.snapshot(capability_path).sha256

        entries = rsa._entry_map(self.root, shadow, self.policy, None)
        ledger = rsa.build_snapshot_ledger(entries=entries, policy_snapshot=self.policy_snapshot, runner_snapshot=self.runner_snapshot)
        tcb = rsa.runtime_tcb_document(self.runner_snapshot)
        response = self.local_case_response()
        tcb["loaded_python_module_file_closure"] = response["runtime_observation"]
        case_results = [{
            "case_id": "SAFE-1", "fixture_path": "fixture.json",
            "fixture_sha256": self.snapshot(self.fixture_path).sha256,
            "expected_result_sha256": response["result_sha256"],
            "actual_result_sha256": response["result_sha256"],
            "result_type": response["result_type"],
            "result_byte_length": response["result_byte_length"],
            "output_inventory_digest_sha256": response["output_inventory_digest_sha256"],
            "loaded_module_file_closure_digest_sha256": response["runtime_observation"]["loaded_module_file_closure_digest_sha256"],
        }]
        graph = rsa.validate_program(self.program, self.policy)
        report = {
            "schema_version": "otts.shadow-acceptance-test-report/3",
            "result": "LOCAL_DETERMINISTIC_DECLARATIVE_EVALUATION_PASS",
            "runner_sha256": self.runner_snapshot.sha256,
            "policy_sha256": self.policy_snapshot.sha256,
            "sbom_sha256": self.snapshot(sbom_path).sha256,
            "capability_report_sha256": self.snapshot(capability_path).sha256,
            "program_sha256": self.snapshot(self.program_path).sha256,
            "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
            "snapshot_ledger_sha256": self.snapshot(ledger_path).sha256,
            "runtime_tcb_digest_sha256": rsa.sha256_json(tcb),
            "loaded_module_file_closure_digest_sha256": response["runtime_observation"]["loaded_module_file_closure_digest_sha256"],
            "acceptance_output_set_digest_sha256": rsa.sha256_json(case_results),
            "program": "program.json", "cases": case_results,
            "language_level_artifact_executable_constructs": "ABSENT_BY_EXACT_SCHEMA",
            "os_sandbox_observed_enforcement": response["sandbox_observed_enforcement"],
            "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
            "exact_opened_unlinked_snapshot_execution": True,
            "staged_target_controlled_pathname_reopen_count": 0,
            "same_uid_concurrent_mutation_resistance_proven": False,
            "host_level_universal_noninterference_proven": False,
            "sandbox_inherited_fd_boundary": "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_BOUNDED_UNLINKED_STDIO_FDS; POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED",
            "sandbox_same_runtime_reexec_residual": "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; CLOSED_IR_HAS_NO_EXEC_OPCODE",
            "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED",
            "aggregate_deadline_enforced": True,
            "aggregate_wall_timeout_seconds": self.policy["limits"]["aggregate_wall_timeout_seconds"],
            "runtime_authority": False, "deployment_authority": False,
            "freeze_authority": False, "external_action_authority": False,
        }
        report_path = self.root / "ACCEPTANCE_TEST_REPORT.json"
        write_json(report_path, report)
        shadow["entries"].append({"path": report_path.name, "sha256": self.snapshot(report_path).sha256, "role": "acceptance-report"})
        shadow["acceptance_test_report"]["sha256"] = self.snapshot(report_path).sha256
        return shadow, response

    def test_valid_ir_evaluates_and_has_no_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, steps = rsa.evaluate_program(
                self.program, self.fixture, self.policy, Path(temporary)
            )
        self.assertEqual(result, {"value": "safe fixture"})
        self.assertEqual(steps, 3)
        shadow, response = self.materialize_package()
        with mock.patch.object(rsa, "run_case", return_value=response):
            accepted = rsa.validate_shadow_acceptance(
                shadow_root=self.root, shadow=shadow, policy_path=POLICY,
                runner_path=RUNNER, policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )
        self.assertTrue(accepted["local_deterministic_declarative_evaluation_pass"])
        self.assertTrue(accepted["exact_opened_unlinked_snapshot_execution"])
        self.assertEqual(accepted["staged_target_controlled_pathname_reopen_count"], 0)
        self.assertFalse(accepted["same_uid_concurrent_mutation_resistance_proven"])
        self.assertFalse(accepted["host_level_universal_noninterference_proven"])
        for key in ("runtime_authority", "deployment_authority", "freeze_authority", "external_action_authority"):
            self.assertFalse(accepted[key])
        for key in ("program_sha256", "snapshot_ledger_sha256", "node_graph_digest_sha256", "runtime_tcb_digest_sha256", "loaded_module_file_closure_digest_sha256", "acceptance_output_set_digest_sha256"):
            self.assertRegex(accepted[key], r"^[0-9a-f]{64}$")

    def test_duplicate_extra_and_missing_keys_rejected(self) -> None:
        duplicate = b'{"schema_version":"x","schema_version":"y"}\n'
        snap = rsa.Snapshot(duplicate, rsa.sha256_bytes(duplicate), (0, 0, 0, 1, len(duplicate), 0, 0), "memory")
        with self.assertRaisesRegex(rsa.CapabilityError, "duplicate JSON key"):
            rsa.canonical_load_snapshot(snap, "duplicate")
        for mutation in (lambda p: p.update({"extra": 1}), lambda p: p.pop("output_type")):
            program = copy.deepcopy(self.program)
            mutation(program)
            with self.assertRaisesRegex(rsa.CapabilityError, "key mismatch"):
                rsa.validate_program(program, self.policy)

    def test_unknown_opcode_type_ref_cycle_and_unreachable_rejected(self) -> None:
        variants: list[tuple[str, dict, str]] = []
        unknown_op = copy.deepcopy(self.program); unknown_op["nodes"][1]["op"] = "EVAL"
        variants.append(("opcode", unknown_op, "unknown opcode"))
        unknown_type = copy.deepcopy(self.program); unknown_type["input_type"] = "PATH"
        variants.append(("type", unknown_type, "must be JSON"))
        unknown_ref = copy.deepcopy(self.program); unknown_ref["nodes"][1]["source"] = "missing"
        variants.append(("ref", unknown_ref, "unknown refs"))
        cycle = copy.deepcopy(self.program); cycle["nodes"][0] = {"id": "input", "op": "JSON_POINTER", "source": "value", "pointer": ""}; cycle["nodes"].insert(0, {"id": "actual", "op": "INPUT"}); cycle["nodes"][2]["source"] = "input"
        variants.append(("cycle", cycle, "cycle"))
        unreachable = copy.deepcopy(self.program); unreachable["nodes"].append({"id": "unused", "op": "LITERAL", "value": 1})
        variants.append(("unreachable", unreachable, "unreachable"))
        for name, program, message in variants:
            with self.subTest(name=name), self.assertRaisesRegex(rsa.CapabilityError, message):
                rsa.validate_program(program, self.policy)

    def test_executable_suffixes_and_file_kinds_rejected(self) -> None:
        for suffix in (".py", ".pyc", ".so", ".dylib", ".exe"):
            path = self.root / f"artifact{suffix}"
            write_bytes(path, b"x")
            shadow = self.base_shadow()
            shadow["entries"].append({"path": path.name, "sha256": self.snapshot(path).sha256, "role": "ir-test-program"})
            with self.subTest(suffix=suffix), self.assertRaisesRegex(rsa.CapabilityError, "suffix"):
                rsa.build_static_reports(shadow_root=self.root, shadow=shadow, policy_path=POLICY)
        symlink = self.root / "link.json"; symlink.symlink_to(self.program_path)
        with self.assertRaises(rsa.CapabilityError):
            rsa.read_once_regular(symlink, "symlink", 1000)
        hardlink = self.root / "hard.json"; os.link(self.program_path, hardlink)
        with self.assertRaisesRegex(rsa.CapabilityError, "hardlinked"):
            rsa.read_once_regular(hardlink, "hardlink", 10000)
        hardlink.unlink()
        with self.assertRaisesRegex(rsa.CapabilityError, "regular"):
            rsa.read_once_regular(self.root, "directory", 10000)
        os.chmod(self.fixture_path, 0o755)
        executable_shadow = self.base_shadow()
        with self.assertRaisesRegex(rsa.CapabilityError, "executable mode"):
            rsa.build_static_reports(
                shadow_root=self.root, shadow=executable_shadow, policy_path=POLICY
            )
        os.chmod(self.fixture_path, 0o644)

    def test_profile_is_exact_template_substitution_without_broad_mach_rule(self) -> None:
        writable = self.root / "runtime"
        profile = rsa._sandbox_profile(
            output_dir=writable, probe_root=self.root, runtime=rsa.TRUSTED_PYTHON
        )
        expected = rsa.SANDBOX_PROFILE_TEMPLATE.format(
            runtime=rsa._sbpl_literal(rsa.TRUSTED_PYTHON),
            python_home=rsa._sbpl_literal(rsa.TRUSTED_PYTHON_HOME),
            output_dir=rsa._sbpl_literal(writable),
            probe_root=rsa._sbpl_literal(self.root),
        )
        self.assertEqual(profile, expected)
        self.assertNotIn("mach-lookup", profile)
        self.assertEqual(
            rsa.runtime_tcb_document(self.runner_snapshot)["profile_template_sha256"],
            rsa.sha256_bytes(rsa.SANDBOX_PROFILE_TEMPLATE.encode("utf-8")),
        )
        self.assertNotIn("staged", profile)

    def test_opened_unlinked_fd_ignores_same_name_substitution(self) -> None:
        staged = self.root / "fd-stage"; staged.mkdir(mode=0o700)
        original = b"trusted opened bytes\n"
        fd = rsa._open_verified_unlinked_bytes(
            staged, "request.json", original, "FD race test"
        )
        replacement = staged / "request.json"
        self.assertFalse(replacement.exists())
        write_bytes(replacement, b"attacker replacement\n")
        try:
            snapshot = rsa._snapshot_open_fd(
                fd, "unlinked FD", 1024, "test-fd", allowed_nlinks=(0,)
            )
            self.assertEqual(snapshot.data, original)
            self.assertEqual(os.fstat(fd).st_nlink, 0)
        finally:
            os.close(fd)
        self.assertEqual(replacement.read_bytes(), b"attacker replacement\n")

    def test_xcode_runtime_anchor_and_parent_residual_are_bound(self) -> None:
        tcb = rsa.runtime_tcb_document(self.runner_snapshot)
        runtime = tcb["python_runtime"]
        self.assertEqual(runtime["anchor"], "/Applications/Xcode.app")
        self.assertEqual(runtime["path"], str(rsa.TRUSTED_PYTHON))
        self.assertEqual(runtime["home"], str(rsa.TRUSTED_PYTHON_HOME))
        for row in runtime["anchor_to_runtime_security_chain"]:
            self.assertEqual(row["uid"], 0)
            self.assertEqual(int(row["mode"], 8) & 0o022, 0)
        residual = tcb["applications_parent_ancestor_residual"]
        self.assertEqual(residual["path"], "/Applications")
        self.assertTrue(residual["group_writable"])
        self.assertEqual(
            residual["threat_model_status"],
            "EXCLUDED_HOSTILE_SAME_UID_OR_ADMIN_RACE_AND_RESTORE",
        )
        self.assertFalse(tcb["same_uid_concurrent_mutation_resistance_proven"])
        self.assertFalse(tcb["full_dynamic_library_and_host_runtime_closure_proven"])

    def test_loaded_module_closure_tamper_is_rejected(self) -> None:
        observation = self.local_case_response()["runtime_observation"]
        self.assertEqual(rsa._validate_runtime_observation(observation), observation)
        tampered = copy.deepcopy(observation)
        tampered["loaded_module_files"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(rsa.CapabilityError, "hash/length mismatch"):
            rsa._validate_runtime_observation(tampered)

    def test_policy_cannot_expand_runner_fixed_ceilings(self) -> None:
        document = rsa.canonical_load_snapshot(self.policy_snapshot, "policy")
        document["limits"]["max_nodes"] += 1
        data = rsa.canonical_text(document).encode("utf-8")
        snapshot = rsa.Snapshot(
            data, rsa.sha256_bytes(data), self.policy_snapshot.stat_identity, "memory"
        )
        with self.assertRaisesRegex(rsa.CapabilityError, "fixed ceilings"):
            rsa.load_policy_snapshot(snapshot)

    def test_manifest_total_input_fanout_cases_and_aggregate_caps(self) -> None:
        too_many = self.base_shadow()
        too_many["entries"] = [
            {"path": f"f-{index}.json", "sha256": self.policy_snapshot.sha256, "role": "fixture"}
            for index in range(self.policy["limits"]["max_manifest_entries"] + 1)
        ]
        with self.assertRaisesRegex(rsa.CapabilityError, "fixed limit"):
            rsa._entry_map(self.root, too_many, self.policy, {})

        large_data = b"x" * self.policy["limits"]["max_report_bytes"]
        large_identity = list(self.policy_snapshot.stat_identity)
        large_identity[6] = len(large_data)
        large_snapshot = rsa.Snapshot(
            large_data, rsa.sha256_bytes(large_data),
            tuple(large_identity), "memory",
        )
        count = self.policy["limits"]["max_total_input_bytes"] // len(large_data) + 1
        total_shadow = self.base_shadow()
        total_shadow["entries"] = [
            {"path": f"doc-{index}.txt", "sha256": large_snapshot.sha256, "role": "document"}
            for index in range(count)
        ]
        snapshots = {entry["path"]: large_snapshot for entry in total_shadow["entries"]}
        with self.assertRaisesRegex(rsa.CapabilityError, "total input"):
            rsa._entry_map(self.root, total_shadow, self.policy, snapshots)

        fanout = copy.deepcopy(self.program)
        fanout["nodes"][2]["entries"] = [
            {"key": f"k{index}", "ref": "value"}
            for index in range(self.policy["limits"]["max_build_object_entries"] + 1)
        ]
        with self.assertRaisesRegex(rsa.CapabilityError, "bounded list"):
            rsa.validate_program(fanout, self.policy)

        shadow, response = self.materialize_package()
        shadow["acceptance_cases"] = [copy.deepcopy(shadow["acceptance_cases"][0])
                                      for _ in range(self.policy["limits"]["max_acceptance_cases"] + 1)]
        with mock.patch.object(rsa, "run_case", return_value=response), self.assertRaisesRegex(
            rsa.CapabilityError, "fixed limit"
        ):
            rsa.validate_shadow_acceptance(
                shadow_root=self.root, shadow=shadow, policy_path=POLICY,
                runner_path=RUNNER, policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )
        shadow, response = self.materialize_package()
        with mock.patch.object(rsa.time, "monotonic", side_effect=[0, 61]), self.assertRaisesRegex(
            rsa.CapabilityError, "aggregate acceptance wall timeout"
        ):
            rsa.validate_shadow_acceptance(
                shadow_root=self.root, shadow=shadow, policy_path=POLICY,
                runner_path=RUNNER, policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )

    def test_literal_path_uri_module_and_operator_strings_never_dispatch(self) -> None:
        value = {
            "path": "/etc/passwd", "uri": "file:///etc/passwd",
            "module": "subprocess", "op": "CAS_GET", "operator": "eval",
        }
        program = {
            "schema_version": "otts.shadow-declarative-ir/1", "program_id": "LITERAL-DATA",
            "input_type": "JSON", "output_type": "JSON",
            "nodes": [{"id": "input", "op": "INPUT"}, {"id": "literal", "op": "LITERAL", "value": value}],
            "result_ref": "literal",
        }
        with self.assertRaisesRegex(rsa.CapabilityError, "unreachable"):
            rsa.validate_program(program, self.policy)
        program["nodes"][1] = {"id": "literal", "op": "BUILD_OBJECT", "entries": [{"key": "payload", "ref": "input"}]}
        with tempfile.TemporaryDirectory() as temporary:
            result, _ = rsa.evaluate_program(program, value, self.policy, Path(temporary))
        self.assertEqual(result, {"payload": value})

    def test_read_once_detects_opened_object_mutation(self) -> None:
        before = os.stat(self.program_path)
        changed = mock.Mock(
            st_dev=before.st_dev, st_ino=before.st_ino, st_mode=before.st_mode,
            st_nlink=before.st_nlink, st_uid=before.st_uid, st_gid=before.st_gid,
            st_size=before.st_size + 1,
            st_mtime_ns=before.st_mtime_ns, st_ctime_ns=before.st_ctime_ns,
        )
        original_fstat = os.fstat
        calls = 0
        def fstat(fd: int):
            nonlocal calls
            calls += 1
            return original_fstat(fd) if calls == 1 else changed
        with mock.patch.object(rsa.os, "fstat", side_effect=fstat), self.assertRaisesRegex(rsa.CapabilityError, "mutated"):
            rsa.read_once_regular(self.program_path, "mutating", 10000)

    def test_cas_digest_addressed_roundtrip_corruption_and_exclusive_create(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = rsa.canonical_bytes({"safe": True})
            flags_seen: list[int] = []
            original_open = rsa.os.open
            def tracked_open(path, flags, *args, **kwargs):
                if flags & os.O_CREAT:
                    flags_seen.append(flags)
                return original_open(path, flags, *args, **kwargs)
            with mock.patch.object(rsa.os, "open", side_effect=tracked_open):
                digest = rsa.cas_put_bytes(root, data, self.policy["limits"])
            self.assertEqual(rsa.cas_get_bytes(root, digest, self.policy["limits"]), data)
            self.assertTrue(any(flags & os.O_EXCL for flags in flags_seen))
            expected_path = root / digest[:2] / digest[2:]
            self.assertTrue(expected_path.is_file())
            os.chmod(expected_path, 0o600); expected_path.write_bytes(b"corrupt")
            with self.assertRaisesRegex(rsa.CapabilityError, "digest mismatch"):
                rsa.cas_get_bytes(root, digest, self.policy["limits"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            limits = dict(self.policy["limits"])
            limits["max_cas_total_bytes"] = 1
            with self.assertRaisesRegex(rsa.CapabilityError, "would exceed"):
                rsa.cas_put_bytes(root, b"two bytes", limits)
            self.assertEqual(list(root.rglob("*")), [])

    def test_size_depth_count_string_integer_step_and_output_boundaries(self) -> None:
        with self.assertRaisesRegex(rsa.CapabilityError, "exceeds"):
            rsa.read_once_regular(self.program_path, "tiny", 1)
        cases = [
            ({"a": {"b": {"c": 1}}}, "max_json_depth", 2, "depth"),
            ([1, 2, 3], "max_json_values", 2, "count"),
            ("abcd", "max_string_bytes", 3, "string"),
            (11, "max_integer_abs", 10, "integer"),
        ]
        for value, key, limit, message in cases:
            limits = dict(self.policy["limits"]); limits[key] = limit
            with self.subTest(key=key), self.assertRaisesRegex(rsa.CapabilityError, message):
                rsa._check_json_limits(value, limits, key)
        policy = copy.deepcopy(self.policy); policy["limits"]["max_steps"] = 2
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(rsa.CapabilityError, "step"):
            rsa.evaluate_program(self.program, self.fixture, policy, Path(temporary))
        policy = copy.deepcopy(self.policy); policy["limits"]["max_output_bytes"] = 4
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(rsa.CapabilityError, "output byte"):
            rsa.evaluate_program(self.program, self.fixture, policy, Path(temporary))
        policy = copy.deepcopy(self.policy)
        policy["limits"]["max_structural_value_bytes_total"] = 10
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            rsa.CapabilityError, "structural value byte total"
        ):
            rsa.evaluate_program(self.program, self.fixture, policy, Path(temporary))
        output = self.root / "quota-output"; output.mkdir()
        write_bytes(output / "one", b"123"); write_bytes(output / "two", b"456")
        limits = dict(self.policy["limits"]); limits["max_output_files"] = 1
        with self.assertRaisesRegex(rsa.CapabilityError, "inventory quota"):
            rsa._output_inventory(output, limits)
        limits = dict(self.policy["limits"]); limits["max_output_total_bytes"] = 5
        with self.assertRaisesRegex(rsa.CapabilityError, "inventory quota"):
            rsa._output_inventory(output, limits)

    def test_host_required_sandbox_denials_and_worker_success(self) -> None:
        if os.environ.get("OTTS_REQUIRE_HOST_SANDBOX") != "1":
            self.skipTest("set OTTS_REQUIRE_HOST_SANDBOX=1 for mandatory host integration")
        response = rsa.run_case(
            shadow_root=self.root, program_path=self.program_path,
            fixture_path=self.fixture_path, policy_path=POLICY,
            runner_path=RUNNER,
        )
        self.assertEqual(set(response["sandbox_observed_enforcement"]), {
            "CHILD_PROCESS_DENIED", "EXTERNAL_READ_DENIED",
            "EXTERNAL_WRITE_DENIED", "NETWORK_LOOPBACK_BIND_DENIED",
        })
        self.assertTrue(all(
            value == "OBSERVED_DENIED"
            for value in response["sandbox_observed_enforcement"].values()
        ))
        self.assertTrue(response["exact_opened_unlinked_snapshot_execution"])
        self.assertGreater(len(response["runtime_observation"]["loaded_module_files"]), 0)
        self.assertFalse(response["same_uid_concurrent_mutation_resistance_proven"])

    def test_sandbox_capability_error_is_never_converted_to_pass(self) -> None:
        with mock.patch.object(
            rsa, "_run_required_probes",
            side_effect=rsa.CapabilityError("sandbox unavailable"),
        ), self.assertRaisesRegex(rsa.CapabilityError, "sandbox unavailable"):
            rsa.run_case(
                shadow_root=self.root, program_path=self.program_path,
                fixture_path=self.fixture_path, policy_path=POLICY,
                runner_path=RUNNER,
            )

    def test_bounded_output_and_wall_timeout_kill_process_group(self) -> None:
        large = self.root / "large.log"; write_bytes(large, b"x" * 20)
        with self.assertRaisesRegex(rsa.CapabilityError, "exceeds"):
            rsa.read_once_regular(large, "bounded", 10)
        class FakeProcess:
            pid = 424242
            calls = 0
            def wait(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired("fake", timeout)
                return -9
        staged = self.root / "staged-timeout"; staged.mkdir(mode=0o700)
        runner_fd = rsa._open_verified_unlinked_bytes(
            staged, "runner.py", self.runner_snapshot.data, "timeout runner"
        )
        try:
            with mock.patch.object(rsa.subprocess, "Popen", return_value=FakeProcess()) as popen, mock.patch.object(rsa.os, "killpg") as killpg:
                with self.assertRaisesRegex(rsa.CapabilityError, "process group killed"):
                    rsa._invoke_sandbox(
                        arguments=[], profile="(version 1)\n", cwd=self.root,
                        runner_fd=runner_fd, inherited_fds=(),
                        limits=self.policy["limits"], timeout=1,
                    )
                killpg.assert_called_once_with(424242, rsa.signal.SIGKILL)
                argv = popen.call_args.args[0]
                self.assertIn("-p", argv); self.assertNotIn("-f", argv)
                self.assertEqual(popen.call_args.kwargs["stdin"], runner_fd)
                self.assertEqual(popen.call_args.kwargs["pass_fds"], ())
        finally:
            os.close(runner_fd)

    def test_report_tamper_and_runner_policy_bindings_fail(self) -> None:
        shadow, response = self.materialize_package()
        for key in ("snapshot_ledger", "sbom", "capability_report", "acceptance_test_report"):
            with self.subTest(key=key):
                changed = copy.deepcopy(shadow)
                path = self.root / changed[key]["path"]
                original = path.read_bytes()
                document = json.loads(original)
                document["tampered"] = True
                write_json(path, document)
                digest = self.snapshot(path).sha256
                changed[key]["sha256"] = digest
                for entry in changed["entries"]:
                    if entry["path"] == path.name:
                        entry["sha256"] = digest
                with mock.patch.object(rsa, "run_case", return_value=response), self.assertRaises(rsa.CapabilityError):
                    rsa.validate_shadow_acceptance(
                        shadow_root=self.root, shadow=changed, policy_path=POLICY,
                        runner_path=RUNNER, policy_snapshot=self.policy_snapshot,
                        runner_snapshot=self.runner_snapshot,
                    )
                path.write_bytes(original)
        shadow, response = self.materialize_package()
        report_path = self.root / shadow["acceptance_test_report"]["path"]
        report = json.loads(report_path.read_text())
        for field in ("runner_sha256", "policy_sha256", "program_sha256", "snapshot_ledger_sha256", "runtime_tcb_digest_sha256"):
            with self.subTest(field=field):
                changed_report = copy.deepcopy(report); changed_report[field] = "f" * 64
                write_json(report_path, changed_report)
                digest = self.snapshot(report_path).sha256
                changed_shadow = copy.deepcopy(shadow)
                changed_shadow["acceptance_test_report"]["sha256"] = digest
                for entry in changed_shadow["entries"]:
                    if entry["path"] == report_path.name:
                        entry["sha256"] = digest
                with mock.patch.object(rsa, "run_case", return_value=response), self.assertRaisesRegex(rsa.CapabilityError, "differs"):
                    rsa.validate_shadow_acceptance(
                        shadow_root=self.root, shadow=changed_shadow,
                        policy_path=POLICY, runner_path=RUNNER,
                        policy_snapshot=self.policy_snapshot,
                        runner_snapshot=self.runner_snapshot,
                    )
        write_json(report_path, report)


if __name__ == "__main__":
    unittest.main()
