import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import guard as g  # noqa: E402

OK_ACCOUNT = SimpleNamespace(trading_blocked=False, equity="10000", last_equity="10000")


def p(**kw):
    base = {"symbol": "BTC/USD", "side": "buy", "notional_usd": 50, "reason": "test"}
    base.update(kw)
    return base


def test_valid_buy_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert g.guard(p(), OK_ACCOUNT, {}) is None


def test_kill_switch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "STOP").write_text("")
    assert g.guard(p(), OK_ACCOUNT, {}) == "kill switch"


def test_blocked_account(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    acc = SimpleNamespace(trading_blocked=True, equity="1", last_equity="1")
    assert g.guard(p(), acc, {}) == "account blocked"


def test_symbol_not_allowed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert g.guard(p(symbol="DOGE/USD"), OK_ACCOUNT, {}) == "symbol not allowed"


def test_order_too_large_or_zero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert g.guard(p(notional_usd=g.MAX_ORDER_USD + 1), OK_ACCOUNT, {}) == "order size out of range"
    assert g.guard(p(notional_usd=0), OK_ACCOUNT, {}) == "order size out of range"
    assert g.guard(p(notional_usd="lots"), OK_ACCOUNT, {}) == "invalid amount"


def test_position_limit_with_both_symbol_forms(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    positions = {"BTCUSD": g.MAX_POSITION_USD - 10}
    assert g.guard(p(notional_usd=50), OK_ACCOUNT, positions) == "position limit"


def test_cannot_sell_more_than_held(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert g.guard(p(side="sell", notional_usd=50), OK_ACCOUNT, {"BTCUSD": 20}) == "would sell more than held"
    assert g.guard(p(side="sell", notional_usd=10), OK_ACCOUNT, {"BTCUSD": 20}) is None


def test_daily_loss_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    acc = SimpleNamespace(trading_blocked=False, equity="9700", last_equity="10000")
    assert g.guard(p(), acc, {}) == "daily loss limit"


def test_invalid_side(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert g.guard(p(side="short"), OK_ACCOUNT, {}) == "invalid side"
