"""Simplified IQ Option API with stubbed behavior for demonstration.

This module provides a minimal yet functional interface that mimics the
behaviour of the real IQ Option API. It is designed for local testing
purposes and does not perform any network communication.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple

try:  # pragma: no cover - optional dependency
    import pandas as pd
except Exception:  # pragma: no cover - pandas is optional
    pd = None


class SymbolNotFoundError(Exception):
    """Raised when an unknown symbol is requested."""


class OrderConflictError(Exception):
    """Raised when an order cannot be found or modified."""


class APIUnavailableError(Exception):
    """Raised when the (simulated) API is unavailable."""


@dataclass
class Order:
    """Simple order representation."""

    id: int
    symbol: str
    direction: str
    amount: float
    status: str = "open"
    result: float = 0.0


class IQOption:
    """Minimal implementation of a trading API for local testing."""

    def __init__(
        self,
        email: str,
        password: str,
        account_type: str = "DEMO",
        *,
        fail_chance: float = 0.0,
        max_retries: int = 3,
    ) -> None:
        self.email = email
        self.password = password
        self.account_type = account_type
        self._balance = 1000.0 if account_type.upper() == "DEMO" else 0.0
        self._orders: Dict[int, Order] = {}
        self._order_counter = 0
        self.fail_chance = fail_chance
        self.max_retries = max_retries
        self.available_symbols = ["EURUSD", "USDJPY", "GBPUSD"]

        self.logger = logging.getLogger("ejtraderIQ")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s:%(name)s:%(message)s")
            )
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # internal helpers
    def _simulate_api_call(self) -> None:
        if random.random() < self.fail_chance:
            self.logger.error("API unavailable")
            raise APIUnavailableError("API unavailable")

    def _with_retry(self, func: Callable, *args, **kwargs):
        attempts = 0
        while True:
            try:
                self._simulate_api_call()
                return func(*args, **kwargs)
            except APIUnavailableError:
                attempts += 1
                if attempts >= self.max_retries:
                    raise
                self.logger.info("Retrying after API error")

    # ------------------------------------------------------------------
    def balance(self) -> float:
        """Return current account balance."""

        return self._balance

    # ------------------------------------------------------------------
    def get_real_time_quote(self, symbol: str):
        """Return a single price quote for *symbol*."""

        def _impl():
            if symbol not in self.available_symbols:
                raise SymbolNotFoundError(symbol)
            price = round(1 + random.random() / 100, 6)
            data = {"symbol": symbol, "price": price, "time": datetime.utcnow()}
            if pd is not None:
                return pd.DataFrame([data]).set_index("time")
            return [data]

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def get_history(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict] | "pd.DataFrame":
        """Return generated candle history for *symbol* between two dates."""

        def _impl():
            if symbol not in self.available_symbols:
                raise SymbolNotFoundError(symbol)
            if start_date >= end_date:
                raise ValueError("start_date must be before end_date")
            data = []
            current = start_date
            price = 1.0
            while current <= end_date:
                open_p = price
                high_p = open_p + random.random() / 1000
                low_p = open_p - random.random() / 1000
                close_p = low_p + random.random() * (high_p - low_p)
                volume = random.randint(100, 500)
                data.append(
                    {
                        "time": current,
                        "open": round(open_p, 6),
                        "high": round(high_p, 6),
                        "low": round(low_p, 6),
                        "close": round(close_p, 6),
                        "volume": volume,
                    }
                )
                current += timedelta(minutes=1)
                price = close_p
            if pd is not None:
                return pd.DataFrame(data).set_index("time")
            return data

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def get_payout_estimate(self, symbol: str) -> float:
        """Return a dummy payout percentage for *symbol*."""

        def _impl():
            if symbol not in self.available_symbols:
                raise SymbolNotFoundError(symbol)
            return 0.80

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def stream_market_depth(self, symbol: str, callback: Callable[[Dict], None]) -> None:
        """Generate a single market depth update and invoke *callback*."""

        def _impl():
            if symbol not in self.available_symbols:
                raise SymbolNotFoundError(symbol)
            depth = {"bid": random.randint(1, 5), "ask": random.randint(1, 5)}
            callback(depth)
            return depth

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def place_order(self, symbol: str, direction: str, amount: float) -> int:
        """Place an order and return its identifier."""

        def _impl():
            if symbol not in self.available_symbols:
                raise SymbolNotFoundError(symbol)
            if direction not in {"buy", "sell"}:
                raise ValueError("direction must be 'buy' or 'sell'")
            if amount <= 0:
                raise ValueError("amount must be positive")
            self._order_counter += 1
            order_id = self._order_counter
            order = Order(order_id, symbol, direction, amount)
            self._orders[order_id] = order
            self._balance -= amount
            self.logger.info("Order %s placed", order_id)
            return order_id

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def check_order_status(self, order_id: int) -> Tuple[str, float]:
        """Return the current status of an order."""

        def _impl():
            order = self._orders.get(order_id)
            if not order:
                raise OrderConflictError(f"Unknown order {order_id}")
            if order.status == "open":
                order.status = random.choice(["win", "loss", "open"])
                if order.status == "win":
                    payout = self.get_payout_estimate(order.symbol)
                    order.result = order.amount * payout
                    self._balance += order.amount + order.result
                elif order.status == "loss":
                    order.result = -order.amount
                else:
                    order.result = 0.0
            return order.status, order.result

        return self._with_retry(_impl)

    # ------------------------------------------------------------------
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an open order."""

        def _impl():
            order = self._orders.get(order_id)
            if not order:
                raise OrderConflictError(f"Unknown order {order_id}")
            if order.status != "open":
                raise OrderConflictError("Order cannot be cancelled")
            order.status = "cancelled"
            self._balance += order.amount
            order.result = 0.0
            self.logger.info("Order %s cancelled", order_id)
            return True

        return self._with_retry(_impl)

