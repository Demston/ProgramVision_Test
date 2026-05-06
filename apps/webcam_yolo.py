import cv2
from ultralytics import YOLO

# Загружаем модель (nano-версия — самая быстрая)
# При первом запуске она сама скачается из инета (около 6 МБ)
model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Узнаем центр кадра
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

# "Мертвая зона" в пикселях (чтобы мотор не дрожал в центре)
DEADZONE = 40


while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    annotated_frame = frame

    # 2. Магия: распознавание и отрисовка одной строкой
    # stream=True помогает видео идти плавнее
    results = model.predict(frame, verbose=False, stream=True)

    best_target = None
    min_distance = float('inf')     # Начальное расстояние — бесконечность

    for r in results:
        for box in r.boxes:

            # 1. Получаем ID класса (0 - это всегда человек в YOLO)
            cls = int(box.cls[0])

            # 2. ФИЛЬТР: Работаем только если это человек
            if cls == 0:
                # Координаты рамки
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Точка прицеливания (центр объекта)
                target_x = x1 + (x2 - x1) // 2
                target_y = y1 + (y2 - y1) // 3  # Целимся в торс

                # Считаем расстояние от центра экрана до этой цели (гипотенуза)
                dist = ((target_x - CENTER_X)**2 + (target_y - CENTER_Y)**2)**0.5

                # Если этот человек ближе к центру, чем предыдущqий — запоминаем его
                if dist < min_distance:
                    min_distance = dist
                    best_target = (x1, y1, x2, y2, target_x, target_y)

    # ОТРИСОВКА (только для одного лучшего кандидата)
    if best_target:
        x1, y1, x2, y2, target_x, target_y = best_target

        # Вычисляем ошибку (смещение от центра экрана)
        error_x = target_x - CENTER_X
        error_y = target_y - CENTER_Y

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Рамка вокруг цели
        cv2.circle(frame, (target_x, target_y), 5, (0, 255, 0), -1)  # Точка в центре цели
        cv2.line(frame, (CENTER_X, CENTER_Y), (target_x, target_y), (0, 255, 255), 2)  # Линия наведения

        cv2.putText(frame, f"TARGET X: {CENTER_X}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 3. Логика для будущего железа
        if abs(error_x) > DEADZONE:
            cmd = f"MOVE {'RIGHT' if error_x > 0 else 'LEFT'} by {abs(error_x)} px"
            cv2.putText(frame, cmd, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Одной строкой, все объекты. Только отрисовка.
        # annotated_frame = r.plot()    # возвращает кадр с уже нарисованными рамками и подписями

    # Статичный прицел центра экрана
    cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (255, 255, 255), cv2.MARKER_CROSS, 20, 2)
    # cv2.imshow("YOLOv8 Real-Time", annotated_frame)
    cv2.imshow("Auto AIM", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
