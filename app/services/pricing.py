"""Price calculator: support tool, not market authority."""


def calc(costs: dict, psale: float, qty_kg: float) -> dict:
    ctotal = sum(costs.get(k, 0) for k in ("cprod", "cproc", "cpack", "ctrans", "cfees"))
    mkg = psale - ctotal
    return {
        "ctotal": round(ctotal, 2),
        "mkg": round(mkg, 2),
        "mtotal": round(mkg * qty_kg, 2),
        "below_cost": psale < ctotal,
        "disclaimer": "Estimate from entered costs only. Illustrative until field validation.",
    }
