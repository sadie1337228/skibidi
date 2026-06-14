import telebot
from googletrans import Translator, LANGUAGES
from telebot import types
import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent

API_TOKEN = '8253461947:AAGz-y5VHVMGeCEP0YLS3T2H1hFJRorM8_I'
bot =telebot.TeleBot(API_TOKEN)

translator = Translator()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет! Я бот-переводчик. Напиши мне текст и я его переведу')

@bot.message_handler(func=lambda message: True)
def translate_to_english(message):
    translated = translator.translate(message.text, dest='en')
    bot.reply_to(message, translated.text)

@bot.inline_handler(func=lambda query: len(query.query) > 0)
def inline_translate(query):
    translated = translator.translate(query.query, dest='en')
    translation_text = translated.text

    result = InlineQueryResultArticle(
        id='1',
        title='Переводчик',
        description=translation_text,
        input_message_content=InputTextMessageContent(translation_text)
    )

    bot.answer_inline_query(query.id, [result])

bot.polling()
