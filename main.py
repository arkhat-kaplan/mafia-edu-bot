import telebot
from telebot import types
import sqlite3
import time

bot = telebot.TeleBot("1999230190:AAGqimG9_RXg1_3WwX_-N5sbSJkpyp9z4Wk")


# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Информация о боте')
    itembtn2 = types.KeyboardButton('Афиша ближайших игр')
    itembtn3 = types.KeyboardButton('Регистрация нового участника')
    itembtn4 = types.KeyboardButton('Запись на игру')
    itembtn5 = types.KeyboardButton('Другое')
    itembtn6 = types.KeyboardButton('Нет, спасибо!')
    keyboard.add(itembtn1, itembtn2)
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6)


@bot.message_handler(commands=['start'])
def send_keyboard_add_gamedate(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Добавить дату')
    itembtn2 = types.KeyboardButton('Отменить')
    keyboard.add(itembtn1, itembtn2)

    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, callback_worker)


conn = sqlite3.connect('mafiaclub_hse.db')
cursor = conn.cursor()

# Таблица с играми
try:
    query = "CREATE TABLE \"games\" (\"ID\" INTEGER UNIQUE, \"inserted_by\" INTEGER, \"description\" TEXT, \"date\" DATE, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
except:
    pass


# Как добавить игру в расписание? - начало
def add_game(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('INSERT INTO games (description, inserted_by, date) VALUES (?, ?, null)',
                       (msg.text, msg.from_user.id))
        con.commit()
    send_keyboard_add_gamedate(msg, "Необходимо внести дату игры в расписание")


def add_gamedate(msg):
    try:
        with sqlite3.connect('planner_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                            UPDATE games 
                            SET "date" = julianday(?)
                            WHERE "inserted_by"  = ?
                                and "date" is null
                            ''',
                           (msg.text, msg.from_user.id))
            con.commit()
        bot.send_message(msg.chat.id, 'Запомню :-)')
        send_keyboard(msg, "Чем еще могу помочь?")
    except:
        bot.send_message(msg.chat.id, 'Необходимо ввести формат даты ГГГГ-ММ-ДД.')


def drop_game(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        DELETE FROM games
                        WHERE "inserted_by"  = ?
                            and "date" is null
                        ''',
                       (msg.from_user.id, msg.text))
        con.commit()
    bot.send_message(msg.chat.id, 'Хорошо')
    send_keyboard(msg, "Чем еще могу помочь?")


# Как добавить игру в расписание? - Конец

# Показать ближайшую игру - Начало

# просто функция, которая делает нам красивые строки для отправки пользователю
def get_games_string(games):
    games_str = []
    for val in list(enumerate(games)):
        games_str.append(str(val[0] + 1) + ') __' + val[1][0] + '__ - **' + val[2] +'**\n')
    return ''.join(games_str)

# отправляем пользователю его планы
def show_games(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT description, date FROM games WHERE date >= julianday(now()) LIMIT 3')
        tasks = get_games_string(cursor.fetchall())
        bot.send_message(msg.chat.id, tasks)
        send_keyboard(msg, "Чем еще могу помочь?")

# Показать ближайшую игру - Начало

bot.polling(none_stop=True, interval=0)
