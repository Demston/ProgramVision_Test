import os

# === НАСТРОЙКИ ПРИЛОЖЕНИЯ ===
script_dir = os.path.dirname(os.path.abspath(__file__))

yolo8n_model = os.path.join(script_dir, "models/yolov8n.pt")                            # usual yolo model
yolo5s_model = os.path.join(script_dir, "models/yolov8n.pt")                            # military yolo model
haarcascades = os.path.join(script_dir, "models/haarcascade_frontalface_default.xml")   # haar cascadeS
DB_PATH = os.path.join(script_dir, "dataset")                                           # dataset photo path
ALERTS_DIR = os.path.join(script_dir, "alerts")                                         # strange photo path
ALERT_IMG_PATH = os.path.normpath(os.path.join(script_dir, "alerts", "alert.jpg"))      # strange photo default name

# === НАСТРОЙКИ ТЕЛЕГРАМА ===
BOT_TOKEN = "ТОКЕН_БОТА"
CHAT_ID = "ЛИЧНЫЙ_CHAT_ID"

# === НАСТРОЙКИ СЕТЕВОГО МОСТА ===
LISTEN_PORT = 5006
LOCALHOST = "127.0.0.1"
