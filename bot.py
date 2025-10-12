import telebot
import os
import time
from main import FusionBrainAPI
from config import TOKEN, API_key, SECRET_key

bot = telebot.TeleBot(TOKEN)
api = FusionBrainAPI('https://api-key.fusionbrain.ai/', API_key, SECRET_key)


@bot.message_handler(commands=['start', 'help'])
def start_help(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот, который создаёт изображения по твоему описанию.\n\n"
        "Просто напиши, что нужно сгенерировать — например: *«Море на закате»*, и я нарисую это!",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    prompt = message.text.strip()

    # Отправляем сообщение "Генерирую..."
    loading_msg = bot.send_message(message.chat.id, "🖌 Генерирую картинку...")

    try:
        pipeline_id = api.get_pipeline()
        uuid = api.generate(prompt, pipeline_id)
        files = api.check_generation(uuid)

        # Сохраняем изображение
        file_path = "file.png"
        api.save_image(files[0], file_path)

        # Удаляем сообщение "Генерирую..."
        bot.delete_message(message.chat.id, loading_msg.message_id)

        # Отправляем картинку
        with open(file_path, "rb") as f:
            bot.send_photo(message.chat.id, f, caption=f"✨ Вот результат по запросу: *{prompt}*", parse_mode="Markdown")

        # Удаляем файл после отправки
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        bot.delete_message(message.chat.id, loading_msg.message_id)
        bot.send_message(message.chat.id, f"⚠️ Ошибка при генерации: {e}")


bot.polling(none_stop=True)