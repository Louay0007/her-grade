"""Serial link — USB 115200 JSONL, mock fallback for offline demo/tests."""

import json
import queue
import time


class SerialLink:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.mode = "B"
        self.outbox = []  # sent messages (for tests/demo)
        self.inbox = queue.Queue()
        self.connected = False
        self._hb = None
        try:
            import serial  # type: ignore

            self.ser = serial.Serial(port, baud, timeout=0.2)
            self.connected = True
        except Exception:
            self.ser = None
            self.connected = False  # mock mode

    def _send(self, obj: dict) -> dict:
        line = json.dumps(obj)
        self.outbox.append(obj)
        if self.ser:
            try:
                self.ser.write((line + "\n").encode())
            except Exception as e:
                return {"ok": False, "mock": False, "error": str(e)}
            return {"ok": True, "mock": False, "sent": obj}
        return {"ok": True, "mock": True, "sent": obj}

    def set_mode(self, mode: str):
        assert mode in ("A", "B")
        self.mode = mode
        return self._send({"t": "mode", "mode": mode, "ts": time.time()})

    def divert(self, evt_id: str, target: str):
        assert target in ("accepted", "verify")
        return self._send({"t": "divert", "id": evt_id, "target": target, "ts": time.time()})

    def stop(self, reason: str):
        return self._send({"t": "stop", "reason": reason, "ts": time.time()})

    def resume(self):
        return self._send({"t": "resume", "ts": time.time()})

    def heartbeat_tick(self):
        return self._send({"t": "hb", "mode": self.mode, "ts": time.time()})


_link = None


def get_link(port="/dev/ttyUSB0", baud=115200) -> SerialLink:
    global _link
    if _link is None:
        _link = SerialLink(port, baud)
    return _link
