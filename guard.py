"""Risk guard: plain code that every model proposal must pass before an order is sent.

The model can be wrong or manipulated (prompt injection). Limits that matter live here,
not in the prompt. Tune the numbers to your own paper account.
"""
import os

ALLOWED = {"BTC/USD", "ETH/USD"}
MAX_ORDER_USD = 100.0
MAX_POSITION_USD = 500.0
MAX_DAILY_LOSS_USD = 200.0
STOP_FILE = "STOP"  # create this file to stop all trading (kill switch)


def norm(symbol: str) -> str:
    """Alpaca reports crypto positions as BTCUSD or BTC/USD depending on endpoint."""
    return symbol.replace("/", "").upper()


def guard(p: dict, account, positions: dict) -> str | None:
    """Return None if the order may go through, otherwise the reason it is rejected.

    p          proposal from the model: symbol, side, notional_usd, reason
    account    object with .trading_blocked, .equity, .last_equity (Alpaca TradeAccount)
    positions  {normalised symbol: market value in USD}
    """
    if os.path.exists(STOP_FILE):
        return "kill switch"
    if account.trading_blocked:
        return "account blocked"
    if p.get("symbol") not in ALLOWED:
        return "symbol not allowed"
    if p.get("side") not in ("buy", "sell"):
        return "invalid side"
    try:
        notional = float(p.get("notional_usd"))
    except (TypeError, ValueError):
        return "invalid amount"
    if not 0 < notional <= MAX_ORDER_USD:
        return "order size out of range"
    held = positions.get(norm(p["symbol"]), 0.0)
    if p["side"] == "buy" and held + notional > MAX_POSITION_USD:
        return "position limit"
    if p["side"] == "sell" and notional > held:
        return "would sell more than held"
    if float(account.equity) - float(account.last_equity) <= -MAX_DAILY_LOSS_USD:
        return "daily loss limit"
    return None
