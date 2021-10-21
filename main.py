import telebot
from telebot import types
import sqlite3
import datetime

bot = telebot.TeleBot("1999230190:AAGqimG9_RXg1_3WwX_-N5sbSJkpyp9z4Wk")

date_list = list((datetime.date.today() + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 5))


# Клавиатуры
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Информация о боте')
    itembtn2 = types.KeyboardButton('Афиша ближайших игр')
    itembtn3 = types.KeyboardButton('Регистрация нового участника')
    itembtn4 = types.KeyboardButton('Запись на игру')
    itembtn5 = types.KeyboardButton('Просмотреть профиль')
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
    keyboard.add(itembtn1, itembtn2)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)


@bot.message_handler(commands=['change'])
def send_keyboard_change_profile(message, text="Выбери что хочешь изменить"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Изменить игровой никнейм')
    itembtn2 = types.KeyboardButton('Изменить имя в профиле')
    itembtn3 = types.KeyboardButton('Нет, спасибо')
    keyboard.add(itembtn1, itembtn2)
    keyboard.add(itembtn3)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)


conn = sqlite3.connect('mafiaclub_hse.db')
cursor = conn.cursor()

# Таблицы
try:
    query = "CREATE TABLE \"games\" (\"ID\" INTEGER UNIQUE, \"inserted_by\" INTEGER, \"description\" TEXT, \"date\" DATE, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
    query = "CREATE TABLE \"gamers\" (\"user_id\" INTEGER UNIQUE, \"nickname\" TEXT, \"name\" TEXT, \"img\" BLOP, \"resume\" BLOP, PRIMARY KEY (\"user_id\"))"
    cursor.execute(query)
except:
    pass


# Как добавить игру в расписание? - начало - работает, аллилуя!
def add_gamedate(msg):
    try:
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                            UPDATE games 
                            SET "date" = strftime('%Y%m%d',?)
                            WHERE "inserted_by"  = ?
                                and "date" is null
                            ''',
                           ((msg.text, msg.from_user.id)))
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
                            INSERT INTO games (inserted_by, description) 
                            VALUES (?, ?)
                            ''',
                           (msg.from_user.id, msg.text))
            con.commit()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for value in date_list:
            markup.add(types.KeyboardButton(value))
        msg = bot.send_message(msg.from_user.id,
                               text="Выбери день из списка",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_gamedate)
    except:
        bot.send_message(msg.chat.id, 'Сломалося(')


# Как добавить игру в расписание? - Конец

# Вывести информацию о боте - Начало - Проверить

def get_info(msg):
    msg = bot.send_message(msg.chat.id,
                           'Привет, я бот-помощник клуба по игре мафия. Ты можешь ознакомиться с тем что я умею с помощью команды /start, по секрету есть еще команда /new но она для администраторов.')
    send_keyboard(msg, "Чем еще могу помочь?")


# Вывести информацию о боте - Конец

# Регистрация нового игрока - Начало - Не работает скотобаза


def change_nickname(msg):
    msg = bot.send_message(msg.chat.id, 'Напиши в чат свой ник.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set nickname = ?
                        where user_id = ?
                        ''',
                       (msg.from_user.id, msg.text))
        con.commit()
    bot.send_message(msg.chat.id, 'Никнейм изменено.')
    send_keyboard_change_profile(msg, "Хочешь что-нибудь изменить?")


def change_name(msg):
    msg = bot.send_message(msg.chat.id, 'Напиши в чат своё имя.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set name = ?
                        where user_id = ?
                        ''',
                       (msg.text, msg.from_user.id))
        con.commit()
    bot.send_message(msg.chat.id, 'Имя изменено.')
    send_keyboard_change_profile(msg, "Хочешь что-нибудь изменить?")


def change_img(msg):
    msg = bot.send_message(msg.chat.id, 'Пришли свою фотографию в чат.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set img = ?
                        where user_id = ?
                        ''',
                       (msg.photo, msg.from_user.id))
        con.commit()
    bot.send_message(msg.chat.id, 'Фото изменено.')
    send_keyboard_change_profile(msg, "Хочешь что-нибудь изменить?")


def registration_resume(msg):
    msg = bot.send_message(msg.chat.id, 'Пришли текстовый файл своего резюме в чат.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set resume = ?
                        where user_id = ?
                        ''',
                       (msg.document, msg.from_user.id))
        con.commit()
    bot.send_message(msg.chat.id, 'Это был последний шаг, поздравляю с регистрацией <3.')
    send_keyboard(msg, "Чем еще могу помочь?")


def registration_img(msg):
    msg = bot.send_message(msg.chat.id, 'Пришли свою фотографию в чат.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set img = ?
                        where user_id = ?
                        ''',
                       (msg.photo, msg.from_user.id))
        con.commit()
    bot.register_next_step_handler(msg, registration_resume)


def registration_name(msg):
    try:
        msg = bot.send_message(msg.chat.id, 'Напиши в чат своё имя.')
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                            update gamers 
                            set name = ?
                            where user_id = ?
                            ''',
                           (msg.text, msg.from_user.id))
            con.commit()
        bot.send_message(msg.chat.id, 'Все готово.')
    except:
        bot.send_message(msg.chat.id, 'Нипалучилося')
    #bot.register_next_step_handler(msg, registration_img)


def registration_start(msg):
    try:
        msg = bot.send_message(msg.chat.id, 'Напиши в чат свой игровой ник.')
        with sqlite3.connect('mafiaclub_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('''
                              INSERT INTO gamers (user_id, nickname) 
                              VALUES (?, ?)
                              ''',
                           (msg.from_user.id, msg.text))
            con.commit()
        bot.send_message(msg.chat.id, 'Запомнил, идем к следующему шагу.')
        bot.register_next_step_handler(msg, registration_name)
    except:
        msg = bot.send_message(msg.chat.id, 'Ты уже зарегистрирован.')
        send_keyboard(msg, "Чем еще могу помочь?")


def change_resume(msg):
    msg = bot.send_message(msg.chat.id, 'Пришли текстовый файл в чат.')
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('''
                        update gamers 
                        set resume = ?
                        where user_id = ?
                        ''',
                       (msg.document, msg.from_user.id))
        con.commit()
    bot.send_message(msg.chat.id, 'Резюме изменено.')
    send_keyboard_change_profile(msg, "Хочешь что-нибудь изменить?")


# Регистрация нового игрока - Конец

# Показать профиль - Начало


def info_get_string(profile):
    info_str = []
    for val in list(enumerate(profile)):
        info_str.append(f'''Игрок № {val[1][0]} - <b>"{val[1][1]}"</b> \nИмя: <i>{val[1][2]}</i> \n''')
    return ''.join(info_str)


def info_get_img(profile):
    info_img = []
    for val in list(enumerate(profile)):
        info_img.append(val[1][3])
    return ''.join(info_img)


def info_get_resume(profile):
    info_resume = []
    for val in list(enumerate(profile)):
        with open(val[1][4], 'r') as file:
            data = file.read().replace('\n', '')
        info_resume.append(data)
    return ''.join(info_resume)


def info_profile(msg):
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('select * from gamers where user_id = ? ',((msg.from_user.id,)))
        info = info_get_string(cursor.fetchall())
        #+ '\n' + info_get_resume(cursor.fetchall())
        #img = info_get_img(cursor.fetchall())
        #bot.send_message(msg.chat.id, img)
    bot.send_message(msg.chat.id, info, parse_mode='HTML')
    send_keyboard_change_profile(msg, "Хочешь что-нибудь изменить?")


# Показать профиль - Конец

# Показать ближайшую игру - Начало - работает, аллилуя!

# просто функция, которая делает нам красивые строки для отправки пользователю
def get_games_string(games):
    games_str = []
    for val in list(enumerate(games)):
        y = str(val[1][1])
        y = y[:4] + '-' + y[4:6] + '-' + y[6:]
        games_str.append(str(val[0] + 1) + ') <i>' + val[1][0] + '</i> - <b>' + y + '</b>\n')
    return ''.join(games_str)


# отправляем пользователю игрули
def show_games(msg):
    with sqlite3.connect('mafiaclub_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT description, date FROM games WHERE date >= strftime(\'%Y%m%d\',\'now\') LIMIT 3')
        games = get_games_string(cursor.fetchall())
        bot.send_message(msg.chat.id, games, parse_mode='HTML')
        send_keyboard(msg, "Чем еще могу помочь?")


# Показать ближайшую игру - Конец

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
    if call.text == "Информация о боте":
        get_info(call)
    if call.text == 'Регистрация нового участника':
        registration_start(call)
    if call.text == 'Просмотреть профиль':
        info_profile(call)
    if call.text == 'Нет, спасибо':
        bot.send_message(msg.chat.id, 'Понял - принял.', parse_mode='HTML')
        send_keyboard(msg, "Чем еще могу помочь?")
    if call.text == 'Изменить игровой никнейм':
        change_nickname(call)
    if call.text == 'Изменить имя в профиле':
        change_name(call)
    if call.text == 'Изменить фотографию':
        change_img(call)
    if call.text == 'Изменить резюме игрока':
        change_resume(call)


bot.polling(none_stop=True, interval=0)
