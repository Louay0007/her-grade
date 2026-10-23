"""Capture: fixed exposure UVC camera, save data/batches/<id>/img_<uuid>.jpg."""

import os
import uuid

try:
    import cv2

    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


def open_camera(index: int = 0, width: int = 1280, height: int = 720):
    if not HAS_CV2:
        return None
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual-ish; lock on bench
    return cap


def capture_to_batch(cap, batch_id: str, out_dir: str = "./data/batches") -> str:
    d = os.path.join(out_dir, batch_id)
    os.makedirs(d, exist_ok=True)
    fname = f"img_{uuid.uuid4().hex[:8]}.jpg"
    path = os.path.join(d, fname)
    if cap is None or not HAS_CV2:
        # placeholder for offline test: write 1px jpg via pillow
        try:
            from PIL import Image

            Image.new("RGB", (224, 224), (60, 120, 60)).save(path)
        except Exception:
            open(path, "wb").write(b"")
        return path
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("camera read failed")
    import cv2 as _cv2

    _cv2.imwrite(path, frame)
    return path
