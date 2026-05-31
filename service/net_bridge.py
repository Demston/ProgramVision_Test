import socket

# Порт, на котором ТГ-бот будет слушать сигналы от турели
BOT_PORT = 5006
LOCALHOST = "127.0.0.1"


def send_alert_signal():
    """Отправляет быстрый сетевой сигнал боту, что появился новый нарушитель"""
    try:
        # Создаем быстрый UDP сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"NEW_ALERT", (LOCALHOST, BOT_PORT))
        sock.close()
        print("[NET] Сигнал NEW_ALERT успешно отправлен боту по сети.")
    except Exception as e:
        print(f"[NET ERROR] Не удалось отправить сигнал боту: {e}")
