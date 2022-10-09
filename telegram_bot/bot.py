import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
import random

token = "token"
conn = sqlite3.connect('../Russian-movie-roulette.db')


logging.basicConfig(level=logging.INFO)
cur = conn.cursor()
rnd = random

bot = Bot(token=token)
dp = Dispatcher(bot)


def get_count():
    cur.execute("""select count(id) from movies""")
    db_count = cur.fetchall()
    return int(db_count[0][0])


def start_negative_ratings():
    cur.execute("""select id from movies where rating = 35""")
    awfull_rating = cur.fetchone()
    return awfull_rating[0]


def positive_rating_films():
    cur.execute("""select movie_name, rating from movies where id = {}""".format(rnd.randint(0, start_negative_ratings())))
    return cur.fetchone()


def negative_rating_film():
    cur.execute("""select movie_name, rating from movies where id = {}""".format(rnd.randint(start_negative_ratings(), get_count())))
    return cur.fetchone()


@dp.message_handler(commands=['start'])
async def start_roullete(message: types.Message):
    film_list = []
    for i in range(5):
        film_list.append(positive_rating_films())
        await message.reply("{}-й фильм в барабане ".format(i+1) + film_list[i][0] + " с рейтингом {}".format(film_list[i][1]))
        time.sleep(1)
    film_list.append(negative_rating_film())
    await message.reply("6-й фильм в барабане " + film_list[5][0] + " с рейтингом {}".format(film_list[5][1]))
    await message.reply("Крутим барабан")
    await bot.send_animation(message.chat.id, animation="CgACAgQAAxkBAAIHB2NBjipJ-W3cmwABJwmZGlcmZu0UUQACFwMAAkSWJFPR7R-4oWeuUyoE")
    rnd.shuffle(film_list)
    time.sleep(1)
    shot = rnd.randint(0, 5)
    if film_list[shot][1] > 35:
        await message.reply("Сегодня удача на твоей стороне, {}".format(message.from_user.first_name) + ". Тебе выпал {}".format(film_list[shot][0]) + " с рейтингом {}".format(film_list[shot][1]))
    else:
        await message.reply("Не в этот раз, {}".format(message.from_user.first_name) + ". Видимо удача сегодня не на твоей стороне, раз тебе выпал {}".format(film_list[shot][0]) + " с рейтингом {}".format(film_list[shot][1]))






executor.start_polling(dp, skip_updates=True)
