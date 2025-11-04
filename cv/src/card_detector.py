import os
import tempfile
import sys
import subprocess

os.environ["OPENCV_DISABLE_QT"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"

if 'cv2' not in sys.modules:
    try:
        try:
            from importlib.metadata import distributions
            installed_packages = {dist.metadata['Name']: dist for dist in distributions()}
        except ImportError:
            import pkg_resources
            installed_packages = {pkg.key: pkg for pkg in pkg_resources.working_set}

        has_opencv = 'opencv-python' in installed_packages
        has_headless = 'opencv-python-headless' in installed_packages

        if has_opencv and has_headless:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if 'cv2' in sys.modules:
                    del sys.modules['cv2']
                import importlib
                if 'cv2' in sys.modules:
                    del sys.modules['cv2']
            except Exception:
                pass
    except Exception:
        pass

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
