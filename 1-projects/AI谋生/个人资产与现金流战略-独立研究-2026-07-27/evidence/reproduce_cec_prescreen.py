#!/usr/bin/env python3
"""Recompute the CEC building-benchmarking prescreen from bound raw files.

This is a read-only evidence transformation.  It makes no legal, demand,
payment, delivery, profit, or authority claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd


EXPECTED_INPUTS = {
    "covered": {
        "bytes": 3_919_934,
        "sha256": "8a996c43d04a8a690d60087c361e6f9580e1492868ee367f9958ff0b1a23bb75",
    },
    "submitted": {
        "bytes": 5_668_934,
        "sha256": "dab1834454bd5ff6c17d9240e978084dd2a4f59c5ee02e7ee2ad70d266b65b00",
    },
}


def file_identity(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return {"bytes": size, "sha256": digest.hexdigest()}


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", "" if value is None else str(value))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def address_city_key(address: object, city: object) -> str:
    return f"{normalize(address)}|{normalize(city)}"


def require_identity(label: str, path: Path) -> dict[str, object]:
    observed = file_identity(path)
    expected = EXPECTED_INPUTS[label]
    if observed != expected:
        raise SystemExit(
            f"{label} identity mismatch: expected={expected!r} observed={observed!r}"
        )
    return observed


def read_covered(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_columns = {
        "Building ID",
        "Street",
        "City",
        "Gross Floor Area",
        "Reporting Year",
        "Compliance Status",
    }
    if not rows or set(rows[0]) != expected_columns:
        raise SystemExit("covered CSV columns changed")
    return rows


def read_submitted(path: Path) -> list[dict[str, object]]:
    # The workbook has a title row and a blank row before its real header.
    frame = pd.read_excel(path, sheet_name="2024", header=2, dtype=object)
    required = {
        "Standard ID",
        "Property Name",
        "Address 1",
        "City",
        "Primary Property Type - Portfolio Manager-Calculated",
        "Property GFA - Calculated (Buildings) (ft²)",
        "Report Generation Date",
        "Year Ending",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit(f"submitted workbook columns changed: missing={missing}")
    return frame.to_dict(orient="records")


def clean_scalar(value: object) -> str:
    if pd.isna(value):
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--covered", required=True, type=Path)
    parser.add_argument("--submitted", required=True, type=Path)
    args = parser.parse_args()

    identities = {
        "covered": require_identity("covered", args.covered),
        "submitted": require_identity("submitted", args.submitted),
    }
    covered = read_covered(args.covered)
    submitted = read_submitted(args.submitted)

    covered_keys = [address_city_key(row["Street"], row["City"]) for row in covered]
    submitted_keys = {
        address_city_key(row["Address 1"], row["City"]) for row in submitted
    }
    not_submitted = [
        row
        for row in covered
        if normalize(row["Compliance Status"]) == "not submitted"
    ]
    matched = [
        row
        for row in not_submitted
        if address_city_key(row["Street"], row["City"]) in submitted_keys
    ]

    target_covered = [row for row in covered if row["Building ID"] == "Building #CA012650"]
    target_submitted = [
        row
        for row in submitted
        if clean_scalar(row["Standard ID"]) == "CA012650"
        or address_city_key(row["Address 1"], row["City"])
        == address_city_key("800 bay marina drive", "national city")
    ]
    if len(target_covered) != 1 or len(target_submitted) != 1:
        raise SystemExit(
            "target identity changed: "
            f"covered={len(target_covered)} submitted={len(target_submitted)}"
        )

    submitted_fields = [
        "Standard ID",
        "Property Name",
        "Address 1",
        "City",
        "Primary Property Type - Portfolio Manager-Calculated",
        "Property GFA - Calculated (Buildings) (ft²)",
        "Report Generation Date",
        "Year Ending",
    ]
    result = {
        "schema_version": "cec-prescreen-reproduction/1",
        "input_identity": identities,
        "transformation": {
            "covered_reader": "Python csv.DictReader with utf-8-sig",
            "submitted_reader": "pandas.read_excel sheet=2024 header=2 dtype=object",
            "normalization": (
                "Unicode NFKD; ASCII fold; lowercase; collapse non-[a-z0-9] to spaces; "
                "exact normalized address|city equality"
            ),
        },
        "covered_dataset_profile": {
            "rows": len(covered),
            "reporting_year_counts": dict(
                sorted(Counter(row["Reporting Year"] for row in covered).items())
            ),
            "compliance_status_counts": dict(
                sorted(Counter(row["Compliance Status"] for row in covered).items())
            ),
            "unique_normalized_address_city_keys": len(set(covered_keys)),
        },
        "prior_submission_crosscheck": {
            "submitted_2024_rows": len(submitted),
            "current_not_submitted_rows_with_exact_prior_address_city_match": len(matched),
            "current_not_submitted_unique_keys_with_exact_prior_address_city_match": len(
                {
                    address_city_key(row["Street"], row["City"])
                    for row in matched
                }
            ),
        },
        "selected_target_observations": {
            "covered_2026_row": target_covered[0],
            "submitted_2024_exact_address_city_row": {
                field: clean_scalar(target_submitted[0][field])
                for field in submitted_fields
            },
        },
        "claim_boundary": {
            "supports": [
                "The exact bound raw bytes reproduce the stated row counts, status counts, address-city crosscheck, and selected rows."
            ],
            "does_not_support": [
                "Current status after the download timestamp.",
                "Why a row has its status or who is responsible.",
                "Demand, willingness to pay, delivery feasibility, profit, repeatability, or an asset claim.",
                "Legal advice or authority for external contact or account access.",
            ],
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
