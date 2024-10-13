from re import S
from telebot import TeleBot
from telebot.types import Message
from telebot.types import Message, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,  InlineKeyboardButton
from random import choice
from time import sleep
import os

from database import *

Token ='7045083536:AAE_bWtbi5QNKxYM26plawjbvrNhY1A7UT4'#(Токен бота)
bot = TeleBot(Token)

game = False
night = False

if not os.path.exists("db.db"):
    create_tables()

def get_killed(night: bool) -> str:
    if not night:
        username_killed = citizen_kill()
        return f"Горожане выгнали: {username_killed}"
    username_killed = mafia_kill()
    return f"Мафия убила: {username_killed}"

def autoplay_citizen(message):
    players_roles = get_pl_roles()
    for player_id, role in players_roles:
        usernames = get_all_alive()
        name = f"robot_{player_id}"
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            vote("citizen_vote", vote_username, player_id)
            bot.send_message(message.chat.id, f"{name} проголосовали против {vote_username}")
            sleep(0.5)

def autopl_mafia(message):
    players_roles = get_pl_roles()
    for player_id, role in players_roles:
        usernames = get_all_alive()
        name = f"robot_{player_id}"
        if player_id < 5 and name in usernames and role == "mafia":
            usernames.remove(name)
            vote_username = choice(usernames)
            vote("mafia_vote", vote_username, player_id)

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, "Добро пожаловать в игру, вам даётся 2 минуты")
    sleep(10)#10секунд
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(message.chat.id, "Город засыпает")
        else:
            bot.send_message(message.chat.id, "Город засыпает")
        winner = check_winner()
        if winner == "Мафия" or winner == "Горожане":
            game = False
            bot.send_message(message.chat.id, f"Игра окончена, победа за :{winner}")
            return
        clear(dead=False)
        night = not night
        alive = get_all_alive()
        alive = "\n".join(alive)
        bot.send_message(message.chat.id, f"В игре:\n{alive}")
        sleep(10)
        autopl_mafia() if night else autoplay_citizen(message)  



@bot.message_handler(func=lambda message: message.text.lower() == "готов", chat_types=["private"])
def send_text(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name} играет")
    insert_player(message.chat.id, message.from_user.first_name)

@bot.message_handler(commands=['start'])
def game_on(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("готов"))
    bot.send_message(message.chat.id, "Нажмите на кнопку ниже", reply_markup=keyboard)

@bot.message_handler(commands=['game'])
def game_start(message):
    global game
    players = players_amount()
    if players >= 5 and not game:
        set_roles(players)
        players_roles = get_pl_roles()
        mafia_usernames = get_mafia_us()
        for player_id, role in players_roles:
            try:
                bot.send_message(player_id, role)
            except:
                print(f"ID: {player_id}\nRole: {role}")
                continue
            if role == "mafia":
                bot.send_message(player_id, f"Все члены мафии:\n{mafia_usernames}")
        game = True
        clear(dead=True)
        bot.send_message(message.chat.id, "Игра началась")
        game_loop(message)
        return
    bot.send_message(message.chat.id, "Недостаточно людей")
    for i in range(5 - players):
        bot_name = f"robot_{i}"
        insert_player(i, bot_name)
        bot.send_message(message.chat.id, f"{bot_name} добавлен")


@bot.message_handler(commands=["kick"])
def kick(message):
    username = "".join(message.text.split(" ")[1:])
    usernames = get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, "Такого имени нет")
            return
        voted = vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, "Ваш голос учтён")
            return
        bot.send_message(message.chat.id, "У вас больше нет права голосовать")
    bot.send_message(message.chat.id, "Сейчас ночь вы не можете никого выгнать")

@bot.message_handler(commands=["kill"])
def kick(message):
    username = "".join(message.text.split(" ")[1:])
    usernames = get_all_alive()
    mafia_usernames = get_mafia_us()
    if  night and message.from_user.first_name in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id, "Такого имени нет")
            return
        voted = vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, "Ваш голос учтён")
            return
        bot.send_message(message.chat.id, "У вас больше нет права голоса)")
        return
    bot.send_message(message.chat.id, "Сейчас нельзя убивать")

        

bot.polling(non_stop=True)