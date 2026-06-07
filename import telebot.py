import telebot
from googletrans import Translator, LANGUAGES
from telebot import types
from telebot.types import InlineQueryResultArticle, InputTextMessageContent

API_TOKEN = '8253461947:AAGz-y5VHVMGeCEP0YLS3T2H1hFJRorM8_I'
bot = telebot.TeleBot(API_TOKEN)

translator = Translator()

user_languages = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Выбрать язык перевода')
    btn2 = types.KeyboardButton('Помощь')
    markup.add(btn1, btn2)
    
    bot.reply_to(message, 
                 'Привет! Я бот-переводчик.\n'
                 'Чтобы выбрать другой язык, нажми "Выбрать язык перевода" или используй команду /set_language',
                 reply_markup=markup)


@bot.message_handler(commands=['set_language'])
def set_language_command(message):
    show_language_selection(message)

@bot.message_handler(func=lambda message: message.text == 'Выбрать язык перевода')
def choose_language(message):
    show_language_selection(message)

def show_language_selection(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    popular_langs = [
        ('Английский', 'en'),
        ('Русский', 'ru'),
        ('Французский', 'fr'),
        ('Немецкий', 'de'),
        ('Испанский', 'es'),
        ('Итальянский', 'it'),
        ('Китайский', 'zh-cn'),
        ('Японский', 'ja'),
    ]
    
    for lang_name, lang_code in popular_langs:
        btn = types.InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}')
        markup.add(btn)
    
    # Кнопка для выбора всех языков
    markup.add(types.InlineKeyboardButton('Все языки', callback_data='show_all_langs'))
    
    # Кнопка сброса (по умолчанию английский)
    markup.add(types.InlineKeyboardButton('Сбросить (Английский)', callback_data='lang_en'))
    
    bot.send_message(message.chat.id, 
                     'Выберите язык, на который нужно переводить:', 
                     reply_markup=markup)

# Обработка выбора языка из всех языков
@bot.callback_query_handler(func=lambda call: call.data == 'show_all_langs')
def show_all_languages(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Показываем все доступные языки
    for lang_code, lang_name in sorted(LANGUAGES.items())[:50]:  # Ограничим 50 языками для удобства
        btn = types.InlineKeyboardButton(f"{lang_name.capitalize()}", callback_data=f'lang_{lang_code}')
        markup.add(btn)
    
    # Кнопка назад
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_popular'))
    
    bot.edit_message_text('Выберите язык из списка:', 
                          call.message.chat.id, 
                          call.message.message_id,
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_popular')
def back_to_popular(call):
    show_language_selection(call.message)
    bot.answer_callback_query(call.id)

# Обработка выбора языка
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang_code = call.data.split('_')[1]
    user_languages[call.from_user.id] = lang_code
    
    lang_name = LANGUAGES.get(lang_code, lang_code)
    if lang_code == 'en':
        lang_name = 'Английский'
    elif lang_code == 'ru':
        lang_name = 'Русский'
    elif lang_code == 'zh-cn':
        lang_name = 'Китайский'
    
    bot.answer_callback_query(call.id, f'Язык перевода изменен на {lang_name}')
    bot.edit_message_text(f'Язык перевода установлен: {lang_name}\n\nТеперь отправьте мне текст для перевода!',
                          call.message.chat.id,
                          call.message.message_id)

# Кнопка "Помощь"
@bot.message_handler(func=lambda message: message.text == 'Помощь')
def help_message(message):
    bot.reply_to(message,
                'Как пользоваться ботом:\n\n'
                '1. Отправьте мне любой текст\n'
                '2. Я переведу его на выбранный вами язык\n'
                '3. По умолчанию перевод на английский\n\n'
                'Команды:\n'
                '/start - начать работу\n'
                '/set_language - выбрать язык перевода\n'
                '/current_language - узнать текущий язык\n'
                '/help - помощь\n\n'
                'Также я работаю в inline режиме:\n'
                '@ваш_username текст')

# Команда /current_language
@bot.message_handler(commands=['current_language'])
def current_language(message):
    lang_code = user_languages.get(message.from_user.id, 'en')
    lang_name = LANGUAGES.get(lang_code, 'Английский')
    if lang_code == 'en':
        lang_name = 'Английский'
    elif lang_code == 'ru':
        lang_name = 'Русский'
    elif lang_code == 'zh-cn':
        lang_name = 'Китайский'
    
    bot.reply_to(message, f'Текущий язык перевода: {lang_name}')

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    help_message(message)

# Основная функция перевода
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/') and message.text not in ['Выбрать язык перевода', 'Помощь'])
def translate_text(message):
    # Получаем выбранный язык пользователя или английский по умолчанию
    dest_lang = user_languages.get(message.from_user.id, 'en')
    
    try:
        # Определяем исходный язык
        detected = translator.detect(message.text)
        
        # Переводим
        translated = translator.translate(message.text, dest=dest_lang)
        
        # Определяем название языка перевода
        lang_name = LANGUAGES.get(dest_lang, dest_lang)
        if dest_lang == 'en':
            lang_name = 'Английский'
        elif dest_lang == 'ru':
            lang_name = 'Русский'
        elif dest_lang == 'zh-cn':
            lang_name = 'Китайский'
        
        # Отправляем результат
        response = f"Исходный текст: {message.text}\n\n"
        response += f"Перевод на {lang_name}:\n{translated.text}\n\n"
        response += f"Определенный язык: {LANGUAGES.get(detected.lang, detected.lang).capitalize()}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, f'Ошибка перевода: {str(e)}\nПопробуйте еще раз.')

# Inline режим
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def inline_translate(query):
    try:
        text_to_translate = query.query
        
        results = []
        
        # Вариант 1: Английский
        translated_en = translator.translate(text_to_translate, dest='en')
        result1 = InlineQueryResultArticle(
            id='1',
            title='На английский',
            description=translated_en.text[:50] + ('...' if len(translated_en.text) > 50 else ''),
            input_message_content=InputTextMessageContent(translated_en.text)
        )
        results.append(result1)
        
        # Вариант 2: Русский (если текст не на русском)
        if translator.detect(text_to_translate).lang != 'ru':
            translated_ru = translator.translate(text_to_translate, dest='ru')
            result2 = InlineQueryResultArticle(
                id='2',
                title='На русский',
                description=translated_ru.text[:50] + ('...' if len(translated_ru.text) > 50 else ''),
                input_message_content=InputTextMessageContent(translated_ru.text)
            )
            results.append(result2)
        
        # Вариант 3: Немецкий
        translated_de = translator.translate(text_to_translate, dest='de')
        result3 = InlineQueryResultArticle(
            id='3',
            title='На немецкий',
            description=translated_de.text[:50] + ('...' if len(translated_de.text) > 50 else ''),
            input_message_content=InputTextMessageContent(translated_de.text)
        )
        results.append(result3)
        
        bot.answer_inline_query(query.id, results)
        
    except Exception as e:
        bot.answer_inline_query(query.id, [])

# Запуск бота
if __name__ == '__main__':
    print('Бот запущен...')
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f'Ошибка: {e}')