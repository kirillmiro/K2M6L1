import telebot
from main import FusionBrainAPI
from config import TOKEN, API_key, SECRET_key

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands = ["start"])
def start(message): 
    bot.send_message(message.chat.id, "Привет! напиши, что за фоторгавию мне сгенерировать.")

@bot.message_handler(func = lambda m: True)
def handle_message(message):
    prompt = message.text
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', API_key, SECRET_key)
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    files = api.check_generation(uuid)
    api.save_image(files[0], "file.png")
    with open ("file.png", "rb") as f:
        bot.send_photo(message.chat.id, f)


bot.polling()