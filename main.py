# API

import pandas as pd
from fastapi import FastAPI


# Cargamos el dataset de películas como un dataframe de pandas
movies = pd.read_csv("data/movies.csv", index_col='id')

# Convertimos estas columnas en listas para practicidad
movies[['genres_id', 'actors_id', 'directors_id']] = movies[[
    'genres_id', 'actors_id', 'directors_id']].apply(lambda x: x.apply(eval))

# Cargamos los datasets como diccionarios para un fácil acceso
genres = pd.read_csv("data/genres.csv", index_col='genre').to_dict(
    orient='dict')['id']
actors = pd.read_csv("data/actors.csv", index_col='actor').to_dict(
    orient='dict')['id']
directors = pd.read_csv("data/directors.csv", index_col='director').to_dict(
    orient='dict')['id']

# Creamos el diccionario de meses para la ruta get months
months = {
    1: 'enero',
    2: 'febrero',
    3: 'marzo',
    4: 'abril',
    5: 'mayo',
    6: 'junio',
    7: 'julio',
    8: 'agosto',
    9: 'septiembre',
    10: 'octubre',
    11: 'noviembre',
    12: 'diciembre'
}


app = FastAPI()


@app.get("/")
def home():

    return genres


# Función para obtener la cantidad de filmaciones en un mes específico
@app.get("/mes/{month}")
def films_per_month(month: str):
    # Lógica para calcular la cantidad de películas estrenadas en el mes
    month = month.lower()
    num_month = None

    # Obtener el número de mes correspondiente al nombre
    for num, name_month in months.items():
        if month == name_month:
            num_month = num
            break

    # Si no está el mes, devolvemos una respuesta pidiendo nuevamente el dato
    if num_month is None:
        return {"message": f"No existe el mes: '{month}', revise el dato envíado"}

    # Contar la cantidad de películas estrenadas en el mes
    amount = len(movies[movies['release_month'] == num_month])

    return {"message": f"{amount} películas fueron estrenadas en el mes de {month}"}


# Función para obtener la cantidad de filmaciones en un día específico
@app.get("/dia/{day}")
def films_per_day(day: str):
    # Lógica para calcular la cantidad de películas estrenadas en el día
    day = day.lower().replace('é', 'e').replace('á', 'a')

    # Contar la cantidad de películas estrenadas en el mes
    amount = len(movies[movies['release_day'] == day])

    if amount == 0:
        return {"message": f"El día {day} no existe, revise el dato enviado."}

    return {"message": f"{amount} películas fueron estrenadas el día {day}."}


# Función para obtener el score de una filmación por su título o sus votos por títulos
@app.get("/movies/{movie}/{info}")
def title_score(movie: str, info: str):
    # Lógica para obtener el título, año de estreno y score de la filmación
    movie = movie.lower()
    info = info.lower()

    if info not in ['score', 'votos']:
        return {"message": f'Se puede solicitar solamente el score y los votos'}

    # Filtrar el DataFrame por título de la película
    filtered_movies = movies[movies['title'].str.lower() == movie]

    if filtered_movies.empty:
        return {"message": f"No se encontró la película {movie}."}

    # Obtener los datos del DataFrame filtrado
    else:
        title = filtered_movies['title'].iloc[0]
        year = filtered_movies['release_year'].iloc[0]
        popularity = filtered_movies['popularity'].iloc[0]
        vote_count = filtered_movies['vote_count'].iloc[0]
        vote_average = filtered_movies['vote_average'].iloc[0]

        if info == 'score':
            return {
                "message": f"La película {title} fue estrenada en el año {year}. La misma cuenta con una popularidad de {popularity}."
            }
        elif info == 'votos':
            if vote_count < 2000:
                return {
                    "message": f"La película {title} fue estrenada en el año {year}, pero no cuenta con las suficientes valoraciones para poder dar un promedio."
                }
            else:
                return {
                    "message": f"La película {title} fue estrenada en el año {year}. La misma cuenta con {vote_count} votos que dan un promedio de {vote_average} de 10."
                }


# Función para obtener el actor
@app.get("/actors/{actor}")
def get_actor(actor: str):
    # Lógica para obtener el éxito del director y detalles de todas sus películas
    actor = actor.lower()
    r_actor = actor.title()
    # Buscar el id del actor en el diccionario, si da un key error es porque no existe
    try:
        actor_id = actors[actor]
    except KeyError:
        return {"message": f"No se encontró el actor {r_actor} revise el dato"}

    # Filtramos las películas en las que ha participado el actor
    actor_films = movies[movies['actors_id'].apply(
        lambda ids: actor_id in ids)]

    if actor_films.empty:
        return {"message": f"No se encontraron filmaciones para el actor {r_actor}"}

    # Se calcula la cantidad de filmaciones y el retorno promedio se calcula solo de las filas en que el retorno es diferente a 0
    films_return = actor_films[actor_films['return'] != 0]
    avg_return = round(films_return['return'].mean(), 2)

    return {"message": f"El actor {r_actor} ha participado de {len(actor_films)} cantidad de filmaciones, el mismo ha conseguido un retorno promedio de {avg_return} por filmación"}


# Función para obtener el éxito de un director y detalles de sus películas
@app.get("/directors/{director}")
def get_director(director: str):
    director = director.lower()
    r_director = director.title()
    # Buscamos el id del actor en el diccionario, si da un key error es porque no existe
    try:
        director_id = directors[director]
    except KeyError:
        return {"message": f"No se encontró el director {r_director} revise el dato"}
    # Buscamos el director en el DataFrame de películas
    director_films = movies[movies['actors_id'].apply(
        lambda ids: director_id in ids)]

    if director_films.empty:
        return {"message": f"No se encontraron filmaciones para el director {r_director}"}

    # Calculamos el éxito del director y los detalles de sus películas
    peliculas = []
    for _, row in director_films.iterrows():
        titulo = row['title']
        fecha_lanzamiento = row['release_date']
        costo = row['budget']
        ganancia = row['revenue']
        retorno = round(row['return'], 2)
        peliculas.append((titulo, fecha_lanzamiento, costo, ganancia, retorno))

    # Sacamos el retorno en promedio de director
    films_return = director_films[director_films['return'] != 0]
    avg_return = round(films_return['return'].mean(), 2)

    return {
        "message": f'{r_director} ha dirigido {len(director_films)} películas',
        "éxito": f'{avg_return} es el promedio de retorno de sus películas',
        "peliculas": [
            {
                "titulo": titulo,
                "fecha_lanzamiento": fecha_lanzamiento,
                "costo": costo,
                "ganancia": ganancia,
                "retorno": retorno
            }
            for titulo, fecha_lanzamiento, costo, ganancia, retorno in peliculas
        ]
    }
