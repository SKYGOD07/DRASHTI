"""Spike harness for ANPR accuracy on Indian plates. Throwaway code, not production.

Usage:
    pip install -r backend/requirements-ai.txt
    python scripts/spike_anpr.py

Reads JPG frames from data/spike/plates/, runs YOLOv8 (generic object/vehicle
detection -- see NOTE below) -> crop candidate plate region -> EasyOCR -> raw
text. Prints per-image results, then a before/after-correction accuracy
summary to stdout, and appends the same summary to
docs/SPIKE_ANPR_RESULTS.md.

NOTE on the detector: this spike uses a stock YOLOv8n (COCO-pretrained, class
'car'/'truck'/'bus'/'motorcycle') to find the vehicle, then crops the lower-
third of the vehicle box as a naive plate-region guess -- there is no
dedicated Indian-plate detector wired in yet. A real plate detector (either
a fine-tuned YOLOv8 head or an open plate-detection model) is a Day 3 task
once we can see how bad naive cropping actually is. Don't read too much into
absolute numbers from this spike either way -- it's here to find failure
modes, not to certify accuracy.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLATES_DIR = REPO_ROOT / "data" / "spike" / "plates"
RESULTS_DOC = REPO_ROOT / "docs" / "SPIKE_ANPR_RESULTS.md"

# --- Indian plate format + correction machinery -----------------------------

PLATE_REGEX = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$")

# Real Indian RTO state/UT codes (first two letters of the plate).
VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN", "GA", "GJ",
    "HR", "HP", "JK", "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML",
    "MZ", "NL", "OD", "OR", "PB", "PY", "RJ", "SK", "TN", "TS", "TR", "UP",
    "UK", "UA", "WB",
}

# Character confusions observed in OCR of Indian plates (source: brief +
# common ANPR literature). digit_map corrects a char that should be a digit
# but OCR read as a letter; letter_map corrects the reverse.
_TO_DIGIT = {"O": "0", "D": "0", "I": "1", "L": "1", "Z": "2", "S": "5", "B": "8", "G": "6"}
_TO_LETTER = {"0": "O", "1": "I", "2": "Z", "5": "S", "8": "B", "6": "G"}


def correct_plate(raw: str) -> str | None:
    """Positional correction against the Indian plate format, then validate.

    Format: SS DD LLL DDDD (state, RTO code, series letters, number) where
    S/L must be letters and D must be digits. We don't know the exact
    segment boundaries from OCR alone, so this applies a simpler two-pass
    positional rule: first 2 chars must be letters (state code), last 4
    chars must be digits (registration number), everything in between is
    mixed digits/letters (RTO code + series) and is left as-is except for
    obvious single-char confusions.
    """
    s = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if len(s) < 8 or len(s) > 10:
        return None

    chars = list(s)
    # first 2: must be letters (state code)
    for i in (0, 1):
        if chars[i].isdigit():
            chars[i] = _TO_LETTER.get(chars[i], chars[i])
    # last 4: must be digits (registration number)
    for i in range(len(chars) - 4, len(chars)):
        if chars[i].isalpha():
            chars[i] = _TO_DIGIT.get(chars[i], chars[i])

    corrected = "".join(chars)
    if not PLATE_REGEX.match(corrected):
        return None
    if corrected[:2] not in VALID_STATE_CODES:
        return None
    return corrected


# --- main pipeline ------------------------------------------------------------


def main() -> int:
    images = sorted(PLATES_DIR.glob("*.jpg")) + sorted(PLATES_DIR.glob("*.jpeg"))
    if not images:
        print(f"BLOCKED: no JPG frames found in {PLATES_DIR}")
        print("Drop test frames there and re-run. Not fabricating results.")
        return 1

    # Deferred imports -- heavy deps, only needed once we actually have images.
    from ultralytics import YOLO
    import easyocr

    detector = YOLO("yolov8n.pt")
    reader = easyocr.Reader(["en"], gpu=False)

    VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle"}

    n_total = len(images)
    n_detected = 0
    n_ocr_raw_valid = 0
    n_ocr_corrected_valid = 0

    print(f"{'file':<30} {'det_conf':<10} {'raw_ocr':<15} {'corrected':<15} {'time_s':<8}")
    for img_path in images:
        t0 = time.time()
        results = detector(str(img_path), verbose=False)[0]

        best_box = None
        best_conf = 0.0
        for box in results.boxes:
            cls_name = detector.names[int(box.cls[0])]
            conf = float(box.conf[0])
            if cls_name in VEHICLE_CLASSES and conf > best_conf:
                best_conf = conf
                best_box = box

        raw_text = ""
        corrected = None
        if best_box is not None:
            n_detected += 1
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            h = y2 - y1
            plate_crop_y1 = y1 + int(h * 0.66)  # naive: lower third of vehicle box
            import cv2

            img = cv2.imread(str(img_path))
            crop = img[plate_crop_y1:y2, x1:x2]
            ocr_result = reader.readtext(crop)
            if ocr_result:
                raw_text = "".join(t[1] for t in ocr_result).upper().replace(" ", "")
                if PLATE_REGEX.match(re.sub(r"[^A-Z0-9]", "", raw_text)):
                    n_ocr_raw_valid += 1
                corrected = correct_plate(raw_text)
                if corrected:
                    n_ocr_corrected_valid += 1

        elapsed = time.time() - t0
        print(
            f"{img_path.name:<30} {best_conf:<10.2f} {raw_text:<15} "
            f"{corrected or '-':<15} {elapsed:<8.2f}"
        )

    print()
    print("=== Summary ===")
    print(f"Total images:              {n_total}")
    print(f"Plate/vehicle detected:    {n_detected} ({n_detected/n_total:.0%})")
    print(f"Raw OCR format-valid:      {n_ocr_raw_valid} ({n_ocr_raw_valid/n_total:.0%})")
    print(f"Corrected format-valid:    {n_ocr_corrected_valid} ({n_ocr_corrected_valid/n_total:.0%})")
    print()
    print("Write these numbers into docs/SPIKE_ANPR_RESULTS.md by hand -- do not")
    print("auto-generate the narrative, the failure-mode analysis needs a human")
    print("look at the actual images.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
