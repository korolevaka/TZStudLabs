
from telebot.async_telebot import AsyncTeleBot
from database import engine, Base
import json
import requests
from telebot import types
from database import Session, log_user_action
from models import UserSettings
from keyboards import (main_menu_keyboard, return_menu_keyboard, joke_keyboard)
import config
from googletrans import Translator
translator = Translator()


bot = AsyncTeleBot(config.BOT_TOKEN)
Base.metadata.create_all(engine)

user_states_weather = {}
user_states_joke = {}
user_states_news = {}

markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
help = types.KeyboardButton('Информация о боте')
settings = types.KeyboardButton('Настройки')
weather = types.KeyboardButton('Погода')
news = types.KeyboardButton('Новости')
joke = types.KeyboardButton('Шутки')
markup_menu.add(help, settings, weather, news, joke)

@bot.message_handler(commands=["start"])
async def start_menu(message):
    await bot.send_message(message.chat.id, f"Привет👋🏻, {message.from_user.first_name}! Выбери категорию!",reply_markup=main_menu_keyboard())
@bot.message_handler(func=lambda message: message.text == 'Информация о боте')
async def info(message):
    await bot.send_message(message.chat.id, "Я чат-бот Погода/Новости/Шутки!🤖\nМеня сделала: Королева Ксения Алексеевна \n"
                                         "Я умею:\n"
                             "start👋🏻 - приветствие, вывод меню\n"
                             "help🙏🏻 - информация о боте\n"
                             "settings🛠 - настройки\n"
                             "weather☀️ - выбор города, отображение погоды\n"
                             "news📱 - выбор категории, отображение новостей\n"
                             "joke🤣 - отображение случайной шутки", reply_markup=return_menu_keyboard())
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()

@bot.message_handler(func=lambda message: message.text == 'Погода')
async def weather(message):
    user_states_weather[message.chat.id] = "get_city"
    markup = types.ReplyKeyboardRemove(selective=False)
    await bot.send_message(message.chat.id, "Введите свой город📍:", reply_markup=markup)
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()
@bot.message_handler(func=lambda message:user_states_weather.get(message.chat.id) == "get_city")
async def get_weather(message):
    del user_states_weather[message.chat.id]
    city = message.text.strip().lower()
    session = Session()
    user_settings = session.query(UserSettings).get(message.from_user.id)
    user_settings.city = city
    session.commit()
    session.close()
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.API_weather}&units=metric')
    data = json.loads(res.text)
    try:
        temp = data["main"]["temp"]
        await bot.send_message(message.chat.id, f'В вашем городе погода: {temp}°C')
        await bot.send_message(message.chat.id, f'Но ощущается, как: {data["main"]["feels_like"]}°C')
        if temp <= -10.0:
            await bot.send_message(message.chat.id, '⛄️На улице очень холодно!⛄️\n Надевай - теплую куртку, теплую шапку, теплые перчатки, утепленные ботинки ', reply_markup=return_menu_keyboard())
        elif temp > -10.0 and temp <= 0.0:
            await bot.send_message(message.chat.id, '❄️На улице холодно❄️\n Надевай - куртку, шапку, водонепроницаемые перчатки, ботинки', reply_markup=return_menu_keyboard())
        elif temp > 0.0 and temp <= 10.0:
            await bot.send_message(message.chat.id, '⛅️На улице тепло⛅️\n Надевай - ветровку, легкую шапку или шарф, кроссовки или ботинки', reply_markup=return_menu_keyboard())
        elif temp > 10.0 and temp <= 20.0:
            await bot.send_message(message.chat.id, '☀️На улице жарко☀️\n Надевай - джинсы или брюки, футболку или свитер, легкую обувь или кроссовки', reply_markup=return_menu_keyboard())
        elif temp > 20.0:
            await bot.send_message(message.chat.id, '🔥На улице очень жарко, иди загорать!🔥\n Надевай - легкую одежду (футболка, шорты, платье), шляпу или кепку, сандалии или открытую обувь', reply_markup=return_menu_keyboard())
    except KeyError:
        await bot.send_message(message.chat.id,
                         "❌ Не удалось найти город",reply_markup=markup_menu)
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()


@bot.message_handler(func=lambda message: message.text == 'Шутки')
async def joke(message):
    user_states_joke[message.chat.id] = "categorys"
    await bot.send_message(message.chat.id, "Выбери категорию: любое, разное, программирование, мрачное, каламбур, жуткое, рождество",reply_markup=joke_keyboard())
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()
@bot.message_handler(func=lambda message: user_states_joke.get(message.chat.id) == "categorys")
async def send_joke(message):
    del user_states_joke[message.chat.id]
    category = message.text
    session = Session()
    user_settings = session.query(UserSettings).get(message.from_user.id)
    user_settings.joke_category = category
    session.commit()
    session.close()
    res = requests.get(f'https://jokeapi.dev/joke/{category}')
    data = json.loads(res.text)
    if 'joke' in data:
        joke_text = data["joke"]
    elif 'setup' in data and 'delivery' in data:
        joke_text = f'{data["setup"]} {data["delivery"]}'
    else:
        await bot.send_message(message.chat.id, "Не удалось получить шутку. Попробуйте позже.",reply_markup=return_menu_keyboard())
        return
    try:
        translated_text = translator.translate(joke_text, dest='ru').text
    except Exception as e:
        print(f"Translation error: {e}")
        await bot.send_message(message.chat.id, "Ошибка при переводе шутки.",reply_markup=return_menu_keyboard())
        return
    await bot.send_message(message.chat.id, translated_text, reply_markup=return_menu_keyboard())
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()

@bot.message_handler(func=lambda message: message.text == 'Новости')
async def news(message):
    user_states_news[message.chat.id] = "categorys_news"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    world_news = types.KeyboardButton('Общие новости')
    local_news = types.KeyboardButton('Новости по региону')
    markup.add(world_news, local_news)
    await bot.send_message(message.chat.id,
                     "Выбери какие новости вы хотите посмотреть: общие или в выбранной стране:",
                     reply_markup=markup)
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()
    session = Session()

@bot.message_handler(func=lambda message:user_states_news.get(message.chat.id) == "categorys_news")
async def get_news(message):
    del user_states_news[message.chat.id]
    if message.text == 'Общие новости':
        res = requests.get(f'https://newsapi.org/v2/top-headlines?country=ru&apiKey={config.NEWS_API_KEY}')
        news_data = res.json()
        if res.status_code == 200:
            articles = news_data['articles'][:5]
            for article in articles:
                title = article['title']
                url = article['url']
                description = article['description']
                news_text = f"*{title}*\n\n{description}\n\n[Читать далее]({url})"
                await bot.send_message(message.chat.id, news_text, parse_mode='Markdown', reply_markup=return_menu_keyboard())
        else:
            await bot.send_message(message.chat.id, "Ошибка получения новостей.", reply_markup=return_menu_keyboard())
    else:
        user_states_news[message.chat.id] = "region"
        await bot.send_message(message.chat.id, "Введите код региона (например, 'us', 'ru'):")
        return
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()
@bot.message_handler(func=lambda message:user_states_news.get(message.chat.id) == "region")
async def get_news_by_region(message):
    del user_states_news[message.chat.id]
    region = message.text.lower()
    session = Session()
    user_settings = session.query(UserSettings).get(message.from_user.id)
    user_settings.news_category = region
    session.commit()
    session.close()
    res = requests.get(f'https://newsapi.org/v2/top-headlines?country={region}&apiKey={config.NEWS_API_KEY}')
    news_data = res.json()
    if res.status_code == 200:
        articles = news_data['articles'][:5]
        for article in articles:
            title = article['title']
            url = article['url']
            description = article['description']
            news_text = f"*{title}*\n\n{description}\n\n[Читать далее]({url})"
            await bot.send_message(message.chat.id, news_text, parse_mode='Markdown', reply_markup=return_menu_keyboard())
    else:
        await bot.send_message(message.chat.id, "Ошибка получения новостей.", reply_markup=return_menu_keyboard())
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()


@bot.message_handler(func=lambda message: message.text == 'Настройки')
async def handle_settings(message):
    session = Session()
    user_settings = session.query(UserSettings).get(message.from_user.id)
    if not user_settings:
        user_settings = UserSettings(user_id=message.from_user.id)
        session.add(user_settings)
        session.commit()
        await bot.send_message(message.chat.id, "У вас пока нет сохраненных настроек. Используйте команды ниже, чтобы установить их.")
    else:
        settings_text = "Ваши текущие настройки:\n"
        if user_settings.city:
            settings_text += f"Город: {user_settings.city}\n"
        if user_settings.joke_category:
            settings_text += f"Категория шуток: {user_settings.joke_category}\n"
        if user_settings.news_category:
            settings_text += f"Регион: {user_settings.news_category}\n"
        await bot.send_message(message.chat.id, settings_text)
    session.close()


@bot.message_handler(func=lambda message: message.text == "Вернуться в меню")
async def handle_back_to_menu(message):
    # Clear user state (if needed)
    if message.chat.id in user_states_joke:
        del user_states_joke[message.chat.id]
    elif message.chat.id in user_states_weather:
        del user_states_weather[message.chat.id]
    await start_menu(message)
    session = Session()
    log_user_action(session, message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)
    session.close()

@bot.message_handler(func=lambda message: True)
async def any_message(message):
    log_user_action(message.from_user.id, message.from_user.username,
                    message.from_user.first_name, message.text)

async def go():
    await bot.infinity_polling()