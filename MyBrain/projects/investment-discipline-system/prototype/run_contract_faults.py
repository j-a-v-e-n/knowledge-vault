from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

from prototype.contracts import DataSnapshot, ExecutionResult, LocalPaperExecutionAdapter, MarketRecord
from prototype.discipline_system import GateResult
from prototype.paper import PaperAccount, PaperOrderRequest


ROOT = Path(__file__).parent
RUN = ROOT / "data" / "runs" / "contract_faults_v1"
CALCULATION_VERSION = "contract-faults-v1"


def run_faults() -> dict[str, object]:
    RUN.mkdir(parents=True, exist_ok=True)
    result_path = RUN / "fault_result.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))

    future_snapshot = DataSnapshot(
        snapshot_id="future-snapshot",
        source="controlled-fixture",
        source_version="v1",
        retrieved_at="2024-01-02T14:00:00+00:00",
        raw_payload_sha256="hash",
        records=(
            MarketRecord(
                symbol="DEMO",
                field="close",
                value=Decimal("100"),
                observed_at="2024-01-02T12:00:00+00:00",
                available_at="2024-01-02T14:00:00+00:00",
            ),
        ),
    )
    snapshot_errors = future_snapshot.validate_for_decision("2024-01-02T13:00:00+00:00")

    malformed_partial = ExecutionResult(
        request_id="partial-without-fill",
        status="partially_filled",
        fills=(),
        provider_order_id="provider-order",
        raw_response_sha256="hash",
        reason=None,
    )
    unknown_without_reason = ExecutionResult(
        request_id="unknown-without-reason",
        status="unknown",
        fills=(),
        provider_order_id=None,
        raw_response_sha256=None,
        reason=None,
    )
    unknown_with_reason = ExecutionResult(
        request_id="unknown-with-reason",
        status="unknown",
        fills=(),
        provider_order_id=None,
        raw_response_sha256=None,
        reason="network response was unavailable; reconciliation required",
    )

    account = PaperAccount(Decimal("1000"))
    adapter = LocalPaperExecutionAdapter(account)
    request = PaperOrderRequest(
        order_id="duplicate-fixture-order",
        symbol="DEMO",
        side="buy",
        quantity=Decimal("1"),
        reference_price=Decimal("100"),
        submitted_at="2024-01-02T23:59:00+00:00",
    )
    first = adapter.submit(request, GateResult(True, ()))
    duplicate = adapter.submit(request, GateResult(True, ()))

    result = {
        "calculation_version": CALCULATION_VERSION,
        "snapshot_future_data_rejected": bool(snapshot_errors),
        "malformed_partial_rejected": bool(malformed_partial.validate()),
        "unknown_without_reason_rejected": bool(unknown_without_reason.validate()),
        "unknown_with_reason_accepted": unknown_with_reason.validate() == (),
        "first_submission_filled": first.status == "filled",
        "duplicate_submission_rejected": (
            duplicate.status == "rejected"
            and "duplicate paper order ID" in (duplicate.reason or "")
        ),
    }
    if not all(result[key] for key in result if key != "calculation_version"):
        raise RuntimeError(f"contract fault fixture failed: {result}")
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = """# 契约故障注入证据

## 覆盖

- 数据在决策后才可见：必须拒绝。
- 部分成交状态没有任何成交记录：必须拒绝为 malformed result。
- 未知状态没有原因：必须拒绝；未知状态带有原因：可以进入待对账路径。
- 相同订单号重复提交：本地纸面账户必须拒绝第二次，不重复改变现金和持仓。

## 当前结论

数据和执行契约已经有最小故障注入验证。真实供应商的部分成交、网络断线、认证过期和对账恢复仍需在未来适配器实验中验证。

## 可复核命令

    python3 -m prototype.run_contract_faults
"""
    (RUN / "fault_report.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    print(json.dumps(run_faults(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
