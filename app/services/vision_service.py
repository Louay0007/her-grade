"""Vision decision — visual screening only. No food-safety claim."""


def decide(
    pred: str,
    conf: float,
    thresh: float = 0.75,
    mode: str = "B",
    area_ok: bool = True,
    overlap: bool = False,
) -> dict:
    """Return {target, action, reason}. Mode A: uncertain->stop+red alert. Mode B: uncertain->verify+continue."""
    if not area_ok or overlap:
        return {
            "target": "verify",
            "action": "divert_verify" if mode == "B" else "stop_alert",
            "reason": "gate_invalid_area_or_overlap",
            "conf": conf,
        }
    if pred == "accepted" and conf >= thresh:
        return {
            "target": "accepted",
            "action": "divert_accepted",
            "reason": "confident_accepted",
            "conf": conf,
        }
    # uncertain / verify
    if mode == "A":
        return {
            "target": "verify",
            "action": "stop_alert",
            "reason": "uncertain_modeA_stop",
            "conf": conf,
        }
    return {
        "target": "verify",
        "action": "divert_verify",
        "reason": "uncertain_modeB_verify",
        "conf": conf,
    }
