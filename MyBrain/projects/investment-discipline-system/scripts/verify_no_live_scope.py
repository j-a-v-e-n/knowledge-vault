#!/usr/bin/env python3
"""Fail closed when the declared local Paper V1 tree exposes a live surface."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlsplit


SCRIPT_PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
DEFAULT_POLICY_RELATIVE = Path("governance/NO_LIVE_SCOPE_POLICY_V1.json")
EXPECTED_POLICY_CANONICAL_SHA256 = (
    "220d2c5358709b99459742c7f5e1cb9b0f0ca79b11b3b5fac5ec6ed226040045"
)

POLICY_TOP_LEVEL_FIELDS = {
    "schema_version",
    "policy_id",
    "scope",
    "python_ast_policy",
    "endpoint_policy",
    "local_paper_only_surface",
    "work_packet_policy",
    "claim_boundary",
}
SCOPE_FIELDS = {
    "runtime_entrypoints",
    "implementation_roots",
    "entrypoint_discovery",
    "active_work_packet_directory",
    "active_work_packet_states",
    "ignored_directory_names",
    "python_suffix",
    "configuration_suffixes",
    "inert_data_or_document_suffixes",
    "reject_unknown_file_suffixes",
    "reject_symlinks",
}
ENTRYPOINT_DISCOVERY_FIELDS = {
    "filename_prefix",
    "filename_suffix",
    "recursive",
    "require_main_guard",
}
PYTHON_AST_FIELDS = {
    "allowed_import_roots",
    "forbidden_import_prefixes",
    "forbidden_call_prefixes",
    "forbidden_call_paths",
    "forbidden_call_leaf_names",
    "dynamic_import_call_paths",
    "allowed_dynamic_import_modules",
    "reject_nonliteral_dynamic_imports",
    "reject_star_imports",
}
ENDPOINT_FIELDS = {
    "allowed_read_only_endpoints",
    "python_endpoint_name_fragments",
    "text_url_schemes",
    "require_https",
    "reject_userinfo",
    "reject_fragments",
    "reject_unlisted_endpoints",
    "reject_dynamic_python_endpoint_values",
}
ENDPOINT_INSTANCE_FIELDS = {
    "scheme",
    "host",
    "port",
    "path",
    "allowed_query_keys",
    "purpose",
}
PAPER_SURFACE_FIELDS = {
    "definitions",
    "execution_capable_class_suffixes",
    "allowed_execution_capable_classes",
    "reject_unlisted_public_methods",
}
PAPER_DEFINITION_FIELDS = {
    "path",
    "class_name",
    "required_public_methods",
    "allowed_public_methods",
}
WORK_PACKET_POLICY_FIELDS = {
    "filename_suffix",
    "instance_schema_version",
    "required_fields",
    "state_specific_optional_fields",
    "all_state_values",
    "allowed_active_external_side_effects",
    "forbidden_active_side_effect_fragments",
    "reject_unlisted_active_external_side_effects",
    "reject_unexpected_directory_entries",
}
CLAIM_BOUNDARY_FIELDS = {
    "proves",
    "does_not_prove",
    "required_companion_controls",
}

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
TOKEN_NORMALIZER = re.compile(r"[^a-z0-9]+")
PACKET_ID_PATTERN = re.compile(r"[A-Z0-9][A-Z0-9._-]{1,127}")


class DuplicateKeyError(ValueError):
    """Raised when an object in a purported JSON document repeats a key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def add_error(
    errors: list[dict[str, Any]],
    oracle_id: str,
    message: str,
    *,
    path: str | None = None,
    line: int | None = None,
) -> None:
    error: dict[str, Any] = {"oracle_id": oracle_id, "message": message}
    if path is not None:
        error["path"] = path
    if line is not None:
        error["line"] = line
    errors.append(error)


def exact_keys(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[dict[str, Any]],
) -> bool:
    if not isinstance(value, dict):
        add_error(
            errors,
            "NLS-POLICY-SCHEMA",
            f"{label} must be an object",
        )
        return False
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        add_error(
            errors,
            "NLS-POLICY-SCHEMA",
            f"{label} fields differ; missing={missing}, extra={extra}",
        )
        return False
    return True


def read_strict_json(
    path: Path,
    label: str,
    errors: list[dict[str, Any]],
    *,
    oracle_id: str,
    relative_path: str | None = None,
) -> tuple[dict[str, Any] | None, bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        add_error(
            errors,
            oracle_id,
            f"{label} is unreadable: {exc}",
            path=relative_path,
        )
        return None, b""
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        add_error(
            errors,
            oracle_id,
            f"{label} is not strict JSON: {exc}",
            path=relative_path,
        )
        return None, raw
    if not isinstance(value, dict):
        add_error(
            errors,
            oracle_id,
            f"{label} top-level value must be an object",
            path=relative_path,
        )
        return None, raw
    return value, raw


def is_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item) for item in value)
        and len(value) == len(set(value))
    )


def validate_policy_schema(
    policy: dict[str, Any], errors: list[dict[str, Any]]
) -> bool:
    start = len(errors)
    if not exact_keys(policy, POLICY_TOP_LEVEL_FIELDS, "policy", errors):
        return False
    if policy["schema_version"] != "no-live-scope-policy/v1":
        add_error(
            errors,
            "NLS-POLICY-SCHEMA",
            "unsupported policy schema_version",
        )
    if policy["policy_id"] != "NO-LIVE-PAPER-V1":
        add_error(errors, "NLS-POLICY-SCHEMA", "unexpected policy_id")

    scope = policy["scope"]
    exact_keys(scope, SCOPE_FIELDS, "policy.scope", errors)
    if isinstance(scope, dict):
        exact_keys(
            scope.get("entrypoint_discovery"),
            ENTRYPOINT_DISCOVERY_FIELDS,
            "policy.scope.entrypoint_discovery",
            errors,
        )
        for field in (
            "runtime_entrypoints",
            "implementation_roots",
            "active_work_packet_states",
            "ignored_directory_names",
            "configuration_suffixes",
            "inert_data_or_document_suffixes",
        ):
            if not is_string_list(scope.get(field), nonempty=True):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.scope.{field} must be a nonempty unique string list",
                )
        for field in (
            "active_work_packet_directory",
            "python_suffix",
        ):
            if not isinstance(scope.get(field), str) or not scope[field]:
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.scope.{field} must be a nonempty string",
                )
        for field in ("reject_unknown_file_suffixes", "reject_symlinks"):
            if not isinstance(scope.get(field), bool):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.scope.{field} must be boolean",
                )

    ast_policy = policy["python_ast_policy"]
    exact_keys(ast_policy, PYTHON_AST_FIELDS, "policy.python_ast_policy", errors)
    if isinstance(ast_policy, dict):
        for field in (
            "allowed_import_roots",
            "forbidden_import_prefixes",
            "forbidden_call_prefixes",
            "forbidden_call_paths",
            "forbidden_call_leaf_names",
            "dynamic_import_call_paths",
        ):
            if not is_string_list(ast_policy.get(field), nonempty=True):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.python_ast_policy.{field} must be a nonempty unique string list",
                )
        if not is_string_list(ast_policy.get("allowed_dynamic_import_modules")):
            add_error(
                errors,
                "NLS-POLICY-SCHEMA",
                "allowed_dynamic_import_modules must be a unique string list",
            )
        for field in ("reject_nonliteral_dynamic_imports", "reject_star_imports"):
            if not isinstance(ast_policy.get(field), bool):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.python_ast_policy.{field} must be boolean",
                )

    endpoint_policy = policy["endpoint_policy"]
    exact_keys(endpoint_policy, ENDPOINT_FIELDS, "policy.endpoint_policy", errors)
    if isinstance(endpoint_policy, dict):
        endpoints = endpoint_policy.get("allowed_read_only_endpoints")
        if not isinstance(endpoints, list) or not endpoints:
            add_error(
                errors,
                "NLS-POLICY-SCHEMA",
                "allowed_read_only_endpoints must be a nonempty list",
            )
        else:
            for index, endpoint in enumerate(endpoints):
                exact_keys(
                    endpoint,
                    ENDPOINT_INSTANCE_FIELDS,
                    f"allowed_read_only_endpoints[{index}]",
                    errors,
                )
        for field in ("python_endpoint_name_fragments", "text_url_schemes"):
            if not is_string_list(endpoint_policy.get(field), nonempty=True):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.endpoint_policy.{field} must be a nonempty unique string list",
                )
        for field in (
            "require_https",
            "reject_userinfo",
            "reject_fragments",
            "reject_unlisted_endpoints",
            "reject_dynamic_python_endpoint_values",
        ):
            if not isinstance(endpoint_policy.get(field), bool):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.endpoint_policy.{field} must be boolean",
                )

    surface = policy["local_paper_only_surface"]
    exact_keys(surface, PAPER_SURFACE_FIELDS, "policy.local_paper_only_surface", errors)
    if isinstance(surface, dict):
        definitions = surface.get("definitions")
        if not isinstance(definitions, list) or not definitions:
            add_error(
                errors,
                "NLS-POLICY-SCHEMA",
                "local paper definitions must be a nonempty list",
            )
        else:
            for index, definition in enumerate(definitions):
                exact_keys(
                    definition,
                    PAPER_DEFINITION_FIELDS,
                    f"local paper definitions[{index}]",
                    errors,
                )
        for field in (
            "execution_capable_class_suffixes",
            "allowed_execution_capable_classes",
        ):
            if not is_string_list(surface.get(field), nonempty=True):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.local_paper_only_surface.{field} must be a nonempty unique string list",
                )
        if not isinstance(surface.get("reject_unlisted_public_methods"), bool):
            add_error(
                errors,
                "NLS-POLICY-SCHEMA",
                "reject_unlisted_public_methods must be boolean",
            )

    packet_policy = policy["work_packet_policy"]
    exact_keys(packet_policy, WORK_PACKET_POLICY_FIELDS, "policy.work_packet_policy", errors)
    if isinstance(packet_policy, dict):
        for field in (
            "required_fields",
            "all_state_values",
            "allowed_active_external_side_effects",
            "forbidden_active_side_effect_fragments",
        ):
            if not is_string_list(
                packet_policy.get(field),
                nonempty=(field != "allowed_active_external_side_effects"),
            ):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.work_packet_policy.{field} must be a unique string list",
                )
        for field in (
            "filename_suffix",
            "instance_schema_version",
        ):
            if not isinstance(packet_policy.get(field), str) or not packet_policy[field]:
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.work_packet_policy.{field} must be a nonempty string",
                )
        optional_fields = packet_policy.get(
            "state_specific_optional_fields"
        )
        if (
            not isinstance(optional_fields, dict)
            or optional_fields != {"superseded": ["superseded_by"]}
        ):
            add_error(
                errors,
                "NLS-POLICY-SCHEMA",
                "work-packet state-specific optional fields differ",
            )
        for field in (
            "reject_unlisted_active_external_side_effects",
            "reject_unexpected_directory_entries",
        ):
            if not isinstance(packet_policy.get(field), bool):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"policy.work_packet_policy.{field} must be boolean",
                )

    boundary = policy["claim_boundary"]
    exact_keys(boundary, CLAIM_BOUNDARY_FIELDS, "policy.claim_boundary", errors)
    if isinstance(boundary, dict):
        if not isinstance(boundary.get("proves"), str) or not boundary["proves"]:
            add_error(errors, "NLS-POLICY-SCHEMA", "claim_boundary.proves must be nonempty")
        for field in ("does_not_prove", "required_companion_controls"):
            if not is_string_list(boundary.get(field), nonempty=True):
                add_error(
                    errors,
                    "NLS-POLICY-SCHEMA",
                    f"claim_boundary.{field} must be a nonempty unique string list",
                )
    return len(errors) == start


def normalize_relative_path(
    value: Any,
    label: str,
    errors: list[dict[str, Any]],
) -> str | None:
    if not isinstance(value, str) or not value:
        add_error(errors, "NLS-SCOPE-PATH", f"{label} must be a nonempty string")
        return None
    if "\\" in value:
        add_error(errors, "NLS-SCOPE-PATH", f"{label} must use POSIX separators", path=value)
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or value.startswith("~"):
        add_error(errors, "NLS-SCOPE-PATH", f"{label} must be project-relative", path=value)
        return None
    parts = pure.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        add_error(errors, "NLS-SCOPE-PATH", f"{label} is not normalized", path=value)
        return None
    normalized = pure.as_posix()
    if normalized != value:
        add_error(errors, "NLS-SCOPE-PATH", f"{label} is not canonical", path=value)
        return None
    return normalized


def path_has_symlink(project_root: Path, relative: str) -> bool:
    current = project_root
    for part in PurePosixPath(relative).parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError:
            return False
        if stat.S_ISLNK(mode):
            return True
    return False


def resolve_declared_path(
    project_root: Path,
    value: Any,
    label: str,
    errors: list[dict[str, Any]],
    *,
    must_exist: bool = True,
    reject_symlinks: bool = True,
) -> tuple[str, Path] | None:
    relative = normalize_relative_path(value, label, errors)
    if relative is None:
        return None
    candidate = project_root.joinpath(*PurePosixPath(relative).parts)
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(project_root)
    except (OSError, ValueError) as exc:
        add_error(
            errors,
            "NLS-SCOPE-PATH",
            f"{label} escapes project root: {exc}",
            path=relative,
        )
        return None
    if reject_symlinks and path_has_symlink(project_root, relative):
        add_error(
            errors,
            "NLS-SCOPE-SYMLINK",
            f"{label} contains a symbolic link",
            path=relative,
        )
        return None
    if must_exist and not candidate.exists():
        add_error(
            errors,
            "NLS-SCOPE-MISSING",
            f"{label} does not exist",
            path=relative,
        )
        return None
    return relative, candidate


def path_is_inside(relative: str, root_relative: str) -> bool:
    path = PurePosixPath(relative)
    root = PurePosixPath(root_relative)
    return path == root or root in path.parents


def module_matches(name: str, prefixes: Iterable[str]) -> bool:
    lowered = name.casefold()
    return any(
        lowered == prefix.casefold()
        or lowered.startswith(prefix.casefold() + ".")
        for prefix in prefixes
    )


def module_name_for(relative: str) -> str:
    pure = PurePosixPath(relative)
    without_suffix = pure.with_suffix("")
    parts = list(without_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def has_main_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
            continue
        if not isinstance(test.ops[0], ast.Eq):
            continue
        left = test.left
        right = test.comparators[0]
        pairs = ((left, right), (right, left))
        for candidate_name, candidate_value in pairs:
            if (
                isinstance(candidate_name, ast.Name)
                and candidate_name.id == "__name__"
                and isinstance(candidate_value, ast.Constant)
                and candidate_value.value == "__main__"
            ):
                return True
    return False


def resolve_dotted(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        resolved = aliases.get(node.id, node.id)
        if resolved in {"eval", "exec", "compile", "__import__"}:
            return f"builtins.{resolved}"
        return resolved
    if isinstance(node, ast.Attribute):
        base = resolve_dotted(node.value, aliases)
        if base is None:
            return None
        return f"{base}.{node.attr}"
    if isinstance(node, ast.Call):
        target = resolve_call_target(node, aliases)
        return f"{target}()" if target else None
    return None


def resolve_call_target(node: ast.Call, aliases: dict[str, str]) -> str | None:
    if isinstance(node.func, ast.Call):
        getter = resolve_dotted(node.func.func, aliases)
        if getter in {"getattr", "builtins.getattr"} and len(node.func.args) >= 2:
            base = resolve_dotted(node.func.args[0], aliases)
            attribute = node.func.args[1]
            if base and isinstance(attribute, ast.Constant) and isinstance(attribute.value, str):
                return f"{base}.{attribute.value}"
    return resolve_dotted(node.func, aliases)


def assignment_target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [
            name
            for element in node.elts
            for name in assignment_target_names(element)
        ]
    return []


def build_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                bound = imported.asname or imported.name.split(".", 1)[0]
                aliases[bound] = imported.name if imported.asname else bound
        elif isinstance(node, ast.ImportFrom) and node.module:
            for imported in node.names:
                if imported.name == "*":
                    continue
                bound = imported.asname or imported.name
                aliases[bound] = f"{node.module}.{imported.name}"

    assignments = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Assign, ast.AnnAssign))
        ),
        key=lambda item: getattr(item, "lineno", 0),
    )
    for _ in range(4):
        changed = False
        for node in assignments:
            value = node.value
            if value is None:
                continue
            resolved = resolve_dotted(value, aliases)
            if resolved is None:
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for name in assignment_target_names(target):
                    if aliases.get(name) != resolved:
                        aliases[name] = resolved
                        changed = True
        if not changed:
            break
    return aliases


def endpoint_like_name(name: str, fragments: list[str]) -> bool:
    lowered = TOKEN_NORMALIZER.sub("_", name.casefold()).strip("_")
    return any(fragment.casefold() in lowered for fragment in fragments)


def literal_string_values(node: ast.AST) -> tuple[bool, list[str]]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return True, [node.value]
        return False, []
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        values: list[str] = []
        for element in node.elts:
            complete, nested = literal_string_values(element)
            if not complete:
                return False, []
            values.extend(nested)
        return True, values
    if isinstance(node, ast.Dict):
        values = []
        for value in node.values:
            complete, nested = literal_string_values(value)
            if not complete:
                return False, []
            values.extend(nested)
        return True, values
    return False, []


def trim_detected_url(value: str) -> str:
    return value.rstrip("),.;]}")


def validate_url(
    value: str,
    relative: str,
    line: int | None,
    endpoint_policy: dict[str, Any],
    errors: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> None:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        add_error(
            errors,
            "NLS-ENDPOINT-MALFORMED",
            f"malformed endpoint URL: {exc}",
            path=relative,
            line=line,
        )
        return
    if parsed.scheme.casefold() not in {
        item.casefold() for item in endpoint_policy["text_url_schemes"]
    }:
        return
    if endpoint_policy["require_https"] and parsed.scheme.casefold() != "https":
        add_error(
            errors,
            "NLS-ENDPOINT-UNAPPROVED",
            "endpoint is not HTTPS",
            path=relative,
            line=line,
        )
        return
    if endpoint_policy["reject_userinfo"] and (parsed.username or parsed.password):
        add_error(
            errors,
            "NLS-ENDPOINT-UNAPPROVED",
            "endpoint contains user information",
            path=relative,
            line=line,
        )
        return
    if endpoint_policy["reject_fragments"] and parsed.fragment:
        add_error(
            errors,
            "NLS-ENDPOINT-UNAPPROVED",
            "endpoint contains a fragment",
            path=relative,
            line=line,
        )
        return
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query_keys = [key for key, _ in query_pairs]
    matched: dict[str, Any] | None = None
    for allowed in endpoint_policy["allowed_read_only_endpoints"]:
        if (
            parsed.scheme.casefold() == allowed["scheme"].casefold()
            and (parsed.hostname or "").casefold() == allowed["host"].casefold()
            and port == allowed["port"]
            and parsed.path == allowed["path"]
            and set(query_keys).issubset(set(allowed["allowed_query_keys"]))
            and len(query_keys) == len(set(query_keys))
        ):
            matched = allowed
            break
    if matched is None and endpoint_policy["reject_unlisted_endpoints"]:
        add_error(
            errors,
            "NLS-ENDPOINT-UNAPPROVED",
            f"endpoint is outside the frozen read-only allowlist: {value}",
            path=relative,
            line=line,
        )
        return
    if matched is not None:
        observations.append(
            {
                "path": relative,
                "line": line,
                "url": value,
                "purpose": matched["purpose"],
            }
        )


def python_docstring_node_ids(tree: ast.AST) -> set[int]:
    result: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(
            node,
            (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue
        body = getattr(node, "body", [])
        if not body:
            continue
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            result.add(id(first.value))
    return result


def inspect_python(
    relative: str,
    path: Path,
    policy: dict[str, Any],
    errors: list[dict[str, Any]],
    endpoint_observations: list[dict[str, Any]],
) -> ast.AST | None:
    try:
        source = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as exc:
        add_error(
            errors,
            "NLS-PYTHON-READ",
            f"Python source is unreadable UTF-8: {exc}",
            path=relative,
        )
        return None
    try:
        tree = ast.parse(source, filename=relative)
    except (SyntaxError, ValueError) as exc:
        add_error(
            errors,
            "NLS-PYTHON-SYNTAX",
            f"Python source does not parse: {exc}",
            path=relative,
            line=getattr(exc, "lineno", None),
        )
        return None

    ast_policy = policy["python_ast_policy"]
    aliases = build_aliases(tree)
    allowed_roots = set(ast_policy["allowed_import_roots"])
    forbidden_imports = ast_policy["forbidden_import_prefixes"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                module = imported.name
                if module_matches(module, forbidden_imports):
                    add_error(
                        errors,
                        "NLS-PYTHON-FORBIDDEN-IMPORT",
                        f"forbidden broker/network/execution import {module!r}",
                        path=relative,
                        line=node.lineno,
                    )
                elif module.split(".", 1)[0] not in allowed_roots:
                    add_error(
                        errors,
                        "NLS-PYTHON-UNAPPROVED-IMPORT",
                        f"import root is outside the closed allowlist: {module!r}",
                        path=relative,
                        line=node.lineno,
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if any(imported.name == "*" for imported in node.names) and ast_policy["reject_star_imports"]:
                add_error(
                    errors,
                    "NLS-PYTHON-STAR-IMPORT",
                    "star imports are outside the closed AST surface",
                    path=relative,
                    line=node.lineno,
                )
            if module_matches(module, forbidden_imports):
                add_error(
                    errors,
                    "NLS-PYTHON-FORBIDDEN-IMPORT",
                    f"forbidden broker/network/execution import {module!r}",
                    path=relative,
                    line=node.lineno,
                )
            elif not module or module.split(".", 1)[0] not in allowed_roots:
                add_error(
                    errors,
                    "NLS-PYTHON-UNAPPROVED-IMPORT",
                    f"import root is outside the closed allowlist: {module!r}",
                    path=relative,
                    line=node.lineno,
                )

    dynamic_paths = set(ast_policy["dynamic_import_call_paths"])
    allowed_dynamic = set(ast_policy["allowed_dynamic_import_modules"])
    forbidden_paths = set(ast_policy["forbidden_call_paths"])
    forbidden_leaf_names = set(ast_policy["forbidden_call_leaf_names"])
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in forbidden_leaf_names:
            add_error(
                errors,
                "NLS-PYTHON-FORBIDDEN-DEFINITION",
                f"order-execution function definition is outside paper-only scope: {node.name}",
                path=relative,
                line=node.lineno,
            )
        if not isinstance(node, ast.Call):
            continue
        call_path = resolve_call_target(node, aliases)
        if call_path is None:
            continue
        if call_path in dynamic_paths:
            target: str | None = None
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                target = node.args[0].value
            if target is None and ast_policy["reject_nonliteral_dynamic_imports"]:
                add_error(
                    errors,
                    "NLS-PYTHON-DYNAMIC-IMPORT",
                    "nonliteral dynamic import is outside the closed module surface",
                    path=relative,
                    line=node.lineno,
                )
            elif target not in allowed_dynamic:
                add_error(
                    errors,
                    "NLS-PYTHON-DYNAMIC-IMPORT",
                    f"dynamic import is not allowed: {target!r}",
                    path=relative,
                    line=node.lineno,
                )
            continue
        leaf = call_path.rsplit(".", 1)[-1]
        if "()" in leaf:
            leaf = leaf.rsplit("()", 1)[-1].lstrip(".")
        if (
            module_matches(call_path, ast_policy["forbidden_call_prefixes"])
            or call_path in forbidden_paths
            or leaf in forbidden_leaf_names
        ):
            add_error(
                errors,
                "NLS-PYTHON-FORBIDDEN-CALL",
                f"broker/order/network execution call is outside paper-only scope: {call_path}",
                path=relative,
                line=node.lineno,
            )

    endpoint_policy = policy["endpoint_policy"]
    endpoint_fragments = endpoint_policy["python_endpoint_name_fragments"]
    # Only module-level assignments define this frozen program's endpoint
    # configuration.  Dataclass fields such as ``Evidence.url`` are data
    # schema, not executable endpoint selection.
    for node in getattr(tree, "body", []):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [name for target in targets for name in assignment_target_names(target)]
        endpoint_names = [name for name in names if endpoint_like_name(name, endpoint_fragments)]
        if not endpoint_names or node.value is None:
            continue
        complete, strings = literal_string_values(node.value)
        if not complete and endpoint_policy["reject_dynamic_python_endpoint_values"]:
            add_error(
                errors,
                "NLS-ENDPOINT-DYNAMIC",
                f"endpoint assignment is not a closed literal value: {endpoint_names}",
                path=relative,
                line=node.lineno,
            )
            continue
        for string_value in strings:
            matches = [trim_detected_url(match.group(0)) for match in URL_PATTERN.finditer(string_value)]
            if not matches:
                add_error(
                    errors,
                    "NLS-ENDPOINT-MALFORMED",
                    f"endpoint assignment contains a non-URL value: {string_value!r}",
                    path=relative,
                    line=node.lineno,
                )
            for url in matches:
                validate_url(
                    url,
                    relative,
                    node.lineno,
                    endpoint_policy,
                    errors,
                    endpoint_observations,
                )

    docstrings = python_docstring_node_ids(tree)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
        ):
            for match in URL_PATTERN.finditer(node.value):
                validate_url(
                    trim_detected_url(match.group(0)),
                    relative,
                    getattr(node, "lineno", None),
                    endpoint_policy,
                    errors,
                    endpoint_observations,
                )
    return tree


def walk_json_endpoints(
    value: Any,
    *,
    relative: str,
    context_is_endpoint: bool,
    endpoint_policy: dict[str, Any],
    errors: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> None:
    fragments = endpoint_policy["python_endpoint_name_fragments"]
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_context = context_is_endpoint or endpoint_like_name(key, fragments)
            walk_json_endpoints(
                nested,
                relative=relative,
                context_is_endpoint=nested_context,
                endpoint_policy=endpoint_policy,
                errors=errors,
                observations=observations,
            )
        return
    if isinstance(value, list):
        for nested in value:
            walk_json_endpoints(
                nested,
                relative=relative,
                context_is_endpoint=context_is_endpoint,
                endpoint_policy=endpoint_policy,
                errors=errors,
                observations=observations,
            )
        return
    if isinstance(value, str):
        matches = [trim_detected_url(match.group(0)) for match in URL_PATTERN.finditer(value)]
        if context_is_endpoint and not matches:
            add_error(
                errors,
                "NLS-ENDPOINT-MALFORMED",
                f"endpoint configuration contains a non-URL value: {value!r}",
                path=relative,
            )
        for url in matches:
            validate_url(
                url,
                relative,
                None,
                endpoint_policy,
                errors,
                observations,
            )
        return
    if context_is_endpoint:
        add_error(
            errors,
            "NLS-ENDPOINT-DYNAMIC",
            "endpoint configuration contains a non-string leaf",
            path=relative,
        )


def inspect_json_configuration(
    relative: str,
    path: Path,
    endpoint_policy: dict[str, Any],
    errors: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> None:
    value, _ = read_strict_json(
        path,
        "implementation JSON",
        errors,
        oracle_id="NLS-CONFIG-STRICT-JSON",
        relative_path=relative,
    )
    if value is not None:
        walk_json_endpoints(
            value,
            relative=relative,
            context_is_endpoint=False,
            endpoint_policy=endpoint_policy,
            errors=errors,
            observations=observations,
        )


def inspect_text_configuration(
    relative: str,
    path: Path,
    endpoint_policy: dict[str, Any],
    errors: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as exc:
        add_error(
            errors,
            "NLS-CONFIG-READ",
            f"configuration is unreadable UTF-8: {exc}",
            path=relative,
        )
        return
    for line_number, line in enumerate(text.splitlines(), 1):
        matches = [trim_detected_url(match.group(0)) for match in URL_PATTERN.finditer(line)]
        for url in matches:
            validate_url(
                url,
                relative,
                line_number,
                endpoint_policy,
                errors,
                observations,
            )
        assignment = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*[:=]\s*(.*?)\s*$", line)
        if assignment and endpoint_like_name(
            assignment.group(1), endpoint_policy["python_endpoint_name_fragments"]
        ):
            raw_value = assignment.group(2).strip().strip("\"'")
            if raw_value and not matches and not raw_value.startswith(("#", ";")):
                add_error(
                    errors,
                    "NLS-ENDPOINT-MALFORMED",
                    f"endpoint configuration is not an absolute allowlisted URL: {raw_value!r}",
                    path=relative,
                    line=line_number,
                )


def discover_implementation_files(
    project_root: Path,
    roots: list[tuple[str, Path]],
    policy: dict[str, Any],
    errors: list[dict[str, Any]],
) -> list[tuple[str, Path, str]]:
    scope = policy["scope"]
    ignored = set(scope["ignored_directory_names"])
    python_suffix = scope["python_suffix"]
    config_suffixes = set(scope["configuration_suffixes"])
    inert_suffixes = set(scope["inert_data_or_document_suffixes"])
    discovered: dict[str, tuple[Path, str]] = {}
    for root_relative, root_path in roots:
        for directory, directory_names, filenames in os.walk(
            root_path,
            topdown=True,
            followlinks=False,
        ):
            directory_path = Path(directory)
            kept_directories: list[str] = []
            for name in sorted(directory_names):
                candidate = directory_path / name
                relative = candidate.relative_to(project_root).as_posix()
                if name in ignored:
                    continue
                if candidate.is_symlink():
                    add_error(
                        errors,
                        "NLS-SCOPE-SYMLINK",
                        "implementation directory is a symbolic link",
                        path=relative,
                    )
                    continue
                kept_directories.append(name)
            directory_names[:] = kept_directories
            for filename in sorted(filenames):
                candidate = directory_path / filename
                relative = candidate.relative_to(project_root).as_posix()
                if candidate.is_symlink():
                    add_error(
                        errors,
                        "NLS-SCOPE-SYMLINK",
                        "implementation file is a symbolic link",
                        path=relative,
                    )
                    continue
                suffix = candidate.suffix.casefold()
                if candidate.name == ".env":
                    suffix = ".env"
                if suffix == python_suffix.casefold():
                    kind = "python"
                elif suffix in {item.casefold() for item in config_suffixes}:
                    kind = "json_config" if suffix == ".json" else "text_config"
                elif suffix in {item.casefold() for item in inert_suffixes}:
                    kind = "inert"
                else:
                    if scope["reject_unknown_file_suffixes"]:
                        add_error(
                            errors,
                            "NLS-SCOPE-UNKNOWN-FILE",
                            "implementation file type is outside the closed surface",
                            path=relative,
                        )
                    continue
                previous = discovered.get(relative)
                if previous is not None and previous[0] != candidate:
                    add_error(
                        errors,
                        "NLS-SCOPE-OVERLAP",
                        f"implementation roots discover the same path more than once: {root_relative}",
                        path=relative,
                    )
                discovered[relative] = (candidate, kind)
    return [
        (relative, candidate, kind)
        for relative, (candidate, kind) in sorted(discovered.items())
    ]


def validate_entrypoints(
    project_root: Path,
    policy: dict[str, Any],
    roots: list[tuple[str, Path]],
    trees: dict[str, ast.AST],
    errors: list[dict[str, Any]],
) -> list[str]:
    scope = policy["scope"]
    root_relatives = [relative for relative, _ in roots]
    declared: list[str] = []
    for index, value in enumerate(scope["runtime_entrypoints"]):
        resolved = resolve_declared_path(
            project_root,
            value,
            f"runtime_entrypoints[{index}]",
            errors,
            reject_symlinks=scope["reject_symlinks"],
        )
        if resolved is None:
            continue
        relative, candidate = resolved
        if not candidate.is_file():
            add_error(
                errors,
                "NLS-SCOPE-ENTRYPOINT",
                "declared runtime entrypoint is not a regular file",
                path=relative,
            )
            continue
        if candidate.suffix.casefold() != scope["python_suffix"].casefold():
            add_error(
                errors,
                "NLS-SCOPE-ENTRYPOINT",
                "declared runtime entrypoint is not Python",
                path=relative,
            )
        if not any(path_is_inside(relative, root) for root in root_relatives):
            add_error(
                errors,
                "NLS-SCOPE-ENTRYPOINT",
                "declared runtime entrypoint is outside implementation roots",
                path=relative,
            )
        tree = trees.get(relative)
        if tree is None:
            add_error(
                errors,
                "NLS-SCOPE-ENTRYPOINT",
                "declared runtime entrypoint did not produce a valid AST",
                path=relative,
            )
        elif scope["entrypoint_discovery"]["require_main_guard"] and not has_main_guard(tree):
            add_error(
                errors,
                "NLS-SCOPE-ENTRYPOINT",
                "declared runtime entrypoint lacks a structural __main__ guard",
                path=relative,
            )
        declared.append(relative)

    discovery = scope["entrypoint_discovery"]
    discovered: list[str] = []
    for root_relative, root_path in roots:
        iterator = root_path.rglob(f"{discovery['filename_prefix']}*{discovery['filename_suffix']}") if discovery["recursive"] else root_path.glob(f"{discovery['filename_prefix']}*{discovery['filename_suffix']}")
        for candidate in sorted(iterator):
            if candidate.is_file() and not candidate.is_symlink():
                discovered.append(candidate.relative_to(project_root).as_posix())
    if sorted(declared) != sorted(set(discovered)):
        add_error(
            errors,
            "NLS-SCOPE-ENTRYPOINT-SET",
            f"declared entrypoints differ from structural discovery; declared={sorted(declared)}, discovered={sorted(set(discovered))}",
        )
    return sorted(declared)


def validate_paper_surface(
    project_root: Path,
    policy: dict[str, Any],
    trees: dict[str, ast.AST],
    errors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    surface = policy["local_paper_only_surface"]
    observations: list[dict[str, Any]] = []
    for definition in surface["definitions"]:
        relative = definition["path"]
        tree = trees.get(relative)
        if tree is None:
            add_error(
                errors,
                "NLS-PAPER-SURFACE",
                "declared local paper surface file is missing or invalid",
                path=relative,
            )
            continue
        classes = [
            node
            for node in getattr(tree, "body", [])
            if isinstance(node, ast.ClassDef) and node.name == definition["class_name"]
        ]
        if len(classes) != 1:
            add_error(
                errors,
                "NLS-PAPER-SURFACE",
                f"expected exactly one class {definition['class_name']!r}, found {len(classes)}",
                path=relative,
            )
            continue
        class_node = classes[0]
        methods = sorted(
            node.name
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.name.startswith("_")
        )
        required = set(definition["required_public_methods"])
        allowed = set(definition["allowed_public_methods"])
        missing = sorted(required - set(methods))
        unexpected = sorted(set(methods) - allowed)
        if missing:
            add_error(
                errors,
                "NLS-PAPER-SURFACE",
                f"local paper class is missing required public methods: {missing}",
                path=relative,
                line=class_node.lineno,
            )
        if unexpected and surface["reject_unlisted_public_methods"]:
            add_error(
                errors,
                "NLS-PAPER-SURFACE",
                f"local paper class exposes unlisted public methods: {unexpected}",
                path=relative,
                line=class_node.lineno,
            )
        observations.append(
            {
                "qualified_class": f"{module_name_for(relative)}.{definition['class_name']}",
                "public_methods": methods,
            }
        )

    allowed_classes = set(surface["allowed_execution_capable_classes"])
    suffixes = tuple(surface["execution_capable_class_suffixes"])
    for relative, tree in sorted(trees.items()):
        module = module_name_for(relative)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or not node.name.endswith(suffixes):
                continue
            qualified = f"{module}.{node.name}"
            if qualified not in allowed_classes:
                add_error(
                    errors,
                    "NLS-PAPER-EXECUTION-CLASS",
                    f"execution-capable class is outside the local paper allow surface: {qualified}",
                    path=relative,
                    line=node.lineno,
                )
    observed_classes = {item["qualified_class"] for item in observations}
    declared_definition_classes = {
        f"{module_name_for(item['path'])}.{item['class_name']}"
        for item in surface["definitions"]
    }
    if observed_classes != declared_definition_classes:
        add_error(
            errors,
            "NLS-PAPER-SURFACE",
            "observed local paper definitions differ from the frozen declaration",
        )
    return sorted(observations, key=lambda item: item["qualified_class"])


def normalize_effect(value: str) -> str:
    return TOKEN_NORMALIZER.sub("_", value.casefold()).strip("_")


def validate_work_packets(
    project_root: Path,
    policy: dict[str, Any],
    errors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scope = policy["scope"]
    packet_policy = policy["work_packet_policy"]
    resolved = resolve_declared_path(
        project_root,
        scope["active_work_packet_directory"],
        "active_work_packet_directory",
        errors,
        reject_symlinks=scope["reject_symlinks"],
    )
    if resolved is None:
        return []
    directory_relative, directory = resolved
    if not directory.is_dir():
        add_error(
            errors,
            "NLS-PACKET-DIRECTORY",
            "active work-packet path is not a directory",
            path=directory_relative,
        )
        return []
    observations: list[dict[str, Any]] = []
    suffix = packet_policy["filename_suffix"]
    for entry in sorted(directory.iterdir(), key=lambda item: item.name):
        relative = entry.relative_to(project_root).as_posix()
        if entry.is_symlink():
            add_error(
                errors,
                "NLS-PACKET-SYMLINK",
                "work-packet entry is a symbolic link",
                path=relative,
            )
            continue
        if not entry.is_file() or not entry.name.endswith(suffix):
            if packet_policy["reject_unexpected_directory_entries"]:
                add_error(
                    errors,
                    "NLS-PACKET-UNEXPECTED-ENTRY",
                    "unexpected entry in authoritative packet directory",
                    path=relative,
                )
            continue
        packet, _ = read_strict_json(
            entry,
            "work packet",
            errors,
            oracle_id="NLS-PACKET-STRICT-JSON",
            relative_path=relative,
        )
        if packet is None:
            continue
        expected_fields = set(packet_policy["required_fields"])
        state = packet.get("state")
        optional_by_state = packet_policy[
            "state_specific_optional_fields"
        ]
        optional_fields = set(optional_by_state.get(state, []))
        allowed_fields = expected_fields | optional_fields
        if set(packet) != allowed_fields:
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                f"work-packet fields differ; missing={sorted(allowed_fields - set(packet))}, extra={sorted(set(packet) - allowed_fields)}",
                path=relative,
            )
            continue
        packet_id = packet["packet_id"]
        if not isinstance(packet_id, str) or PACKET_ID_PATTERN.fullmatch(packet_id) is None:
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                "work packet has an invalid packet_id",
                path=relative,
            )
            packet_id = entry.name
        if packet["schema_version"] != packet_policy["instance_schema_version"]:
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                "work packet has an unsupported schema_version",
                path=relative,
            )
        if state not in packet_policy["all_state_values"]:
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                "work packet has an invalid state",
                path=relative,
            )
            continue
        if state == "superseded" and (
            not isinstance(packet.get("superseded_by"), str)
            or not packet["superseded_by"]
        ):
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                "superseded work packet has an invalid superseded_by",
                path=relative,
            )
            continue
        effects = packet["external_side_effects"]
        if not is_string_list(effects):
            add_error(
                errors,
                "NLS-PACKET-SCHEMA",
                "external_side_effects must be a unique string list",
                path=relative,
            )
            continue
        active = state in scope["active_work_packet_states"]
        if active:
            allowed = set(packet_policy["allowed_active_external_side_effects"])
            forbidden_fragments = packet_policy["forbidden_active_side_effect_fragments"]
            for effect in effects:
                normalized = normalize_effect(effect)
                matched = [fragment for fragment in forbidden_fragments if fragment in normalized]
                if matched:
                    add_error(
                        errors,
                        "NLS-PACKET-LIVE-SIDE-EFFECT",
                        f"active work packet declares a live/real-money/order side effect: {effect!r}",
                        path=relative,
                    )
                if (
                    packet_policy["reject_unlisted_active_external_side_effects"]
                    and effect not in allowed
                ):
                    add_error(
                        errors,
                        "NLS-PACKET-UNAPPROVED-SIDE-EFFECT",
                        f"active work packet declares an unapproved external side effect: {effect!r}",
                        path=relative,
                    )
        observations.append(
            {
                "packet_id": packet_id,
                "state": state,
                "active_for_no_live_check": active,
                "external_side_effects": effects,
            }
        )
    return sorted(observations, key=lambda item: item["packet_id"])


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    encoded: dict[str, dict[str, Any]] = {}
    for record in records:
        key = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        encoded[key] = record
    return [encoded[key] for key in sorted(encoded)]


def verify(project_root: Path, policy_path: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        return {
            "status": "fail",
            "policy_id": None,
            "policy_canonical_sha256": None,
            "declared_runtime_entrypoints": [],
            "implementation_roots": [],
            "paper_surface": [],
            "endpoint_observations": [],
            "work_packet_observations": [],
            "counts": {},
            "errors": [
                {
                    "oracle_id": "NLS-PROJECT-ROOT",
                    "message": f"project root is unavailable: {exc}",
                }
            ],
            "claim_boundary": {},
        }
    if not root.is_dir():
        add_error(errors, "NLS-PROJECT-ROOT", "project root is not a directory")

    candidate_policy = policy_path if policy_path.is_absolute() else root / policy_path
    try:
        candidate_policy.resolve(strict=False).relative_to(root)
    except ValueError:
        add_error(
            errors,
            "NLS-POLICY-PATH",
            "policy path must stay inside project root",
        )
        policy = None
    else:
        policy, _ = read_strict_json(
            candidate_policy,
            "no-live policy",
            errors,
            oracle_id="NLS-POLICY-STRICT-JSON",
            relative_path=(
                candidate_policy.relative_to(root).as_posix()
                if candidate_policy.is_relative_to(root)
                else str(candidate_policy)
            ),
        )
    if policy is None:
        return {
            "status": "fail",
            "policy_id": None,
            "policy_canonical_sha256": None,
            "declared_runtime_entrypoints": [],
            "implementation_roots": [],
            "paper_surface": [],
            "endpoint_observations": [],
            "work_packet_observations": [],
            "counts": {},
            "errors": deduplicate_records(errors),
            "claim_boundary": {},
        }
    policy_digest = canonical_json_sha256(policy)
    schema_valid = validate_policy_schema(policy, errors)
    if policy_digest != EXPECTED_POLICY_CANONICAL_SHA256:
        add_error(
            errors,
            "NLS-POLICY-FROZEN-DIGEST",
            f"policy canonical digest differs; expected {EXPECTED_POLICY_CANONICAL_SHA256}, observed {policy_digest}",
        )
    if not schema_valid or policy_digest != EXPECTED_POLICY_CANONICAL_SHA256:
        return {
            "status": "fail",
            "policy_id": policy.get("policy_id"),
            "policy_canonical_sha256": policy_digest,
            "declared_runtime_entrypoints": [],
            "implementation_roots": [],
            "paper_surface": [],
            "endpoint_observations": [],
            "work_packet_observations": [],
            "counts": {},
            "errors": deduplicate_records(errors),
            "claim_boundary": policy.get("claim_boundary", {}),
        }

    scope = policy["scope"]
    roots: list[tuple[str, Path]] = []
    for index, value in enumerate(scope["implementation_roots"]):
        resolved = resolve_declared_path(
            root,
            value,
            f"implementation_roots[{index}]",
            errors,
            reject_symlinks=scope["reject_symlinks"],
        )
        if resolved is None:
            continue
        relative, candidate = resolved
        if not candidate.is_dir():
            add_error(
                errors,
                "NLS-SCOPE-ROOT",
                "declared implementation root is not a directory",
                path=relative,
            )
            continue
        roots.append((relative, candidate))

    files = discover_implementation_files(root, roots, policy, errors)
    trees: dict[str, ast.AST] = {}
    endpoint_observations: list[dict[str, Any]] = []
    counts = {
        "implementation_file_count": len(files),
        "python_file_count": 0,
        "configuration_file_count": 0,
        "inert_file_count": 0,
        "endpoint_observation_count": 0,
        "active_work_packet_count": 0,
    }
    for relative, path, kind in files:
        if kind == "python":
            counts["python_file_count"] += 1
            tree = inspect_python(
                relative,
                path,
                policy,
                errors,
                endpoint_observations,
            )
            if tree is not None:
                trees[relative] = tree
        elif kind == "json_config":
            counts["configuration_file_count"] += 1
            inspect_json_configuration(
                relative,
                path,
                policy["endpoint_policy"],
                errors,
                endpoint_observations,
            )
        elif kind == "text_config":
            counts["configuration_file_count"] += 1
            inspect_text_configuration(
                relative,
                path,
                policy["endpoint_policy"],
                errors,
                endpoint_observations,
            )
        else:
            counts["inert_file_count"] += 1

    entrypoints = validate_entrypoints(root, policy, roots, trees, errors)
    paper_surface = validate_paper_surface(root, policy, trees, errors)
    packet_observations = validate_work_packets(root, policy, errors)
    endpoint_observations = deduplicate_records(endpoint_observations)
    counts["endpoint_observation_count"] = len(endpoint_observations)
    counts["active_work_packet_count"] = sum(
        1 for item in packet_observations if item["active_for_no_live_check"]
    )
    errors = deduplicate_records(errors)
    return {
        "status": "pass" if not errors else "fail",
        "policy_id": policy["policy_id"],
        "policy_canonical_sha256": policy_digest,
        "declared_runtime_entrypoints": entrypoints,
        "implementation_roots": [relative for relative, _ in roots],
        "paper_surface": paper_surface,
        "endpoint_observations": endpoint_observations,
        "work_packet_observations": packet_observations,
        "counts": counts,
        "errors": errors,
        "claim_boundary": policy["claim_boundary"],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=SCRIPT_PROJECT_ROOT,
        help="Project root containing the frozen local Paper V1 scope.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_RELATIVE,
        help="Policy path inside project root.",
    )
    parser.add_argument("--json", action="store_true", help="Emit one machine JSON object.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = verify(args.project_root, args.policy)
    except Exception as exc:  # pragma: no cover - final fail-closed boundary
        result = {
            "status": "fail",
            "policy_id": None,
            "policy_canonical_sha256": None,
            "declared_runtime_entrypoints": [],
            "implementation_roots": [],
            "paper_surface": [],
            "endpoint_observations": [],
            "work_packet_observations": [],
            "counts": {},
            "errors": [
                {
                    "oracle_id": "NLS-INTERNAL-ERROR",
                    "message": f"internal verifier error: {type(exc).__name__}: {exc}",
                }
            ],
            "claim_boundary": {},
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True))
    elif result["status"] == "pass":
        print(
            "no-live scope verification: PASS "
            f"({result['counts']['python_file_count']} Python files, "
            f"{result['counts']['active_work_packet_count']} active work packets)"
        )
        for limitation in result["claim_boundary"]["does_not_prove"]:
            print(f"LIMITATION: {limitation}")
    else:
        print("no-live scope verification: FAIL")
        for error in result["errors"]:
            location = error.get("path", "")
            if error.get("line") is not None:
                location = f"{location}:{error['line']}"
            print(f"ERROR {error['oracle_id']} {location}: {error['message']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
