#!/usr/bin/env python3
"""Derive and verify the IMP-04 / SEC-06 dependency boundary."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shlex
import stat
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit


SCRIPT_PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
DEFAULT_MANIFEST_RELATIVE = Path("governance/DEPENDENCY_BOUNDARY_V1.json")

EXPECTED_PYTHON_ROOTS = [
    {"path": "prototype", "role": "runtime"},
    {"path": "scripts", "role": "governance"},
    {"path": "governance_tests", "role": "governance_tests"},
    {
        "path": "research/evidence/r8/RS-04/probe",
        "role": "research_tooling",
    },
]
EXPECTED_EXCLUDED_DIRECTORIES = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
]
EXPECTED_RULES = {
    "stdlib_only_python_roles": ["runtime"],
    "unregistered_dependency_outcome": "blocked",
    "nonliteral_dynamic_import_outcome": "blocked",
    "floating_install_outcome": "blocked",
    "remote_installer_outcome": "blocked",
    "new_python_root_outcome": "blocked",
    "unknown_telemetry_outcome": "blocked",
    "external_action_revision": "full_40_lowercase_hex_commit_or_docker_sha256",
    "manifest_dependency_required_fields": [
        "name",
        "version_or_commit",
        "sha256_or_lock_hash",
        "canonical_source",
        "license",
        "necessity",
        "permissions_or_telemetry",
        "removal_plan",
    ],
}
EXPECTED_CLAIM_BOUNDARY = {
    "proves": (
        "For the declared repository bytes, the verifier derives Python imports, "
        "literal dynamic imports, statically visible installer commands, supported "
        "dependency configuration entries, and external GitHub Action revisions; "
        "it rejects unregistered or floating dependencies and unknown declared telemetry."
    ),
    "does_not_prove": [
        "absence of vulnerabilities or telemetry in the operating system, Python runtime, standard library, GitHub runner, external Actions, upstream binaries, or service providers",
        "behavior hidden behind runtime-generated non-shell process arguments",
        "correctness or safety of a dependency merely because its identity and review fields are registered",
        "transitive artifacts selected by an installer unless a future enforced lock or hash installation path binds them",
    ],
    "current_expected_observation": (
        "runtime and governance Python third-party import sets are empty; the "
        "separately reported CI tool set contains only registered ruff"
    ),
}

TOP_LEVEL_FIELDS = {
    "schema_version",
    "boundary_id",
    "failure_ids",
    "status",
    "scope",
    "rules",
    "third_party_dependencies",
    "claim_boundary",
}
SCOPE_FIELDS = {
    "python_roots",
    "project_config_search_root",
    "project_config_excluded_directories",
    "repository_workflow_root",
}
ROOT_FIELDS = {"path", "role"}
DEPENDENCY_FIELDS = {
    "name",
    "kind",
    "import_names",
    "allowed_contexts",
    "version_or_commit",
    "sha256_or_lock_hash",
    "canonical_source",
    "license",
    "necessity",
    "permissions_or_telemetry",
    "removal_plan",
}
HASH_FIELDS = {"kind", "value", "artifact"}
TELEMETRY_FIELDS = {
    "status",
    "network",
    "filesystem",
    "process",
    "telemetry",
    "evidence_basis",
}
CLAIM_FIELDS = {"proves", "does_not_prove", "current_expected_observation"}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ACTION_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
EXACT_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses\s*:\s*(?:\"([^\"]+)\"|'([^']+)'|([^#\s]+))")
RUN_RE = re.compile(r"^(\s*)(?:-\s*)?run\s*:\s*(.*)$")
DEPENDENCY_FILENAMES = {
    "Pipfile.lock",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pyproject.toml",
    "uv.lock",
    "yarn.lock",
}
CONTROL_TOKENS = {"&&", "||", ";", "|"}


class DuplicateKeyError(ValueError):
    """Raised when strict JSON contains a duplicate key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


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


def read_strict_json(
    path: Path,
    errors: list[dict[str, Any]],
    *,
    oracle_id: str,
    label: str,
) -> dict[str, Any] | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        add_error(errors, oracle_id, f"{label} is unreadable: {exc}")
        return None
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        add_error(errors, oracle_id, f"{label} is not strict JSON: {exc}")
        return None
    if not isinstance(value, dict):
        add_error(errors, oracle_id, f"{label} top level must be an object")
        return None
    return value


def exact_fields(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[dict[str, Any]],
) -> bool:
    if not isinstance(value, dict):
        add_error(errors, "DEP-MANIFEST-SCHEMA", f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        add_error(
            errors,
            "DEP-MANIFEST-SCHEMA",
            f"{label} fields differ; missing={sorted(expected - actual)}, extra={sorted(actual - expected)}",
        )
        return False
    return True


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_strings(value: Any, *, nonempty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def normalized_relative(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or value.startswith("~"):
        return None
    if value == ".":
        return value
    if any(part in {"", ".", ".."} for part in pure.parts):
        return None
    if pure.as_posix() != value:
        return None
    return value


def validate_manifest(
    manifest: dict[str, Any], errors: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    if not exact_fields(manifest, TOP_LEVEL_FIELDS, "manifest", errors):
        return {}
    if manifest.get("schema_version") != 1:
        add_error(errors, "DEP-MANIFEST-SCHEMA", "schema_version must be 1")
    if manifest.get("boundary_id") != "IMP-04-SEC-06-DEPENDENCY-BOUNDARY-V1":
        add_error(errors, "DEP-MANIFEST-SCHEMA", "boundary_id differs")
    if manifest.get("failure_ids") != ["IMP-04", "SEC-06"]:
        add_error(errors, "DEP-MANIFEST-SCHEMA", "failure_ids differ")
    if manifest.get("status") != "active_stdlib_runtime_boundary":
        add_error(errors, "DEP-MANIFEST-SCHEMA", "status differs")

    scope = manifest.get("scope")
    if exact_fields(scope, SCOPE_FIELDS, "manifest.scope", errors):
        assert isinstance(scope, dict)
        roots = scope.get("python_roots")
        if roots != EXPECTED_PYTHON_ROOTS:
            add_error(
                errors,
                "DEP-SCOPE-ROOTS",
                "declared Python roots or roles differ from the frozen complete set",
            )
        elif isinstance(roots, list):
            for index, root in enumerate(roots):
                exact_fields(root, ROOT_FIELDS, f"python_roots[{index}]", errors)
        if scope.get("project_config_search_root") != ".":
            add_error(
                errors,
                "DEP-SCOPE-CONFIG",
                "project_config_search_root must be project root '.'",
            )
        if (
            scope.get("project_config_excluded_directories")
            != EXPECTED_EXCLUDED_DIRECTORIES
        ):
            add_error(
                errors,
                "DEP-SCOPE-CONFIG",
                "config exclusions differ from the frozen cache-only set",
            )
        if scope.get("repository_workflow_root") != ".github/workflows":
            add_error(
                errors,
                "DEP-SCOPE-WORKFLOW",
                "repository_workflow_root differs",
            )

    if manifest.get("rules") != EXPECTED_RULES:
        add_error(errors, "DEP-MANIFEST-RULES", "rules differ from fail-closed policy")
    boundary = manifest.get("claim_boundary")
    if not exact_fields(boundary, CLAIM_FIELDS, "manifest.claim_boundary", errors):
        pass
    elif boundary != EXPECTED_CLAIM_BOUNDARY:
        add_error(
            errors,
            "DEP-CLAIM-BOUNDARY",
            "claim boundary differs or overstates the static proof",
        )

    dependencies = manifest.get("third_party_dependencies")
    if not isinstance(dependencies, list):
        add_error(
            errors,
            "DEP-MANIFEST-SCHEMA",
            "third_party_dependencies must be a list",
        )
        return {}
    by_name: dict[str, dict[str, Any]] = {}
    import_owners: dict[str, str] = {}
    for index, dependency in enumerate(dependencies):
        label = f"third_party_dependencies[{index}]"
        if not exact_fields(dependency, DEPENDENCY_FIELDS, label, errors):
            continue
        assert isinstance(dependency, dict)
        name = dependency.get("name")
        if not isinstance(name, str) or not PACKAGE_NAME_RE.fullmatch(name):
            add_error(errors, "DEP-MANIFEST-IDENTITY", f"{label}.name is invalid")
            continue
        normalized_name = normalize_package_name(name)
        if normalized_name in by_name:
            add_error(
                errors,
                "DEP-MANIFEST-IDENTITY",
                f"duplicate dependency name {normalized_name!r}",
            )
        by_name[normalized_name] = dependency
        if dependency.get("kind") not in {
            "runtime",
            "governance",
            "test",
            "research_tool",
            "ci_tool",
        }:
            add_error(errors, "DEP-MANIFEST-SCHEMA", f"{label}.kind is invalid")
        if not unique_strings(dependency.get("import_names"), nonempty=False):
            add_error(
                errors,
                "DEP-MANIFEST-SCHEMA",
                f"{label}.import_names must be a unique string list",
            )
        else:
            for import_name in dependency["import_names"]:
                if not PACKAGE_NAME_RE.fullmatch(import_name):
                    add_error(
                        errors,
                        "DEP-MANIFEST-IDENTITY",
                        f"{label}.import_names contains an invalid name",
                    )
                    continue
                normalized_import = normalize_package_name(import_name)
                prior = import_owners.get(normalized_import)
                if prior is not None and prior != normalized_name:
                    add_error(
                        errors,
                        "DEP-MANIFEST-IDENTITY",
                        f"import name {normalized_import!r} has multiple owners",
                    )
                import_owners[normalized_import] = normalized_name
        if not unique_strings(dependency.get("allowed_contexts")):
            add_error(
                errors,
                "DEP-MANIFEST-SCHEMA",
                f"{label}.allowed_contexts must be a nonempty unique string list",
            )
        version = dependency.get("version_or_commit")
        if not nonempty_string(version) or is_floating_version(str(version)):
            add_error(
                errors,
                "DEP-MANIFEST-FLOATING",
                f"{label}.version_or_commit is absent or floating",
            )
        integrity = dependency.get("sha256_or_lock_hash")
        if exact_fields(integrity, HASH_FIELDS, f"{label}.sha256_or_lock_hash", errors):
            assert isinstance(integrity, dict)
            if integrity.get("kind") not in {"artifact_sha256", "lock_sha256"}:
                add_error(
                    errors,
                    "DEP-MANIFEST-HASH",
                    f"{label}.sha256_or_lock_hash.kind is invalid",
                )
            if not isinstance(integrity.get("value"), str) or not SHA256_RE.fullmatch(
                integrity["value"]
            ):
                add_error(
                    errors,
                    "DEP-MANIFEST-HASH",
                    f"{label}.sha256_or_lock_hash.value must be lowercase SHA-256",
                )
            if not nonempty_string(integrity.get("artifact")):
                add_error(
                    errors,
                    "DEP-MANIFEST-HASH",
                    f"{label}.sha256_or_lock_hash.artifact must be nonempty",
                )
        source = dependency.get("canonical_source")
        if not nonempty_string(source):
            add_error(
                errors, "DEP-MANIFEST-SOURCE", f"{label}.canonical_source is missing"
            )
        else:
            parsed = urlsplit(source)
            if parsed.scheme != "https" or not parsed.netloc or parsed.fragment:
                add_error(
                    errors,
                    "DEP-MANIFEST-SOURCE",
                    f"{label}.canonical_source must be a canonical HTTPS URL without fragment",
                )
        for field in ("license", "necessity", "removal_plan"):
            if not nonempty_string(dependency.get(field)):
                add_error(
                    errors,
                    f"DEP-MANIFEST-{field.replace('_', '-').upper()}",
                    f"{label}.{field} must be nonempty",
                )
        telemetry = dependency.get("permissions_or_telemetry")
        if exact_fields(
            telemetry, TELEMETRY_FIELDS, f"{label}.permissions_or_telemetry", errors
        ):
            assert isinstance(telemetry, dict)
            for field in TELEMETRY_FIELDS:
                if not nonempty_string(telemetry.get(field)):
                    add_error(
                        errors,
                        "DEP-MANIFEST-TELEMETRY",
                        f"{label}.permissions_or_telemetry.{field} must be nonempty",
                    )
            status = str(telemetry.get("status", "")).casefold()
            if status not in {
                "project_configuration_reviewed",
                "telemetry_present_and_explicitly_bounded",
                "no_telemetry_by_verified_source",
            }:
                add_error(
                    errors,
                    "DEP-TELEMETRY-UNKNOWN",
                    f"{label} telemetry status is unknown or unreviewed",
                )
    return by_name


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).casefold()


def is_floating_version(value: str) -> bool:
    lowered = value.strip().casefold()
    return (
        not lowered
        or lowered in {"latest", "main", "master", "head", "stable", "*"}
        or any(token in lowered for token in (">", "<", "~=", "^", "*", ","))
    )


def path_has_symlink(base: Path, relative: str) -> bool:
    current = base
    if relative == ".":
        return current.is_symlink()
    for part in PurePosixPath(relative).parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError:
            return False
        if stat.S_ISLNK(mode):
            return True
    return False


def safe_declared_directory(
    base: Path,
    relative: str,
    label: str,
    errors: list[dict[str, Any]],
) -> Path | None:
    normalized = normalized_relative(relative)
    if normalized is None:
        add_error(errors, "DEP-SCOPE-PATH", f"{label} is not normalized", path=relative)
        return None
    candidate = (
        base if normalized == "." else base.joinpath(*PurePosixPath(normalized).parts)
    )
    try:
        candidate.resolve().relative_to(base.resolve())
    except (OSError, ValueError) as exc:
        add_error(
            errors,
            "DEP-SCOPE-PATH",
            f"{label} escapes its base: {exc}",
            path=relative,
        )
        return None
    if path_has_symlink(base, normalized):
        add_error(
            errors, "DEP-SCOPE-SYMLINK", f"{label} contains a symlink", path=relative
        )
        return None
    if not candidate.is_dir():
        add_error(
            errors, "DEP-SCOPE-MISSING", f"{label} is not a directory", path=relative
        )
        return None
    return candidate


def is_under(relative: str, root: str) -> bool:
    path = PurePosixPath(relative)
    base = PurePosixPath(root)
    return path == base or base in path.parents


def collect_python_files(
    project_root: Path,
    errors: list[dict[str, Any]],
) -> list[tuple[str, str, Path]]:
    role_by_root = {item["path"]: item["role"] for item in EXPECTED_PYTHON_ROOTS}
    files: list[tuple[str, str, Path]] = []
    declared_paths: set[str] = set()
    for root_relative, role in role_by_root.items():
        root = safe_declared_directory(
            project_root,
            root_relative,
            f"Python root {root_relative}",
            errors,
        )
        if root is None:
            continue
        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(project_root).as_posix()
            if path.is_symlink():
                add_error(
                    errors,
                    "DEP-SCOPE-SYMLINK",
                    "Python source is a symlink",
                    path=relative,
                )
                continue
            if not path.is_file():
                continue
            declared_paths.add(relative)
            files.append((relative, role, path))

    excluded = set(EXPECTED_EXCLUDED_DIRECTORIES)
    for path in sorted(project_root.rglob("*.py")):
        relative = path.relative_to(project_root).as_posix()
        if any(part in excluded for part in PurePosixPath(relative).parts):
            continue
        if relative not in declared_paths:
            add_error(
                errors,
                "DEP-UNDECLARED-PYTHON-ROOT",
                "Python source exists outside every declared scan root",
                path=relative,
            )
    return files


def local_module_roots(project_root: Path) -> set[str]:
    roots: set[str] = set()
    for child in project_root.iterdir():
        if child.is_symlink():
            continue
        if child.is_file() and child.suffix == ".py":
            roots.add(child.stem)
        elif child.is_dir() and any(child.rglob("*.py")):
            roots.add(child.name)
    return roots


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
                aliases[imported.asname or imported.name] = (
                    f"{node.module}.{imported.name}"
                )
    return aliases


def resolve_dotted(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        if node.id == "__import__":
            return "builtins.__import__"
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = resolve_dotted(node.value, aliases)
        return f"{base}.{node.attr}" if base else None
    return None


def constant_bindings(tree: ast.AST) -> dict[str, ast.AST]:
    result: dict[str, ast.AST] = {}
    for node in getattr(tree, "body", []):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            result[node.targets[0].id] = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value
        ):
            result[node.target.id] = node.value
    return result


def command_tokens(
    node: ast.AST,
    bindings: dict[str, ast.AST],
    *,
    depth: int = 0,
) -> tuple[list[str], bool]:
    if depth > 5:
        return ["<dynamic>"], False
    if isinstance(node, ast.Name) and node.id in bindings:
        return command_tokens(bindings[node.id], bindings, depth=depth + 1)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return shlex.split(node.value), True
        except ValueError:
            return [node.value], False
    if isinstance(node, (ast.List, ast.Tuple)):
        values: list[str] = []
        complete = True
        for item in node.elts:
            if isinstance(item, ast.Starred):
                values.append("<dynamic>")
                complete = False
                continue
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                values.append(item.value)
            else:
                nested, nested_complete = command_tokens(
                    item, bindings, depth=depth + 1
                )
                if nested_complete and len(nested) == 1:
                    values.extend(nested)
                else:
                    values.append("<dynamic>")
                    complete = False
        return values, complete
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, left_complete = command_tokens(node.left, bindings, depth=depth + 1)
        right, right_complete = command_tokens(node.right, bindings, depth=depth + 1)
        return left + right, left_complete and right_complete
    return ["<dynamic>"], False


def classify_module(
    module: str,
    local_roots: set[str],
) -> str:
    if module.startswith("."):
        return "project_local"
    root = module.split(".", 1)[0]
    if (
        root in sys.stdlib_module_names
        or root in sys.builtin_module_names
        or root == "__future__"
    ):
        return "stdlib"
    if root in local_roots:
        return "project_local"
    return "third_party"


def inspect_install_tokens(
    tokens: list[str],
    *,
    context: str,
    path: str,
    line: int | None,
    installs: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    lowered = [token.casefold() for token in tokens]
    for index, token in enumerate(lowered):
        executable = PurePosixPath(token).name
        if executable in {"curl", "wget"}:
            installs.append(
                {
                    "name": executable,
                    "version": None,
                    "context": context,
                    "path": path,
                    "line": line,
                    "kind": "remote_installer",
                }
            )
            add_error(
                errors,
                "DEP-REMOTE-INSTALLER",
                f"{executable} download/install command is outside the reviewed package path",
                path=path,
                line=line,
            )
            return

        manager: str | None = None
        install_index: int | None = None
        if executable in {"pip", "pip3"} and index + 1 < len(tokens):
            if lowered[index + 1] == "install":
                manager, install_index = "pip", index + 1
        elif token == "-m" and index + 2 < len(tokens):
            if lowered[index + 1] == "pip" and lowered[index + 2] == "install":
                manager, install_index = "pip", index + 2
        elif executable == "npm" and index + 1 < len(tokens):
            if lowered[index + 1] in {"install", "i", "add"}:
                manager, install_index = "npm", index + 1
        elif executable == "brew" and index + 1 < len(tokens):
            if lowered[index + 1] == "install":
                manager, install_index = "brew", index + 1
        if manager is None or install_index is None:
            continue

        specs: list[str] = []
        skip_next = False
        options_with_values = {
            "-c",
            "--constraint",
            "-f",
            "--find-links",
            "-i",
            "--index-url",
            "--extra-index-url",
            "--trusted-host",
            "-r",
            "--requirement",
            "--hash",
        }
        for raw in tokens[install_index + 1 :]:
            if raw in CONTROL_TOKENS:
                break
            if skip_next:
                skip_next = False
                continue
            if raw in options_with_values:
                skip_next = True
                continue
            if raw.startswith("-") or raw == "<dynamic>":
                continue
            specs.append(raw)
        if not specs:
            installs.append(
                {
                    "name": None,
                    "version": None,
                    "context": context,
                    "path": path,
                    "line": line,
                    "kind": f"{manager}_install",
                }
            )
            return
        for spec in specs:
            name, version = parse_install_spec(manager, spec)
            installs.append(
                {
                    "name": name,
                    "version": version,
                    "context": context,
                    "path": path,
                    "line": line,
                    "kind": f"{manager}_install",
                    "raw": spec,
                }
            )
            if name is None or version is None or is_floating_version(version):
                add_error(
                    errors,
                    "DEP-FLOATING-INSTALL",
                    f"{manager} install requirement is not an exact version: {spec!r}",
                    path=path,
                    line=line,
                )
        return


def parse_install_spec(manager: str, spec: str) -> tuple[str | None, str | None]:
    if manager == "pip":
        match = re.fullmatch(
            r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]+\])?==([^\s*<>=!~,]+)",
            spec,
        )
        return (match.group(1), match.group(2)) if match else (None, None)
    if manager == "npm":
        if spec.startswith("@"):
            split = spec.rfind("@")
            if split <= 0:
                return None, None
            name, version = spec[:split], spec[split + 1 :]
        elif "@" in spec:
            name, version = spec.rsplit("@", 1)
        else:
            return None, None
        return (name, version) if EXACT_VERSION_RE.fullmatch(version) else (name, None)
    if manager == "brew" and "@" in spec:
        name, version = spec.rsplit("@", 1)
        return (name, version) if EXACT_VERSION_RE.fullmatch(version) else (name, None)
    return None, None


def scan_python_file(
    relative: str,
    role: str,
    path: Path,
    local_roots: set[str],
    imports: list[dict[str, Any]],
    installs: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    try:
        source = path.read_text(encoding="utf-8", errors="strict")
        tree = ast.parse(source, filename=relative)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
        add_error(
            errors,
            "DEP-PYTHON-PARSE",
            f"Python source cannot be parsed: {exc}",
            path=relative,
            line=getattr(exc, "lineno", None),
        )
        return
    aliases = build_aliases(tree)
    bindings = constant_bindings(tree)

    def observe(module: str, kind: str, line: int) -> None:
        classification = classify_module(module, local_roots)
        imports.append(
            {
                "path": relative,
                "line": line,
                "role": role,
                "kind": kind,
                "module": module,
                "classification": classification,
            }
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                observe(imported.name, "import", node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                module = "." * node.level + (node.module or "")
            else:
                module = node.module or ""
            if not module:
                add_error(
                    errors,
                    "DEP-IMPORT-UNRESOLVED",
                    "relative import has no resolvable module",
                    path=relative,
                    line=node.lineno,
                )
            else:
                observe(module, "from_import", node.lineno)
        if not isinstance(node, ast.Call):
            continue
        target = resolve_dotted(node.func, aliases)
        if target in {
            "importlib.import_module",
            "builtins.__import__",
            "builtins.import_module",
        }:
            if (
                not node.args
                or not isinstance(node.args[0], ast.Constant)
                or not isinstance(node.args[0].value, str)
            ):
                add_error(
                    errors,
                    "DEP-DYNAMIC-IMPORT-NONLITERAL",
                    "dynamic import target is not a literal string",
                    path=relative,
                    line=node.lineno,
                )
            else:
                observe(node.args[0].value, "dynamic_import", node.lineno)
        if target in {
            "subprocess.run",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
            "os.system",
            "os.popen",
        }:
            argument: ast.AST | None = node.args[0] if node.args else None
            for keyword in node.keywords:
                if keyword.arg in {"args", "command"}:
                    argument = keyword.value
            if argument is None:
                continue
            tokens, complete = command_tokens(argument, bindings)
            shell_true = any(
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in node.keywords
            )
            if shell_true and not complete:
                add_error(
                    errors,
                    "DEP-OPAQUE-SHELL",
                    "shell=True command is not statically resolvable",
                    path=relative,
                    line=node.lineno,
                )
            inspect_install_tokens(
                tokens,
                context=role,
                path=relative,
                line=node.lineno,
                installs=installs,
                errors=errors,
            )


def dependency_file_candidates(project_root: Path) -> list[Path]:
    excluded = set(EXPECTED_EXCLUDED_DIRECTORIES)
    result: list[Path] = []
    for path in project_root.rglob("*"):
        relative = path.relative_to(project_root)
        if any(part in excluded for part in relative.parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if path.name in DEPENDENCY_FILENAMES or (
            path.name.startswith("requirements") and path.suffix == ".txt"
        ):
            result.append(path)
    return sorted(result)


def add_config_dependency(
    observed: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    *,
    name: Any,
    version: Any,
    path: str,
    source: str,
) -> None:
    if not isinstance(name, str) or not PACKAGE_NAME_RE.fullmatch(name):
        add_error(
            errors,
            "DEP-CONFIG-UNPARSEABLE",
            f"dependency name is not parseable: {name!r}",
            path=path,
        )
        return
    if not isinstance(version, str) or is_floating_version(version):
        add_error(
            errors,
            "DEP-CONFIG-FLOATING",
            f"dependency {name!r} lacks an exact version",
            path=path,
        )
        version_value = None
    else:
        version_value = version
    observed.append(
        {
            "name": name,
            "version": version_value,
            "context": "project_config",
            "path": path,
            "line": None,
            "kind": source,
        }
    )


def parse_requirement_string(value: str) -> tuple[str | None, str | None]:
    stripped = value.split(";", 1)[0].strip()
    match = re.fullmatch(
        r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]+\])?==([^\s*<>=!~,]+)",
        stripped,
    )
    return (match.group(1), match.group(2)) if match else (None, None)


def scan_dependency_file(
    project_root: Path,
    path: Path,
    observed: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    relative = path.relative_to(project_root).as_posix()
    try:
        raw = path.read_bytes()
    except OSError as exc:
        add_error(
            errors,
            "DEP-CONFIG-READ",
            f"dependency file unreadable: {exc}",
            path=relative,
        )
        return
    if path.name.startswith("requirements") and path.suffix == ".txt":
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            add_error(
                errors,
                "DEP-CONFIG-READ",
                f"requirements is not UTF-8: {exc}",
                path=relative,
            )
            return
        for number, line in enumerate(text.splitlines(), start=1):
            value = line.split("#", 1)[0].strip()
            if not value or value.startswith("-"):
                continue
            name, version = parse_requirement_string(value)
            if name is None:
                add_error(
                    errors,
                    "DEP-CONFIG-FLOATING",
                    f"requirement is not an exact name==version pin: {value!r}",
                    path=relative,
                    line=number,
                )
            else:
                add_config_dependency(
                    observed,
                    errors,
                    name=name,
                    version=version,
                    path=relative,
                    source="requirements",
                )
        return
    if path.name in {"pyproject.toml", "poetry.lock", "uv.lock"}:
        try:
            data = tomllib.loads(raw.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            add_error(
                errors,
                "DEP-CONFIG-PARSE",
                f"TOML cannot be parsed: {exc}",
                path=relative,
            )
            return
        if path.name == "pyproject.toml":
            project = data.get("project", {})
            values: list[Any] = []
            if isinstance(project, dict):
                values.extend(project.get("dependencies", []) or [])
                optional = project.get("optional-dependencies", {}) or {}
                if isinstance(optional, dict):
                    for group in optional.values():
                        if isinstance(group, list):
                            values.extend(group)
            build = data.get("build-system", {})
            if isinstance(build, dict):
                values.extend(build.get("requires", []) or [])
            for value in values:
                if not isinstance(value, str):
                    add_error(
                        errors,
                        "DEP-CONFIG-UNPARSEABLE",
                        "pyproject dependency is not a string",
                        path=relative,
                    )
                    continue
                name, version = parse_requirement_string(value)
                if name is None:
                    add_error(
                        errors,
                        "DEP-CONFIG-FLOATING",
                        f"pyproject dependency is not exactly pinned: {value!r}",
                        path=relative,
                    )
                else:
                    add_config_dependency(
                        observed,
                        errors,
                        name=name,
                        version=version,
                        path=relative,
                        source="pyproject",
                    )
        else:
            packages = data.get("package", [])
            if not isinstance(packages, list):
                add_error(
                    errors,
                    "DEP-CONFIG-PARSE",
                    "lock package table must be a list",
                    path=relative,
                )
                return
            for package in packages:
                if not isinstance(package, dict):
                    add_error(
                        errors,
                        "DEP-CONFIG-PARSE",
                        "lock package entry must be an object",
                        path=relative,
                    )
                    continue
                add_config_dependency(
                    observed,
                    errors,
                    name=package.get("name"),
                    version=package.get("version"),
                    path=relative,
                    source=path.name,
                )
        return
    if path.name in {"package.json", "package-lock.json", "Pipfile.lock"}:
        json_errors: list[dict[str, Any]] = []
        data = read_strict_json(
            path, json_errors, oracle_id="DEP-CONFIG-PARSE", label=relative
        )
        errors.extend(json_errors)
        if data is None:
            return
        if path.name == "package.json":
            for group_name in (
                "dependencies",
                "devDependencies",
                "optionalDependencies",
            ):
                group = data.get(group_name, {})
                if not isinstance(group, dict):
                    add_error(
                        errors,
                        "DEP-CONFIG-PARSE",
                        f"{group_name} must be an object",
                        path=relative,
                    )
                    continue
                for name, version in group.items():
                    add_config_dependency(
                        observed,
                        errors,
                        name=name,
                        version=version,
                        path=relative,
                        source=group_name,
                    )
        elif path.name == "Pipfile.lock":
            for group_name in ("default", "develop"):
                group = data.get(group_name, {})
                if not isinstance(group, dict):
                    add_error(
                        errors,
                        "DEP-CONFIG-PARSE",
                        f"{group_name} must be an object",
                        path=relative,
                    )
                    continue
                for name, metadata in group.items():
                    version = (
                        metadata.get("version") if isinstance(metadata, dict) else None
                    )
                    if isinstance(version, str) and version.startswith("=="):
                        version = version[2:]
                    add_config_dependency(
                        observed,
                        errors,
                        name=name,
                        version=version,
                        path=relative,
                        source=group_name,
                    )
        else:
            packages = data.get("packages")
            if not isinstance(packages, dict):
                add_error(
                    errors,
                    "DEP-CONFIG-PARSE",
                    "package-lock packages must be an object",
                    path=relative,
                )
                return
            for key, metadata in packages.items():
                if key == "" or not isinstance(metadata, dict):
                    continue
                name = metadata.get("name") or PurePosixPath(key).name
                add_config_dependency(
                    observed,
                    errors,
                    name=name,
                    version=metadata.get("version"),
                    path=relative,
                    source="package-lock",
                )
        return
    add_error(
        errors,
        "DEP-CONFIG-UNSUPPORTED-LOCK",
        "dependency/lock file exists but this verifier has no reviewed parser",
        path=relative,
    )


def extract_workflow_runs(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    result: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = RUN_RE.match(lines[index])
        if not match:
            index += 1
            continue
        indent = len(match.group(1))
        value = match.group(2).strip()
        start = index + 1
        if value in {"|", "|-", "|+", ">", ">-", ">+"}:
            block: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if (
                    candidate.strip()
                    and len(candidate) - len(candidate.lstrip()) <= indent
                ):
                    break
                if candidate.strip():
                    block.append(candidate.strip())
                index += 1
            result.append((start, "\n".join(block)))
            continue
        result.append((start, value))
        index += 1
    return result


def scan_workflows(
    repository_root: Path,
    errors: list[dict[str, Any]],
    installs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    workflow_root = safe_declared_directory(
        repository_root,
        ".github/workflows",
        "repository workflow root",
        errors,
    )
    if workflow_root is None:
        return [], []
    actions: list[dict[str, Any]] = []
    workflow_files: list[str] = []
    for path in sorted(workflow_root.iterdir()):
        if path.suffix not in {".yml", ".yaml"} or not path.is_file():
            continue
        relative = path.relative_to(repository_root).as_posix()
        workflow_files.append(relative)
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeDecodeError) as exc:
            add_error(
                errors,
                "DEP-WORKFLOW-READ",
                f"workflow unreadable: {exc}",
                path=relative,
            )
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            match = USES_RE.match(line)
            if not match:
                continue
            value = next(group for group in match.groups() if group is not None)
            if value.startswith("./"):
                continue
            if value.startswith("docker://"):
                revision = value.rsplit("@", 1)[-1] if "@" in value else ""
                pinned = bool(re.fullmatch(r"sha256:[0-9a-f]{64}", revision))
            else:
                revision = value.rsplit("@", 1)[-1] if "@" in value else ""
                pinned = bool(ACTION_COMMIT_RE.fullmatch(revision))
            actions.append(
                {
                    "path": relative,
                    "line": number,
                    "uses": value,
                    "revision": revision,
                    "pinned": pinned,
                }
            )
            if not pinned:
                add_error(
                    errors,
                    "DEP-ACTION-UNPINNED",
                    f"external action is not pinned to a full commit/digest: {value!r}",
                    path=relative,
                    line=number,
                )
        for number, command in extract_workflow_runs(text):
            try:
                tokens = shlex.split(command.replace("\n", " "))
            except ValueError:
                tokens = command.replace("\n", " ").split()
            inspect_install_tokens(
                tokens,
                context="workflow_ci_tool",
                path=relative,
                line=number,
                installs=installs,
                errors=errors,
            )
    return actions, workflow_files


def discover_repository_root(project_root: Path) -> Path:
    for candidate in (project_root, *project_root.parents):
        if (candidate / ".git").exists():
            return candidate
    return project_root


def verify_observed_dependencies(
    imports: list[dict[str, Any]],
    installs: list[dict[str, Any]],
    registered: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    import_owner: dict[str, dict[str, Any]] = {}
    for dependency in registered.values():
        for import_name in dependency.get("import_names", []):
            import_owner[normalize_package_name(import_name)] = dependency

    observed_registered: set[str] = set()
    for observation in imports:
        if observation["classification"] != "third_party":
            continue
        root = observation["module"].lstrip(".").split(".", 1)[0]
        dependency = import_owner.get(normalize_package_name(root))
        context = observation["role"]
        if context == "runtime":
            add_error(
                errors,
                "DEP-RUNTIME-NON-STDLIB",
                f"runtime imports third-party module {observation['module']!r}",
                path=observation["path"],
                line=observation["line"],
            )
        if dependency is None:
            add_error(
                errors,
                "DEP-UNREGISTERED-DEPENDENCY",
                f"third-party import {observation['module']!r} has no manifest entry",
                path=observation["path"],
                line=observation["line"],
            )
            continue
        normalized = normalize_package_name(dependency["name"])
        observed_registered.add(normalized)
        if context not in dependency.get("allowed_contexts", []):
            add_error(
                errors,
                "DEP-CONTEXT-NOT-ALLOWED",
                f"dependency {dependency['name']!r} is not allowed in context {context!r}",
                path=observation["path"],
                line=observation["line"],
            )

    for install in installs:
        name = install.get("name")
        version = install.get("version")
        if not isinstance(name, str):
            continue
        normalized = normalize_package_name(name)
        dependency = registered.get(normalized)
        if dependency is None:
            add_error(
                errors,
                "DEP-UNREGISTERED-DEPENDENCY",
                f"installed/configured dependency {name!r} has no manifest entry",
                path=install["path"],
                line=install.get("line"),
            )
            continue
        observed_registered.add(normalized)
        if install["context"] not in dependency.get("allowed_contexts", []):
            add_error(
                errors,
                "DEP-CONTEXT-NOT-ALLOWED",
                f"dependency {name!r} is not allowed in context {install['context']!r}",
                path=install["path"],
                line=install.get("line"),
            )
        if version is not None and str(dependency.get("version_or_commit")) != version:
            add_error(
                errors,
                "DEP-VERSION-MISMATCH",
                f"observed {name}=={version} differs from manifest {dependency.get('version_or_commit')!r}",
                path=install["path"],
                line=install.get("line"),
            )

    for name in sorted(set(registered) - observed_registered):
        add_error(
            errors,
            "DEP-MANIFEST-STALE",
            f"manifest dependency {name!r} was not observed in imports, configs, or install commands",
        )


def verify_dependency_boundary(
    project_root: Path,
    *,
    manifest_path: Path | None = None,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    manifest_path = manifest_path or project_root / DEFAULT_MANIFEST_RELATIVE
    repository_root = (
        repository_root or discover_repository_root(project_root)
    ).resolve()
    errors: list[dict[str, Any]] = []
    manifest = read_strict_json(
        manifest_path,
        errors,
        oracle_id="DEP-MANIFEST-STRICT-JSON",
        label="dependency boundary manifest",
    )
    registered: dict[str, dict[str, Any]] = {}
    if manifest is not None:
        registered = validate_manifest(manifest, errors)

    imports: list[dict[str, Any]] = []
    installs: list[dict[str, Any]] = []
    python_files = collect_python_files(project_root, errors)
    local_roots = local_module_roots(project_root)
    for relative, role, path in python_files:
        scan_python_file(
            relative,
            role,
            path,
            local_roots,
            imports,
            installs,
            errors,
        )

    dependency_files = dependency_file_candidates(project_root)
    for path in dependency_files:
        scan_dependency_file(project_root, path, installs, errors)
    actions, workflow_files = scan_workflows(repository_root, errors, installs)
    verify_observed_dependencies(imports, installs, registered, errors)

    imports.sort(
        key=lambda item: (
            item["classification"],
            item["role"],
            item["module"],
            item["path"],
            item["line"],
        )
    )
    installs.sort(
        key=lambda item: (
            item["context"],
            str(item.get("name")),
            item["path"],
            item.get("line") or 0,
        )
    )
    third_party_imports = [
        item for item in imports if item["classification"] == "third_party"
    ]
    runtime_third_party = sorted(
        {
            item["module"].split(".", 1)[0]
            for item in third_party_imports
            if item["role"] == "runtime"
        }
    )
    governance_third_party = sorted(
        {
            item["module"].split(".", 1)[0]
            for item in third_party_imports
            if item["role"] == "governance"
        }
    )
    ci_tools = sorted(
        {
            normalize_package_name(item["name"])
            for item in installs
            if item["context"] == "workflow_ci_tool"
            and isinstance(item.get("name"), str)
        }
    )
    report = {
        "status": "pass" if not errors else "fail",
        "boundary_id": manifest.get("boundary_id") if manifest else None,
        "observed": {
            "python_files_scanned": len(python_files),
            "dependency_files_scanned": [
                path.relative_to(project_root).as_posix() for path in dependency_files
            ],
            "workflow_files_scanned": workflow_files,
            "imports": imports,
            "installs_and_config_dependencies": installs,
            "external_actions": actions,
            "runtime_third_party_dependencies": runtime_third_party,
            "governance_third_party_dependencies": governance_third_party,
            "ci_tool_dependencies": ci_tools,
        },
        "errors": errors,
        "claim_boundary": manifest.get("claim_boundary") if manifest else None,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=SCRIPT_PROJECT_ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    manifest_path = args.manifest
    if manifest_path is not None and not manifest_path.is_absolute():
        manifest_path = project_root / manifest_path
    report = verify_dependency_boundary(
        project_root,
        manifest_path=manifest_path,
        repository_root=args.repository_root,
    )
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    elif report["status"] == "pass":
        observed = report["observed"]
        print("dependency boundary: PASS")
        print(
            "observed runtime third-party dependencies: "
            f"{observed['runtime_third_party_dependencies']}"
        )
        print(
            "observed governance third-party dependencies: "
            f"{observed['governance_third_party_dependencies']}"
        )
        print(f"observed CI tool dependencies: {observed['ci_tool_dependencies']}")
        print(f"external actions checked: {len(observed['external_actions'])}")
    else:
        print("dependency boundary: FAIL")
        for error in report["errors"]:
            location = error.get("path", "manifest")
            if error.get("line") is not None:
                location = f"{location}:{error['line']}"
            print(f"- {error['oracle_id']} {location}: {error['message']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
