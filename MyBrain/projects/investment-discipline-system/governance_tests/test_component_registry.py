from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.verify_component_registry import (
    DuplicateKeyError,
    load_registry,
    removal_impact,
    verify_registry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "governance" / "COMPONENT_REGISTRY_V1.json"
FIXED_TODAY = date(2026, 7, 25)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ComponentRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in (
            "governance",
            "research",
            "prototype",
            "governance_tests",
            "audits",
        ):
            (self.root / directory).mkdir(parents=True)
        (self.root / "governance" / "control.json").write_text(
            '{"uses":["research/source.md","prototype/runtime.py"]}\n',
            encoding="utf-8",
        )
        (self.root / "research" / "source.md").write_text(
            "# Research evidence\nstatus: bounded_incomplete\n",
            encoding="utf-8",
        )
        (self.root / "prototype" / "runtime.py").write_text(
            "class DataSnapshot:\n    pass\n",
            encoding="utf-8",
        )
        (self.root / "audits" / "review.md").write_text(
            "ECO-03-REVIEW\nfinding: gap\ninventory required\n",
            encoding="utf-8",
        )
        (self.root / "governance_tests" / "test_components.py").write_text(
            "import unittest\n\n"
            "class GovernanceTests(unittest.TestCase):\n"
            "    def test_contract(self):\n"
            "        pass\n\n"
            "class ResearchTests(unittest.TestCase):\n"
            "    def test_evidence(self):\n"
            "        pass\n\n"
            "class PrototypeTests(unittest.TestCase):\n"
            "    def test_runtime(self):\n"
            "        pass\n\n"
            "class OrphanTests(unittest.TestCase):\n"
            "    def test_orphan(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        self.registry = self._fixture_registry()
        self._write_registry()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _locator(self, relative: str, *anchors: str) -> dict:
        path = self.root / relative
        return {
            "path": relative,
            "sha256": _sha256(path),
            "anchors": list(anchors),
        }

    def _component(
        self,
        component_id: str,
        responsibility_id: str,
        summary: str,
        root: str,
        layer: str,
        selector: str,
        contract_anchor: str,
        dependencies: list[dict],
    ) -> dict:
        review = self._locator(
            "audits/review.md", "ECO-03-REVIEW", "finding: gap"
        )
        return {
            "id": component_id,
            "owner": "fixture owner",
            "purpose": f"Purpose for {component_id}.",
            "responsibility": {
                "id": responsibility_id,
                "summary": summary,
            },
            "paths": [root],
            "layer": layer,
            "contract_interface": {
                "kind": "fixture contract",
                "summary": f"Contract for {component_id}.",
                "locators": [
                    self._locator(
                        f"{root}/"
                        + {
                            "governance": "control.json",
                            "research": "source.md",
                            "prototype": "runtime.py",
                        }[root],
                        contract_anchor,
                    )
                ],
            },
            "tests": {"selectors": [selector]},
            "observability": {
                "signals": [f"{component_id} signal"],
                "locators": [
                    self._locator(
                        f"{root}/"
                        + {
                            "governance": "control.json",
                            "research": "source.md",
                            "prototype": "runtime.py",
                        }[root],
                        contract_anchor,
                    )
                ],
            },
            "dependencies": dependencies,
            "failure_mode": {
                "summary": f"{component_id} failure",
                "detection": "fixture detection",
                "containment": "fixture containment",
            },
            "removal_path": {
                "mode": "retire_after_dependents_migrate",
                "preconditions": ["migrate dependents"],
                "steps": ["run dry run"],
                "blocker_locators": [
                    self._locator(
                        f"{root}/"
                        + {
                            "governance": "control.json",
                            "research": "source.md",
                            "prototype": "runtime.py",
                        }[root],
                        contract_anchor,
                    )
                ],
            },
            "replacement_migration_path": {
                "mode": "retire_without_replacement",
                "target_component_id": None,
                "steps": ["preserve evidence"],
                "rollback_steps": ["restore component"],
                "evidence_locators": [
                    self._locator(
                        f"{root}/"
                        + {
                            "governance": "control.json",
                            "research": "source.md",
                            "prototype": "runtime.py",
                        }[root],
                        contract_anchor,
                    )
                ],
            },
            "status": "partial",
            "last_review_binding": {
                **review,
                "review_id": "ECO-03-REVIEW",
                "reviewed_on": "2026-07-25",
                "max_age_days": 90,
                "finding": "gap",
                "scope": "fixture pre-registry gap review",
            },
            "evidence_locators": [
                self._locator(
                    f"{root}/"
                    + {
                        "governance": "control.json",
                        "research": "source.md",
                        "prototype": "runtime.py",
                    }[root],
                    contract_anchor,
                )
            ],
        }

    def _fixture_registry(self) -> dict:
        governance_dependencies = [
            {
                "component_id": "research-evidence-corpus",
                "reason": "control references research",
                "evidence_locators": [
                    self._locator(
                        "governance/control.json", "research/source.md"
                    )
                ],
            },
            {
                "component_id": "paper-prototype-runtime",
                "reason": "control references prototype",
                "evidence_locators": [
                    self._locator(
                        "governance/control.json", "prototype/runtime.py"
                    )
                ],
            },
        ]
        return {
            "schema_version": 1,
            "registry_id": "fixture-registry",
            "as_of_date": "2026-07-25",
            "status": "partial",
            "scope_roots": [
                {
                    "path": "governance",
                    "component_id": "governance-control-plane",
                },
                {
                    "path": "research",
                    "component_id": "research-evidence-corpus",
                },
                {
                    "path": "prototype",
                    "component_id": "paper-prototype-runtime",
                },
            ],
            "layer_order": [
                "research-evidence",
                "prototype-runtime",
                "governance-control",
            ],
            "entry_component_ids": ["governance-control-plane"],
            "dependency_scan": {
                "text_extensions": [
                    ".csv",
                    ".json",
                    ".md",
                    ".py",
                    ".toml",
                    ".txt",
                    ".yaml",
                    ".yml",
                ],
                "excluded_directories": ["__pycache__"],
                "excluded_files": ["governance/COMPONENT_REGISTRY_V1.json"],
            },
            "longitudinal_maintenance": {
                "minimum_distinct_periods_per_component": 2,
                "receipts": [],
                "reassessment_eligible": False,
                "longitudinal_cost_proved": False,
            },
            "claim_boundary": {
                "allowed_claim": "fixture inventory is checked",
                "forbidden_claim": "fixture does not prove longitudinal cost",
            },
            "components": [
                self._component(
                    "governance-control-plane",
                    "RESP-GOV",
                    "Own fixture governance.",
                    "governance",
                    "governance-control",
                    "governance_tests.test_components.GovernanceTests.test_contract",
                    "research/source.md",
                    governance_dependencies,
                ),
                self._component(
                    "research-evidence-corpus",
                    "RESP-RESEARCH",
                    "Own fixture research.",
                    "research",
                    "research-evidence",
                    "governance_tests.test_components.ResearchTests.test_evidence",
                    "bounded_incomplete",
                    [],
                ),
                self._component(
                    "paper-prototype-runtime",
                    "RESP-PROTOTYPE",
                    "Own fixture prototype.",
                    "prototype",
                    "prototype-runtime",
                    "governance_tests.test_components.PrototypeTests.test_runtime",
                    "class DataSnapshot",
                    [],
                ),
            ],
        }

    def _write_registry(self) -> None:
        (self.root / "governance" / "COMPONENT_REGISTRY_V1.json").write_text(
            json.dumps(self.registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _errors(self) -> list[str]:
        return verify_registry(self.root, self.registry, today=FIXED_TODAY)

    def _update_locator_hashes(self, relative: str) -> None:
        new_hash = _sha256(self.root / relative)

        def visit(value) -> None:
            if isinstance(value, dict):
                if value.get("path") == relative and "sha256" in value:
                    value["sha256"] = new_hash
                for nested in value.values():
                    visit(nested)
            elif isinstance(value, list):
                for nested in value:
                    visit(nested)

        visit(self.registry)

    def test_benign_registry_passes(self) -> None:
        registry = load_registry(REGISTRY_PATH)
        self.assertEqual(
            verify_registry(PROJECT_ROOT, registry, today=FIXED_TODAY),
            [],
        )
        self.assertEqual(self._errors(), [])

    def test_orphan_component_is_rejected(self) -> None:
        (self.root / "orphan").mkdir()
        (self.root / "orphan" / "component.md").write_text(
            "orphan contract\n", encoding="utf-8"
        )
        orphan = self._component(
            "orphan-component",
            "RESP-ORPHAN",
            "Own an intentionally disconnected fixture.",
            "research",
            "research-evidence",
            "governance_tests.test_components.OrphanTests.test_orphan",
            "bounded_incomplete",
            [],
        )
        orphan["paths"] = ["orphan"]
        locator = self._locator("orphan/component.md", "orphan contract")
        orphan["contract_interface"]["locators"] = [copy.deepcopy(locator)]
        orphan["observability"]["locators"] = [copy.deepcopy(locator)]
        orphan["removal_path"]["blocker_locators"] = [copy.deepcopy(locator)]
        orphan["replacement_migration_path"]["evidence_locators"] = [
            copy.deepcopy(locator)
        ]
        orphan["evidence_locators"] = [copy.deepcopy(locator)]
        self.registry["scope_roots"].append(
            {"path": "orphan", "component_id": "orphan-component"}
        )
        self.registry["components"].append(orphan)
        self.assertTrue(
            any("orphan components" in error for error in self._errors())
        )

    def test_duplicate_responsibility_is_rejected(self) -> None:
        self.registry["components"][1]["responsibility"]["id"] = "RESP-GOV"
        self.assertTrue(
            any("duplicate responsibility id" in error for error in self._errors())
        )

    def test_missing_test_selector_is_rejected(self) -> None:
        self.registry["components"][2]["tests"]["selectors"][0] = (
            "governance_tests.test_components.PrototypeTests.test_missing"
        )
        self.assertTrue(
            any("test method is missing" in error for error in self._errors())
        )

    def test_stale_hash_and_review_are_rejected(self) -> None:
        original = copy.deepcopy(self.registry)
        self.registry["components"][0]["last_review_binding"]["sha256"] = "0" * 64
        self.assertTrue(
            any("sha256 is stale" in error for error in self._errors())
        )
        self.registry = original
        self.registry["components"][0]["last_review_binding"][
            "reviewed_on"
        ] = "2020-01-01"
        self.assertTrue(
            any("last_review_binding is stale" in error for error in self._errors())
        )

    def test_undeclared_dependency_edge_is_rejected(self) -> None:
        self.registry["components"][0]["dependencies"] = self.registry[
            "components"
        ][0]["dependencies"][1:]
        self.assertTrue(
            any("undeclared dependency edge" in error for error in self._errors())
        )

    def test_partial_status_cannot_upgrade_without_repeated_receipts(self) -> None:
        self.registry["status"] = "eligible_for_reassessment"
        self.registry["components"][0]["status"] = "eligible_for_reassessment"
        errors = self._errors()
        self.assertTrue(
            any(
                "registry status must remain partial" in error for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "status must remain partial" in error for error in errors
            ),
            errors,
        )

    def test_illegal_cycle_is_rejected(self) -> None:
        research_path = self.root / "research" / "source.md"
        research_path.write_text(
            research_path.read_text(encoding="utf-8")
            + "depends on governance/control.json\n",
            encoding="utf-8",
        )
        self._update_locator_hashes("research/source.md")
        self.registry["components"][1]["dependencies"].append(
            {
                "component_id": "governance-control-plane",
                "reason": "intentional cycle",
                "evidence_locators": [
                    self._locator(
                        "research/source.md", "governance/control.json"
                    )
                ],
            }
        )
        errors = self._errors()
        self.assertTrue(
            any("dependency cycle detected" in error for error in errors), errors
        )
        self.assertTrue(
            any("violates declared layering" in error for error in errors), errors
        )

    def test_invalid_removal_or_migration_evidence_is_rejected(self) -> None:
        original = copy.deepcopy(self.registry)
        self.registry["components"][0]["removal_path"]["blocker_locators"] = []
        self.assertTrue(
            any(
                "removal_path.blocker_locators must be a non-empty locator list"
                in error
                for error in self._errors()
            )
        )
        self.registry = original
        self.registry["components"][0]["replacement_migration_path"][
            "evidence_locators"
        ][0]["anchors"] = ["missing migration evidence"]
        self.assertTrue(
            any("anchor is missing" in error for error in self._errors())
        )

    def test_removal_dry_run_reports_blocker_without_deleting(self) -> None:
        target = self.root / "research" / "source.md"
        before = target.read_bytes()
        impact = removal_impact(
            self.root, self.registry, "research-evidence-corpus"
        )
        self.assertEqual(impact["status"], "blocked")
        self.assertTrue(impact["dry_run"])
        self.assertFalse(impact["deletion_performed"])
        self.assertEqual(impact["would_delete"], [])
        self.assertTrue(
            any(
                blocker["kind"] == "dependent_component"
                for blocker in impact["blockers"]
            )
        )
        self.assertEqual(target.read_bytes(), before)

    def test_strict_json_rejects_duplicate_key(self) -> None:
        duplicate = self.root / "governance" / "duplicate.json"
        duplicate.write_text(
            '{"schema_version":1,"schema_version":1}\n',
            encoding="utf-8",
        )
        with self.assertRaises(DuplicateKeyError):
            load_registry(duplicate)


if __name__ == "__main__":
    unittest.main()
