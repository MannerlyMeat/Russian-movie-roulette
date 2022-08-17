import requests
import MySQLdb
from bs4 import BeautifulSoup as bs

conn = MySQLdb.connect("127.0.0.1", "root", "", "roulette_movies")
url = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get(url, headers=headers, allow_redirects=True)
soup = bs(r.text, "html.parser")
print(r.status_code)


def get_count_pages():
    pages_count = soup.find_all('a', class_="page_num")
    return pages_count[len(pages_count) - 1].string


def get_fnames():
    film_names = soup.find_all('a', class_="title")
    rating = soup.find_all('div', class_="metascore_w large movie positive")
    fill_database(film_names, rating)


def check_database(film_name):
    check_film = conn.cursor()
    check_film.execute('select exists(select * from roulette_movies.movies where movie_name = "%s")' % film_name)
    res = check_film.fetchone()
    return res[0]


def fill_database(film_names, film_rating):
    insert_table = conn.cursor()
    for i in range(len(film_names)):
        sip = film_names[i].h3.string
        temp_bool = check_database(sip)
        if not temp_bool:
            insert_table.execute("INSERT INTO roulette_movies.movies (movie_name, rating) VALUES (%s, %s)",
                                 (film_names[i].h3.string, int(film_rating[i].string)))
            conn.commit()
    conn.close()


count = soup.find_all('span', class_="title numbered")
count = len(count)

get_fnames()
all_Pages = get_count_pages()
