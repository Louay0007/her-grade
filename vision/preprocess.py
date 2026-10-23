"""Preprocess: ROI crop, denoise, HSV mask, largest contour, area/overlap gate."""

try:
    import cv2

    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


def gate_contour(area: float, count: int, min_area: float = 1200, max_area: float = 90000) -> tuple:
    """Return (ok, reason). Invalid -> auto verify, no guess."""
    if count != 1:
        return False, f"count_{count}_expected_1"
    if area < min_area:
        return False, "area_too_small"
    if area > max_area:
        return False, "area_too_large"
    return True, "ok"


def preprocess_roi(image, roi=(80, 80, 480, 480)):
    """Crop ROI, return 224x224 normalized array + gate info. Falls back gracefully without cv2."""
    if not HAS_CV2:
        return {"ok": True, "reason": "no_cv2_passthrough", "size": (224, 224)}
    x0, y0, x1, y1 = roi
    h, w = image.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    crop = image[y0:y1, x0:x1]
    blur = cv2.GaussianBlur(crop, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # green vegetation mask (rosemary) — tuned on bench, documented in dataset_card
    mask = cv2.inRange(hsv, (25, 30, 30), (90, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {"ok": False, "reason": "no_contour", "size": (224, 224)}
    biggest = max(contours, key=cv2.contourArea)
    area = float(cv2.contourArea(biggest))
    ok, reason = gate_contour(area, len(contours))
    resized = cv2.resize(crop, (224, 224))
    norm = resized.astype("float32") / 255.0
    return {
        "ok": ok,
        "reason": reason,
        "area": area,
        "count": len(contours),
        "tensor": norm,
    }
