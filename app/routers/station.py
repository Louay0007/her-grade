"""Station: Mode A/B switch + serial status + e-stop tracking (software mirror; HW e-stop cuts motor power)."""

from fastapi import APIRouter

from .. import schemas
from ..config import settings
from ..services.serial_link import get_link

router = APIRouter()
STATE = {"mode": "B", "estop": False}


@router.get("/status")
def status():
    link = get_link(settings.serial_port, settings.serial_baud)
    return {
        "mode": STATE["mode"],
        "estop": STATE["estop"],
        "serial_connected": link.connected,
        "thresh": settings.thresh_version,
        "note": "E-stop cuts motor power in hardware. This flag is a software mirror only.",
    }


@router.post("/mode")
def set_mode(body: schemas.ModeIn):
    link = get_link(settings.serial_port, settings.serial_baud)
    STATE["mode"] = body.mode
    r = link.set_mode(body.mode)
    return {"mode": body.mode, "serial": r}


@router.post("/stop")
def stop(reason: str = "operator"):
    link = get_link(settings.serial_port, settings.serial_baud)
    r = link.stop(reason)
    return {"stopped": True, "serial": r}


@router.post("/resume")
def resume():
    link = get_link(settings.serial_port, settings.serial_baud)
    STATE["estop"] = False
    return {"resumed": True, "serial": link.resume()}


@router.post("/estop")
def estop():
    link = get_link(settings.serial_port, settings.serial_baud)
    STATE["estop"] = True
    link.stop("estop_pressed")
    return {
        "estop": True,
        "warning": "Restart requires deliberate local button + resume. HW relay cuts motor power.",
    }
