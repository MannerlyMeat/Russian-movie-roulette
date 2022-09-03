import requests
import sqlite3
# import MySQLdb
from bs4 import BeautifulSoup as bs

# conn = MySQLdb.connect("127.0.0.1", "root", "", "roulette_movies")
conn = sqlite3.connect('Russian-movie-roulette.db')

url = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
requestSite = requests.get(url, headers=headers, allow_redirects=True)
soup = bs(requestSite.text, "html.parser")
#print(r.status_code)


def get_count_pages():
    pages_count = soup.find_all('a', class_="page_num")
    return pages_count[len(pages_count) - 1].string


def get_fnames():
    for pages in range(int(get_count_pages())):
        print(pages)
        active_url = ("https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc&page={}".format(pages))
        requestSite = requests.get(active_url, headers=headers, allow_redirects=True)
        soup = bs(requestSite.text, "html.parser")
        film_names = soup.find_all('a', class_="title")
        rating = soup.find_all('div', class_="metascore_w large movie positive")
        print(rating)
        fill_database(film_names, rating)

#    film_names = soup.find_all('a', class_="title")
#    rating = soup.find_all('div', class_="metascore_w large movie positive")
#    fill_database(film_names, rating)

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
    # check_film = conn.cursor()
    cur = conn.cursor()
    # check_film.execute('select exists(select * from roulette_movies.movies where movie_name = "{}")'.film_name)
    cur.execute('select exists(select * from movies where movie_name = "{}")'.format(film_name))
    res = cur.fetchone()
    return res[0]


def insert_to_bd(movie_name: str, rating: int):
    cur = conn.cursor()
    print(movie_name, rating)
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
    
    # insert_table = conn.cursor()
    for i in range(len(film_names)):
        sip = film_names[i].h3.string
        temp_bool = check_database(sip)
        if not temp_bool:
            # insert_table.execute("INSERT INTO roulette_movies.movies (movie_name, rating) VALUES (%s, %s)",
            #                       (film_names[i].h3.string, int(film_rating[i].string)))
            insert_to_bd(film_names[i].h3.string, int(film_rating[i].string))
            conn.commit()
    


#count = soup.find_all('span', class_="title numbered")
#count = len(count)

get_fnames()
#all_Pages = get_count_pages()
