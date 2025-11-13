import os
import tempfile
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

def remove_duplicate_cards(detections):
    """Ensure only one detection per card class (highest confidence kept)."""
    unique = {}
    for det in detections:
        cls = det["class"]
        if cls not in unique or det["confidence"] > unique[cls]["confidence"]:
            unique[cls] = det
    return list(unique.values())

def run_inference(image_file):
    """Run YOLOv8 inference on the given image file and remove duplicate detections."""
    img = Image.open(image_file).convert("RGB")
    width, height = img.size

    temp_path = tempfile.mktemp(suffix=".jpg")
    img.save(temp_path)

    with st.spinner("🔍 Detecting cards... please wait"):
        results = model.predict(source=temp_path, conf=0.4)

    detections = []

    for box in results[0].boxes:
        cls_name = results[0].names[int(box.cls)]
        conf = float(box.conf)
        xyxy = box.xyxy[0].cpu().numpy().tolist()
        detections.append({
            "class": cls_name,
            "confidence": conf,
            "bbox": xyxy
        })

    valid_detections = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        if 0 <= x1 < width and 0 <= y1 < height and 0 < x2 <= width and 0 < y2 <= height:
            valid_detections.append(det)
    detections = valid_detections

    detections = remove_duplicate_cards(detections)

    boxes_image = results[0].plot()

    return boxes_image, detections
