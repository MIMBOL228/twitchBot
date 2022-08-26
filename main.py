import re
import json
import requests
import telebot
from mysql.connector import connect, Error

# get config
Config = json.load(open("config.json"))

# bot instance
bot = telebot.TeleBot(Config["token"])

# connect to database
connection = connect(
    user=Config["username"], password=Config["passwd"],
    host=Config["IP"],
    database=Config["dbName"],
    port=Config["port"]
)


# /start
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, ('1) Зарегистрируйтесь: /register\n'
                                '2) Отправляйте деньги другим игрокам: /send'
                                ' [Ник получателя] [Сумма]'))

# /register
@bot.message_handler(commands=["register"])
def register(msg):
    bot.send_message(msg.chat.id, ('Чтобы зарегистрироваться, напишите'
                                ' на сервере команду: /regtelegram '
                                '{id пользователя в Telegram}'))

# /send
@bot.message_handler(commands=["send"])
def send(msg):
    args = msg.text[5:].split()
    
    # Проверка количества параметров
    if len(args)<2:
        bot.send_message(msg.chat.id, 'Слишком мало парамтеров')
        return

    # Параметры
    username = args[0]
    sum_: int = args[1]
    print(username, sum_, type(sum_), sep="[DD]")

    # Проверка на валидность никнейма
    if re.fullmatch(r"[a-zA-Z0-9_]{3,16}", username)==None:
        print(re.fullmatch(r"[a-zA-Z0-9_]{3,16}", username))
        bot.send_message(msg.chat.id, 'Неверный ник')
        return
    # Проверка целочисленности данных
    try:
        int(sum_)
    except:
        bot.send_message(msg.chat.id, 'Неверная сумма')
        return
    # if not isinstance(sum_, int):
        

    url = f'https://api.mojang.com/users/profiles/minecraft/{username}?'

    response = requests.get(url)

    if not response:
        bot.send_message(msg.chat.id, 'Получатель не найден')
        return

    uuid = response.json()['id']

    with connection.cursor() as cursor:
        print(f"SELECT count(*) FROM `users` WHERE `uuid`=`{uuid}`")
        cursor.execute(f"SELECT count(*) FROM `users` WHERE `uuid`='{uuid}'")

        length = cursor.fetchall()[0]
        if length[0]<1:
            bot.send_message(msg.chat.id, 'Получатель не найден')
            return
        
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM `users` WHERE `tg_id`='{msg.from_user.id}'")

        result = cursor.fetchall()[0]
        balance = result["balance"]
        if balance<sum_:
            bot.send_message(msg.chat.id, 'Недостаточно средств')
            return

    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE `users` SET `balance`=`{balance-sum_}` WHERE `tg_id` = '{msg.from_user.id}'")
        connection.commit()

    with connection.cursor() as cursor:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `users` WHERE uuid = '{uuid}'")

            balancethis = cursor.fetchall()[0]['balance']
        
        cursor.execute(f"UPDATE `users` SET `balance`={balancethis+balance} WHERE `uuid` = '{uuid}'")
        connection.commit()

    bot.send_message(msg.chat.id, 'Успешно!')

bot.polling(none_stop=True, interval=0)
