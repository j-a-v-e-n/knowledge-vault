#!/usr/bin/env python3
"""Verify the ECO-03 component registry and perform removal-impact dry runs."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


REGISTRY_RELATIVE_PATH = Path("governance/COMPONENT_REGISTRY_V1.json")
COMPONENT_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_SCOPE_ROOTS = {"governance", "research", "prototype"}
REQUIRED_SCAN_EXTENSIONS = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOWED_SCAN_EXCLUDED_DIRECTORIES = {"__pycache__"}
ALLOWED_SCAN_EXCLUDED_FILES = {
    REGISTRY_RELATIVE_PATH.as_posix(),
}

TOP_LEVEL_FIELDS = {
    "schema_version",
    "registry_id",
    "as_of_date",
    "status",
    "scope_roots",
    "layer_order",
    "entry_component_ids",
    "dependency_scan",
    "longitudinal_maintenance",
    "claim_boundary",
    "components",
}
SCOPE_ROOT_FIELDS = {"path", "component_id"}
DEPENDENCY_SCAN_FIELDS = {
    "text_extensions",
    "excluded_directories",
    "excluded_files",
}
CLAIM_BOUNDARY_FIELDS = {"allowed_claim", "forbidden_claim"}
LONGITUDINAL_FIELDS = {
    "minimum_distinct_periods_per_component",
    "receipts",
    "reassessment_eligible",
    "longitudinal_cost_proved",
}
RECEIPT_FIELDS = {
    "component_id",
    "period_start",
    "period_end",
    "locator",
}
COMPONENT_FIELDS = {
    "id",
    "owner",
    "purpose",
    "responsibility",
    "paths",
    "layer",
    "contract_interface",
    "tests",
    "observability",
    "dependencies",
    "failure_mode",
    "removal_path",
    "replacement_migration_path",
    "status",
    "last_review_binding",
    "evidence_locators",
}
RESPONSIBILITY_FIELDS = {"id", "summary"}
CONTRACT_FIELDS = {"kind", "summary", "locators"}
TEST_FIELDS = {"selectors"}
OBSERVABILITY_FIELDS = {"signals", "locators"}
DEPENDENCY_FIELDS = {"component_id", "reason", "evidence_locators"}
FAILURE_MODE_FIELDS = {"summary", "detection", "containment"}
REMOVAL_FIELDS = {"mode", "preconditions", "steps", "blocker_locators"}
MIGRATION_FIELDS = {
    "mode",
    "target_component_id",
    "steps",
    "rollback_steps",
    "evidence_locators",
}
REVIEW_FIELDS = {
    "path",
    "sha256",
    "anchors",
    "review_id",
    "reviewed_on",
    "max_age_days",
    "finding",
    "scope",
}
LOCATOR_FIELDS = {"path", "sha256", "anchors"}


class DuplicateKeyError(ValueError):
    """Raised when strict JSON contains a duplicate object key."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError("registry top level must be an object")
    return value


def _expect_fields(
    value: Any,
    expected: set[str],
    context: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{context} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        errors.append(f"{context} fields differ; missing={missing}, extra={extra}")
        return False
    return True


def _nonempty_string(value: Any, context: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context} must be a non-empty string")
        return False
    return True


def _string_list(
    value: Any,
    context: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (
        not allow_empty and not value
    ) or not all(isinstance(item, str) and item.strip() for item in value):
        qualifier = "a list of strings" if allow_empty else "a non-empty list of strings"
        errors.append(f"{context} must be {qualifier}")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{context} contains duplicates")
    return value


def _safe_relative_path(value: Any, context: str, errors: list[str]) -> str | None:
    if not _nonempty_string(value, context, errors):
        return None
    assert isinstance(value, str)
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or ".." in parsed.parts or "." in parsed.parts:
        errors.append(f"{context} must be a normalized project-relative path")
        return None
    if parsed.as_posix() != value or value.endswith("/"):
        errors.append(f"{context} must use normalized POSIX spelling")
        return None
    return value


def _project_path(
    project_root: Path,
    relative: str,
    context: str,
    errors: list[str],
) -> Path | None:
    candidate = project_root / relative
    try:
        candidate.resolve().relative_to(project_root.resolve())
    except ValueError:
        errors.append(f"{context} escapes the project root")
        return None
    return candidate


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_locator(
    locator: Any,
    project_root: Path,
    context: str,
    errors: list[str],
    evidence_cache: dict[str, tuple[bytes, str]],
) -> str | None:
    if not _expect_fields(locator, LOCATOR_FIELDS, context, errors):
        return None
    relative = _safe_relative_path(locator["path"], f"{context}.path", errors)
    declared_hash = locator["sha256"]
    if not isinstance(declared_hash, str) or not SHA256_RE.fullmatch(declared_hash):
        errors.append(f"{context}.sha256 must be a lowercase SHA-256 digest")
    anchors = _string_list(locator["anchors"], f"{context}.anchors", errors)
    if relative is None:
        return None
    path = _project_path(project_root, relative, f"{context}.path", errors)
    if path is None:
        return None
    if path.is_symlink():
        errors.append(f"{context}.path must not be a symlink: {relative}")
        return None
    if not path.is_file():
        errors.append(f"{context}.path is not an existing file: {relative}")
        return None
    if relative not in evidence_cache:
        data = path.read_bytes()
        evidence_cache[relative] = (data, _sha256(data))
    data, actual_hash = evidence_cache[relative]
    if declared_hash != actual_hash:
        errors.append(
            f"{context}.sha256 is stale for {relative}: "
            f"declared={declared_hash}, actual={actual_hash}"
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"{context}.path is not UTF-8 text: {relative}")
        return relative
    for anchor in anchors:
        if anchor not in text:
            errors.append(f"{context}.anchor is missing from {relative}: {anchor!r}")
    return relative


def _validate_locator_list(
    value: Any,
    project_root: Path,
    context: str,
    errors: list[str],
    evidence_cache: dict[str, tuple[bytes, str]],
) -> list[str]:
    if not isinstance(value, list) or not value:
        errors.append(f"{context} must be a non-empty locator list")
        return []
    paths: list[str] = []
    for index, locator in enumerate(value):
        path = _validate_locator(
            locator,
            project_root,
            f"{context}[{index}]",
            errors,
            evidence_cache,
        )
        if path is not None:
            paths.append(path)
    return paths


def _parse_date(value: Any, context: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{context} must be an ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{context} must be an ISO date")
        return None


def _selector_file_and_nodes(
    project_root: Path,
    selector: str,
    context: str,
    errors: list[str],
) -> Path | None:
    parts = selector.split(".")
    if len(parts) < 4 or any(not part.isidentifier() for part in parts):
        errors.append(
            f"{context} must be module.ClassName.test_method with identifiers"
        )
        return None
    module_parts, class_name, method_name = parts[:-2], parts[-2], parts[-1]
    if not method_name.startswith("test_"):
        errors.append(f"{context} method must start with test_: {selector}")
        return None
    module_path = project_root.joinpath(*module_parts).with_suffix(".py")
    if not module_path.is_file():
        errors.append(f"{context} module file is missing: {module_path.relative_to(project_root)}")
        return None
    try:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        errors.append(f"{context} module cannot be parsed: {exc}")
        return None
    class_node = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if class_node is None:
        errors.append(f"{context} test class is missing: {selector}")
        return None
    is_test_case = any(
        (isinstance(base, ast.Name) and base.id == "TestCase")
        or (isinstance(base, ast.Attribute) and base.attr == "TestCase")
        for base in class_node.bases
    )
    if not is_test_case:
        errors.append(f"{context} class is not a unittest TestCase: {selector}")
        return None
    method_node = next(
        (
            node
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
        ),
        None,
    )
    if method_node is None:
        errors.append(f"{context} test method is missing: {selector}")
        return None
    return module_path


def _normalize_responsibility(value: str) -> str:
    return " ".join(value.casefold().split())


def _validate_component_shape(
    component: Any,
    project_root: Path,
    index: int,
    today: date,
    layer_names: set[str],
    component_ids: set[str],
    errors: list[str],
    evidence_cache: dict[str, tuple[bytes, str]],
) -> None:
    context = f"components[{index}]"
    if not _expect_fields(component, COMPONENT_FIELDS, context, errors):
        return
    component_id = component["id"]
    if not isinstance(component_id, str) or not COMPONENT_ID_RE.fullmatch(component_id):
        errors.append(f"{context}.id has invalid format")
        component_id = f"<invalid-{index}>"
    _nonempty_string(component["owner"], f"{context}.owner", errors)
    _nonempty_string(component["purpose"], f"{context}.purpose", errors)
    _string_list(component["paths"], f"{context}.paths", errors)
    if component["layer"] not in layer_names:
        errors.append(f"{context}.layer is not declared in layer_order")
    if component["status"] not in {"partial", "eligible_for_reassessment"}:
        errors.append(f"{context}.status is invalid")

    responsibility = component["responsibility"]
    if _expect_fields(
        responsibility, RESPONSIBILITY_FIELDS, f"{context}.responsibility", errors
    ):
        _nonempty_string(
            responsibility["id"], f"{context}.responsibility.id", errors
        )
        _nonempty_string(
            responsibility["summary"], f"{context}.responsibility.summary", errors
        )

    contract = component["contract_interface"]
    if _expect_fields(contract, CONTRACT_FIELDS, f"{context}.contract_interface", errors):
        _nonempty_string(contract["kind"], f"{context}.contract_interface.kind", errors)
        _nonempty_string(
            contract["summary"], f"{context}.contract_interface.summary", errors
        )
        _validate_locator_list(
            contract["locators"],
            project_root,
            f"{context}.contract_interface.locators",
            errors,
            evidence_cache,
        )

    tests = component["tests"]
    if _expect_fields(tests, TEST_FIELDS, f"{context}.tests", errors):
        selectors = _string_list(
            tests["selectors"], f"{context}.tests.selectors", errors
        )
        for selector_index, selector in enumerate(selectors):
            _selector_file_and_nodes(
                project_root,
                selector,
                f"{context}.tests.selectors[{selector_index}]",
                errors,
            )

    observability = component["observability"]
    if _expect_fields(
        observability, OBSERVABILITY_FIELDS, f"{context}.observability", errors
    ):
        _string_list(
            observability["signals"], f"{context}.observability.signals", errors
        )
        _validate_locator_list(
            observability["locators"],
            project_root,
            f"{context}.observability.locators",
            errors,
            evidence_cache,
        )

    dependencies = component["dependencies"]
    if not isinstance(dependencies, list):
        errors.append(f"{context}.dependencies must be a list")
    else:
        seen_dependencies: set[str] = set()
        for dep_index, dependency in enumerate(dependencies):
            dep_context = f"{context}.dependencies[{dep_index}]"
            if not _expect_fields(
                dependency, DEPENDENCY_FIELDS, dep_context, errors
            ):
                continue
            target = dependency["component_id"]
            if target not in component_ids:
                errors.append(f"{dep_context}.component_id is unknown: {target}")
            if target == component_id:
                errors.append(f"{dep_context} cannot be a self-dependency")
            if target in seen_dependencies:
                errors.append(f"{context}.dependencies duplicates {target}")
            seen_dependencies.add(target)
            _nonempty_string(dependency["reason"], f"{dep_context}.reason", errors)
            locator_paths = _validate_locator_list(
                dependency["evidence_locators"],
                project_root,
                f"{dep_context}.evidence_locators",
                errors,
                evidence_cache,
            )
            if not locator_paths:
                errors.append(f"{dep_context} lacks valid dependency evidence")

    failure_mode = component["failure_mode"]
    if _expect_fields(
        failure_mode, FAILURE_MODE_FIELDS, f"{context}.failure_mode", errors
    ):
        for field in sorted(FAILURE_MODE_FIELDS):
            _nonempty_string(
                failure_mode[field], f"{context}.failure_mode.{field}", errors
            )

    removal = component["removal_path"]
    if _expect_fields(removal, REMOVAL_FIELDS, f"{context}.removal_path", errors):
        if removal["mode"] not in {
            "retire_after_dependents_migrate",
            "archive_after_dependents_migrate",
        }:
            errors.append(f"{context}.removal_path.mode is invalid")
        _string_list(
            removal["preconditions"],
            f"{context}.removal_path.preconditions",
            errors,
        )
        _string_list(removal["steps"], f"{context}.removal_path.steps", errors)
        _validate_locator_list(
            removal["blocker_locators"],
            project_root,
            f"{context}.removal_path.blocker_locators",
            errors,
            evidence_cache,
        )

    migration = component["replacement_migration_path"]
    if _expect_fields(
        migration,
        MIGRATION_FIELDS,
        f"{context}.replacement_migration_path",
        errors,
    ):
        mode = migration["mode"]
        target = migration["target_component_id"]
        if mode not in {"replace_then_remove", "retire_without_replacement"}:
            errors.append(f"{context}.replacement_migration_path.mode is invalid")
        if mode == "replace_then_remove":
            if target not in component_ids or target == component_id:
                errors.append(
                    f"{context}.replacement_migration_path target must be "
                    "a different registered component"
                )
        elif target is not None:
            errors.append(
                f"{context}.replacement_migration_path target must be null "
                "for retire_without_replacement"
            )
        _string_list(
            migration["steps"],
            f"{context}.replacement_migration_path.steps",
            errors,
        )
        _string_list(
            migration["rollback_steps"],
            f"{context}.replacement_migration_path.rollback_steps",
            errors,
        )
        _validate_locator_list(
            migration["evidence_locators"],
            project_root,
            f"{context}.replacement_migration_path.evidence_locators",
            errors,
            evidence_cache,
        )

    review = component["last_review_binding"]
    if _expect_fields(
        review, REVIEW_FIELDS, f"{context}.last_review_binding", errors
    ):
        review_locator = {
            "path": review["path"],
            "sha256": review["sha256"],
            "anchors": review["anchors"],
        }
        _validate_locator(
            review_locator,
            project_root,
            f"{context}.last_review_binding",
            errors,
            evidence_cache,
        )
        _nonempty_string(
            review["review_id"], f"{context}.last_review_binding.review_id", errors
        )
        _nonempty_string(
            review["scope"], f"{context}.last_review_binding.scope", errors
        )
        reviewed_on = _parse_date(
            review["reviewed_on"],
            f"{context}.last_review_binding.reviewed_on",
            errors,
        )
        max_age = review["max_age_days"]
        if not isinstance(max_age, int) or isinstance(max_age, bool) or not 1 <= max_age <= 366:
            errors.append(
                f"{context}.last_review_binding.max_age_days must be 1..366"
            )
        elif reviewed_on is not None:
            age = (today - reviewed_on).days
            if age < 0:
                errors.append(f"{context}.last_review_binding is future-dated")
            elif age > max_age:
                errors.append(
                    f"{context}.last_review_binding is stale: "
                    f"age_days={age}, max_age_days={max_age}"
                )
        if review["finding"] not in {"gap", "partially_covered"}:
            errors.append(
                f"{context}.last_review_binding.finding must preserve an open finding"
            )
        if review["finding"] == "gap" and component["status"] != "partial":
            errors.append(f"{context}.status cannot exceed its bound gap review")

    _validate_locator_list(
        component["evidence_locators"],
        project_root,
        f"{context}.evidence_locators",
        errors,
        evidence_cache,
    )


def _component_dependency_edges(
    components: list[dict[str, Any]],
) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for component in components:
        source = component.get("id")
        dependencies = component.get("dependencies")
        if not isinstance(source, str) or not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if isinstance(dependency, dict) and isinstance(
                dependency.get("component_id"), str
            ):
                edges.add((source, dependency["component_id"]))
    return edges


def _scan_dependency_edges(
    project_root: Path,
    registry: dict[str, Any],
    components_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[set[tuple[str, str]], dict[tuple[str, str], list[str]]]:
    config = registry["dependency_scan"]
    text_extensions = set(config["text_extensions"])
    excluded_directories = set(config["excluded_directories"])
    excluded_files = set(config["excluded_files"])
    roots_by_component: dict[str, list[str]] = defaultdict(list)
    for scope in registry["scope_roots"]:
        roots_by_component[scope["component_id"]].append(scope["path"])

    observed: set[tuple[str, str]] = set()
    evidence: dict[tuple[str, str], list[str]] = defaultdict(list)
    for source_id, source_roots in roots_by_component.items():
        for source_root in source_roots:
            root_path = project_root / source_root
            for path in sorted(root_path.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(project_root).as_posix()
                if relative in excluded_files:
                    continue
                if any(part in excluded_directories for part in path.parts):
                    continue
                if path.suffix not in text_extensions:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    errors.append(
                        f"dependency scan expected UTF-8 for {relative}"
                    )
                    continue
                for target_id in components_by_id:
                    if target_id == source_id:
                        continue
                    for target_root in roots_by_component[target_id]:
                        path_reference = f"{target_root}/"
                        import_pattern = re.compile(
                            rf"\b(?:from|import)\s+{re.escape(target_root)}"
                            rf"(?:\.|\b)"
                        )
                        if path_reference in text or import_pattern.search(text):
                            edge = (source_id, target_id)
                            observed.add(edge)
                            evidence[edge].append(relative)
                            break
    return observed, evidence


def _dependency_cycles(
    component_ids: set[str],
    edges: set[tuple[str, str]],
) -> list[list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)
    visiting: list[str] = []
    active: set[str] = set()
    complete: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        if node in complete:
            return
        if node in active:
            start = visiting.index(node)
            cycles.append(visiting[start:] + [node])
            return
        active.add(node)
        visiting.append(node)
        for target in sorted(adjacency[node]):
            visit(target)
        visiting.pop()
        active.remove(node)
        complete.add(node)

    for component_id in sorted(component_ids):
        visit(component_id)
    return cycles


def _verify_longitudinal(
    registry: dict[str, Any],
    components_by_id: dict[str, dict[str, Any]],
    project_root: Path,
    errors: list[str],
    evidence_cache: dict[str, tuple[bytes, str]],
) -> None:
    value = registry["longitudinal_maintenance"]
    if not _expect_fields(
        value, LONGITUDINAL_FIELDS, "longitudinal_maintenance", errors
    ):
        return
    minimum = value["minimum_distinct_periods_per_component"]
    if (
        not isinstance(minimum, int)
        or isinstance(minimum, bool)
        or minimum < 2
    ):
        errors.append(
            "longitudinal_maintenance.minimum_distinct_periods_per_component "
            "must be at least 2"
        )
        minimum = 2
    receipts = value["receipts"]
    periods_by_component: dict[str, set[tuple[date, date]]] = defaultdict(set)
    if not isinstance(receipts, list):
        errors.append("longitudinal_maintenance.receipts must be a list")
        receipts = []
    for index, receipt in enumerate(receipts):
        context = f"longitudinal_maintenance.receipts[{index}]"
        if not _expect_fields(receipt, RECEIPT_FIELDS, context, errors):
            continue
        component_id = receipt["component_id"]
        if component_id not in components_by_id:
            errors.append(f"{context}.component_id is unknown")
        period_start = _parse_date(
            receipt["period_start"], f"{context}.period_start", errors
        )
        period_end = _parse_date(
            receipt["period_end"], f"{context}.period_end", errors
        )
        if (
            period_start is not None
            and period_end is not None
            and period_start > period_end
        ):
            errors.append(f"{context} period_start is after period_end")
        elif (
            isinstance(component_id, str)
            and period_start is not None
            and period_end is not None
        ):
            periods_by_component[component_id].add((period_start, period_end))
        _validate_locator(
            receipt["locator"],
            project_root,
            f"{context}.locator",
            errors,
            evidence_cache,
        )
    derived_eligible = bool(components_by_id) and all(
        len(periods_by_component[component_id]) >= minimum
        for component_id in components_by_id
    )
    if value["reassessment_eligible"] is not derived_eligible:
        errors.append(
            "longitudinal_maintenance.reassessment_eligible was not derived "
            f"(declared={value['reassessment_eligible']}, derived={derived_eligible})"
        )
    if value["longitudinal_cost_proved"] is not False:
        errors.append(
            "longitudinal_maintenance.longitudinal_cost_proved must remain false; "
            "repeated receipts only permit reassessment"
        )
    if not derived_eligible:
        if registry["status"] != "partial":
            errors.append(
                "registry status must remain partial without repeated "
                "maintenance receipts for every component"
            )
        for component_id, component in components_by_id.items():
            if component.get("status") != "partial":
                errors.append(
                    f"{component_id} status must remain partial without repeated "
                    "maintenance receipts"
                )


def verify_registry(
    project_root: Path,
    registry: dict[str, Any],
    *,
    today: date | None = None,
) -> list[str]:
    project_root = project_root.resolve()
    today = today or datetime.now(timezone.utc).date()
    errors: list[str] = []
    evidence_cache: dict[str, tuple[bytes, str]] = {}
    if not _expect_fields(registry, TOP_LEVEL_FIELDS, "registry", errors):
        return errors
    if registry["schema_version"] != 1:
        errors.append("schema_version must equal 1")
    _nonempty_string(registry["registry_id"], "registry_id", errors)
    _parse_date(registry["as_of_date"], "as_of_date", errors)
    if registry["status"] not in {"partial", "eligible_for_reassessment"}:
        errors.append("registry status is invalid")

    claim_boundary = registry["claim_boundary"]
    if _expect_fields(
        claim_boundary, CLAIM_BOUNDARY_FIELDS, "claim_boundary", errors
    ):
        _nonempty_string(
            claim_boundary["allowed_claim"], "claim_boundary.allowed_claim", errors
        )
        _nonempty_string(
            claim_boundary["forbidden_claim"],
            "claim_boundary.forbidden_claim",
            errors,
        )

    dependency_scan = registry["dependency_scan"]
    if _expect_fields(
        dependency_scan, DEPENDENCY_SCAN_FIELDS, "dependency_scan", errors
    ):
        extensions = _string_list(
            dependency_scan["text_extensions"],
            "dependency_scan.text_extensions",
            errors,
        )
        if any(not extension.startswith(".") for extension in extensions):
            errors.append("dependency_scan.text_extensions must start with '.'")
        missing_extensions = REQUIRED_SCAN_EXTENSIONS - set(extensions)
        if missing_extensions:
            errors.append(
                "dependency_scan.text_extensions omits required authored "
                f"formats: {sorted(missing_extensions)}"
            )
        excluded_directories = _string_list(
            dependency_scan["excluded_directories"],
            "dependency_scan.excluded_directories",
            errors,
            allow_empty=True,
        )
        unexpected_directories = (
            set(excluded_directories) - ALLOWED_SCAN_EXCLUDED_DIRECTORIES
        )
        if unexpected_directories:
            errors.append(
                "dependency_scan.excluded_directories contains unapproved "
                f"dependency blind spots: {sorted(unexpected_directories)}"
            )
        excluded_files = _string_list(
            dependency_scan["excluded_files"],
            "dependency_scan.excluded_files",
            errors,
            allow_empty=True,
        )
        unexpected_files = set(excluded_files) - ALLOWED_SCAN_EXCLUDED_FILES
        if unexpected_files:
            errors.append(
                "dependency_scan.excluded_files contains unapproved dependency "
                f"blind spots: {sorted(unexpected_files)}"
            )
        for index, excluded in enumerate(excluded_files):
            _safe_relative_path(
                excluded, f"dependency_scan.excluded_files[{index}]", errors
            )

    layers = _string_list(registry["layer_order"], "layer_order", errors)
    layer_names = set(layers)
    entries = _string_list(
        registry["entry_component_ids"], "entry_component_ids", errors
    )
    components = registry["components"]
    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty list")
        return errors
    component_ids_list = [
        component.get("id")
        for component in components
        if isinstance(component, dict) and isinstance(component.get("id"), str)
    ]
    component_ids = set(component_ids_list)
    if len(component_ids_list) != len(component_ids):
        errors.append("component ids must be unique")
    components_by_id = {
        component["id"]: component
        for component in components
        if isinstance(component, dict)
        and isinstance(component.get("id"), str)
        and component_ids_list.count(component["id"]) == 1
    }
    for entry in entries:
        if entry not in component_ids:
            errors.append(f"entry component is unknown: {entry}")

    for index, component in enumerate(components):
        _validate_component_shape(
            component,
            project_root,
            index,
            today,
            layer_names,
            component_ids,
            errors,
            evidence_cache,
        )

    responsibilities: dict[str, str] = {}
    responsibility_summaries: dict[str, str] = {}
    selectors: dict[str, str] = {}
    for component in components:
        if not isinstance(component, dict) or not isinstance(
            component.get("id"), str
        ):
            continue
        component_id = component["id"]
        responsibility = component.get("responsibility")
        if isinstance(responsibility, dict):
            responsibility_id = responsibility.get("id")
            summary = responsibility.get("summary")
            if isinstance(responsibility_id, str):
                if responsibility_id in responsibilities:
                    errors.append(
                        "duplicate responsibility id "
                        f"{responsibility_id}: {responsibilities[responsibility_id]}, "
                        f"{component_id}"
                    )
                responsibilities[responsibility_id] = component_id
            if isinstance(summary, str) and summary.strip():
                normalized = _normalize_responsibility(summary)
                if normalized in responsibility_summaries:
                    errors.append(
                        "duplicate responsibility summary: "
                        f"{responsibility_summaries[normalized]}, {component_id}"
                    )
                responsibility_summaries[normalized] = component_id
        tests = component.get("tests")
        if isinstance(tests, dict) and isinstance(tests.get("selectors"), list):
            for selector in tests["selectors"]:
                if not isinstance(selector, str):
                    continue
                if selector in selectors:
                    errors.append(
                        f"test selector is assigned to multiple components: {selector}"
                    )
                selectors[selector] = component_id

    scope_roots = registry["scope_roots"]
    root_owner: dict[str, str] = {}
    if not isinstance(scope_roots, list) or not scope_roots:
        errors.append("scope_roots must be a non-empty list")
        scope_roots = []
    for index, scope in enumerate(scope_roots):
        context = f"scope_roots[{index}]"
        if not _expect_fields(scope, SCOPE_ROOT_FIELDS, context, errors):
            continue
        relative = _safe_relative_path(scope["path"], f"{context}.path", errors)
        component_id = scope["component_id"]
        if component_id not in component_ids:
            errors.append(f"{context}.component_id is unknown")
        if relative is None:
            continue
        if relative in root_owner:
            errors.append(f"scope root is assigned more than once: {relative}")
        root_owner[relative] = component_id
        path = _project_path(project_root, relative, f"{context}.path", errors)
        if path is None:
            continue
        if path.is_symlink() or not path.is_dir():
            errors.append(f"{context}.path is not an existing non-symlink directory")
        elif not any(candidate.is_file() for candidate in path.rglob("*")):
            errors.append(f"{context}.path contains no files")
    sorted_roots = sorted(root_owner)
    missing_required_roots = REQUIRED_SCOPE_ROOTS - set(root_owner)
    if missing_required_roots:
        errors.append(
            f"scope_roots omits current component groups: {sorted(missing_required_roots)}"
        )
    for left_index, left in enumerate(sorted_roots):
        left_parts = PurePosixPath(left).parts
        for right in sorted_roots[left_index + 1 :]:
            right_parts = PurePosixPath(right).parts
            if right_parts[: len(left_parts)] == left_parts:
                errors.append(f"scope roots overlap: {left}, {right}")

    declared_component_paths: dict[str, set[str]] = defaultdict(set)
    for component_id, component in components_by_id.items():
        paths = component.get("paths")
        if isinstance(paths, list):
            for index, relative in enumerate(paths):
                checked = _safe_relative_path(
                    relative, f"{component_id}.paths[{index}]", errors
                )
                if checked is not None:
                    declared_component_paths[component_id].add(checked)
    mapped_component_paths: dict[str, set[str]] = defaultdict(set)
    for root, owner in root_owner.items():
        mapped_component_paths[owner].add(root)
    for component_id in component_ids:
        if declared_component_paths[component_id] != mapped_component_paths[component_id]:
            errors.append(
                f"{component_id} paths do not exactly match assigned scope roots"
            )

    declared_edges = _component_dependency_edges(components)
    for source_id, component in components_by_id.items():
        dependencies = component.get("dependencies")
        if not isinstance(dependencies, list):
            continue
        for dependency_index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict):
                continue
            target_id = dependency.get("component_id")
            locators = dependency.get("evidence_locators")
            if target_id not in mapped_component_paths or not isinstance(
                locators, list
            ):
                continue
            markers = [
                f"{target_root}/"
                for target_root in mapped_component_paths[target_id]
            ]
            witnessed = False
            for locator in locators:
                if not isinstance(locator, dict):
                    continue
                relative = locator.get("path")
                if relative not in evidence_cache:
                    continue
                if not any(
                    relative == source_root
                    or relative.startswith(f"{source_root}/")
                    for source_root in mapped_component_paths[source_id]
                ):
                    errors.append(
                        f"{source_id}.dependencies[{dependency_index}] evidence "
                        f"is not owned by the source component: {relative}"
                    )
                    continue
                data = evidence_cache[relative][0]
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if any(marker in text for marker in markers):
                    witnessed = True
                    break
            if not witnessed:
                errors.append(
                    f"{source_id}.dependencies[{dependency_index}] evidence "
                    f"does not contain a target-root reference for {target_id}"
                )
    if (
        isinstance(dependency_scan, dict)
        and set(dependency_scan) == DEPENDENCY_SCAN_FIELDS
        and isinstance(dependency_scan.get("text_extensions"), list)
        and isinstance(dependency_scan.get("excluded_directories"), list)
        and isinstance(dependency_scan.get("excluded_files"), list)
        and all(
            isinstance(item, str)
            for field in DEPENDENCY_SCAN_FIELDS
            for item in dependency_scan[field]
        )
        and all(
            isinstance(scope, dict)
            and set(scope) == SCOPE_ROOT_FIELDS
            and isinstance(scope.get("path"), str)
            and isinstance(scope.get("component_id"), str)
            for scope in scope_roots
        )
    ):
        observed_edges, observed_evidence = _scan_dependency_edges(
            project_root, registry, components_by_id, errors
        )
        for edge in sorted(observed_edges - declared_edges):
            errors.append(
                f"undeclared dependency edge {edge[0]} -> {edge[1]} "
                f"observed in {sorted(set(observed_evidence[edge]))}"
            )
        for edge in sorted(declared_edges - observed_edges):
            errors.append(
                f"declared dependency edge lacks an observed path/import reference: "
                f"{edge[0]} -> {edge[1]}"
            )

    layer_index = {layer: index for index, layer in enumerate(layers)}
    for source, target in sorted(declared_edges):
        if source not in components_by_id or target not in components_by_id:
            continue
        source_layer = components_by_id[source].get("layer")
        target_layer = components_by_id[target].get("layer")
        if source_layer in layer_index and target_layer in layer_index:
            if layer_index[source_layer] <= layer_index[target_layer]:
                errors.append(
                    f"dependency violates declared layering: {source} "
                    f"({source_layer}) -> {target} ({target_layer})"
                )
    for cycle in _dependency_cycles(component_ids, declared_edges):
        errors.append(f"dependency cycle detected: {' -> '.join(cycle)}")

    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in declared_edges:
        adjacency[source].add(target)
    reachable: set[str] = set()
    pending = [entry for entry in entries if entry in component_ids]
    while pending:
        component_id = pending.pop()
        if component_id in reachable:
            continue
        reachable.add(component_id)
        pending.extend(sorted(adjacency[component_id] - reachable))
    orphans = component_ids - reachable
    if orphans:
        errors.append(f"orphan components are unreachable from entrypoints: {sorted(orphans)}")

    _verify_longitudinal(
        registry,
        components_by_id,
        project_root,
        errors,
        evidence_cache,
    )
    return errors


def _all_component_locators(component: dict[str, Any]) -> list[dict[str, Any]]:
    locators: list[dict[str, Any]] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if set(value) == LOCATOR_FIELDS:
                locators.append(value)
            else:
                for nested in value.values():
                    visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(component)
    return locators


def removal_impact(
    project_root: Path,
    registry: dict[str, Any],
    component_id: str,
) -> dict[str, Any]:
    components = {
        component["id"]: component
        for component in registry["components"]
        if isinstance(component, dict) and isinstance(component.get("id"), str)
    }
    if component_id not in components:
        raise KeyError(component_id)
    component = components[component_id]
    dependencies = _component_dependency_edges(registry["components"])
    blockers: list[dict[str, str]] = []
    if component_id in registry["entry_component_ids"]:
        blockers.append(
            {
                "kind": "entrypoint",
                "detail": f"{component_id} is a declared system entry component",
            }
        )
    for dependent, target in sorted(dependencies):
        if target == component_id:
            blockers.append(
                {
                    "kind": "dependent_component",
                    "detail": f"{dependent} declares a dependency on {component_id}",
                }
            )
    owned_roots = component["paths"]
    for other_id, other in sorted(components.items()):
        if other_id == component_id:
            continue
        for locator in _all_component_locators(other):
            locator_path = locator["path"]
            if any(
                locator_path == root or locator_path.startswith(f"{root}/")
                for root in owned_roots
            ):
                blockers.append(
                    {
                        "kind": "cross_component_evidence",
                        "detail": f"{other_id} binds evidence at {locator_path}",
                    }
                )
    for selector in component["tests"]["selectors"]:
        blockers.append(
            {
                "kind": "test_migration",
                "detail": f"declared selector must be removed or reassigned: {selector}",
            }
        )
    migration = component["replacement_migration_path"]
    if migration["mode"] == "retire_without_replacement":
        blockers.append(
            {
                "kind": "unassigned_responsibility",
                "detail": (
                    f"{component['responsibility']['id']} has no registered "
                    "replacement component"
                ),
            }
        )
    return {
        "status": "blocked" if blockers else "ready",
        "component_id": component_id,
        "dry_run": True,
        "deletion_performed": False,
        "would_delete": [],
        "owned_paths": list(owned_roots),
        "blockers": blockers,
        "required_steps": (
            list(component["removal_path"]["steps"])
            + list(component["replacement_migration_path"]["steps"])
        ),
    }


def _result_payload(
    registry: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "status": "fail" if errors else "pass",
        "registry_id": registry.get("registry_id"),
        "registry_status": registry.get("status"),
        "component_count": (
            len(registry["components"])
            if isinstance(registry.get("components"), list)
            else 0
        ),
        "longitudinal_cost_proved": (
            registry.get("longitudinal_maintenance", {}).get(
                "longitudinal_cost_proved"
            )
            if isinstance(registry.get("longitudinal_maintenance"), dict)
            else None
        ),
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--removal-impact", metavar="COMPONENT_ID")
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    registry_path = args.registry or project_root / REGISTRY_RELATIVE_PATH
    if not registry_path.is_absolute():
        registry_path = project_root / registry_path
    try:
        registry = load_registry(registry_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        payload = {
            "status": "fail",
            "registry_id": None,
            "registry_status": None,
            "component_count": 0,
            "longitudinal_cost_proved": None,
            "errors": [str(exc)],
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        else:
            print(f"component registry verification: FAIL\n- {exc}")
        return 1
    errors = verify_registry(project_root, registry)
    if errors:
        payload = _result_payload(registry, errors)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        else:
            print("component registry verification: FAIL")
            for error in errors:
                print(f"- {error}")
        return 1
    if args.removal_impact:
        try:
            payload = removal_impact(
                project_root, registry, args.removal_impact
            )
        except KeyError:
            payload = {
                "status": "fail",
                "component_id": args.removal_impact,
                "dry_run": True,
                "deletion_performed": False,
                "would_delete": [],
                "blockers": [
                    {
                        "kind": "unknown_component",
                        "detail": f"unknown component: {args.removal_impact}",
                    }
                ],
                "required_steps": [],
            }
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 1
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0
    payload = _result_payload(registry, errors)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "component registry verification: PASS "
            f"({payload['component_count']} components; "
            f"status={payload['registry_status']}; "
            "longitudinal_cost_proved=false)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
