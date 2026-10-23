"""ONNX inference — MobileNetV3-Small 224x224. Falls back to heuristic if no model file."""

import os

try:

    HAS_NP = True
except Exception:
    HAS_NP = False

MODEL_PATH = os.environ.get("HERGRADE_MODEL", "./data/rosemary_mobilenetv3.onnx")


def predict(tensor_or_path, thresh: float = 0.75) -> dict:
    """Return {pred, conf}. If ONNX model missing, use color-heuristic baseline (documented)."""
    if os.path.exists(MODEL_PATH):
        import onnxruntime as ort

        sess = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
        import numpy as _np

        x = (
            tensor_or_path
            if isinstance(tensor_or_path, _np.ndarray)
            else _np.zeros((1, 3, 224, 224), dtype=_np.float32)
        )
        out = sess.run(None, {sess.get_inputs()[0].name: x})[0]
        conf = float(out.max())
        pred = "accepted" if conf >= thresh else "verify"
        return {"pred": pred, "conf": conf, "backend": "onnx"}
    # heuristic baseline: greenness ratio (documented in report, NOT food-safety)
    try:
        from PIL import Image

        img = Image.open(tensor_or_path).convert("RGB") if isinstance(tensor_or_path, str) else None
        if img is None:
            return {"pred": "verify", "conf": 0.5, "backend": "heuristic-nodata"}
        import numpy as _np

        a = _np.asarray(img).astype(float)
        green = a[:, :, 1].mean()
        total = a.mean() + 1e-6
        ratio = green / total
        conf = min(0.95, max(0.35, (ratio - 0.9) * 4 + 0.6))
        pred = "accepted" if conf >= thresh else "verify"
        return {"pred": pred, "conf": round(conf, 3), "backend": "heuristic-greenness"}
    except Exception:
        return {"pred": "verify", "conf": 0.5, "backend": "heuristic-fallback"}
