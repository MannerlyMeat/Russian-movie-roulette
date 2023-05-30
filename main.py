import requests
import sqlite3
import re
from bs4 import BeautifulSoup as bs


conn = sqlite3.connect('Russian-movie-roulette.db')


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}



#def get_count_pages():             #Функция получения количества страниц на metacritic
#    url_metacriric = "https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc"
#    requestSite = requests.get(url_metacriric, headers=headers, allow_redirects=True)
#    soup = bs(requestSite.text, "html.parser")
#    pages_count = soup.find_all('a', class_="page_num")
#    return pages_count[len(pages_count) - 1].string


#def get_fnames():                  #Функция парсинга фильмов с metacritic
#    for pages in range(int(get_count_pages())):
#        active_url = ("https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc&page={}".format(pages))
#        requestSite = requests.get(active_url, headers=headers, allow_redirects=True)
#        soup = bs(requestSite.text, "html.parser")
#        film_names = soup.find_all('a', class_="title")
#        rating = soup.find_all('div', attrs={'class': re.compile("metascore_w large movie")})
#        film_url = soup.find_all('a', class_="title", href=True)
#        fill_database(film_names, rating, film_url)


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


def fill_database(film_names, film_rating, film_url):       #Заполнение бд
    for i in range(len(film_names)):
        sip = film_names
        sip = sip.replace('"', '')
        temp_bool = check_database(sip)

        if not temp_bool:
            insert_to_bd(sip, film_rating, str(film_url))
            conn.commit()


def get_films_imdb():                   #Главная функция по парсингу с imdb
    url_imdb = "https://www.imdb.com/search/title/?title_type=short,tv_series,tv_movie,tv_miniseries&explore=title_type&view=advanced&user_rating=1.0,10.0"
    pages = round(get_imdb_films_number(url_imdb) / 50)
    for page in range(pages):
        filmName = get_film_name_imdb(url_imdb)
        rating = get_film_rating_imdb(url_imdb)
        filmUrl = get_film_address_imdb(url_imdb)
        print(len(rating))
        for films in range(len(filmName)-1):
            tmp = float(rating[films].strong.text)
            fill_database(filmName[films].a.string, int(tmp*10),
                          "https://www.imdb.com{0}".format(filmUrl[films].a.get('href')))
        url_imdb = get_next_address_imdb(url_imdb)
        print(url_imdb)


def get_imdb_films_number(url):            #Количество фильмов и сериалов на imdb. На этом строится логика перехода по страницам
    request = requests.get(url, headers=headers, allow_redirects=True)
    soup = bs(request.text, "html.parser")
    count_films = soup.find_all("div", class_="desc")
    count_films = re.findall(r"[-+]?\d+", count_films[1].span.string)
    for i in range(len(count_films)):
        if i <= 1:
            count_films.pop(0)
        else:
            imdb_film_count = "".join(count_films)
    return(int(imdb_film_count))


def get_next_address_imdb(url):          #Следущая ссылка
    url = requests.get(url, headers=headers, allow_redirects=True)
    soup = bs(url.text, "html.parser")
    url = soup.find_all("a", class_="lister-page-next next-page", href=True)
    url = "https://www.imdb.com{0}".format(url[0].get('href'))
    return url


def get_film_address_imdb(url):             #Парсер ссылкок на фильмы
    url = requests.get(url, headers=headers, allow_redirects=True)
    soup = bs(url.text, "html.parser")
    filmUrl = soup.find_all('h3', class_='lister-item-header')
    #filmUrl = tmp[num].a
    #url = "https://www.imdb.com{0}".format(filmUrl.get('href'))
    return filmUrl


def get_film_name_imdb(url):                #Функция получения названий
    url = requests.get(url, headers=headers, allow_redirects=True)
    soup = bs(url.text, "html.parser")
    filmName = soup.find_all('h3', class_='lister-item-header')
    return filmName


def get_film_rating_imdb(url):                  #Функция получение рейтингов фильмов
    url = requests.get(url, headers=headers, allow_redirects=True)
    soup = bs(url.text, "html.parser")
    rating = soup.find_all('div', class_='ratings-bar')
    #print(len(tmp))
    #rating = float(tmp[num].strong.text)
    return rating


get_films_imdb()
#get_fnames()



