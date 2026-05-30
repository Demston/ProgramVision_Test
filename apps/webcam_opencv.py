import cv2
import numpy as np
from config import *

# Camera init (0-default, 1,2 etc - ext)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("rtsp://admin:password@192.168.1.100:554/stream") # connection to ip cam

# Check the webcam has opened
if not cap.isOpened():
    print("Camera don't open")
    exit()

face_cascade = cv2.CascadeClassifier(haarcascades)

# Standart detection of people

#  DefaultPeopleDetector
# hog = cv2.HOGDescriptor()     # Histogram of Oriented Gradients
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

#  DaimlerPeopleDetector
hog = cv2.HOGDescriptor((48, 96), (16, 16), (8, 8), (8, 8), 9)  # Histogram of Oriented Gradients
detector = cv2.HOGDescriptor.getDaimlerPeopleDetector()
hog.setSVMDetector(np.array(detector, dtype=np.float32))
"""(48, 96) — размер самого окна (ширина и высота). Именно под этот размер обучен детектор Daimler.
(16, 16) — размер блока. Окно делится на блоки для нормализации освещения (чтобы тени не мешали).
(8, 8) — шаг блока (cell stride).
(8, 8) — размер «ячейки» (cell). Внутри каждой ячейки считаются направления линий.
9 — количество направлений (ориентаций) градиента. Представь розу ветров, только для направлений линий в кадре."""

# frame center
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
screen_center_x = frame_width // 2

while True:
    # Frame capture
    ret, frame = cap.read()     # ret - logical flag (True/False)

    if not ret:
        print("Error: Failed to get frame")
        break

    # Converting a frame to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #  DefaultPeopleDetector
    # rects, weights = hog.detectMultiScale(img=frame_gray, hitThreshold=0.1, winStride=(8, 8),
    #                                       padding=(8, 8), scale=1.1, groupThreshold=2.0)

    #  DaimlerPeopleDetector
    rects, weights = hog.detectMultiScale(
        img=frame_gray,
        hitThreshold=0.5,     # 0.8 # Сделали "строже"
        winStride=(8, 8),
        padding=(8, 8),
        scale=1.05,
        groupThreshold=10  # 6 Склеиваем рамки (было 2.0)
    )

    # Finding faces
    faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=9, minSize=(35, 35))

    #  DefaultPeopleDetector
    # for (x, y, w, h) in rects:
    #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #  DaimlerPeopleDetector
    # for (x, y, w, h) in rects:
    #     # Рисовать только если высота объекта больше, например, 1/3 высоты кадра
    #     if h > frame.shape[0] / 3:
    #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # for (x, y, w, h) in faces:
    #     # Parametrs (кадр, (x, y) верхнего левого угла, (x+w, y+h) нижнего правого, цвет (BGR), толщина линии)
    #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

    # 1. Сначала отрисуем лица (белым), как и было
    for (fx, fy, fw, fh) in faces:
        cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (255, 255, 255), 2)

    # 2. А теперь логика для туловища с проверкой на лицо
    for (hx, hy, hw, hh) in rects:
        # Проверка на размер (чтобы не ловить мелочь)
        if hh > frame.shape[0] / 3:

            is_real_person = False

            # Проверяем каждое найденное лицо
            for (fx, fy, fw, fh) in faces:
                # Условие: центр лица находится внутри границ туловища
                face_center_x = fx + fw // 2
                face_center_y = fy + fh // 2

                if hx < face_center_x < hx + hw and hy < face_center_y < hy + hh:
                    is_real_person = True
                    break  # Одно лицо нашли — человек подтвержден

            if is_real_person:
                # ВЫЧИСЛЯЕМ ЦЕНТР ЧЕЛОВЕКА
                obj_center_x = hx + hw // 2

                # РИСУЕМ ПРИЦЕЛ (линия от центра экрана к тебе)
                mid_y = frame.shape[0] // 2
                cv2.line(frame, (screen_center_x, mid_y), (obj_center_x, mid_y), (0, 255, 255), 2)

                # ВЫЧИСЛЯЕМ ОТКЛОНЕНИЕ (на сколько пикселей ты не в центре)
                error_x = obj_center_x - screen_center_x

                # ВЫВОДИМ КОМАНДУ ДЛЯ БУДУЩЕГО МОТОРА
                if abs(error_x) > 50:  # 50 - это "мертвая зона", чтобы камера не дергалась по мелочам
                    direction = "MOVE LEFT" if error_x < 0 else "MOVE RIGHT"
                    cv2.putText(frame, direction, (screen_center_x - 50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # Рисуем рамку туловища
            # Зеленый если подтвержден, оранжевый если просто "силуэт"
            if is_real_person:
                color = (0, 255, 0)
                thickness = 3
                label = "Human Confirmed"   # Добавим текст для солидности
            # else:
            #     color = (0, 165, 255)
            #     thickness = 1
            # label = "Unknown Silhouette"

                cv2.rectangle(frame, (hx, hy), (hx + hw, hy + hh), color, thickness)
                cv2.putText(frame, label, (hx, hy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Frame view (optional: processing)
    cv2.imshow('Camera Feed', frame)

    # Exit by 'q' or 'ESC'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Resource release
cap.release()
cv2.destroyAllWindows()
