import requests
import sqlite3
import re
from bs4 import BeautifulSoup as bs


# conn = MySQLdb.connect("127.0.0.1", "root", "", "roulette_movies")
conn = sqlite3.connect('Russian-movie-roulette.db')

#url_metacriric = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
url_imdb = "https://www.imdb.com/search/title/?&explore=title_type&view=simple&title_type=short,tvSeries,tvMovie,tvMiniSeries"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
#requestSite = requests.get(url_metacriric, headers=headers, allow_redirects=True)
#soup = bs(requestSite.text, "html.parser")


def get_count_pages():
    pages_count = soup.find_all('a', class_="page_num")
    return pages_count[len(pages_count) - 1].string


def get_fnames():
    for pages in range(int(get_count_pages())):
        active_url = ("https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc&page={}".format(pages))
        requestSite = requests.get(active_url, headers=headers, allow_redirects=True)
        soup = bs(requestSite.text, "html.parser")
        film_names = soup.find_all('a', class_="title")
        rating = soup.find_all('div', attrs={'class': re.compile("metascore_w large movie")})
        film_url = soup.find_all('a', class_="title", href=True)
        #print(film_url[1].get('href'))
        fill_database(film_names, rating, film_url)


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


def insert_to_bd(movie_name: str, rating: int, film_url: str):
    cur = conn.cursor()
    text = r"""
                INSERT INTO movies(movie_name, rating, url) 
                VALUES('{movie_name}', {rating}, '{film_url}');
                """.format(movie_name=movie_name, rating=rating, film_url=film_url)
    print(text)
    cur.execute(r"""
                INSERT INTO movies(movie_name, rating, url) 
                VALUES("{movie_name}", {rating}, '{film_url}');
                """.format(movie_name=movie_name, rating=rating, film_url=film_url))
    conn.commit()


def delete_name_film(movie_name):
    cur = conn.cursor()
    cur.execute("DELETE FROM movies WHERE movie_name='{}'".format(movie_name))
    conn.commit()
    print(cur.fetchall())


def fill_database(film_names, film_rating, film_url):

    for i in range(len(film_names)):
        sip = film_names[i].h3.string
        sip = sip.replace('"', '')
        temp_bool = check_database(sip)
        print(len(film_names))
        print(len(film_rating))
        if not temp_bool:
            insert_to_bd(sip, int(film_rating[i].string), str(film_url[i].get('href')))
            conn.commit()


def get_films_imdb():
    imdb_film("1-50 of 1,309,202 titles.")
    print(imdb_film("1-50 of 1,309,202 titles."))


def imdb_film(a):
    a = re.findall(r"[-+]?\d+", a)
    for i in range(len(a)):
        if i <= 1:
            a.pop(0)
        else:
            imdb_film_count = "".join(a)
    return(int(imdb_film_count))




get_films_imdb()
#get_fnames()

