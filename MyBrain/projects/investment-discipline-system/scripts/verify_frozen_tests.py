#!/usr/bin/env python3
"""Verify the exact source and executable baseline of selected frozen tests.

This control protects only the selectors named by FROZEN_TEST_MANIFEST_V1.json.
It does not establish that a protected test's oracle is correct.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
MANIFEST_RELATIVE = Path("governance/FROZEN_TEST_MANIFEST_V1.json")
AST_HASH_ALGORITHM = "sha256-canonical-python-ast-v1"
SOURCE_HASH_ALGORITHM = "sha256-raw-file-bytes"
ASSERTION_HASH_ALGORITHM = "sha256-canonical-assertion-ast-list-v1"
BASELINE_SENTINEL = "__IDS_FROZEN_TEST_BASELINE_V1__="

CLAIM_BOUNDARY = {
    "protects": (
        "only the exact selectors listed in this manifest, their containing "
        "classes, source modules, and clean baseline outcomes"
    ),
    "does_not_prove": [
        "correctness of any listed test oracle",
        "integrity or executability of unlisted tests",
        "correctness of product code or transitive dependencies",
    ],
}
HASH_CONTRACT = {
    "source": SOURCE_HASH_ALGORITHM,
    "class_ast": AST_HASH_ALGORITHM,
    "test_ast": AST_HASH_ALGORITHM,
    "assertions": ASSERTION_HASH_ALGORITHM,
}
FORBIDDEN_DISABLE_MECHANISMS = [
    "unittest.skip",
    "unittest.skipIf",
    "unittest.skipUnless",
    "unittest.expectedFailure",
    "pytest.mark.skip",
    "pytest.mark.skipif",
    "pytest.mark.xfail",
    "dynamic SkipTest/skipTest/pytest.skip/pytest.xfail",
]
BASELINE_CONTRACT = {
    "runner": "current-python-stdlib-unittest",
    "working_directory": "project_root",
    "process_isolation": "fresh_subprocess",
    "timeout_seconds": 120,
}
BASELINE_ZERO_OUTCOMES = {
    "failures": 0,
    "errors": 0,
    "skipped": 0,
    "expected_failures": 0,
    "unexpected_successes": 0,
}


@dataclass(frozen=True)
class FrozenIdentity:
    file: str
    class_name: str
    test_name: str

    @property
    def module_name(self) -> str:
        return ".".join(PurePosixPath(self.file).with_suffix("").parts)

    @property
    def selector(self) -> str:
        return f"{self.module_name}.{self.class_name}.{self.test_name}"


EXPECTED_TESTS = (
    FrozenIdentity(
        "governance_tests/test_project_method.py",
        "ProjectMethodPolicyTests",
        "test_criterion_weakening_is_rejected",
    ),
    FrozenIdentity(
        "governance_tests/test_project_method.py",
        "ProjectMethodPolicyTests",
        "test_reviewer_candidate_write_access_is_rejected",
    ),
    FrozenIdentity(
        "governance_tests/test_project_method.py",
        "ProjectMethodPolicyTests",
        "test_frozen_test_baseline_bypass_is_rejected",
    ),
    FrozenIdentity(
        "governance_tests/test_context_recovery.py",
        "ContextRecoveryDesignFreezeTests",
        "test_receipt_claim_cannot_override_derived_observation",
    ),
    FrozenIdentity(
        "governance_tests/test_work_packets.py",
        "WorkPacketVerifierTests",
        "test_disjoint_text_changes_can_fail_joint_semantic_invariant",
    ),
    FrozenIdentity(
        "governance_tests/test_assurance_runner.py",
        "AssuranceRunnerTests",
        "test_timeout_fails_closed_and_preserves_partial_output",
    ),
)


class StrictJsonError(ValueError):
    """Raised when input is not strict, duplicate-free JSON."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJsonError(f"duplicate object key: {key}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str) -> None:
    raise StrictJsonError(f"non-finite JSON number: {value}")


def load_strict_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_constant,
        )
    except FileNotFoundError:
        errors.append(f"missing frozen-test manifest: {MANIFEST_RELATIVE.as_posix()}")
        return None
    except UnicodeDecodeError as exc:
        errors.append(f"frozen-test manifest is not UTF-8: {exc}")
        return None
    except (json.JSONDecodeError, StrictJsonError) as exc:
        errors.append(f"invalid strict JSON in frozen-test manifest: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append("frozen-test manifest top level must be an object")
        return None
    return value


def exact_object(
    value: Any,
    expected_keys: set[str],
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    actual_keys = set(value)
    if actual_keys != expected_keys:
        errors.append(
            f"{label} fields differ: "
            f"missing={sorted(expected_keys - actual_keys)}, "
            f"extra={sorted(actual_keys - expected_keys)}"
        )
    return value


def exact_list(value: Any, label: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array")
        return None
    return value


def unique_in_order(values: list[Any], label: str, errors: list[str]) -> bool:
    try:
        unique_count = len(set(values))
    except TypeError:
        errors.append(f"{label} contains non-scalar identities")
        return False
    if unique_count != len(values):
        errors.append(f"{label} contains duplicates")
        return False
    return True


def expected_source_files() -> list[str]:
    return list(dict.fromkeys(item.file for item in EXPECTED_TESTS))


def expected_classes() -> list[tuple[str, str]]:
    return list(dict.fromkeys((item.file, item.class_name) for item in EXPECTED_TESTS))


def validate_manifest_shape(
    manifest: dict[str, Any], errors: list[str]
) -> dict[str, dict[Any, dict[str, Any]]]:
    exact_object(
        manifest,
        {
            "schema_version",
            "manifest_id",
            "requirement",
            "hash_contract",
            "forbidden_disable_mechanisms",
            "claim_boundary",
            "baseline",
            "sources",
            "classes",
            "tests",
        },
        "frozen-test manifest",
        errors,
    )
    if (
        type(manifest.get("schema_version")) is not int
        or manifest.get("schema_version") != 1
    ):
        errors.append("frozen-test schema_version must equal integer 1")
    if manifest.get("manifest_id") != "FROZEN-TEST-MANIFEST-V1":
        errors.append("frozen-test manifest_id differs")

    requirement = exact_object(
        manifest.get("requirement"),
        {"failure_id", "invariant_id"},
        "frozen-test requirement",
        errors,
    )
    if requirement is not None and requirement != {
        "failure_id": "VER-07",
        "invariant_id": "PM-09-FROZEN-TESTS",
    }:
        errors.append("frozen-test requirement binding differs")

    hash_contract = exact_object(
        manifest.get("hash_contract"),
        set(HASH_CONTRACT),
        "frozen-test hash_contract",
        errors,
    )
    if hash_contract is not None and hash_contract != HASH_CONTRACT:
        errors.append("frozen-test hash contract differs")

    mechanisms = exact_list(
        manifest.get("forbidden_disable_mechanisms"),
        "frozen-test forbidden_disable_mechanisms",
        errors,
    )
    if mechanisms is not None and mechanisms != FORBIDDEN_DISABLE_MECHANISMS:
        errors.append("frozen-test forbidden disable mechanisms differ")

    boundary = exact_object(
        manifest.get("claim_boundary"),
        {"protects", "does_not_prove"},
        "frozen-test claim_boundary",
        errors,
    )
    if boundary is not None and boundary != CLAIM_BOUNDARY:
        errors.append("frozen-test claim boundary differs")

    baseline = exact_object(
        manifest.get("baseline"),
        {
            "runner",
            "working_directory",
            "process_isolation",
            "timeout_seconds",
            "expected",
        },
        "frozen-test baseline",
        errors,
    )
    if baseline is not None:
        for field, expected in BASELINE_CONTRACT.items():
            if baseline.get(field) != expected:
                errors.append(f"frozen-test baseline {field} differs")
        expected_outcome = exact_object(
            baseline.get("expected"),
            {"tests_run", *BASELINE_ZERO_OUTCOMES},
            "frozen-test baseline expected outcome",
            errors,
        )
        if expected_outcome is not None:
            if expected_outcome.get("tests_run") != len(EXPECTED_TESTS):
                errors.append("frozen-test baseline tests_run differs")
            for field, expected in BASELINE_ZERO_OUTCOMES.items():
                if expected_outcome.get(field) != expected:
                    errors.append(
                        f"frozen-test baseline expected {field} must equal {expected}"
                    )

    source_map: dict[str, dict[str, Any]] = {}
    sources = exact_list(manifest.get("sources"), "frozen-test sources", errors)
    if sources is not None:
        observed_order: list[Any] = []
        for index, source_value in enumerate(sources):
            source = exact_object(
                source_value,
                {"file", "sha256"},
                f"frozen-test sources[{index}]",
                errors,
            )
            if source is None:
                continue
            file_value = source.get("file")
            observed_order.append(file_value)
            if isinstance(file_value, str) and file_value not in source_map:
                source_map[file_value] = source
            digest = source.get("sha256")
            if not is_sha256(digest):
                errors.append(f"frozen-test sources[{index}].sha256 is invalid")
        unique_in_order(observed_order, "frozen-test source files", errors)
        if observed_order != expected_source_files():
            errors.append("frozen-test source file identities or order differ")

    class_map: dict[tuple[str, str], dict[str, Any]] = {}
    classes = exact_list(manifest.get("classes"), "frozen-test classes", errors)
    if classes is not None:
        observed_classes: list[tuple[Any, Any]] = []
        for index, class_value in enumerate(classes):
            class_entry = exact_object(
                class_value,
                {"file", "class_name", "normalized_ast_sha256"},
                f"frozen-test classes[{index}]",
                errors,
            )
            if class_entry is None:
                continue
            identity = (class_entry.get("file"), class_entry.get("class_name"))
            observed_classes.append(identity)
            if all(isinstance(item, str) for item in identity):
                typed_identity = (str(identity[0]), str(identity[1]))
                if typed_identity not in class_map:
                    class_map[typed_identity] = class_entry
            if not is_sha256(class_entry.get("normalized_ast_sha256")):
                errors.append(
                    f"frozen-test classes[{index}].normalized_ast_sha256 is invalid"
                )
        unique_in_order(observed_classes, "frozen-test class identities", errors)
        if observed_classes != expected_classes():
            errors.append("frozen-test class identities or order differ")

    test_map: dict[FrozenIdentity, dict[str, Any]] = {}
    tests = exact_list(manifest.get("tests"), "frozen-test tests", errors)
    if tests is not None:
        observed_tests: list[tuple[Any, Any, Any, Any]] = []
        for index, test_value in enumerate(tests):
            test = exact_object(
                test_value,
                {
                    "selector",
                    "file",
                    "class_name",
                    "test_name",
                    "normalized_ast_sha256",
                    "assertion_count",
                    "assertion_ast_sha256",
                },
                f"frozen-test tests[{index}]",
                errors,
            )
            if test is None:
                continue
            identity_values = (
                test.get("file"),
                test.get("class_name"),
                test.get("test_name"),
                test.get("selector"),
            )
            observed_tests.append(identity_values)
            if all(isinstance(item, str) for item in identity_values):
                identity = FrozenIdentity(
                    str(identity_values[0]),
                    str(identity_values[1]),
                    str(identity_values[2]),
                )
                if identity not in test_map:
                    test_map[identity] = test
                if test.get("selector") != identity.selector:
                    errors.append(
                        f"frozen-test tests[{index}] selector is not derived from "
                        "its actual file/class/test identity"
                    )
            if not is_sha256(test.get("normalized_ast_sha256")):
                errors.append(
                    f"frozen-test tests[{index}].normalized_ast_sha256 is invalid"
                )
            if not is_sha256(test.get("assertion_ast_sha256")):
                errors.append(
                    f"frozen-test tests[{index}].assertion_ast_sha256 is invalid"
                )
            assertion_count = test.get("assertion_count")
            if type(assertion_count) is not int or assertion_count < 1:
                errors.append(
                    f"frozen-test tests[{index}].assertion_count must be positive"
                )
        unique_in_order(observed_tests, "frozen-test selector identities", errors)
        expected_test_values = [
            (item.file, item.class_name, item.test_name, item.selector)
            for item in EXPECTED_TESTS
        ]
        if observed_tests != expected_test_values:
            errors.append("frozen-test selector identities or order differ")

    return {"sources": source_map, "classes": class_map, "tests": test_map}


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def ast_payload(value: Any) -> Any:
    if isinstance(value, ast.AST):
        return {
            "_type": type(value).__name__,
            **{field: ast_payload(getattr(value, field)) for field in value._fields},
        }
    if isinstance(value, list):
        return [ast_payload(item) for item in value]
    if isinstance(value, bytes):
        return {"_scalar": "bytes", "hex": value.hex()}
    if isinstance(value, complex):
        return {
            "_scalar": "complex",
            "real": repr(value.real),
            "imag": repr(value.imag),
        }
    if value is Ellipsis:
        return {"_scalar": "ellipsis"}
    return value


def normalized_ast_sha256(node: ast.AST) -> str:
    return hashlib.sha256(canonical_json(ast_payload(node))).hexdigest()


def assertion_nodes(node: ast.AST) -> list[ast.AST]:
    assertions: list[ast.AST] = []
    for candidate in ast.walk(node):
        if isinstance(candidate, ast.Assert):
            assertions.append(candidate)
        elif isinstance(candidate, ast.Call):
            name = dotted_name(candidate.func)
            leaf = name.rsplit(".", 1)[-1] if name else ""
            if leaf.startswith("assert") or leaf == "fail":
                assertions.append(candidate)
    return assertions


def assertion_ast_sha256(nodes: list[ast.AST]) -> str:
    return hashlib.sha256(
        canonical_json([ast_payload(node) for node in nodes])
    ).hexdigest()


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def decorator_name(node: ast.expr) -> str | None:
    return dotted_name(node.func if isinstance(node, ast.Call) else node)


def forbidden_decorator(name: str | None) -> bool:
    if not name:
        return False
    leaf = name.rsplit(".", 1)[-1].casefold()
    return leaf in {"skip", "skipif", "skipunless", "expectedfailure", "xfail"}


def forbidden_runtime_disable(node: ast.AST) -> str | None:
    for candidate in ast.walk(node):
        if isinstance(candidate, ast.Call):
            name = dotted_name(candidate.func)
            leaf = name.rsplit(".", 1)[-1].casefold() if name else ""
            if leaf in {"skip", "skiptest", "xfail"}:
                return name or leaf
        if isinstance(candidate, ast.Raise) and candidate.exc is not None:
            raised = candidate.exc
            if isinstance(raised, ast.Call):
                raised = raised.func
            name = dotted_name(raised)
            if name and name.rsplit(".", 1)[-1].casefold() == "skiptest":
                return name
    return None


def literal_value(node: ast.AST) -> tuple[bool, Any]:
    try:
        return True, ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return False, None


def comparison_truth(node: ast.AST) -> bool | None:
    if (
        not isinstance(node, ast.Compare)
        or len(node.ops) != 1
        or len(node.comparators) != 1
    ):
        return None
    left_known, left = literal_value(node.left)
    right_known, right = literal_value(node.comparators[0])
    if not left_known or not right_known:
        if ast_payload(node.left) == ast_payload(node.comparators[0]):
            if isinstance(node.ops[0], (ast.Eq, ast.Is, ast.LtE, ast.GtE)):
                return True
        return None
    operator = node.ops[0]
    try:
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right
        if isinstance(operator, ast.Is):
            return left is right
        if isinstance(operator, ast.IsNot):
            return left is not right
        if isinstance(operator, ast.In):
            return left in right
        if isinstance(operator, ast.NotIn):
            return left not in right
        if isinstance(operator, ast.Lt):
            return left < right
        if isinstance(operator, ast.LtE):
            return left <= right
        if isinstance(operator, ast.Gt):
            return left > right
        if isinstance(operator, ast.GtE):
            return left >= right
    except (TypeError, ValueError):
        return None
    return None


def static_truth(node: ast.AST) -> bool | None:
    comparison = comparison_truth(node)
    if comparison is not None:
        return comparison
    known, value = literal_value(node)
    return bool(value) if known else None


def tautological_assertion(node: ast.AST) -> bool:
    if isinstance(node, ast.Assert):
        return static_truth(node.test) is True
    if not isinstance(node, ast.Call):
        return False
    name = dotted_name(node.func)
    leaf = name.rsplit(".", 1)[-1] if name else ""
    if leaf == "assertTrue" and node.args:
        return static_truth(node.args[0]) is True
    if leaf == "assertFalse" and node.args:
        return static_truth(node.args[0]) is False
    if len(node.args) < 2:
        return False
    left_known, left = literal_value(node.args[0])
    right_known, right = literal_value(node.args[1])
    same_ast = ast_payload(node.args[0]) == ast_payload(node.args[1])
    if leaf in {"assertEqual", "assertIs", "assertLessEqual", "assertGreaterEqual"}:
        if same_ast:
            return True
        if left_known and right_known:
            if leaf in {"assertEqual", "assertIs"}:
                return left == right
            if leaf == "assertLessEqual":
                return left <= right
            return left >= right
    if left_known and right_known:
        if leaf in {"assertNotEqual", "assertIsNot"}:
            return left != right
        if leaf == "assertLess":
            return left < right
        if leaf == "assertGreater":
            return left > right
        if leaf == "assertIn":
            return left in right
        if leaf == "assertNotIn":
            return left not in right
    return False


def safe_source_path(root: Path, relative: str, errors: list[str]) -> Path | None:
    pure = PurePosixPath(relative)
    if (
        not relative
        or "\\" in relative
        or pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.suffix != ".py"
        or pure.parts[0] not in {"governance_tests", "tests", "acceptance"}
    ):
        errors.append(f"unsafe frozen-test source path: {relative!r}")
        return None
    candidate = root.joinpath(*pure.parts)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"frozen-test source path uses symlink: {relative}")
            return None
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError:
        errors.append(f"missing frozen-test source file: {relative}")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        errors.append(f"frozen-test source escapes project root: {relative}")
        return None
    if not resolved.is_file():
        errors.append(f"frozen-test source is not a regular file: {relative}")
        return None
    return resolved


def find_top_level_class(module: ast.Module, class_name: str) -> list[ast.ClassDef]:
    return [
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]


def find_direct_test_method(
    class_node: ast.ClassDef, test_name: str
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == test_name
    ]


def unittest_testcase_class(class_node: ast.ClassDef) -> bool:
    return any(
        (dotted_name(base) or "").rsplit(".", 1)[-1] == "TestCase"
        for base in class_node.bases
    )


def validate_module_disable_assignments(
    module: ast.Module, relative: str, errors: list[str]
) -> None:
    forbidden_targets = {
        "pytestmark",
        "__unittest_skip__",
        "__unittest_expecting_failure__",
    }
    for node in ast.walk(module):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets.append(node.target)
        for target in targets:
            name = dotted_name(target)
            leaf = name.rsplit(".", 1)[-1] if name else ""
            if leaf in forbidden_targets:
                errors.append(
                    f"forbidden test-disable assignment {name or leaf} in {relative}"
                )


def validate_sources(
    root: Path,
    entries: dict[str, dict[Any, dict[str, Any]]],
    errors: list[str],
) -> None:
    parsed_modules: dict[str, ast.Module] = {}
    class_nodes: dict[tuple[str, str], ast.ClassDef] = {}

    for relative in expected_source_files():
        path = safe_source_path(root, relative, errors)
        if path is None:
            continue
        try:
            source_bytes = path.read_bytes()
            source_text = source_bytes.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"cannot read frozen-test source {relative}: {exc}")
            continue
        source_entry = entries["sources"].get(relative)
        observed_source_hash = hashlib.sha256(source_bytes).hexdigest()
        if source_entry is None:
            errors.append(f"missing source binding for frozen-test file: {relative}")
        elif source_entry.get("sha256") != observed_source_hash:
            errors.append(f"source sha256 mismatch for frozen-test file: {relative}")
        try:
            module = ast.parse(source_text, filename=relative, type_comments=True)
        except SyntaxError as exc:
            errors.append(
                f"invalid Python in frozen-test source {relative}: "
                f"{exc.lineno}:{exc.offset}: {exc.msg}"
            )
            continue
        parsed_modules[relative] = module
        validate_module_disable_assignments(module, relative, errors)

    for identity in EXPECTED_TESTS:
        class_identity = (identity.file, identity.class_name)
        if class_identity in class_nodes:
            continue
        module = parsed_modules.get(identity.file)
        if module is None:
            continue
        matches = find_top_level_class(module, identity.class_name)
        if len(matches) != 1:
            errors.append(
                "missing, renamed, or duplicate exact frozen-test class: "
                f"{identity.file}::{identity.class_name}"
            )
            continue
        class_node = matches[0]
        class_nodes[class_identity] = class_node
        if not unittest_testcase_class(class_node):
            errors.append(
                f"frozen-test class no longer derives from TestCase: "
                f"{identity.file}::{identity.class_name}"
            )
        for decorator in class_node.decorator_list:
            name = decorator_name(decorator)
            if forbidden_decorator(name):
                errors.append(
                    "forbidden test-disable mechanism on frozen-test class: "
                    f"{identity.file}::{identity.class_name}: {name}"
                )
        class_entry = entries["classes"].get(class_identity)
        observed_class_hash = normalized_ast_sha256(class_node)
        if class_entry is None:
            errors.append(
                "missing class AST binding for frozen-test class: "
                f"{identity.file}::{identity.class_name}"
            )
        elif class_entry.get("normalized_ast_sha256") != observed_class_hash:
            errors.append(
                "class AST sha256 mismatch for frozen-test class: "
                f"{identity.file}::{identity.class_name}"
            )

    for identity in EXPECTED_TESTS:
        class_node = class_nodes.get((identity.file, identity.class_name))
        if class_node is None:
            continue
        matches = find_direct_test_method(class_node, identity.test_name)
        if len(matches) != 1:
            errors.append(
                "missing, renamed, or duplicate exact frozen-test method: "
                f"{identity.file}::{identity.class_name}::{identity.test_name}"
            )
            continue
        method = matches[0]
        if isinstance(method, ast.AsyncFunctionDef):
            errors.append(
                f"frozen unittest method cannot be async: {identity.selector}"
            )
        if (
            len(method.args.posonlyargs) + len(method.args.args) != 1
            or method.args.vararg is not None
            or method.args.kwarg is not None
            or method.args.kwonlyargs
            or method.args.defaults
            or method.args.kw_defaults
        ):
            errors.append(
                f"frozen unittest method signature differs: {identity.selector}"
            )
        for decorator in method.decorator_list:
            name = decorator_name(decorator)
            if forbidden_decorator(name):
                errors.append(
                    "forbidden test-disable mechanism on frozen-test method: "
                    f"{identity.selector}: {name}"
                )
        runtime_disable = forbidden_runtime_disable(method)
        if runtime_disable is not None:
            errors.append(
                "forbidden dynamic test-disable mechanism in frozen-test method: "
                f"{identity.selector}: {runtime_disable}"
            )

        test_entry = entries["tests"].get(identity)
        observed_test_hash = normalized_ast_sha256(method)
        assertions = assertion_nodes(method)
        observed_assertion_hash = assertion_ast_sha256(assertions)
        if not assertions:
            errors.append(f"frozen-test method has no assertions: {identity.selector}")
        if any(tautological_assertion(node) for node in assertions):
            errors.append(
                "literal or structural always-pass assertion in frozen-test method: "
                f"{identity.selector}"
            )
        if test_entry is None:
            errors.append(
                f"missing method binding for frozen test: {identity.selector}"
            )
            continue
        if test_entry.get("normalized_ast_sha256") != observed_test_hash:
            errors.append(
                f"test AST sha256 mismatch for frozen-test method: {identity.selector}"
            )
        if test_entry.get("assertion_count") != len(assertions):
            errors.append(
                f"assertion count mismatch for frozen-test method: {identity.selector}"
            )
        if test_entry.get("assertion_ast_sha256") != observed_assertion_hash:
            errors.append(
                f"assertion AST sha256 mismatch for frozen-test method: {identity.selector}"
            )


BASELINE_CHILD = r"""
import json
import os
import sys
import unittest

root = sys.argv[1]
selectors = sys.argv[2:]
sys.path.insert(0, root)
os.chdir(root)
loader = unittest.TestLoader()
suite = unittest.TestSuite()
loaded_counts = []
for selector in selectors:
    loaded = loader.loadTestsFromName(selector)
    loaded_counts.append({"selector": selector, "count": loaded.countTestCases()})
    suite.addTest(loaded)
result = unittest.TestResult()
suite.run(result)
payload = {
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "expected_failures": len(result.expectedFailures),
    "unexpected_successes": len(result.unexpectedSuccesses),
    "loaded_counts": loaded_counts,
    "failure_ids": [test.id() for test, _ in result.failures],
    "error_ids": [test.id() for test, _ in result.errors],
    "skipped_ids": [test.id() for test, _ in result.skipped],
    "expected_failure_ids": [test.id() for test, _ in result.expectedFailures],
    "unexpected_success_ids": [test.id() for test in result.unexpectedSuccesses],
}
print("__IDS_FROZEN_TEST_BASELINE_V1__=" + json.dumps(payload, sort_keys=True))
clean = (
    result.wasSuccessful()
    and result.testsRun == len(selectors)
    and all(item["count"] == 1 for item in loaded_counts)
    and not result.skipped
    and not result.expectedFailures
    and not result.unexpectedSuccesses
)
raise SystemExit(0 if clean else 1)
"""


def run_baseline(root: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["IDS_PROJECT_ROOT"] = str(root)
    command = [
        sys.executable,
        "-B",
        "-c",
        BASELINE_CHILD,
        str(root),
        *(identity.selector for identity in EXPECTED_TESTS),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=BASELINE_CONTRACT["timeout_seconds"],
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        errors.append(
            "frozen-test baseline timed out after "
            f"{BASELINE_CONTRACT['timeout_seconds']} seconds"
        )
        return {
            "status": "fail",
            "process_exit": 124,
            "stdout_tail": str(output)[-4000:],
        }, errors

    payload: dict[str, Any] | None = None
    for line in reversed(completed.stdout.splitlines()):
        if line.startswith(BASELINE_SENTINEL):
            try:
                candidate = json.loads(line.removeprefix(BASELINE_SENTINEL))
            except json.JSONDecodeError as exc:
                errors.append(
                    f"frozen-test baseline emitted invalid receipt JSON: {exc}"
                )
                break
            if isinstance(candidate, dict):
                payload = candidate
            else:
                errors.append("frozen-test baseline receipt must be an object")
            break
    if payload is None:
        errors.append("frozen-test baseline emitted no machine receipt")
        return {
            "status": "fail",
            "process_exit": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
        }, errors

    receipt = {
        "status": "pass",
        "process_exit": completed.returncode,
        **payload,
    }
    expected_counts = {"tests_run": len(EXPECTED_TESTS), **BASELINE_ZERO_OUTCOMES}
    for field, expected in expected_counts.items():
        if payload.get(field) != expected:
            errors.append(
                f"frozen-test baseline {field} differs: "
                f"expected={expected}, observed={payload.get(field)!r}"
            )
    loaded_counts = payload.get("loaded_counts")
    expected_loaded_counts = [
        {"selector": identity.selector, "count": 1} for identity in EXPECTED_TESTS
    ]
    if loaded_counts != expected_loaded_counts:
        errors.append("frozen-test baseline did not load each exact selector once")
    if completed.returncode != 0:
        errors.append(
            f"frozen-test baseline process exited {completed.returncode}; "
            f"output tail={completed.stdout[-2000:]!r}"
        )
    if errors:
        receipt["status"] = "fail"
        receipt["stdout_tail"] = completed.stdout[-4000:]
    return receipt, errors


def verify(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = root / MANIFEST_RELATIVE
    if manifest_path.is_symlink():
        errors.append("frozen-test manifest must not be a symlink")
        manifest = None
    else:
        manifest = load_strict_json(manifest_path, errors)

    baseline: dict[str, Any] = {
        "status": "not_run",
        "reason": "static_integrity_failure",
    }
    if manifest is not None:
        entries = validate_manifest_shape(manifest, errors)
        validate_sources(root, entries, errors)
    if not errors:
        baseline, baseline_errors = run_baseline(root)
        errors.extend(baseline_errors)

    return {
        "schema_version": 1,
        "status": "pass" if not errors else "fail",
        "manifest": MANIFEST_RELATIVE.as_posix(),
        "selectors_checked": len(EXPECTED_TESTS),
        "claim_boundary": CLAIM_BOUNDARY,
        "baseline": baseline,
        "errors": errors,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="project root (defaults to IDS_PROJECT_ROOT or this script's parent)",
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON receipt")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise NotADirectoryError(root)
        receipt = verify(root)
    except Exception as exc:  # fail closed on verifier defects and I/O races
        receipt = {
            "schema_version": 1,
            "status": "fail",
            "manifest": MANIFEST_RELATIVE.as_posix(),
            "selectors_checked": len(EXPECTED_TESTS),
            "claim_boundary": CLAIM_BOUNDARY,
            "baseline": {
                "status": "not_run",
                "reason": "verifier_internal_error",
            },
            "errors": [
                f"frozen-test verifier internal error: {type(exc).__name__}: {exc}"
            ],
        }
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    elif receipt["status"] == "pass":
        print(
            "frozen-test verification: PASS "
            f"({receipt['selectors_checked']} selectors; "
            f"baseline ran {receipt['baseline'].get('tests_run')} tests)"
        )
        print(
            "claim boundary: listed selectors only; "
            "test-oracle correctness is not proved"
        )
    else:
        print("frozen-test verification: FAIL")
        for error in receipt["errors"]:
            print(f"- {error}")
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
