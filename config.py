import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(script_dir, "dataset")                     # photo dataset
yolo8n_model = os.path.join(script_dir, "models/yolov8n.pt")    # usual model
yolo5s_model = os.path.join(script_dir, "models/yolov8n.pt")    # military model
haarcascades = os.path.join(script_dir, "models/haarcascade_frontalface_default.xml")
