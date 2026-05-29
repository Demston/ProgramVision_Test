import os
import cv2
import threading
from deepface import DeepFace

current_user = "UNKNOWN"  # Здесь храним имя распознанного
lock = threading.Lock()
is_processing = False

miss_counter = 0     # Счетчик "неузнаваний" подряд
MAX_MISSES = 2       # Допустимое число промахов, пока не включится тревога (секунды)


def _async_worker(person_crop, db_path):
    global is_processing, miss_counter, current_user
    try:
        # Запуск верификации. enforce_detection=False спасет от падений, если лицо смазано
        dfs = DeepFace.find(img_path=person_crop, db_path=db_path,
                            enforce_detection=False, silent=True)
        match_name = "UNKNOWN"

        # Проверяем, что вернулся список и он не пустой
        if isinstance(dfs, list) and len(dfs) > 0:
            df = dfs[0]  # Берем первый датафрейм из списка результатов
            if not df.empty:  # Проверяем, есть ли там хоть одна строка с совпадением
                matched_file_path = df['identity'].values[0]  # Вытаскиваем путь к самой первой совпавшей фотке из базы
                # Магия os.path: берем имя папки, в которой лежит этот файл (получим "Bruce")
                match_name = os.path.basename(os.path.dirname(matched_file_path))

        with lock:
            if match_name != "UNKNOWN":
                current_user = match_name
                miss_counter = 0  # Сброс счетчика, раз лицо успешно опознано
            else:
                miss_counter += 1
                # Теряем доверие только если накопили серию промахов подряд
                if miss_counter >= MAX_MISSES:
                    current_user = "UNKNOWN"

    except Exception as e:
        # Выводим ошибку в консоль, если она вдруг случится
        print(f"[ERROR] Ошибка биометрии: {e}")
        with lock:
            miss_counter += 1
            if miss_counter >= MAX_MISSES:
                current_user = False

    is_processing = False


def verify_face_async(frame, box, db_path):
    global is_processing

    if is_processing:
        return get_auth_status()

    x1, y1, x2, y2 = box
    h, w, _ = frame.shape

    # Заставляем брать координаты YOLO целиком, просто защищаясь от вылета за края экрана
    y1_safe, y2_safe = max(0, y1), min(h, y2)
    x1_safe, x2_safe = max(0, x1), min(w, x2)

    # Вырезаем силуэт полностью — вблизи это будут голова и плечи, удаленно — весь рост
    person_crop = frame[y1_safe:y2_safe, x1_safe:x2_safe]

    if person_crop.size == 0:
        return get_auth_status()

    is_processing = True
    t = threading.Thread(target=_async_worker, args=(person_crop, db_path), daemon=True)
    t.start()

    return get_auth_status()  # вернет имя или "UNKNOWN"


def get_auth_status():
    with lock:
        return current_user
