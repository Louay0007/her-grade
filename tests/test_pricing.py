"""Pricing — Ctotal/Mkg/Mtotal + below-cost warn."""

from app.services.pricing import calc


def test_basic_margin():
    out = calc({"cprod": 8.0, "cproc": 0, "cpack": 1.0, "ctrans": 0.5, "cfees": 0.5}, 12.0, 20)
    assert out["ctotal"] == 10.0 and out["mkg"] == 2.0 and out["mtotal"] == 40.0
    assert out["below_cost"] is False


def test_below_cost_warn():
    out = calc({"cprod": 9, "cproc": 1, "cpack": 1, "ctrans": 1, "cfees": 0.5}, 11.0, 10)
    assert out["below_cost"] is True and out["mtotal"] < 0


def test_zero_qty():
    out = calc({"cprod": 5}, 8.0, 0)
    assert out["mtotal"] == 0
