import socket
from datetime import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *


def network_listener(our_bot):
    """Работает в фоне. Слушает порт 5006"""
    print(f"[BOT NET] Сетевой мост запущен. Слушаем порт {LISTEN_PORT}...")

    bot = our_bot
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCALHOST, LISTEN_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            signal = data.decode('utf-8')

            if signal == "NEW_ALERT":
                print("[BOT NET] Получен сигнал тревоги от турели! Отправляю фото нарушителя...")
                send_security_alert(bot)
        except Exception as e:
            print(f"[BOT NET ERROR] Ошибка сокета: {e}")


def send_security_alert(bot):
    """ОТПРАВКА ФОТО И КНОПОК В ТЕЛЕГРАМ"""
    try:
        if os.path.exists(ALERT_IMG_PATH):
            with open(ALERT_IMG_PATH, 'rb') as photo:
                # Создаем интерактивные кнопки под фото
                markup = InlineKeyboardMarkup()
                btn_allow = InlineKeyboardButton("💚 Доверить", callback_data="cmd_allow")
                btn_fire = InlineKeyboardButton("🔴 АТАКОВАТЬ", callback_data="cmd_fire")
                markup.row(btn_allow, btn_fire)

                bot.send_photo(
                    CHAT_ID,
                    photo,
                    caption="🚨 ВНИМАНИЕ! Обнаружен неопознанный объект периметра!",
                    reply_markup=markup
                )
                print("[BOT HANDLER] Фото успешно отправлено в Telegram.")

                # формируем архивное имя по дате и времени
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_filename = f"alert_{timestamp}.jpg"
                archive_path = os.path.join(ALERTS_DIR, archive_filename)  # Полный путь для архивной фотки
                os.rename(ALERT_IMG_PATH, archive_path)         # Переименовываем временный файл в архивный
                print(f"[BOT HANDLER] Файл перенесен в архив: {archive_path}")
        else:
            print(f"[BOT ERROR] Файл {ALERT_IMG_PATH} не найден на диске!")
    except Exception as e:
        print(f"[BOT ERROR] Не удалось отправить сообщение в ТГ: {e}")
