from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from typing import Literal, Sequence


Action = Literal["buy", "sell", "hold", "no_trade", "wait"]
DecisionStatus = Literal["accept", "reject", "defer", "modify"]


def _parse_time(value: str) -> int:
    normalized = value.replace("Z", "+00:00")
    from datetime import datetime

    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return int(parsed.timestamp() * 1_000_000)


@dataclass(frozen=True)
class Evidence:
    source: str
    source_type: str
    observed_at: str
    claim_kind: Literal["fact", "inference", "assumption", "unknown"]
    statement: str
    url: str = ""


@dataclass(frozen=True)
class EvidencePacket:
    idea_id: str
    as_of: str
    evidence: tuple[Evidence, ...]
    invalidation_conditions: tuple[str, ...]
    version: str = "prototype"

    def validate_before(self, decision_time: str) -> list[str]:
        decision_stamp = _parse_time(decision_time)
        reasons: list[str] = []
        if _parse_time(self.as_of) > decision_stamp:
            reasons.append("evidence packet is newer than the decision")
        for item in self.evidence:
            if _parse_time(item.observed_at) > decision_stamp:
                reasons.append(f"evidence from {item.source} is newer than the decision")
        if not self.invalidation_conditions:
            reasons.append("missing invalidation conditions")
        return reasons


@dataclass(frozen=True)
class Recommendation:
    action: Action
    thesis: str
    conditions: tuple[str, ...]
    invalidation_conditions: tuple[str, ...]
    uncertainty: str
    version: str = "prototype"


@dataclass(frozen=True)
class Decision:
    status: DecisionStatus
    rationale: str
    decided_at: str
    chosen_action: Action
    emotion_note: str
    deviated_from_recommendation: bool


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    idea_id: str
    action: Literal["buy", "sell"]
    allocation_fraction: float
    submitted_at: str


@dataclass(frozen=True)
class RiskRules:
    max_allocation_fraction: float
    max_orders_per_window: int
    require_invalidation_conditions: bool = True
    version: str = "prototype"


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PaperReview:
    idea_id: str
    reviewed_at: str
    system_return: str
    benchmark_return: str
    executed_as_planned: bool
    observations: tuple[str, ...]
    benchmark_series: str
    source_snapshot: str

    @property
    def relative_difference(self) -> Decimal:
        return Decimal(self.system_return) - Decimal(self.benchmark_return)


def evaluate_paper_order(
    packet: EvidencePacket,
    recommendation: Recommendation,
    decision: Decision,
    order: PaperOrder,
    rules: RiskRules,
    prior_orders: Sequence[PaperOrder],
    actual_allocation_fraction: Decimal | None = None,
) -> GateResult:
    reasons: list[str] = []

    if decision.status not in {"accept", "modify"}:
        reasons.append("decision did not authorize a paper action")
    expected_deviation = decision.chosen_action != recommendation.action
    if decision.deviated_from_recommendation != expected_deviation:
        reasons.append("deviation flag does not match the chosen action")
    if not decision.emotion_note.strip():
        reasons.append("decision is missing an emotion or impulse note")
    if order.idea_id != packet.idea_id:
        reasons.append("order does not match the evidence packet")
    if order.action != decision.chosen_action:
        reasons.append("order does not match the human decision")
    allocation = Decimal(str(order.allocation_fraction))
    max_allocation = Decimal(str(rules.max_allocation_fraction))
    if allocation <= 0:
        reasons.append("allocation must be positive")
    if allocation > max_allocation:
        reasons.append("allocation exceeds the configured maximum")
    if actual_allocation_fraction is not None and actual_allocation_fraction > max_allocation:
        reasons.append("actual requested allocation exceeds the configured maximum")
    if len(prior_orders) >= rules.max_orders_per_window:
        reasons.append("operation frequency exceeds the configured maximum")
    if rules.require_invalidation_conditions:
        if not packet.invalidation_conditions:
            reasons.append("evidence packet has no invalidation conditions")
        if not recommendation.invalidation_conditions:
            reasons.append("recommendation has no invalidation conditions")
    reasons.extend(packet.validate_before(decision.decided_at))
    if _parse_time(order.submitted_at) < _parse_time(decision.decided_at):
        reasons.append("paper order predates the human decision")

    return GateResult(allowed=not reasons, reasons=tuple(dict.fromkeys(reasons)))


def record_paper_workflow(
    packet: EvidencePacket,
    recommendation: Recommendation,
    decision: Decision,
    order: PaperOrder,
    rules: RiskRules,
    prior_orders: Sequence[PaperOrder],
    ledger: "AppendOnlyLedger",
    actual_allocation_fraction: Decimal | None = None,
) -> GateResult:
    ledger.append("evidence_packet", asdict(packet), packet.as_of)
    ledger.append("recommendation", asdict(recommendation), decision.decided_at)
    ledger.append("decision", asdict(decision), decision.decided_at)
    gate = evaluate_paper_order(
        packet,
        recommendation,
        decision,
        order,
        rules,
        prior_orders,
        actual_allocation_fraction=actual_allocation_fraction,
    )
    ledger.append(
        "risk_gate",
        {
            "allowed": gate.allowed,
            "reasons": list(gate.reasons),
            "order_id": order.order_id,
            "rules_version": rules.version,
            "packet_version": packet.version,
            "recommendation_version": recommendation.version,
            "actual_allocation_fraction": (
                str(actual_allocation_fraction)
                if actual_allocation_fraction is not None
                else None
            ),
        },
        order.submitted_at,
    )
    ledger.append(
        "paper_order_accepted" if gate.allowed else "paper_order_rejected",
        asdict(order),
        order.submitted_at,
    )
    return gate


def record_paper_review(review: PaperReview, ledger: "AppendOnlyLedger") -> None:
    ledger.append("paper_review", asdict(review), review.reviewed_at)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


class AppendOnlyLedger:
    """A tamper-evident JSONL ledger for the prototype.

    This detects changes to the recorded chain; it does not provide absolute
    immutability against an actor who can rewrite the entire file and its
    verification environment.
    """

    genesis = "GENESIS"

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _last_hash(self) -> str:
        if not self.path.exists():
            return self.genesis
        last = ""
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last = json.loads(line)["event_hash"]
        return last or self.genesis

    def append(self, event_type: str, payload: dict[str, object], occurred_at: str) -> str:
        previous_hash = self._last_hash()
        body = {
            "occurred_at": occurred_at,
            "event_type": event_type,
            "payload": payload,
            "previous_hash": previous_hash,
        }
        event_hash = sha256(_canonical_bytes(body)).hexdigest()
        record = {**body, "event_hash": event_hash}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return event_hash

    def records(self) -> tuple[dict[str, object], ...]:
        if not self.path.exists():
            return ()
        records: list[dict[str, object]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return tuple(records)

    def verify(self) -> tuple[bool, tuple[str, ...]]:
        if not self.path.exists():
            return True, ()
        expected_previous = self.genesis
        errors: list[str] = []
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                body = {
                    "occurred_at": record["occurred_at"],
                    "event_type": record["event_type"],
                    "payload": record["payload"],
                    "previous_hash": record["previous_hash"],
                }
                expected_hash = sha256(_canonical_bytes(body)).hexdigest()
                if record["previous_hash"] != expected_previous:
                    errors.append(f"line {line_number}: broken previous hash")
                if record["event_hash"] != expected_hash:
                    errors.append(f"line {line_number}: event hash mismatch")
                expected_previous = record["event_hash"]
            except (KeyError, json.JSONDecodeError, TypeError):
                errors.append(f"line {line_number}: malformed record")
        return not errors, tuple(errors)
