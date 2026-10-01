"""Round-scoped CNY reservations for paid model calls.

Prices are supplied and confirmed by the user. This ledger is an application
soft limit; it cannot replace a provider-side spending limit or final invoice.
"""

from __future__ import annotations

import fcntl
import json
import os
import uuid
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path
from typing import Any, Dict


MICRO = Decimal(1000000)
LIMITS = {"integration": 15_000_000, "goal": 25_000_000, "repair": 10_000_000}


class CostLedger:
    def __init__(self, workspace: Path):
        root = Path(workspace)
        self.prices_path = root / ".muse_model_prices.json"
        self.ledger_path = root / ".muse_model_cost_ledger.json"
        self.lock_path = root / ".muse_model_cost.lock"

    @contextmanager
    def _lock(self):
        with self.lock_path.open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    @staticmethod
    def _write(path: Path, value: Dict[str, Any]) -> None:
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, path)

    @staticmethod
    def _rate(value: Any) -> str:
        try:
            rate = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("invalid_model_price") from exc
        if not rate.is_finite() or rate < 0 or rate > 100000:
            raise ValueError("invalid_model_price")
        return str(rate)

    def configure_price(self, *, profile_id: str, model: str, protocol: str,
                        origin: str, input_cny_per_million: Any,
                        output_cny_per_million: Any, source: str,
                        confirmed: bool) -> Dict[str, Any]:
        if (not all(isinstance(x, str) and x.strip() for x in
                    (profile_id, model, protocol, origin, source)) or not confirmed
                or len(source) > 500):
            raise ValueError("price_confirmation_required")
        price = {"profile_id": profile_id, "model": model, "protocol": protocol,
                 "origin": origin, "input_cny_per_million": self._rate(input_cny_per_million),
                 "output_cny_per_million": self._rate(output_cny_per_million),
                 "source": source.strip(), "currency": "CNY"}
        with self._lock():
            prices = self._read_prices()
            prices[profile_id] = price
            self._write(self.prices_path, {"version": 1, "prices": prices})
        return dict(price)

    def _read_prices(self) -> Dict[str, Dict[str, Any]]:
        if not self.prices_path.exists():
            return {}
        try:
            state = json.loads(self.prices_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("invalid_price_state") from exc
        if not isinstance(state, dict) or state.get("version") != 1 or not isinstance(state.get("prices"), dict):
            raise ValueError("invalid_price_state")
        return state["prices"]

    def price_for(self, profile_id: str, model: str, protocol: str, origin: str) -> Dict[str, Any]:
        with self._lock():
            price = self._read_prices().get(profile_id, {})
            if any(price.get(key) != value for key, value in
                   (("profile_id", profile_id), ("model", model),
                    ("protocol", protocol), ("origin", origin))):
                raise ValueError("cost_unknown")
            self._rate(price.get("input_cny_per_million"))
            self._rate(price.get("output_cny_per_million"))
            return price

    def prices(self) -> Dict[str, Dict[str, Any]]:
        with self._lock():
            return self._read_prices()

    @staticmethod
    def _micros(price: Dict[str, Any], input_tokens: int, output_tokens: int) -> int:
        if min(input_tokens, output_tokens) < 0:
            raise ValueError("invalid_model_usage")
        amount = (Decimal(input_tokens) * Decimal(price["input_cny_per_million"])
                  + Decimal(output_tokens) * Decimal(price["output_cny_per_million"]))
        return int(amount.to_integral_value(rounding=ROUND_CEILING))

    def _read(self) -> Dict[str, Any]:
        if not self.ledger_path.exists():
            return {"version": 1, "spent_micros": {key: 0 for key in LIMITS},
                    "reservations": {}}
        try:
            state = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            if (isinstance(state, dict) and state.get("version") == 1 and isinstance(state.get("reservations"), dict)
                    and isinstance(state.get("spent_micros"), dict)
                    and all(type(state["spent_micros"].get(key)) is int
                            and state["spent_micros"][key] >= 0 for key in LIMITS)
                    and all(isinstance(item, dict) and item.get("bucket") in LIMITS
                            and type(item.get("micros")) is int and item["micros"] >= 0
                            and item.get("status") in {"reserved", "uncertain"}
                            for item in state["reservations"].values())):
                return state
        except (OSError, ValueError, TypeError):
            pass
        raise ValueError("invalid_cost_ledger")

    def reserve(self, price: Dict[str, Any], input_token_bound: int,
                max_output_tokens: int, bucket: str) -> tuple[str, int]:
        if bucket not in LIMITS or type(input_token_bound) is not int or input_token_bound < 1 or \
                type(max_output_tokens) is not int or max_output_tokens < 1:
            raise ValueError("invalid_cost_reservation")
        micros = self._micros(price, input_token_bound, max_output_tokens)
        with self._lock():
            state = self._read()
            outstanding = sum(item["micros"] for item in state["reservations"].values()
                              if item["bucket"] == bucket)
            if state["spent_micros"][bucket] + outstanding + micros > LIMITS[bucket]:
                raise ValueError("model_money_budget_exhausted")
            reservation_id = uuid.uuid4().hex
            state["reservations"][reservation_id] = {"bucket": bucket, "micros": micros,
                                                       "status": "reserved"}
            self._write(self.ledger_path, state)
            return reservation_id, micros

    def settle(self, reservation_id: str, price: Dict[str, Any],
               input_tokens: int, output_tokens: int) -> int:
        actual = self._micros(price, input_tokens, output_tokens)
        with self._lock():
            state = self._read()
            item = state["reservations"].pop(reservation_id, None)
            if item is None:
                raise ValueError("cost_reservation_missing")
            state["spent_micros"][item["bucket"]] += actual
            self._write(self.ledger_path, state)
        return actual

    def uncertain(self, reservation_id: str) -> None:
        with self._lock():
            state = self._read()
            item = state["reservations"].get(reservation_id)
            if item is not None:
                item["status"] = "uncertain"
                self._write(self.ledger_path, state)

    def status(self) -> Dict[str, Any]:
        with self._lock():
            state = self._read()
        reserved = {key: sum(item["micros"] for item in state["reservations"].values()
                             if item["bucket"] == key) for key in LIMITS}
        return {"currency": "CNY", "limit_micros": sum(LIMITS.values()),
                "bucket_limits_micros": dict(LIMITS), "spent_micros": state["spent_micros"],
                "reserved_micros": reserved,
                "remaining_micros": sum(LIMITS.values()) - sum(state["spent_micros"].values())
                                    - sum(reserved.values()),
                "uncertain_count": sum(item["status"] == "uncertain"
                                       for item in state["reservations"].values()),
                "alert_80_percent": sum(state["spent_micros"].values()) + sum(reserved.values())
                                    >= 40_000_000}
