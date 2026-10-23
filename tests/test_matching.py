"""Matching T-M1..M7 — must pass before freeze."""

from app.services.matching import hard_filter, propose


def base_req():
    return {
        "herb_type": "rosemary",
        "qty_need_g": 20000,
        "grade_required": "premium",
        "harvest_from": "2026-10-15",
        "harvest_to": "2026-10-25",
        "max_price": 14.0,
        "needs_qr": True,
    }


def base_lot(**kw):
    d = {
        "id": "lot-x",
        "batch_id": "batch-x",
        "producer_id": "prod-A",
        "herb_type": "rosemary",
        "grade": "premium",
        "avail_g": 11000,
        "harvest_date": "2026-10-20",
        "qr_id": "batch-x",
        "status": "published",
        "unit_ask": 12.0,
        "visual_sim": 0.85,
        "delivery_band": "region",
    }
    d.update(kw)
    return d


def test_m1_collective_11_plus_9():
    req = base_req()
    lots = [
        base_lot(id="lot-A", batch_id="batch-A11", producer_id="prod-A", avail_g=11000),
        base_lot(id="lot-B", batch_id="batch-B09", producer_id="prod-B", avail_g=9000),
    ]
    out = propose(req, lots)
    assert out["total_g"] == 20000 and not out["partial"]
    assert sum(l["qty_g"] for l in out["lines"]) == 20000
    assert not out["mixed_grades"]


def test_m2_reject_wrong_herb():
    ok, reason = hard_filter(base_req(), base_lot(herb_type="mint"))
    assert not ok and reason == "herb_mismatch"


def test_m3_reject_low_grade():
    ok, reason = hard_filter(base_req(), base_lot(grade="standard"))
    assert not ok and reason == "grade_below_required"


def test_m4_reject_old_harvest():
    ok, reason = hard_filter(base_req(), base_lot(harvest_date="2026-09-01"))
    assert not ok and reason == "harvest_too_old"


def test_m5_reject_no_avail():
    ok, reason = hard_filter(base_req(), base_lot(avail_g=0))
    assert not ok and reason == "unavailable"


def test_m6_missing_qr():
    ok, reason = hard_filter(base_req(), base_lot(qr_id=""))
    assert not ok and reason == "missing_qr"


def test_m7_mixed_grades_flagged_not_merged():
    req = base_req()
    req["grade_required"] = "standard"
    lots = [
        base_lot(id="lot-A", grade="premium", avail_g=11000),
        base_lot(id="lot-B", batch_id="batch-b", grade="standard", avail_g=9000),
    ]
    out = propose(req, lots)
    assert out["mixed_grades"] is True
    assert len({l["grade"] for l in out["lines"]}) == 2
