from __future__ import annotations

from dataclasses import dataclass

from prototype.discipline_system import (
    AppendOnlyLedger,
    Decision,
    EvidencePacket,
    GateResult,
    PaperOrder,
    Recommendation,
    RiskRules,
    record_paper_workflow,
)
from prototype.contracts import ExecutionResult, LocalPaperExecutionAdapter
from prototype.paper import PaperAccount, PaperFill, PaperOrderRequest


@dataclass(frozen=True)
class WorkflowResult:
    gate: GateResult
    fill: PaperFill | None
    execution_error: str | None
    execution: ExecutionResult | None = None


def run_gated_paper_workflow(
    packet: EvidencePacket,
    recommendation: Recommendation,
    decision: Decision,
    paper_order: PaperOrder,
    request: PaperOrderRequest,
    rules: RiskRules,
    prior_orders: tuple[PaperOrder, ...],
    account: PaperAccount,
    ledger: AppendOnlyLedger,
) -> WorkflowResult:
    gate = record_paper_workflow(
        packet,
        recommendation,
        decision,
        paper_order,
        rules,
        prior_orders,
        ledger,
        actual_allocation_fraction=(
            request.quantity * request.reference_price / account.cash
            if request.side == "buy" and account.cash > 0
            else None
        ),
    )
    if not gate.allowed:
        return WorkflowResult(gate=gate, fill=None, execution_error=None, execution=None)
    if paper_order.order_id != request.order_id:
        error = "paper order and execution request have different order IDs"
        ledger.append(
            "paper_execution_failed",
            {"order_id": paper_order.order_id, "reason": error},
            request.submitted_at,
        )
        execution = ExecutionResult(
            request_id=request.order_id,
            status="rejected",
            fills=(),
            provider_order_id=None,
            raw_response_sha256=None,
            reason=error,
        )
        return WorkflowResult(gate=gate, fill=None, execution_error=error, execution=execution)
    execution = LocalPaperExecutionAdapter(account, ledger).submit(request, gate)
    if execution.status == "rejected":
        error = execution.reason or "paper execution rejected"
        ledger.append(
            "paper_execution_failed",
            {"order_id": request.order_id, "reason": error},
            request.submitted_at,
        )
        return WorkflowResult(gate=gate, fill=None, execution_error=error, execution=execution)
    fill = execution.fills[0] if execution.fills else None
    return WorkflowResult(gate=gate, fill=fill, execution_error=None, execution=execution)
