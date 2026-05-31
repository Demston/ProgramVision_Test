import threading
import telebot
from service.bot_handler import *


bot = telebot.TeleBot(BOT_TOKEN)


# === ОБРАБОТКА НАЖАТИЯ КНОПОК В ТЕЛЕГРАМЕ ===
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "cmd_allow":
        bot.answer_callback_query(call.id, text="Команда: Добавить в доверенные")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Статус периметра: ОБЪЕКТ АВТОРИЗОВАН УДАЛЕННО")

        # !!! Тут дописать отправку команды обратно в турель
        print("[BOT] Нажата кнопка ДОВЕРИТЬ")

    elif call.data == "cmd_fire":
        bot.answer_callback_query(call.id, text="ВКЛЮЧЕН СТРОБОСКОП И ЛАЗЕР!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Статус периметра: ОБЪЕКТ АТАКОВАН ОПТИЧЕСКИМ ИЗЛУЧАТЕЛЕМ")

        # !!! Тут дописать отправку команды обратно в турель
        print("[BOT] Нажата кнопка АТАКА")


if __name__ == "__main__":
    # Запускаем прослушку портов в отдельном фоновом потоке (чтобы она не мешала боту опрашивать ТГ)
    net_thread = threading.Thread(target=network_listener(bot), daemon=True)
    net_thread.start()

    # Запуск самого ТГ бота
    print("[BOT] Telegram-сервис успешно запущен . . .")
    bot.infinity_polling()
