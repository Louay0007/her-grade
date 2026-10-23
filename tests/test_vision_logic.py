"""Vision decision Mode A/B — red alert vs verify divert."""

from app.services.vision_service import decide


def test_confident_accepted_both_modes():
    for m in ("A", "B"):
        d = decide("accepted", 0.9, thresh=0.75, mode=m)
        assert d["target"] == "accepted"


def test_uncertain_modeA_stops():
    d = decide("accepted", 0.5, thresh=0.75, mode="A")
    assert d["action"] == "stop_alert" and d["target"] == "verify"


def test_uncertain_modeB_diverts():
    d = decide("accepted", 0.5, thresh=0.75, mode="B")
    assert d["action"] == "divert_verify"


def test_overlap_always_verify():
    d = decide("accepted", 0.99, mode="B", overlap=True)
    assert d["target"] == "verify"
