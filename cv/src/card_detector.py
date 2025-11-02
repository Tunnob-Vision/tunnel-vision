import os
import tempfile
import sys

os.environ["OPENCV_DISABLE_QT"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Force use of opencv-python-headless by prioritizing it in sys.path
# This prevents libGL.so.1 errors on Streamlit Cloud when both packages are installed
if 'cv2' not in sys.modules:
    try:
        import pkg_resources
        import site
        
        # Find both opencv packages
        headless_pkg = None
        regular_pkg = None
        
        for pkg in pkg_resources.working_set:
            if pkg.key == 'opencv-python-headless':
                headless_pkg = pkg
            elif pkg.key == 'opencv-python':
                regular_pkg = pkg
        
        # If both are installed, prioritize headless version
        if headless_pkg and regular_pkg:
            # Insert headless package location at the beginning of sys.path
            # so it's found before the regular opencv-python
            headless_location = headless_pkg.location
            if headless_location not in sys.path or sys.path.index(headless_location) > 0:
                if headless_location in sys.path:
                    sys.path.remove(headless_location)
                sys.path.insert(0, headless_location)
    except Exception:
        pass  # If package detection fails, proceed with normal import

# Now import cv2 - it should use the headless version if both are installed
try:
    import cv2
except ImportError as e:
    if 'libGL' in str(e):
        raise ImportError(
            "OpenCV import failed due to missing libGL.so.1. "
            "Please ensure 'opencv-python-headless' is installed and 'opencv-python' is removed."
        ) from e
    raise

from ultralytics import YOLO
from PIL import Image
import streamlit as st

@st.cache_resource
def load_model():
    """Load and cache the YOLO model."""
    model_path = os.path.join("models", "best.pt")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return YOLO(model_path)

model = load_model()

def run_inference(image_file):
    """Run YOLOv8 inference on the given image file."""
    img = Image.open(image_file).convert("RGB")

    temp_path = tempfile.mktemp(suffix=".jpg")
    img.save(temp_path)

    with st.spinner("🔍 Detecting cards... please wait"):
        results = model.predict(source=temp_path, conf=0.4)

    boxes_image = results[0].plot()
    detections = []

    for box in results[0].boxes:
        cls_name = results[0].names[int(box.cls)]
        conf = float(box.conf)
        detections.append({"class": cls_name, "confidence": conf})

    return boxes_image, detections
