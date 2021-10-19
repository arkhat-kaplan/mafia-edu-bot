import telebot
from telebot import types
import sqlite3
import datetime

bot = telebot.TeleBot("1999230190:AAGqimG9_RXg1_3WwX_-N5sbSJkpyp9z4Wk")

date_list = list([(datetime.date.today() + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 5)])


# Клавиатуры
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
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)


@bot.message_handler(commands=['new'])
def send_keyboard_add_gamedate(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Добавить новую игру в расписание')
    itembtn2 = types.KeyboardButton('Удалить ошибочную запись об игре')
    itembtn3 = types.KeyboardButton('Тест')
    keyboard.add(itembtn1, itembtn2)
    keyboard.add(itembtn3)
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
def add_gamedate(msg):
    try:
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                            UPDATE games 
                            SET "date" = substr({msg.text},1,4)||substr({msg.text},6,2)||substr({msg.text},9,2) 
                            WHERE "inserted_by"  = {msg.from_user.id}
                                and "date" is null
                            '''
                           .format((msg.text, msg.from_user.id)))
            con.commit()
        bot.send_message(msg.chat.id, 'Запомню :-)')
        send_keyboard(msg, "Чем еще могу помочь?")
    except:
        bot.send_message(msg.chat.id, 'Необходимо ввести формат даты ГГГГ-ММ-ДД.')
        bot.register_next_step_handler(msg, add_gamedate)


def drop_game(msg):
    if msg == 'Да':
        with sqlite3.connect('mafiaclub_hse.db') as con:
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
    else:
        bot.send_message(msg.chat.id, 'Ладно:С')


def add_game(msg):
    try:
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                            INSERT INTO "games" (inserted_by, description) 
                            VALUES (%s, %s)
                            '''
                           .format(msg.from_user.id, msg.text))
            con.commit()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(date_list)
        msg = bot.reply_to(msg.from_user.id,
                           text="Выбери день из списка",
                           reply_markup=markup)
        bot.register_next_step_handler(msg, add_gamedate)
    except:
        bot.send_message(msg.chat.id, 'Сломалося(')


# Как добавить игру в расписание? - Конец

# Показать ближайшую игру - Начало

# просто функция, которая делает нам красивые строки для отправки пользователю
def get_games_string(games):
    games_str = []
    for val in list(enumerate(games)):
        y = str(val[1][1])
        y = y[:4] + '-' + y[4:6] + '-' + y[6:]
        games_str.append(str(val[0] + 1) + ') __' + val[1][0] + '__ - **' + y + '**\n')
    return ''.join(games_str)


# отправляем пользователю его планы
def show_games(msg):
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT description, date FROM games WHERE date >= julianday(\'now\') LIMIT 3')
        games = get_games_string(cursor.fetchall())
        bot.send_message(msg.chat.id, games)
        send_keyboard(msg, "Чем еще могу помочь?", parse_mode='Markdown')
        return games


# Показать ближайшую игру - Конец

# Тест - начало
def test(msg):
    if msg == 'Да':
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
            bot.send_message(msg.chat.id, cursor.fetchall())
    else:
        pass
# Тест - конец

# Все соединяем - Начало
@bot.message_handler(content_types=['text'])
def callback_worker(call):
    if call.text == "Добавить новую игру в расписание":
        msg = bot.send_message(call.chat.id, 'Давайте добавим игру! Напишите ее описание в чат!')
        bot.register_next_step_handler(msg, add_game)
    if call.text == "Добавить дату новой игры в расписание":
        msg = bot.send_message(call.chat.id, 'Напиши в чат дату формата ГГГГ-ММ-ДД')
        bot.register_next_step_handler(msg, add_gamedate)
    if call.text == "Удалить ошибочную запись об игре":
        msg = bot.send_message(call.chat.id, 'Ты уверен?')
        bot.register_next_step_handler(msg, drop_game)
    if call.text == "Афиша ближайших игр":
        show_games(call)


bot.polling(none_stop=True, interval=0)
