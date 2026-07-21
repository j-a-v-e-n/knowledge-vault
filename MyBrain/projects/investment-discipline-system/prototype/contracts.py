from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal, Protocol

from prototype.discipline_system import AppendOnlyLedger, GateResult
from prototype.paper import PaperAccount, PaperFill, PaperOrderRequest


def _timestamp_value(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return int(parsed.timestamp() * 1_000_000)


@dataclass(frozen=True)
class SnapshotQuery:
    symbols: tuple[str, ...]
    fields: tuple[str, ...]
    start: str
    end: str
    decision_time: str


@dataclass(frozen=True)
class MarketRecord:
    symbol: str
    field: str
    value: Decimal
    observed_at: str
    available_at: str


@dataclass(frozen=True)
class DataSnapshot:
    snapshot_id: str
    source: str
    source_version: str
    retrieved_at: str
    raw_payload_sha256: str
    records: tuple[MarketRecord, ...]

    def validate_for_decision(self, decision_time: str) -> tuple[str, ...]:
        decision_stamp = _timestamp_value(decision_time)
        errors: list[str] = []
        if not self.snapshot_id.strip():
            errors.append("snapshot is missing an ID")
        if not self.source.strip():
            errors.append("snapshot is missing a source")
        if not self.source_version.strip():
            errors.append("snapshot is missing a source version")
        if not self.raw_payload_sha256.strip():
            errors.append("snapshot is missing a raw payload hash")
        if not self.records:
            errors.append("snapshot has no records")
        for record in self.records:
            if _timestamp_value(record.observed_at) > decision_stamp:
                errors.append(f"{record.symbol} observation is newer than the decision")
            if _timestamp_value(record.available_at) > decision_stamp:
                errors.append(f"{record.symbol} data was not available by the decision")
        return tuple(dict.fromkeys(errors))


class DataSource(Protocol):
    def get_snapshot(self, query: SnapshotQuery) -> DataSnapshot:
        """Return a frozen, hash-identified snapshot for the requested query."""


ExecutionStatus = Literal["filled", "partially_filled", "rejected", "unknown"]


@dataclass(frozen=True)
class ExecutionResult:
    request_id: str
    status: ExecutionStatus
    fills: tuple[PaperFill, ...]
    provider_order_id: str | None
    raw_response_sha256: str | None
    reason: str | None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.request_id.strip():
            errors.append("execution result is missing a request ID")
        if self.status in {"filled", "partially_filled"} and not self.fills:
            errors.append("filled execution result has no fills")
        if self.status == "rejected" and self.fills:
            errors.append("rejected execution result contains fills")
        if self.status == "unknown" and not self.reason:
            errors.append("unknown execution result is missing a reason")
        return tuple(errors)


class ExecutionAdapter(Protocol):
    def submit(self, request: PaperOrderRequest, gate: GateResult) -> ExecutionResult:
        """Submit only a gate-approved request and return a structured result."""


class LocalPaperExecutionAdapter:
    """Adapt the local paper account to the provider-neutral execution contract."""

    def __init__(self, account: PaperAccount, ledger: AppendOnlyLedger | None = None):
        self.account = account
        self.ledger = ledger

    def submit(self, request: PaperOrderRequest, gate: GateResult) -> ExecutionResult:
        try:
            fill = self.account.execute(request, gate, self.ledger)
        except (PermissionError, ValueError) as exc:
            result = ExecutionResult(
                request_id=request.order_id,
                status="rejected",
                fills=(),
                provider_order_id=None,
                raw_response_sha256=None,
                reason=str(exc),
            )
            return result
        return ExecutionResult(
            request_id=request.order_id,
            status="filled",
            fills=(fill,),
            provider_order_id=None,
            raw_response_sha256=None,
            reason=None,
        )
