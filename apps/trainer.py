import re
import cv2
import time
import os
from deepface import DeepFace

from config import *


def is_valid_folder_name(name: str) -> bool:
    """Проверка на запрещенку"""
    if not name or name.strip() == '':
        return False
    forbidden_chars = re.compile(r'[<>:"/\\|?*]')
    return not bool(forbidden_chars.search(name))


"""Фотосессия"""

person_name = input("Введи своё имя: ")
if is_valid_folder_name(person_name):
    save_dir = os.path.join(script_dir, 'dataset', person_name)
    os.makedirs(save_dir, exist_ok=True)
else:
    print("Ты ввёл имя с недопустимыми символами")
    exit()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# СОЗДАЕМ ОКНО ЗАРАНЕЕ И ВЫТАСКИВАЕМ НА ПЕРЕДНИЙ ПЛАН
cv2.namedWindow("Record", cv2.WINDOW_AUTOSIZE)
cv2.setWindowProperty("Record", cv2.WND_PROP_TOPMOST, 1)

last_photo_time = time.time()
photo_interval = 2.5  # Даем 2.5 секунды на смену позы
photo_count = 0
TOTAL_PHOTOS_NEEDED = 5  # Сколько всего фоток сделать

# Флаг для включения вспышки на один кадр
flash_active = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Если сработал флаг вспышки — заливаем экран белым
    if flash_active:
        display_frame = frame.copy()
        display_frame.fill(255)  # 255 — белый цвет во всех каналах
        flash_active = False  # Сразу выключаем, чтобы мигнуло только на 1 кадр
    else:
        display_frame = frame.copy()
        # ИСПРАВЛЕНО: Текст на английском, чтобы шрифт OpenCV его отобразил
        cv2.putText(display_frame, f'LOOK AT THE CAMERA! {photo_count}/{TOTAL_PHOTOS_NEEDED}', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Record", display_frame)

    current_time = time.time()
    if current_time - last_photo_time >= photo_interval:
        last_photo_time = current_time

        faces = DeepFace.extract_faces(img_path=frame, detector_backend='opencv', enforce_detection=False)

        if faces and len(faces) > 0:
            face_img = faces[0]['face']
            face_img = (face_img * 255).astype('uint8')

            photo_path = os.path.join(save_dir, f"face_{photo_count}.jpg")
            cv2.imwrite(photo_path, face_img)
            print(f"[SUCCESS] Сохранено: {photo_path}")

            photo_count += 1
            flash_active = True  # Включаем вспышку для следующего кадра

    # АВТОВЫХОД: Если набрали нужное количество фото — завершаем сессию
    if photo_count >= TOTAL_PHOTOS_NEEDED:
        print(f"\n[SYSTEM] База для {person_name} успешно создана! Закрываемся...")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
