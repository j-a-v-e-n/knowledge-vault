from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from prototype.discipline_system import AppendOnlyLedger, GateResult


Side = Literal["buy", "sell"]


@dataclass(frozen=True)
class PaperOrderRequest:
    order_id: str
    symbol: str
    side: Side
    quantity: Decimal
    reference_price: Decimal
    submitted_at: str


@dataclass(frozen=True)
class PaperPosition:
    symbol: str
    quantity: Decimal
    average_price: Decimal


@dataclass(frozen=True)
class PaperFill:
    order_id: str
    symbol: str
    side: Side
    quantity: Decimal
    price: Decimal
    notional: Decimal
    submitted_at: str


class PaperAccount:
    """A local-only paper account.

    This class has no network, broker, or live-order method by design.
    """

    def __init__(self, initial_cash: Decimal):
        if initial_cash <= 0:
            raise ValueError("initial cash must be positive")
        self.cash = initial_cash
        self._positions: dict[str, PaperPosition] = {}
        self.fills: list[PaperFill] = []

    @property
    def positions(self) -> tuple[PaperPosition, ...]:
        return tuple(self._positions.values())

    def execute(
        self,
        request: PaperOrderRequest,
        gate: GateResult,
        ledger: AppendOnlyLedger | None = None,
    ) -> PaperFill:
        if not gate.allowed:
            raise PermissionError("paper execution blocked by risk gate")
        if any(fill.order_id == request.order_id for fill in self.fills):
            raise ValueError("duplicate paper order ID")
        if request.quantity <= 0 or request.reference_price <= 0:
            raise ValueError("quantity and reference price must be positive")

        notional = request.quantity * request.reference_price
        current = self._positions.get(request.symbol)
        if request.side == "buy":
            if notional > self.cash:
                raise ValueError("insufficient paper cash")
            new_quantity = (current.quantity if current else Decimal("0")) + request.quantity
            old_notional = (
                current.quantity * current.average_price if current else Decimal("0")
            )
            average_price = (old_notional + notional) / new_quantity
            self.cash -= notional
            self._positions[request.symbol] = PaperPosition(
                symbol=request.symbol,
                quantity=new_quantity,
                average_price=average_price,
            )
        else:
            if current is None or request.quantity > current.quantity:
                raise ValueError("insufficient paper position")
            remaining = current.quantity - request.quantity
            self.cash += notional
            if remaining == 0:
                del self._positions[request.symbol]
            else:
                self._positions[request.symbol] = PaperPosition(
                    symbol=request.symbol,
                    quantity=remaining,
                    average_price=current.average_price,
                )

        fill = PaperFill(
            order_id=request.order_id,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            price=request.reference_price,
            notional=notional,
            submitted_at=request.submitted_at,
        )
        self.fills.append(fill)
        if ledger is not None:
            ledger.append(
                "paper_fill",
                {
                    "order_id": fill.order_id,
                    "symbol": fill.symbol,
                    "side": fill.side,
                    "quantity": str(fill.quantity),
                    "price": str(fill.price),
                    "notional": str(fill.notional),
                    "cash_after": str(self.cash),
                },
                fill.submitted_at,
            )
        return fill

    def mark_to_market(self, prices: dict[str, Decimal]) -> Decimal:
        value = self.cash
        for position in self._positions.values():
            if position.symbol not in prices:
                raise ValueError(f"missing mark price for {position.symbol}")
            value += position.quantity * prices[position.symbol]
        return value
