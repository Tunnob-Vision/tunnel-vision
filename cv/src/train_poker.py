import os
from ultralytics import YOLO
import zipfile

zip_path = os.path.join(os.path.dirname(__file__), "dataset.zip")
dataset_folder = os.path.join(os.path.dirname(__file__), "dataset")

if not os.path.exists(dataset_folder) or not os.listdir(dataset_folder):
    print(f"Unzipping {zip_path} ...")
    os.makedirs(dataset_folder, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dataset_folder)
else:
    print(f"Dataset already unzipped at {dataset_folder}, skipping unzip.")

print("✅ Dataset location:", dataset_folder)
print(os.listdir(dataset_folder))

model = YOLO("yolov8n.pt")  # or yolov8s.pt for higher accuracy
data_yaml = os.path.join(dataset_folder, "data.yaml")

if not os.path.exists(data_yaml):
    raise FileNotFoundError(f"Could not find {data_yaml}. Make sure the zip contains data.yaml.")

model.train(
    data=data_yaml,
    epochs=50,  # Adjust for faster or longer training
    imgsz=640, # Adjust for faster or more accurate training
    batch=16,
    name="poker_cards"
)
