"""Matching engine: hard filter -> rank -> combine -> explain. Pure functions, no DB."""

GRADE_ORDER = {"standard": 0, "premium": 1}


def hard_filter(req: dict, lot: dict):
    """Return (ok, reason). Never merge different grades silently."""
    if lot["herb_type"] != req["herb_type"]:
        return False, "herb_mismatch"
    if lot["avail_g"] <= 0 or lot.get("status") not in ("published", "ready"):
        return False, "unavailable"
    if GRADE_ORDER.get(lot["grade"], 0) < GRADE_ORDER.get(req["grade_required"], 0):
        return False, "grade_below_required"
    if req.get("harvest_from") and lot["harvest_date"] < req["harvest_from"]:
        return False, "harvest_too_old"
    if req.get("harvest_to") and lot["harvest_date"] > req["harvest_to"]:
        return False, "harvest_too_new"
    if req.get("needs_qr") and not lot.get("qr_id"):
        return False, "missing_qr"
    return True, "ok"


def score(req: dict, lot: dict) -> dict:
    visual = min(1.0, max(0.0, lot.get("visual_sim", 0.7)))
    date_fit = 1.0  # simplified Phase 1; refine with window math
    delivery = {"same": 1.0, "region": 0.7, "far": 0.4}.get(lot.get("delivery_band", "region"), 0.7)
    price_ok = 1.0 if lot.get("unit_ask", 0) <= req.get("max_price", 9999) else 0.5
    total = 0.35 * visual + 0.25 * date_fit + 0.20 * delivery + 0.20 * price_ok
    return {
        "total": round(total, 3),
        "visual": visual,
        "date": date_fit,
        "delivery": delivery,
        "price": price_ok,
    }


def propose(req: dict, lots: list) -> dict:
    cands, excluded = [], []
    for lot in lots:
        ok, reason = hard_filter(req, lot)
        if ok:
            cands.append((score(req, lot)["total"], lot))
        else:
            excluded.append({"lot_id": lot["id"], "reason": reason})
    cands.sort(key=lambda x: x[0], reverse=True)
    lines, total = [], 0
    for s, lot in cands:
        if total >= req["qty_need_g"]:
            break
        take = min(lot["avail_g"], req["qty_need_g"] - total)
        lines.append(
            {
                "lot_id": lot["id"],
                "batch_id": lot["batch_id"],
                "producer_id": lot["producer_id"],
                "qty_g": take,
                "unit_price": lot.get("unit_ask"),
                "score": s,
                "grade": lot.get("grade"),
            }
        )
        total += take
    grades = {ln["grade"] for ln in lines}
    return {
        "lines": lines,
        "total_g": total,
        "partial": total < req["qty_need_g"],
        "missing_g": req["qty_need_g"] - total,
        "mixed_grades": len(grades) > 1,
        "excluded": excluded,
    }
