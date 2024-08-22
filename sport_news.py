import threading
from email.mime import message
from hashlib import new
from http import client
from io import BufferedRandom
from operator import ne
from pstats import Stats
from unicodedata import category
import requests
from bs4 import BeautifulSoup
import telebot
import time
import sqlite3
from telebot import types
import threading
lock = threading.Lock()

on_off=True

with open('token.txt', 'r') as f:
    token = f.read().strip()

bot = telebot.TeleBot(token)

#створення бази даних
try:
    my_file = open("orders.db", "r+")
except BaseException:
    my_file = open("orders.db", "w+")

conn = sqlite3.connect('orders.db',check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id INT PRIMARY KEY,
   user_name TEXT,
   user_admin INT,
   football_news INT,
   MMA_news INT,
   biathlon_news INT,
   tenis_news INT,
   basketball_news INT,
   hockey_news INT,
   on_off TEXT);
""")
conn.commit()

#створення кнопок
markup = types.InlineKeyboardMarkup(row_width=2)
all_bt = types.InlineKeyboardButton("🌐Всі новини🌐", callback_data='all_news')
football_bt = types.InlineKeyboardButton("⚽Футбол⚽", callback_data='football')
mma_bt = types.InlineKeyboardButton("🥊Бокс🥊", callback_data='mma')
biathlon_bt = types.InlineKeyboardButton("🎿Біатлон🎿", callback_data='biathlon')
tennis_bt = types.InlineKeyboardButton("🎾Теніс🎾", callback_data='tennis')
basketball_bt = types.InlineKeyboardButton("🏀Баскетбол🏀", callback_data='basketball')
hockey_bt = types.InlineKeyboardButton("🏒Хокей🏒", callback_data='hockey')
markup.add(football_bt, mma_bt, biathlon_bt, tennis_bt, basketball_bt, hockey_bt, all_bt)


keyboard = types.ReplyKeyboardMarkup(row_width=2)
adds_bt = types.KeyboardButton("Замовити рекламу")
category_choose_bt = types.KeyboardButton("Вибрати категорію")
categoryse_bt = types.KeyboardButton("Підключені категорії")
settings_bt = types.KeyboardButton("Налаштування")
statistic_bt = types.KeyboardButton("Статистика користувачів")
keyboard.add(category_choose_bt, categoryse_bt, settings_bt, statistic_bt, adds_bt)

setting_keys = types.ReplyKeyboardMarkup()
resume_bt = types.KeyboardButton("Відновити розсилку")
stop_news_bt = types.KeyboardButton("Зупинити розсилку")
setting_keys.add(resume_bt, stop_news_bt)

confirm_keys = types.ReplyKeyboardMarkup()
confirm_bt = types.KeyboardButton("Так")
cancel_bt = types.KeyboardButton("Ні")
confirm_keys.add(confirm_bt, cancel_bt)

def data_insert(message):
    now_id=message.chat.id
    cur.execute(f"SELECT user_id FROM users WHERE user_id={now_id}")
    data=cur.fetchone()
    if data == None:
        user=(message.chat.id,message.from_user.username,0,0,0,0,0,0,0,"on")
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", user)
        conn.commit()
        
def save_image_from_url(image_url, file_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Не вдалося завантажити зображення: HTTP статус {response.status_code}")
    except Exception as e:
        print(f"Виникла помилка: {e}")


#start
@bot.message_handler(commands=["start"])
def start(message, res=False):
    data_insert(message)
    bot.send_message(message.chat.id, "Привіт. я бот зі спортивними новинами")
    bot.send_message(message.chat.id,"Виберіть категорію розсилки:", reply_markup=markup)
 

#admin help
@bot.message_handler(commands=["admin_help"])
def admin_help(message, res=False):
    data_insert(message)
    cur.execute(f"SELECT * FROM users WHERE user_id={message.chat.id}")
    data=cur.fetchall()
    if data[0][2]==1:
        bot.send_message(message.chat.id, "/post_message - постить текст усім користувачам бота\n")


#статистика
total_users="0"
new_users="0"


@bot.message_handler(commands=["post_message"])
def send_welcome(message):
    data_insert(message)
    cur.execute(f"SELECT * FROM users WHERE user_id={message.chat.id}")
    data=cur.fetchall()
    if data[0][2]==1:
        msg = bot.reply_to(message,"Напишіть пост")
        bot.register_next_step_handler(msg,process_post)
        
def process_post(message):
    global post_txt
    post_txt=message.id
    global chat_id
    chat_id=message.chat.id
    msg = bot.reply_to(message,"Для підтвердження натисніть Так, інакше натисніть Ні", reply_markup=confirm_keys)
    bot.register_next_step_handler(msg,post_confirm)
    
def post_confirm(message):
    if message.text=="Так":
        bot.send_message(message.chat.id, "Пост відправлений", reply_markup=keyboard)
        cur.execute("SELECT * FROM users")
        data=cur.fetchall()
        for i in range(len(data)):
            bot.copy_message(data[i][0],chat_id,post_txt)
    else:
        bot.send_message(message.chat.id, "Пост був скасований", reply_markup=keyboard)


category_texts = {
    "football": "⚽️Футбол⚽️",
    "mma": "🥊Бокс🥊",
    "biathlon": "🎿Біатлон🎿",
    "tenis": "🎾Теніс🎾",
    "basketball": "🏀Баскетбол🏀",
    "hockey": "🏒Хокей🏒"
}

@bot.callback_query_handler(func=lambda call: True)
def choose_url(call):
    u_id = call.from_user.id
    data = call.data
    cur.execute(f"SELECT user_id FROM users WHERE user_id={u_id}")
    data_check=cur.fetchone()
    if data_check == None:
        user=(call.from_user.id,call.from_user.username,0,0,0,0,0,0,0,"on")
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", user)
        conn.commit()
    cur.execute(f"SELECT * FROM users WHERE user_id={u_id}")
    user_data = cur.fetchone()
    if data == "all_news":
        cur.execute(f"UPDATE users SET football_news=1, MMA_news=1, biathlon_news=1, tenis_news=1, basketball_news=1, hockey_news=1 WHERE user_id = {u_id}")
        conn.commit()
        bot.send_message(call.message.chat.id, "усі категорії підключені", reply_markup=keyboard)
    elif data in ("football", "mma", "biathlon", "tenis", "basketball", "hockey"):
        category_index = {'football': 3, 'mma': 4, 'biathlon': 5, 'tenis': 6, 'basketball': 7, 'hockey': 8}[data]
        
        category_news = user_data[category_index]
        new_state = 1 if category_news == 0 else 0
        cur.execute(f"UPDATE users SET {data}_news = {new_state} WHERE user_id = {u_id}")
        conn.commit()

        category_text = category_texts[data]
        if new_state == 1:
            bot.send_message(call.message.chat.id, f"ви підключили: {category_text}", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, f"ви відключили: {category_text}", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def choose_url(m, res=False):
    if(m.text == "Замовити рекламу"):
        bot.send_message(m.chat.id,"щоб замовити рекламу пишіть https://t.me/Deonax")
    elif(m.text =="Вибрати категорію"):
        bot.send_message(m.chat.id,"Виберіть категорію:", reply_markup=markup)
    elif(m.text =="Підключені категорії"):
        u_id=m.chat.id
        data_insert(m)
        cur.execute(f"SELECT * FROM users WHERE user_id={u_id}")
        data=cur.fetchone()
        ct_text=""
        if data[3]==1:
            ct_text=ct_text+"⚽Футбол⚽\n"
        if data[4]==1:
            ct_text=ct_text+"🥊Бокс🥊\n"
        if data[5]==1:
            ct_text=ct_text+"🎿Біатлон🎿\n"
        if data[6]==1:
            ct_text=ct_text+"🎾Теніс🎾\n"
        if data[7]==1:
            ct_text=ct_text+"🏀Баскетбол🏀\n"
        if data[8]==1:
            ct_text=ct_text+"🏒Хокей🏒\n"
        if ct_text:
            bot.send_message(u_id,ct_text,parse_mode="Markdown")
        else:
            bot.send_message(u_id,"У вас немає підключених категорій",parse_mode="Markdown")
    elif(m.text =="Налаштування"):
        bot.send_message(m.chat.id,"Налаштуйте бота", reply_markup=setting_keys)    
        
    elif(m.text =="Відновити розсилку"):
        u_id=m.chat.id
        data_insert(m)
        cur.execute(f"UPDATE users SET on_off = 'on' WHERE user_id = {u_id}")
        bot.send_message(m.chat.id,"Новини відновлені", reply_markup=keyboard)
        conn.commit()
        
    elif(m.text == "Зупинити розсилку"):
        u_id=m.chat.id
        data_insert(m)
        cur.execute(f"UPDATE users SET on_off = 'off' WHERE user_id = {u_id}")
        bot.send_message(m.chat.id,"Новини вимкнені", reply_markup=keyboard)
        conn.commit()
        
    elif(m.text == "Статистика користувачів"):
        cur.execute("SELECT COUNT(*) FROM users")
        users_count = cur.fetchone()[0]
        stats="Активних користувачів -- "+str(users_count)
        bot.send_message(m.chat.id,stats)
    

def send_news(url, column_index):
    old_url = ""
    while True:
        try:
            time.sleep(5)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            headline = soup.find("div", {"class": "item team-news"})
            inf_url = headline.find("div", {"class": "item-title"}).find('a').get("href")
            if old_url != inf_url:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                headline = soup.find("div", {"class": "item team-news"})
                img_url = headline.find("div", {"class": "team-news-img"}).find("img").get("data-src")
                inf_url = headline.find("div", {"class": "item-title"}).find('a').get("href")
                title = headline.find("div", {"class": "item-title"}).find('a').get_text()
                txt =headline.find("p", {"class": "item-text"}).get_text()
                markup_url = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text='Читати більше', url=inf_url)
                markup_url.add(url_button)
                news_txt = title + "\n" + txt
                image_url = img_url
                file_path = 'image.jpg'
                save_image_from_url(image_url, file_path)
                with open(file_path, 'rb') as file:
                    photo_content = file.read()
                with lock:
                    cur.execute("SELECT * FROM users")
                    data = cur.fetchall()
                    print(data)
                if data != "":
                    for i in range(len(data)):
                        if data[i][column_index] == 1:
                            if data[i][-1] == "on":
                                if old_url != inf_url:
                                    bot.send_photo(chat_id=data[i][0], photo=photo_content, caption=news_txt, reply_markup=markup_url)
                old_url = inf_url
        except Exception as e:
            print("Виникла помилка:", type(e).__name__)

def start_news_threads():
    urls = [
        ("https://sport.ua/uk/news/football", 1),
        ("https://sport.ua/uk/news/mma", 4),
        ("https://sport.ua/uk/news/biathlon", 5),
        ("https://sport.ua/uk/news/basketball", 7),
        ("https://sport.ua/uk/news/tennis", 6),
        ("https://sport.ua/uk/news/hockey", 8),
    ]

    threads = []
    
    bot_thread = threading.Thread(target=bot.polling)
    bot_thread.start()
    
    for url, column_index in urls:
        t = threading.Thread(target=send_news, args=(url, column_index))
        t.start()
        threads.append(t)
        time.sleep(5)

    for t in threads:
        t.join()
        time.sleep(5)
        

start_news_threads()
bot.polling()
