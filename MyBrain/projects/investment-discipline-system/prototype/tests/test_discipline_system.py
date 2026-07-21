from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import json
from decimal import Decimal

from prototype.discipline_system import (
    AppendOnlyLedger,
    Decision,
    Evidence,
    EvidencePacket,
    GateResult,
    PaperOrder,
    PaperReview,
    Recommendation,
    RiskRules,
    evaluate_paper_order,
    record_paper_review,
    record_paper_workflow,
)
from prototype.backtest import (
    BacktestConfig,
    MovingAverageStrategy,
    PricePoint,
    evaluate_split,
    run_phase,
)
from prototype.paper import PaperAccount, PaperOrderRequest
from prototype.workflow import run_gated_paper_workflow
from prototype.run_real_data_case import reusable_result_or_none, validate_required_dates
from prototype.contracts import DataSnapshot, ExecutionResult, LocalPaperExecutionAdapter, MarketRecord
from prototype.research_run import record_backtest_run


def make_packet() -> EvidencePacket:
    return EvidencePacket(
        idea_id="idea-alpha",
        as_of="2026-01-10T12:00:00+00:00",
        evidence=(
            Evidence(
                source="source-a",
                source_type="public filing",
                observed_at="2026-01-10T11:00:00+00:00",
                claim_kind="fact",
                statement="The source contains the stated fact.",
            ),
        ),
        invalidation_conditions=("The stated fact is later contradicted.",),
    )


def make_recommendation() -> Recommendation:
    return Recommendation(
        action="buy",
        thesis="The evidence supports a paper-trading experiment.",
        conditions=("Only paper execution is allowed.",),
        invalidation_conditions=("The core evidence is contradicted.",),
        uncertainty="The result is not established and must be reviewed against a benchmark.",
    )


class PaperWorkflowTests(unittest.TestCase):
    def test_allows_valid_paper_order(self) -> None:
        packet = make_packet()
        recommendation = make_recommendation()
        decision = Decision(
            status="accept",
            rationale="Accept for paper testing.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="buy",
            emotion_note="Calm; no urgency recorded.",
            deviated_from_recommendation=False,
        )
        order = PaperOrder(
            order_id="order-1",
            idea_id="idea-alpha",
            action="buy",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        result = evaluate_paper_order(
            packet,
            recommendation,
            decision,
            order,
            RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
            prior_orders=(),
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.reasons, ())

    def test_rejects_unsafe_order(self) -> None:
        packet = make_packet()
        recommendation = make_recommendation()
        decision = Decision(
            status="accept",
            rationale="Accept for paper testing.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="buy",
            emotion_note="Calm; no urgency recorded.",
            deviated_from_recommendation=False,
        )
        order = PaperOrder(
            order_id="order-2",
            idea_id="idea-alpha",
            action="buy",
            allocation_fraction=0.4,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        result = evaluate_paper_order(
            packet,
            recommendation,
            decision,
            order,
            RiskRules(max_allocation_fraction=0.2, max_orders_per_window=1),
            prior_orders=(
                PaperOrder(
                    order_id="prior",
                    idea_id="other",
                    action="buy",
                    allocation_fraction=0.1,
                    submitted_at="2026-01-10T12:30:00+00:00",
                ),
            ),
        )
        self.assertFalse(result.allowed)
        self.assertIn("allocation exceeds the configured maximum", result.reasons)
        self.assertIn("operation frequency exceeds the configured maximum", result.reasons)

    def test_rejects_actual_request_above_allocation_cap(self) -> None:
        packet = make_packet()
        recommendation = make_recommendation()
        decision = Decision(
            status="accept",
            rationale="Accept for paper testing.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="buy",
            emotion_note="Calm; no urgency recorded.",
            deviated_from_recommendation=False,
        )
        order = PaperOrder(
            order_id="order-actual-cap",
            idea_id="idea-alpha",
            action="buy",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        result = evaluate_paper_order(
            packet,
            recommendation,
            decision,
            order,
            RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
            prior_orders=(),
            actual_allocation_fraction=Decimal("0.3"),
        )
        self.assertFalse(result.allowed)
        self.assertIn("actual requested allocation exceeds the configured maximum", result.reasons)

    def test_rejects_future_information(self) -> None:
        packet = EvidencePacket(
            idea_id="idea-future",
            as_of="2026-01-10T15:00:00+00:00",
            evidence=(),
            invalidation_conditions=("The evidence is contradicted.",),
        )
        recommendation = make_recommendation()
        decision = Decision(
            status="accept",
            rationale="Accept for paper testing.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="buy",
            emotion_note="Calm; no urgency recorded.",
            deviated_from_recommendation=False,
        )
        order = PaperOrder(
            order_id="order-3",
            idea_id="idea-future",
            action="buy",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        result = evaluate_paper_order(
            packet,
            recommendation,
            decision,
            order,
            RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
            prior_orders=(),
        )
        self.assertFalse(result.allowed)
        self.assertIn("evidence packet is newer than the decision", result.reasons)

    def test_allows_human_modified_action_when_recorded(self) -> None:
        packet = make_packet()
        recommendation = make_recommendation()
        decision = Decision(
            status="modify",
            rationale="The human chose the opposite paper action for a controlled rejection-path test.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="sell",
            emotion_note="Recorded disagreement with the original recommendation.",
            deviated_from_recommendation=True,
        )
        order = PaperOrder(
            order_id="order-modified",
            idea_id="idea-alpha",
            action="sell",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        result = evaluate_paper_order(
            packet,
            recommendation,
            decision,
            order,
            RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
            prior_orders=(),
        )
        self.assertTrue(result.allowed)


class LedgerTests(unittest.TestCase):
    def test_records_workflow_and_review_across_reload(self) -> None:
        with TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.jsonl"
            ledger = AppendOnlyLedger(ledger_path)
            packet = make_packet()
            recommendation = make_recommendation()
            decision = Decision(
                status="accept",
                rationale="Accept for paper testing.",
                decided_at="2026-01-10T13:00:00+00:00",
                chosen_action="buy",
                emotion_note="Calm; no urgency recorded.",
                deviated_from_recommendation=False,
            )
            order = PaperOrder(
                order_id="order-4",
                idea_id="idea-alpha",
                action="buy",
                allocation_fraction=0.1,
                submitted_at="2026-01-10T13:01:00+00:00",
            )
            gate = record_paper_workflow(
                packet,
                recommendation,
                decision,
                order,
                RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
                prior_orders=(),
                ledger=ledger,
            )
            self.assertTrue(gate.allowed)
            record_paper_review(
                PaperReview(
                    idea_id="idea-alpha",
                    reviewed_at="2026-02-10T13:00:00+00:00",
                    system_return="0.08",
                    benchmark_return="0.05",
                    executed_as_planned=True,
                    observations=("Paper review completed.",),
                    benchmark_series="SP500",
                    source_snapshot="test-fixture",
                ),
                ledger,
            )

            reloaded = AppendOnlyLedger(ledger_path)
            valid, errors = reloaded.verify()
            self.assertTrue(valid)
            self.assertEqual(errors, ())
            event_types = [record["event_type"] for record in reloaded.records()]
            self.assertIn("paper_order_accepted", event_types)
            self.assertIn("paper_review", event_types)

    def test_detects_tampering(self) -> None:
        with TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.jsonl"
            ledger = AppendOnlyLedger(ledger_path)
            ledger.append("decision", {"idea_id": "idea-alpha", "status": "accept"}, "2026-01-10T13:00:00+00:00")
            ledger.append("gate", {"idea_id": "idea-alpha", "allowed": True}, "2026-01-10T13:01:00+00:00")

            valid, errors = ledger.verify()
            self.assertTrue(valid)
            self.assertEqual(errors, ())

            contents = ledger_path.read_text(encoding="utf-8")
            ledger_path.write_text(contents.replace('"allowed": true', '"allowed": false'), encoding="utf-8")
            valid, errors = ledger.verify()
            self.assertFalse(valid)
            self.assertTrue(errors)


class DataSnapshotTests(unittest.TestCase):
    def test_rejects_missing_required_observation(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing observations"):
            validate_required_dates(
                ["2024-01-01", "2024-01-02"],
                {"2024-01-01": 1},
                "fixture",
            )

    def test_reuses_matching_snapshot(self) -> None:
        with TemporaryDirectory() as directory:
            result_path = Path(directory) / "case_result.json"
            source_files = {"fixture": {"sha256": "abc"}}
            expected = {
                "calculation_version": "v1",
                "source_files": source_files,
                "case_id": "case",
            }
            result_path.write_text(json.dumps(expected), encoding="utf-8")
            self.assertEqual(
                reusable_result_or_none(result_path, "v1", source_files),
                expected,
            )

    def test_rejects_changed_snapshot(self) -> None:
        with TemporaryDirectory() as directory:
            result_path = Path(directory) / "case_result.json"
            result_path.write_text(
                json.dumps(
                    {
                        "calculation_version": "v1",
                        "source_files": {"fixture": {"sha256": "old"}},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "snapshot"):
                reusable_result_or_none(
                    result_path,
                    "v1",
                    {"fixture": {"sha256": "new"}},
                )

    def test_snapshot_separates_observation_and_availability_time(self) -> None:
        snapshot = DataSnapshot(
            snapshot_id="snapshot-1",
            source="fixture",
            source_version="v1",
            retrieved_at="2024-01-02T14:00:00+00:00",
            raw_payload_sha256="hash",
            records=(
                MarketRecord(
                    symbol="DEMO",
                    field="close",
                    value=Decimal("100"),
                    observed_at="2024-01-02T12:00:00+00:00",
                    available_at="2024-01-02T12:30:00+00:00",
                ),
            ),
        )
        self.assertEqual(snapshot.validate_for_decision("2024-01-02T13:00:00+00:00"), ())

    def test_snapshot_rejects_future_available_data(self) -> None:
        snapshot = DataSnapshot(
            snapshot_id="snapshot-2",
            source="fixture",
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
        errors = snapshot.validate_for_decision("2024-01-02T13:00:00+00:00")
        self.assertIn("data was not available by the decision", errors[0])


class ContractTests(unittest.TestCase):
    def test_local_execution_adapter_returns_structured_gate_rejection(self) -> None:
        account = PaperAccount(Decimal("1000"))
        adapter = LocalPaperExecutionAdapter(account)
        request = PaperOrderRequest(
            order_id="contract-buy",
            symbol="DEMO",
            side="buy",
            quantity=Decimal("2"),
            reference_price=Decimal("100"),
            submitted_at="2024-01-02T23:59:00+00:00",
        )
        rejected = adapter.submit(request, GateResult(False, ("blocked",)))
        self.assertEqual(rejected.status, "rejected")
        self.assertEqual(rejected.validate(), ())
        self.assertEqual(account.cash, Decimal("1000"))

    def test_local_execution_adapter_returns_structured_fill(self) -> None:
        account = PaperAccount(Decimal("1000"))
        adapter = LocalPaperExecutionAdapter(account)
        request = PaperOrderRequest(
            order_id="contract-buy",
            symbol="DEMO",
            side="buy",
            quantity=Decimal("2"),
            reference_price=Decimal("100"),
            submitted_at="2024-01-02T23:59:00+00:00",
        )
        filled = adapter.submit(request, GateResult(True, ()))
        self.assertEqual(filled.status, "filled")
        self.assertEqual(filled.validate(), ())
        self.assertEqual(len(filled.fills), 1)


class BacktestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prices = [
            PricePoint(f"2024-01-{day:02d}", Decimal(str(value)))
            for day, value in enumerate((10, 11, 12, 13, 12, 11, 10, 11, 12, 14, 15, 16), start=1)
        ]
        self.benchmark = [
            PricePoint(f"2024-01-{day:02d}", Decimal(str(value)))
            for day, value in enumerate((10, 10, 11, 11, 12, 12, 12, 12, 13, 13, 14, 14), start=1)
        ]

    def test_decisions_cannot_see_future_dates(self) -> None:
        result = run_phase(
            self.prices,
            self.benchmark,
            MovingAverageStrategy(lookback=3),
            "development",
            "2024-01-01",
            "2024-01-08",
            Decimal("0.001"),
        )
        self.assertTrue(result.no_future_information)
        self.assertEqual(result.decision_dates, result.visible_through_dates)

    def test_costs_are_included_in_trade_return(self) -> None:
        free = run_phase(
            self.prices,
            self.benchmark,
            MovingAverageStrategy(lookback=2),
            "free",
            "2024-01-01",
            "2024-01-12",
            Decimal("0"),
        )
        costly = run_phase(
            self.prices,
            self.benchmark,
            MovingAverageStrategy(lookback=2),
            "costly",
            "2024-01-01",
            "2024-01-12",
            Decimal("0.01"),
        )
        self.assertLess(costly.strategy_return, free.strategy_return)

    def test_development_and_holdout_are_separate(self) -> None:
        result = evaluate_split(
            self.prices,
            self.benchmark,
            MovingAverageStrategy(lookback=2),
            BacktestConfig(
                development_start="2024-01-01",
                development_end="2024-01-06",
                holdout_start="2024-01-07",
                holdout_end="2024-01-12",
                transaction_cost_rate=Decimal("0.001"),
            ),
        )
        self.assertEqual(result.development.name, "development")
        self.assertEqual(result.holdout.name, "holdout")
        self.assertLess(result.development.end_date, result.holdout.start_date)

    def test_records_backtest_with_no_future_audit(self) -> None:
        result = evaluate_split(
            self.prices,
            self.benchmark,
            MovingAverageStrategy(lookback=2),
            BacktestConfig(
                development_start="2024-01-01",
                development_end="2024-01-06",
                holdout_start="2024-01-07",
                holdout_end="2024-01-12",
                transaction_cost_rate=Decimal("0.001"),
            ),
        )
        with TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            record_backtest_run(
                result,
                run_id="backtest-fixture",
                strategy_version="moving-average-fixture",
                data_snapshot="fixture-v1",
                occurred_at="2026-02-04T09:01:00+00:00",
                ledger=ledger,
            )
            records = ledger.records()
            self.assertEqual(records[0]["event_type"], "backtest_run")
            self.assertTrue(records[0]["payload"]["development"]["no_future_information"])


class PaperAccountTests(unittest.TestCase):
    def test_only_gate_approved_orders_change_account(self) -> None:
        account = PaperAccount(Decimal("1000"))
        request = PaperOrderRequest(
            order_id="paper-buy",
            symbol="DEMO",
            side="buy",
            quantity=Decimal("2"),
            reference_price=Decimal("100"),
            submitted_at="2024-01-02T23:59:00+00:00",
        )
        with self.assertRaises(PermissionError):
            account.execute(request, GateResult(False, ("blocked",)))
        self.assertEqual(account.cash, Decimal("1000"))
        self.assertEqual(account.positions, ())

        fill = account.execute(request, GateResult(True, ()))
        self.assertEqual(fill.notional, Decimal("200"))
        self.assertEqual(account.cash, Decimal("800"))
        self.assertEqual(account.mark_to_market({"DEMO": Decimal("120")}), Decimal("1040"))

    def test_rejects_selling_more_than_position(self) -> None:
        account = PaperAccount(Decimal("1000"))
        request = PaperOrderRequest(
            order_id="paper-sell",
            symbol="DEMO",
            side="sell",
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            submitted_at="2024-01-02T23:59:00+00:00",
        )
        with self.assertRaisesRegex(ValueError, "insufficient paper position"):
            account.execute(request, GateResult(True, ()))

    def test_rejects_duplicate_order_id(self) -> None:
        account = PaperAccount(Decimal("1000"))
        request = PaperOrderRequest(
            order_id="duplicate-order",
            symbol="DEMO",
            side="buy",
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            submitted_at="2024-01-02T23:59:00+00:00",
        )
        account.execute(request, GateResult(True, ()))
        with self.assertRaisesRegex(ValueError, "duplicate paper order ID"):
            account.execute(request, GateResult(True, ()))

    def test_workflow_cannot_skip_gate_and_records_fill(self) -> None:
        packet = make_packet()
        recommendation = make_recommendation()
        decision = Decision(
            status="accept",
            rationale="Paper workflow integration test.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="buy",
            emotion_note="Calm integration test.",
            deviated_from_recommendation=False,
        )
        paper_order = PaperOrder(
            order_id="workflow-buy",
            idea_id=packet.idea_id,
            action="buy",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        request = PaperOrderRequest(
            order_id="workflow-buy",
            symbol="DEMO",
            side="buy",
            quantity=Decimal("2"),
            reference_price=Decimal("100"),
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        account = PaperAccount(Decimal("1000"))
        with TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            result = run_gated_paper_workflow(
                packet,
                recommendation,
                decision,
                paper_order,
                request,
                RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
                (),
                account,
                ledger,
            )
            self.assertTrue(result.gate.allowed)
            self.assertIsNotNone(result.fill)
            self.assertIsNone(result.execution_error)
            self.assertEqual(account.cash, Decimal("800"))
            self.assertTrue(ledger.verify()[0])
            event_types = [record["event_type"] for record in ledger.records()]
            self.assertIn("paper_fill", event_types)

    def test_workflow_records_execution_failure(self) -> None:
        packet = make_packet()
        recommendation = Recommendation(
            action="sell",
            thesis="The paper position should be reduced.",
            conditions=("Paper execution only.",),
            invalidation_conditions=("The reduction case is no longer relevant.",),
            uncertainty="This is an execution failure fixture.",
        )
        decision = Decision(
            status="accept",
            rationale="Paper workflow failure test.",
            decided_at="2026-01-10T13:00:00+00:00",
            chosen_action="sell",
            emotion_note="Calm failure test.",
            deviated_from_recommendation=False,
        )
        paper_order = PaperOrder(
            order_id="workflow-too-large",
            idea_id=packet.idea_id,
            action="sell",
            allocation_fraction=0.1,
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        request = PaperOrderRequest(
            order_id="workflow-too-large",
            symbol="DEMO",
            side="sell",
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            submitted_at="2026-01-10T13:01:00+00:00",
        )
        account = PaperAccount(Decimal("1000"))
        with TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            result = run_gated_paper_workflow(
                packet,
                recommendation,
                decision,
                paper_order,
                request,
                RiskRules(max_allocation_fraction=0.2, max_orders_per_window=2),
                (),
                account,
                ledger,
            )
            self.assertTrue(result.gate.allowed)
            self.assertIsNone(result.fill)
            self.assertIn("insufficient paper position", result.execution_error or "")
            self.assertEqual(account.cash, Decimal("1000"))
            event_types = [record["event_type"] for record in ledger.records()]
            self.assertIn("paper_execution_failed", event_types)


if __name__ == "__main__":
    unittest.main()
