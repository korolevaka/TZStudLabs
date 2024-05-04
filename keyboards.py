from telebot import types
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    help_button = types.KeyboardButton('Информация о боте')
    settings_button = types.KeyboardButton('Настройки')
    weather_button = types.KeyboardButton('Погода')
    news_button = types.KeyboardButton('Новости')
    joke_button = types.KeyboardButton('Шутки')
    markup.add(help_button, settings_button, weather_button, news_button, joke_button)
    return markup

def return_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start = types.KeyboardButton('Вернуться в меню')
    markup.add(start)
    return markup

def joke_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    any = types.KeyboardButton('Any')
    misc = types.KeyboardButton('Misc')
    programming = types.KeyboardButton('Programming')
    dark = types.KeyboardButton('Dark')
    pun = types.KeyboardButton('Pun')
    spooky = types.KeyboardButton('Spooky')
    christmas = types.KeyboardButton('Christmas')
    markup.add(any, misc, programming, dark, pun, spooky, christmas)
    return markup
