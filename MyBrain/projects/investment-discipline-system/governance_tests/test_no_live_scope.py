from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_no_live_scope.py"
POLICY_RELATIVE = Path("governance") / "NO_LIVE_SCOPE_POLICY_V1.json"
ENTRYPOINTS = [
    "prototype/run_contract_faults.py",
    "prototype/run_paper_suite.py",
    "prototype/run_real_data_backtest.py",
    "prototype/run_real_data_case.py",
    "prototype/run_real_data_unified.py",
    "prototype/run_unified_prototype_case.py",
]


class NoLiveScopeVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "project"
        (self.root / "governance").mkdir(parents=True)
        shutil.copy2(SOURCE_ROOT / POLICY_RELATIVE, self.root / POLICY_RELATIVE)
        shutil.copytree(
            SOURCE_ROOT / "prototype",
            self.root / "prototype",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        self.packet_directory = self.root / ".work_packets" / "packets"
        self.packet_directory.mkdir(parents=True)
        self.write_packet(self.paper_packet())

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def write_text(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative: str, value: Any) -> Path:
        return self.write_text(
            relative,
            json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
        )

    def paper_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "work-packet-instance/v1",
            "packet_id": "WP-PAPER-BASELINE",
            "goal_id": "GOAL-PAPER-ONLY",
            "state": "active",
            "owner": "fixture-owner",
            "reviewer": "fixture-reviewer",
            "bounded_write_paths": [
                {"path": "prototype/backtest.py", "kind": "file"}
            ],
            "read_dependencies": [],
            "acceptance_checks": [],
            "checkpoint_path": None,
            "acceptance_receipt_path": None,
            "retry_budget": 1,
            "external_side_effects": ["git_remote_autobackup_observed"],
            "semantic_invariants": [],
        }

    def write_packet(self, packet: dict[str, Any]) -> Path:
        return self.write_json(
            f".work_packets/packets/{packet['packet_id']}.packet.json",
            packet,
        )

    def append_python(self, relative: str, source: str) -> None:
        path = self.root / relative
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "\n" + source.strip() + "\n", encoding="utf-8")

    def run_verifier(self) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VERIFIER),
                "--project-root",
                str(self.root),
                "--policy",
                POLICY_RELATIVE.as_posix(),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"verifier did not emit one machine JSON object: {exc}\n"
                f"stdout={completed.stdout!r}\nstderr={completed.stderr!r}"
            )
        self.assertIsInstance(payload, dict)
        return completed, payload

    def assert_passes(self) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(0, completed.returncode, payload)
        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual([], payload["errors"], payload)
        return payload

    def assert_rejected(self, oracle_id: str) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(1, completed.returncode, payload)
        self.assertEqual("fail", payload["status"], payload)
        observed = [error["oracle_id"] for error in payload["errors"]]
        self.assertIn(oracle_id, observed, payload)
        return payload

    def test_baseline_is_machine_readable_and_binds_declared_scope(self) -> None:
        payload = self.assert_passes()
        self.assertEqual("NO-LIVE-PAPER-V1", payload["policy_id"])
        self.assertEqual(ENTRYPOINTS, payload["declared_runtime_entrypoints"])
        self.assertEqual(["prototype"], payload["implementation_roots"])
        self.assertGreater(payload["counts"]["python_file_count"], 0)
        self.assertEqual(1, payload["counts"]["active_work_packet_count"])
        self.assertEqual(
            {
                "prototype.contracts.LocalPaperExecutionAdapter",
                "prototype.paper.PaperAccount",
            },
            {item["qualified_class"] for item in payload["paper_surface"]},
        )
        self.assertTrue(payload["endpoint_observations"])
        self.assertIn("does_not_prove", payload["claim_boundary"])

    def test_nonexistent_declared_runtime_entrypoint_is_rejected(self) -> None:
        baseline = self.assert_passes()
        self.assertIn("prototype/run_paper_suite.py", baseline["declared_runtime_entrypoints"])
        (self.root / "prototype" / "run_paper_suite.py").unlink()
        self.assert_rejected("NLS-SCOPE-MISSING")

    def test_direct_broker_import_is_rejected_from_ast(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            "import alpaca_trade_api",
        )
        payload = self.assert_rejected("NLS-PYTHON-FORBIDDEN-IMPORT")
        self.assertTrue(
            any("alpaca_trade_api" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_network_import_and_aliased_network_call_are_both_rejected(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
import urllib.request as wire

def _network_probe():
    return wire.urlopen(
        "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500"
    )
""",
        )
        payload = self.assert_rejected("NLS-PYTHON-FORBIDDEN-CALL")
        oracle_ids = {error["oracle_id"] for error in payload["errors"]}
        self.assertIn("NLS-PYTHON-FORBIDDEN-IMPORT", oracle_ids, payload)
        self.assertTrue(
            any("urllib.request.urlopen" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_order_method_alias_call_is_rejected_from_ast(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
def _aliased_live_order_probe(client):
    transmit = client.submit_order
    return transmit(symbol="SPY", quantity=1)
""",
        )
        payload = self.assert_rejected("NLS-PYTHON-FORBIDDEN-CALL")
        self.assertTrue(
            any("client.submit_order" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_obvious_aliased_dynamic_import_is_rejected_from_ast(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
import importlib as loader

_live_broker_module = loader.import_module("alpaca_trade_api")
""",
        )
        payload = self.assert_rejected("NLS-PYTHON-DYNAMIC-IMPORT")
        self.assertTrue(
            any("alpaca_trade_api" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_nonliteral_dynamic_import_is_rejected_fail_closed(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
def _dynamic_module_probe(module_name):
    return __import__(module_name)
""",
        )
        payload = self.assert_rejected("NLS-PYTHON-DYNAMIC-IMPORT")
        self.assertTrue(
            any("nonliteral" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_live_order_endpoint_configuration_is_rejected(self) -> None:
        self.assert_passes()
        self.write_json(
            "prototype/live_endpoint.json",
            {
                "broker_endpoint": "https://paper-api.alpaca.markets/v2/orders",
                "mode": "live",
            },
        )
        payload = self.assert_rejected("NLS-ENDPOINT-UNAPPROVED")
        self.assertTrue(
            any("paper-api.alpaca.markets" in error["message"] for error in payload["errors"]),
            payload,
        )

    def test_dynamic_python_endpoint_configuration_is_rejected(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
def _build_endpoint():
    return "https://paper-api.alpaca.markets/v2/orders"

BROKER_ENDPOINT = _build_endpoint()
""",
        )
        self.assert_rejected("NLS-ENDPOINT-DYNAMIC")

    def test_active_packet_live_external_side_effect_is_rejected(self) -> None:
        self.assert_passes()
        packet = self.paper_packet()
        packet["external_side_effects"] = ["live_broker_submit_order_real_funds"]
        self.write_packet(packet)
        payload = self.assert_rejected("NLS-PACKET-LIVE-SIDE-EFFECT")
        oracle_ids = {error["oracle_id"] for error in payload["errors"]}
        self.assertIn("NLS-PACKET-UNAPPROVED-SIDE-EFFECT", oracle_ids, payload)

    def test_unlisted_active_external_side_effect_is_rejected_fail_closed(self) -> None:
        self.assert_passes()
        packet = self.paper_packet()
        packet["external_side_effects"] = ["send_external_webhook"]
        self.write_packet(packet)
        self.assert_rejected("NLS-PACKET-UNAPPROVED-SIDE-EFFECT")

    def test_superseded_packet_field_is_state_bound(self) -> None:
        packet = self.paper_packet()
        packet["state"] = "superseded"
        packet["superseded_by"] = "WP-PAPER-SUCCESSOR"
        packet["external_side_effects"] = []
        self.write_packet(packet)
        self.assert_passes()

        packet["state"] = "active"
        self.write_packet(packet)
        self.assert_rejected("NLS-PACKET-SCHEMA")

    def test_unlisted_execution_capable_class_is_rejected(self) -> None:
        self.assert_passes()
        self.append_python(
            "prototype/backtest.py",
            """
class LiveBroker:
    pass
""",
        )
        self.assert_rejected("NLS-PAPER-EXECUTION-CLASS")

    def test_unknown_executable_file_type_is_rejected(self) -> None:
        self.assert_passes()
        self.write_text(
            "prototype/send_live_order.sh",
            "#!/bin/sh\ncurl https://paper-api.alpaca.markets/v2/orders\n",
        )
        self.assert_rejected("NLS-SCOPE-UNKNOWN-FILE")

    def test_duplicate_keys_in_implementation_json_are_rejected(self) -> None:
        self.assert_passes()
        self.write_text(
            "prototype/endpoint.json",
            '{"url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500", '
            '"url": "https://paper-api.alpaca.markets/v2/orders"}\n',
        )
        self.assert_rejected("NLS-CONFIG-STRICT-JSON")

    def test_duplicate_keys_in_policy_are_rejected_before_scanning(self) -> None:
        self.assert_passes()
        policy_path = self.root / POLICY_RELATIVE
        encoded = policy_path.read_text(encoding="utf-8")
        encoded = encoded.replace(
            '"schema_version": "no-live-scope-policy/v1",',
            '"schema_version": "no-live-scope-policy/v1",\n'
            '  "schema_version": "no-live-scope-policy/v1",',
            1,
        )
        policy_path.write_text(encoded, encoding="utf-8")
        self.assert_rejected("NLS-POLICY-STRICT-JSON")

    def test_documented_future_live_risk_is_not_an_executable_surface(self) -> None:
        self.write_text(
            "prototype/README.md",
            """# Paper-only boundary

Future risk to discuss, not implement: live broker, real funds, automatic order,
and https://paper-api.alpaca.markets/v2/orders.
""",
        )
        self.assert_passes()


if __name__ == "__main__":
    unittest.main()
