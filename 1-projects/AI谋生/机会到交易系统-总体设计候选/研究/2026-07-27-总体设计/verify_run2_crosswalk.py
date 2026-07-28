#!/usr/bin/env python3
"""Reconstruct Run2 final CE-IN rows and verify the exhaustive crosswalk.

The verifier treats the sealed lead/independent ledgers and the two joint
adjudications as source data.  It does not infer that every CE-IN row supports
the current design: rows without an explicit human crosswalk mapping are kept
as admitted-but-unused evidence candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


class CrosswalkError(ValueError):
    pass


@dataclass(frozen=True)
class LedgerRow:
    stage: str
    query_rank: str
    result_ref: str
    ce: str
    claim: str
    k: tuple[str, ...]
    scope: str

    @property
    def identity(self) -> str:
        return f"{self.query_rank}/{self.result_ref}"


K_TO_RQ = {
    "K01": ("RQ3", "RQ4"),
    "K02": ("RQ2", "RQ4"),
    "K03": ("RQ1", "RQ5"),
    "K04": ("RQ3",),
    "K05": ("RQ5",),
    "K06": ("RQ1", "RQ5"),
    "K07": ("RQ9",),
    "K08": ("RQ6",),
    "K09": ("RQ6", "RQ7"),
    "K10": ("RQ8",),
    "K11": ("RQ8",),
    "K12": ("RQ5", "RQ8"),
    "K13": ("RQ8",),
}

EXPECTED_STAGE_UNIVERSE = {"S1": 432, "S2": 345}
EXPECTED_FINAL_CE_IN = {"S1": 131, "S2": 141}
EXPECTED_DIRECT_MAPPINGS = {"S1": 18, "S2": 8}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def strip_code(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def normalize_k(value: str) -> tuple[str, ...]:
    return tuple(sorted(set(re.findall(r"K\d{2}", value))))


def normalize_lead_ce(value: str) -> str:
    value = strip_code(value).strip()
    if value == "INCLUDE":
        return "CE-IN"
    match = re.fullmatch(r"EXCLUDE(?:—|:)([A-Z-]+)", value)
    if not match:
        raise CrosswalkError(f"unknown lead CE code: {value!r}")
    return f"CE-OUT/{match.group(1)}"


def normalize_independent_ce(value: str) -> str:
    value = strip_code(value).strip()
    if value.startswith("CE-IN/"):
        return "CE-IN"
    if value.startswith("CE-OUT/"):
        return value
    raise CrosswalkError(f"unknown independent CE code: {value!r}")


def split_markdown_row(line: str) -> list[str]:
    if not line.startswith("|") or not line.rstrip().endswith("|"):
        raise CrosswalkError("not a Markdown table row")
    body = line.rstrip("\n")[1:-1]
    parts = re.split(r"(?<!\\)\|", body)
    return [part.strip().replace(r"\|", "|") for part in parts]


def parse_independent(path: Path, stage: str) -> dict[str, LedgerRow]:
    rows: dict[str, LedgerRow] = {}
    row_prefix = re.compile(rf"^\| `{stage}-K\d{{2}}/R\d{{2}}` \|")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not row_prefix.match(line):
            continue
        parts = split_markdown_row(line)
        if len(parts) != 10:
            raise CrosswalkError(f"{path}: expected 10 columns, got {len(parts)}")
        query_rank = strip_code(parts[0])
        result_ref = strip_code(parts[1])
        row = LedgerRow(
            stage=stage,
            query_rank=query_rank,
            result_ref=result_ref,
            ce=strip_code(parts[5]),
            claim=parts[6],
            k=normalize_k(parts[7]),
            scope=parts[9],
        )
        if row.identity in rows:
            raise CrosswalkError(f"{path}: duplicate identity {row.identity}")
        rows[row.identity] = row
    return rows


def extract_between(line: str, start_pattern: str, end_pattern: str, label: str) -> str:
    start = re.search(start_pattern, line)
    if not start:
        raise CrosswalkError(f"missing {label} start in row: {line[:120]}")
    end = re.search(end_pattern, line[start.end() :])
    if not end:
        raise CrosswalkError(f"missing {label} end in row: {line[:120]}")
    return line[start.end() : start.end() + end.start()].strip("； ")


def parse_lead_s1(path: Path) -> dict[str, LedgerRow]:
    rows: dict[str, LedgerRow] = {}
    identity_re = re.compile(r"^- `(?P<query>S1-K\d{2}/R\d{2})/(?P<ref>[^`]+)`；")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = identity_re.match(line)
        if not match:
            continue
        ce_match = re.search(r"CLAIM-EVIDENCE：`([^`]+)`", line)
        scope_match = re.search(r"；范围/方法/不可外推：(.*)$", line)
        if not ce_match or not scope_match:
            raise CrosswalkError(f"{path}: malformed lead row {match.group(0)}")
        claim = extract_between(
            line,
            r"CLAIM-EVIDENCE：`[^`]+`；精确主张：",
            r"；K mapping：",
            "S1 lead claim",
        )
        k_text = extract_between(
            line,
            r"；K mapping：",
            r"；NC-PROVISIONAL：",
            "S1 K mapping",
        )
        row = LedgerRow(
            stage="S1",
            query_rank=match.group("query"),
            result_ref=match.group("ref"),
            ce=ce_match.group(1),
            claim=claim,
            k=normalize_k(k_text),
            scope=scope_match.group(1).strip(),
        )
        if row.identity in rows:
            raise CrosswalkError(f"{path}: duplicate identity {row.identity}")
        rows[row.identity] = row
    return rows


def parse_lead_s2(path: Path) -> dict[str, LedgerRow]:
    rows: dict[str, LedgerRow] = {}
    bold_identity_re = re.compile(
        r"^- \*\*(?P<query>S2-K\d{2}/R\d{2})/`(?P<ref>[^`]+)`\*\*"
    )
    plain_identity_re = re.compile(
        r"^- `(?P<query>S2-K\d{2}/R\d{2})/(?P<ref>[^`]+)`；"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        match = bold_identity_re.match(line)
        plain = False
        if not match:
            match = plain_identity_re.match(line)
            plain = match is not None
        if not match:
            continue
        if plain:
            ce_match = re.search(r"CLAIM-EVIDENCE：`([^`]+)`", line)
            scope_match = re.search(r"；范围/方法/不可外推：(.*)$", line)
            if not ce_match or not scope_match:
                raise CrosswalkError(f"{path}: malformed plain lead row {match.group(0)}")
            claim = extract_between(
                line,
                r"CLAIM-EVIDENCE：`[^`]+`；精确主张：",
                r"；K mapping：",
                "S2 plain lead claim",
            )
            k_text = extract_between(
                line,
                r"；K mapping：",
                r"；NC-PROVISIONAL：",
                "S2 plain K mapping",
            )
        else:
            ce_match = re.search(r"`CLAIM-EVIDENCE=([^`]+)`", line)
            k_match = re.search(r"`K mapping=([^`]+)`", line)
            scope_match = re.search(r"；范围/方法：(.*)$", line)
            if not ce_match or not k_match or not scope_match:
                raise CrosswalkError(f"{path}: malformed bold lead row {match.group(0)}")
            claim = extract_between(
                line,
                r"`CLAIM-EVIDENCE=[^`]+`",
                r"；`K mapping=",
                "S2 bold lead claim",
            )
            k_text = k_match.group(1)
        row = LedgerRow(
            stage="S2",
            query_rank=match.group("query"),
            result_ref=match.group("ref"),
            ce=ce_match.group(1),
            claim=claim,
            k=normalize_k(k_text),
            scope=scope_match.group(1).strip(),
        )
        if row.identity in rows:
            raise CrosswalkError(f"{path}: duplicate identity {row.identity}")
        rows[row.identity] = row
    return rows


def expand_compact_identity(value: str, stage: str) -> list[str]:
    value = strip_code(value).strip()
    value = value.replace("{", "").replace("}", "")
    match = re.fullmatch(r"(?:(S[12])-)?K(\d{2})/(R\d{2}(?:,R\d{2})*)", value)
    if not match:
        raise CrosswalkError(f"cannot expand compact identity: {value!r}")
    explicit_stage, k_number, ranks = match.groups()
    effective_stage = explicit_stage or stage
    if effective_stage != stage:
        raise CrosswalkError(f"stage mismatch in compact identity: {value!r}")
    return [f"{stage}-K{k_number}/{rank}" for rank in ranks.split(",")]


def parse_s1_ce_overrides(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    section = text.split("### 最终分组", 1)[1].split("### 关键范围决定", 1)[0]
    overrides: dict[str, str] = {}
    current: str | None = None
    declared_count: int | None = None
    seen_in_group = 0
    for line in section.splitlines():
        heading = re.fullmatch(r"`([^`]+)`（`(\d+)`）：", line.strip())
        if heading:
            if current is not None and seen_in_group != declared_count:
                raise CrosswalkError(f"S1 joint count mismatch for {current}")
            current = heading.group(1)
            declared_count = int(heading.group(2))
            seen_in_group = 0
            continue
        bullet = re.fullmatch(r"- `([^`]+)`", line.strip())
        if bullet and current:
            for query_rank in expand_compact_identity(bullet.group(1), "S1"):
                if query_rank in overrides:
                    raise CrosswalkError(f"duplicate S1 CE override {query_rank}")
                overrides[query_rank] = current
                seen_in_group += 1
    if current is not None and seen_in_group != declared_count:
        raise CrosswalkError(f"S1 joint count mismatch for {current}")
    return overrides


def parse_s2_ce_overrides(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    section = "### 5.1" + text.split("### 5.1", 1)[1].split("### 5.9", 1)[0]
    overrides: dict[str, str] = {}
    current: str | None = None
    declared_count: int | None = None
    seen_in_group = 0

    def finish_group() -> None:
        nonlocal current, declared_count, seen_in_group
        if current is not None and declared_count is not None and seen_in_group != declared_count:
            raise CrosswalkError(
                f"S2 joint count mismatch for {current}: {seen_in_group} != {declared_count}"
            )

    for line in section.splitlines():
        heading = re.match(r"### 5\.\d+ `([^`]+)`（`(\d+)`）", line.strip())
        if heading:
            finish_group()
            current = heading.group(1)
            declared_count = int(heading.group(2))
            seen_in_group = 0
            continue
        if current is None:
            continue
        bullet = re.fullmatch(r"- `([^`]+)`", line.strip())
        identities: list[str] = []
        if bullet:
            identities = expand_compact_identity(bullet.group(1), "S2")
        elif line.startswith("| `S2-K"):
            parts = split_markdown_row(line)
            identities = [strip_code(parts[0])]
        for query_rank in identities:
            if query_rank in overrides:
                raise CrosswalkError(f"duplicate S2 CE override {query_rank}")
            outcome = current
            if current == "CE-IN/*" and line.startswith("|"):
                outcome = split_markdown_row(line)[1].replace("`", "").split("（", 1)[0]
            overrides[query_rank] = outcome
            seen_in_group += 1
    finish_group()
    return overrides


def parse_s2_k_rules(path: Path) -> tuple[dict[str, str], dict[str, tuple[str, ...]]]:
    text = path.read_text(encoding="utf-8")
    preliminary: dict[str, str] = {}
    for section_no, selector, next_no in (
        ("6.1", "lead", "6.2"),
        ("6.2", "independent", "6.3"),
    ):
        section = text.split(f"### {section_no}", 1)[1].split(f"### {next_no}", 1)[0]
        for line in section.splitlines():
            bullet = re.fullmatch(r"- `([^`]+)`", line.strip())
            if not bullet:
                continue
            for query_rank in expand_compact_identity(bullet.group(1), "S2"):
                if query_rank in preliminary:
                    raise CrosswalkError(f"duplicate S2 preliminary K rule {query_rank}")
                preliminary[query_rank] = selector
    cross_section = text.split("### 6.3", 1)[1].split("### 6.4", 1)[0]
    cross_values: dict[str, tuple[str, ...]] = {}
    for line in cross_section.splitlines():
        if not line.startswith("| `S2-K"):
            continue
        parts = split_markdown_row(line)
        query_rank = strip_code(parts[0])
        preliminary[query_rank] = "explicit"
        cross_values[query_rank] = normalize_k(parts[3])
    override_section = text.split("### 6.4", 1)[1].split("## 7.", 1)[0]
    final_overrides: dict[str, tuple[str, ...]] = {}
    for line in override_section.splitlines():
        if not line.startswith("| `S2-K"):
            continue
        parts = split_markdown_row(line)
        final_overrides[strip_code(parts[0])] = normalize_k(parts[1])
    if len(preliminary) != 176 or len(cross_values) != 13 or len(final_overrides) != 42:
        raise CrosswalkError(
            "S2 K rule counts do not match joint adjudication: "
            f"preliminary={len(preliminary)}, cross={len(cross_values)}, "
            f"final={len(final_overrides)}"
        )
    return preliminary, {**cross_values, **{f"FINAL:{k}": v for k, v in final_overrides.items()}}


def parse_s1_scope_constraints(path: Path) -> tuple[str, dict[str, list[str]]]:
    text = path.read_text(encoding="utf-8")
    global_match = re.search(
        r"- exact-claim 与 scope 采用 lead 的可核验窄表述；[^\n]+",
        text,
    )
    if not global_match:
        raise CrosswalkError("S1 joint global claim/scope rule is missing")
    specific: dict[str, list[str]] = {}
    section = text.split("### 关键范围决定", 1)[1].split("### 跨查询重复", 1)[0]
    for line in section.splitlines():
        match = re.fullmatch(r"- `(K\d{2}/R\d{2}) [^`]+`：`INCLUDE`，(.+)", line.strip())
        if not match:
            continue
        query_rank = f"S1-{match.group(1)}"
        specific.setdefault(query_rank, []).append(match.group(2).strip())
    return global_match.group(0)[2:], specific


def parse_s2_scope_constraints(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    constraints: dict[str, list[str]] = {}
    section4 = text.split("## 4.", 1)[1].split("## 5.", 1)[0]
    for line in section4.splitlines():
        if not line.startswith("| `S2-K"):
            continue
        parts = split_markdown_row(line)
        query_rank = strip_code(parts[0])
        constraints.setdefault(query_rank, []).append(parts[-1])
    section53 = text.split("### 5.3", 1)[1].split("### 5.4", 1)[0]
    for line in section53.splitlines():
        if not line.startswith("| `S2-K"):
            continue
        parts = split_markdown_row(line)
        query_rank = strip_code(parts[0])
        constraints.setdefault(query_rank, []).append(parts[-1])
    return constraints


def parse_direct_mappings(path: Path) -> dict[str, dict[str, Any]]:
    mappings: dict[str, dict[str, Any]] = {}
    active_stage: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## S1 当前直接使用的 CE-IN"):
            active_stage = "S1"
            continue
        if line.startswith("## S2 当前直接使用的 CE-IN"):
            active_stage = "S2"
            continue
        if line.startswith("## ") and active_stage is not None:
            active_stage = None
        if active_stage is None or not line.startswith(f"| `{active_stage}/K"):
            continue
        parts = split_markdown_row(line)
        if len(parts) != 6:
            raise CrosswalkError(f"human crosswalk row has {len(parts)} columns")
        raw_identity = strip_code(parts[0])
        identity = raw_identity.replace(f"{active_stage}/K", f"{active_stage}-K", 1)
        rq_ids = sorted(set(re.findall(r"RQ\d+", parts[3])))
        claim_ids = sorted(
            set(re.findall(r"(?:TF|EF|SS)-\d+|H-AI-\d+|H-OVERSIGHT-\d+", parts[3]))
        )
        dd_ids = sorted(set(re.findall(r"DD-\d+", parts[4])))
        mappings[identity] = {
            "rq_ids": rq_ids,
            "claim_ids": claim_ids,
            "dd_ids": dd_ids,
            "residual_unknown": parts[5],
        }
    return mappings


def final_rows(root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    run = root / "ssp-run2"
    lead = {
        "S1": parse_lead_s1(run / "lead-screening/S1.md"),
        "S2": parse_lead_s2(run / "lead-screening/S2.md"),
    }
    independent = {
        "S1": parse_independent(run / "independent-screening/S1.md", "S1"),
        "S2": parse_independent(run / "independent-screening/S2.md", "S2"),
    }
    for stage in ("S1", "S2"):
        if set(lead[stage]) != set(independent[stage]):
            raise CrosswalkError(f"{stage}: lead/independent identity universe mismatch")
        if len(lead[stage]) != EXPECTED_STAGE_UNIVERSE[stage]:
            raise CrosswalkError(f"{stage}: unexpected universe size {len(lead[stage])}")
        for identity in lead[stage]:
            if lead[stage][identity].query_rank != independent[stage][identity].query_rank:
                raise CrosswalkError(f"{stage}: query/rank mismatch for {identity}")

    s1_overrides = parse_s1_ce_overrides(run / "S1_JOINT_ADJUDICATION.md")
    s2_overrides = parse_s2_ce_overrides(run / "S2_JOINT_ADJUDICATION.md")
    k_rules, k_values = parse_s2_k_rules(run / "S2_JOINT_ADJUDICATION.md")
    s1_global_scope, s1_specific_scopes = parse_s1_scope_constraints(
        run / "S1_JOINT_ADJUDICATION.md"
    )
    s2_specific_scopes = parse_s2_scope_constraints(run / "S2_JOINT_ADJUDICATION.md")
    direct = parse_direct_mappings(root / "RUN2_CLAIM_EVIDENCE_CROSSWALK.md")

    rows: list[dict[str, Any]] = []
    stage_counts = {"S1": 0, "S2": 0}
    direct_counts = {"S1": 0, "S2": 0}
    for stage in ("S1", "S2"):
        for identity in sorted(lead[stage]):
            lead_row = lead[stage][identity]
            independent_row = independent[stage][identity]
            query_rank = lead_row.query_rank
            lead_ce = normalize_lead_ce(lead_row.ce)
            independent_ce = normalize_independent_ce(independent_row.ce)
            overrides = s1_overrides if stage == "S1" else s2_overrides
            if query_rank in overrides:
                final_ce = overrides[query_rank]
                basis = "JOINT_OVERRIDE"
            else:
                if lead_ce.startswith("CE-OUT/") and independent_ce.startswith("CE-OUT/"):
                    final_ce = lead_ce
                    basis = "BOTH_EXCLUDE_LEAD_REASON_RETAINED"
                elif lead_ce == "CE-IN" and independent_ce == "CE-IN":
                    final_ce = (
                        "INCLUDE/UNSUBTYPED"
                        if stage == "S1"
                        else independent_row.ce
                    )
                    basis = "SEALED_LEDGER_AGREEMENT"
                else:
                    raise CrosswalkError(
                        f"{stage}: unadjudicated CE disagreement {query_rank}: "
                        f"{lead_ce} vs {independent_ce}"
                    )
            included = final_ce == "INCLUDE" or final_ce.startswith("INCLUDE/") or final_ce.startswith("CE-IN/")
            if not included:
                continue

            if stage == "S2":
                if query_rank in k_rules:
                    selector = k_rules[query_rank]
                    if selector == "lead":
                        final_k = lead_row.k
                    elif selector == "independent":
                        final_k = independent_row.k
                    else:
                        final_k = k_values[query_rank]
                else:
                    if lead_row.k != independent_row.k:
                        raise CrosswalkError(f"S2: unadjudicated K disagreement {query_rank}")
                    final_k = lead_row.k
                final_k = k_values.get(f"FINAL:{query_rank}", final_k)
                k_status = "JOINT_ADJUDICATED"
            else:
                final_k = tuple(sorted(set(lead_row.k) | set(independent_row.k)))
                k_status = "ROUTING_UNION_NOT_INDIVIDUALLY_ADJUDICATED"

            direct_mapping = direct.get(identity)
            if direct_mapping:
                mapping_state = "DIRECT_LOAD_BEARING_MAPPING"
                rq_ids = direct_mapping["rq_ids"]
                claim_ids = direct_mapping["claim_ids"]
                dd_ids = direct_mapping["dd_ids"]
                residual_unknown = direct_mapping["residual_unknown"]
                direct_counts[stage] += 1
            else:
                mapping_state = "NO_DIRECT_LOAD_BEARING_USE"
                rq_ids = sorted({rq for k in final_k for rq in K_TO_RQ[k]})
                claim_ids = []
                dd_ids = []
                residual_unknown = (
                    "Admitted claim-evidence candidate only; it adds no direct support weight "
                    "to the current Claim/DD graph unless a future claim-specific synthesis "
                    "with independent review explicitly promotes it."
                )
            if stage == "S1":
                joint_scope_constraints = [
                    s1_global_scope,
                    *s1_specific_scopes.get(query_rank, []),
                ]
            else:
                joint_scope_constraints = s2_specific_scopes.get(query_rank, [])
            rows.append(
                {
                    "schema_version": "otts.run2-ce-crosswalk-row/1",
                    "execution_id": "SSP-1.0-RUN-20260727T154803-0700",
                    "stage": stage,
                    "identity": identity,
                    "query_rank": query_rank,
                    "result_ref": lead_row.result_ref,
                    "final_ce": final_ce,
                    "adjudication_basis": basis,
                    "lead_ce": lead_row.ce,
                    "independent_ce": independent_row.ce,
                    "lead_claim": lead_row.claim,
                    "lead_claim_sha256": sha256_text(lead_row.claim),
                    "independent_claim": independent_row.claim,
                    "independent_claim_sha256": sha256_text(independent_row.claim),
                    "lead_scope": lead_row.scope,
                    "lead_scope_sha256": sha256_text(lead_row.scope),
                    "independent_scope": independent_row.scope,
                    "independent_scope_sha256": sha256_text(independent_row.scope),
                    "joint_scope_constraints": joint_scope_constraints,
                    "joint_scope_constraints_sha256": sha256_text(
                        json.dumps(
                            joint_scope_constraints,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                    ),
                    "lead_k": list(lead_row.k),
                    "independent_k": list(independent_row.k),
                    "final_k": list(final_k),
                    "final_k_status": k_status,
                    "mapping_state": mapping_state,
                    "rq_ids": rq_ids,
                    "claim_ids": claim_ids,
                    "dd_ids": dd_ids,
                    "residual_unknown": residual_unknown,
                    "external_action_authority": False,
                }
            )
            stage_counts[stage] += 1

    if stage_counts != EXPECTED_FINAL_CE_IN:
        raise CrosswalkError(f"final CE-IN counts mismatch: {stage_counts}")
    if direct_counts != EXPECTED_DIRECT_MAPPINGS:
        raise CrosswalkError(f"direct mapping counts mismatch: {direct_counts}")
    if set(direct) != {row["identity"] for row in rows if row["mapping_state"] == "DIRECT_LOAD_BEARING_MAPPING"}:
        raise CrosswalkError("human crosswalk contains an identity outside the final CE-IN set")
    return rows, {
        "s1_final_ce_in": stage_counts["S1"],
        "s2_final_ce_in": stage_counts["S2"],
        "total_final_ce_in": len(rows),
        "s1_direct_mappings": direct_counts["S1"],
        "s2_direct_mappings": direct_counts["S2"],
        "total_direct_mappings": sum(direct_counts.values()),
        "total_no_direct_load_bearing_use": len(rows) - sum(direct_counts.values()),
    }


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def validate_crosswalk(root: Path, crosswalk_path: Path) -> dict[str, Any]:
    expected_rows, counts = final_rows(root)
    expected_text = canonical_jsonl(expected_rows)
    actual_text = crosswalk_path.read_text(encoding="utf-8")
    if actual_text != expected_text:
        actual_rows: list[Any] = []
        for number, line in enumerate(actual_text.splitlines(), start=1):
            try:
                actual_rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise CrosswalkError(f"crosswalk line {number}: invalid JSON: {exc}") from exc
        actual_ids = [row.get("identity") for row in actual_rows if isinstance(row, dict)]
        expected_ids = [row["identity"] for row in expected_rows]
        missing = sorted(set(expected_ids) - set(actual_ids))
        extra = sorted(set(actual_ids) - set(expected_ids))
        duplicates = sorted({identity for identity in actual_ids if actual_ids.count(identity) > 1})
        if missing or extra or duplicates:
            raise CrosswalkError(
                f"crosswalk identity mismatch: missing={missing}, extra={extra}, duplicates={duplicates}"
            )
        for index, (actual, expected) in enumerate(zip(actual_rows, expected_rows), start=1):
            if actual != expected:
                raise CrosswalkError(
                    f"crosswalk row {index} differs from reconstructed source row "
                    f"{expected['identity']}"
                )
        raise CrosswalkError("crosswalk is not in canonical JSONL form")
    return {
        "valid": True,
        "crosswalk_sha256": hashlib.sha256(actual_text.encode("utf-8")).hexdigest(),
        **counts,
        "external_action_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="overall-design research directory",
    )
    parser.add_argument(
        "--crosswalk",
        type=Path,
        default=Path(__file__).resolve().parent / "RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl",
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        rows, _ = final_rows(args.root)
        if args.write:
            args.crosswalk.write_text(canonical_jsonl(rows), encoding="utf-8")
        result = validate_crosswalk(args.root, args.crosswalk)
    except (OSError, UnicodeError, CrosswalkError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
