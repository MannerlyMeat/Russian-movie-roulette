import requests
import sqlite3
import re
from bs4 import BeautifulSoup as bs

# conn = MySQLdb.connect("127.0.0.1", "root", "", "roulette_movies")
conn = sqlite3.connect('Russian-movie-roulette.db')

url = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
requestSite = requests.get(url, headers=headers, allow_redirects=True)
soup = bs(requestSite.text, "html.parser")


def get_count_pages():
    pages_count = soup.find_all('a', class_="page_num")
    return pages_count[len(pages_count) - 1].string


def get_fnames():
    for pages in range(int(get_count_pages())):
        active_url = ("https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc&page={}".format(pages))
        requestSite = requests.get(active_url, headers=headers, allow_redirects=True)
        soup = bs(requestSite.text, "html.parser")
        film_names = soup.find_all('a', class_="title")
        rating = soup.find_all('div', attrs = {'class':re.compile("metascore_w large movie")})
        fill_database(film_names, rating)


def create_sqlite_DB():
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS movies(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_name TEXT NOT NULL,
                    rating INT NOT NULL
                    );
                """)
    conn.commit()


def check_database(film_name):
    cur = conn.cursor()
    cur.execute("""select exists(select * from movies where movie_name = "{}")""".format(film_name))
    res = cur.fetchone()
    return res[0]


def insert_to_bd(movie_name: str, rating: int):
    cur = conn.cursor()
    text = r"""
                INSERT INTO movies(movie_name, rating) 
                VALUES('{movie_name}', {rating});
                """.format(movie_name=movie_name, rating=rating)
    print(text)
    cur.execute(r"""
                INSERT INTO movies(movie_name, rating) 
                VALUES("{movie_name}", {rating});
                """.format(movie_name=movie_name, rating=rating))
    conn.commit()


def delete_name_film(movie_name):
    cur = conn.cursor()
    cur.execute("DELETE FROM movies WHERE movie_name='{}'".format(movie_name))
    conn.commit()
    print(cur.fetchall())


def fill_database(film_names, film_rating):

    for i in range(len(film_names)):
        sip = film_names[i].h3.string
        sip = sip.replace('"', '')
        temp_bool = check_database(sip)
        print(len(film_names))
        print(len(film_rating))
        if not temp_bool:
            insert_to_bd(sip, int(film_rating[i].string))
            conn.commit()
    





get_fnames()

