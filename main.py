# API

from fastapi import FastAPI, status
from sklearn.metrics.pairwise import cosine_similarity

from data import actors, directors, months, movies, titles, weight_matrix


app = FastAPI(
    title="Movies API",
    description="Esta API fue creada con la intención entregar datos acerca de películas.",
    openapi_tags=[
        {
            "name": "Películas",
            "description": "movies routes"
        }
    ],
    version="1.0.0"
)


# Cuando entren a la API, podrán ver como usar la misma
@app.get(
    "/",
    name="Info de la API",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def info():
    return {
        "info": "Bienvenidos a mi API de Películas",
        "funciones": [
            "cantidad_filmaciones_mes/(ingrese un mes)",
            "cantidad_filmaciones_dia/(ingrese un dia)",
            "score_titulo/(ingrese una película)",
            "votos_titulo/(ingrese una película)",
            "get_actor/(ingrese un actor)",
            "get_director/(ingrese un director)",
            "recomendacion/(ingrese una película)"
        ]
    }


# Función para obtener la cantidad de filmaciones en un mes específico
@app.get(
    "/cantidad_filmaciones_mes/{month}",
    name="Obtener la cantidad de filmaciones por mes",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def films_per_month(month: str):
    """Se ingresa el mes y la función retorna la cantidad de películas que se etranaron ese mes históricamente"""

    month = month.lower()

    # Buscar el número del mes en el diccionario, si devuelve None es porque no existe
    num_month = months.get(month, None)

    if num_month == None:
        return {"mes": f"{month} no existe", "cantidad": None}

    # Contar la cantidad de películas estrenadas en el mes
    amount = len(movies[movies["release_month"] == num_month])

    return {"mes": month, "cantidad": amount}


# Función para obtener la cantidad de filmaciones en un día específico
@app.get(
    "/cantidad_filmaciones_dia/{day}",
    name="Obtener la cantidad de filmaciones por día",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def films_per_day(day: str):
    """Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrebaron ese dia historicamente."""

    day = day.lower().replace("é", "e").replace("á", "a")

    # Contar la cantidad de películas estrenadas en el mes
    amount = len(movies[movies["release_day"] == day])

    if amount == 0:
        return {"dia": f"{day} no existe", "cantidad": None}

    return {"dia": day, "cantidad": amount}


# Función para obtener el score de una filmación por su título
@app.get(
    "/score_titulo/{movie}",
    name="Obtener el score de una película",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def title_score(movie: str):
    """Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score."""

    movie = movie.lower()

    # Filtrar el DataFrame por título de la película
    filtered_movies = movies[movies["title"] == movie]

    if filtered_movies.empty:
        return {
            "titulo": f"No se encontró {movie}",
            "anio": None,
            "popularidad": None
        }

    # Obtener los datos del DataFrame filtrado
    else:
        year = filtered_movies["release_year"].iloc[0].item()
        popularity = filtered_movies["popularity"].iloc[0].item()

        return {
            "titulo": movie.title(),
            "anio": year,
            "popularidad": popularity
        }


# Función para obtener los votos de una filmación por su título
@app.get(
    "/votos_titulo/{movie}",
    name="Obtener votos de una película",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def title_votes(movie: str):
    """Se ingresa el título de una filmación esperando como respuesta el título, la cantidad de votos y el valor promedio de las votaciones."""

    movie = movie.lower()

    # Filtrar el DataFrame por título de la película
    filtered_movies = movies[movies["title"] == movie]

    if filtered_movies.empty:
        return {
            "titulo": f"No se encontró {movie}",
            "anio": None,
            "voto_total": None,
            "voto_promedio": None
        }

    else:
        year = filtered_movies["release_year"].iloc[0].item()
        vote_count = filtered_movies["vote_count"].iloc[0].item()
        vote_average = filtered_movies["vote_average"].iloc[0].item()

        if vote_count < 2000:
            return {
                "titulo": movie.title(),
                "anio": year,
                "voto_total": vote_count,
                "voto_promedio": None
            }
        else:
            return {
                "titulo": movie.title(),
                "anio": year,
                "voto_total": vote_count,
                "voto_promedio": vote_average
            }


# Función para obtener el actor
@app.get(
    "/get_actor/{actor}",
    name="Obtener retorno y cantidad de películas de un actor",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def get_actor(actor: str):
    """
    Se ingresa el nombre de un actor que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno, además de la cantidad de películas que en las que ha participado y el promedio de retorno.
    """

    actor = actor.lower()
    r_actor = actor.title()
    # Buscar el id del actor en el diccionario, si devuelve un None es porque no existe
    actor_id = actors.get(actor, None)

    if actor_id == None:
        return {
            "actor": f"{r_actor} no existe",
            "cantidad_filmaciones": None,
            "retorno_total": None,
            "retorno_promedio": None
        }

    # Filtramos las películas en las que ha participado el actor
    actor_films = movies[movies["actors_id"].apply(
        lambda ids: actor_id in ids)]

    if actor_films.empty:
        return {
            "actor": r_actor,
            "cantidad_filmaciones": 0,
            "retorno_total": 0,
            "retorno_promedio": 0
        }

    # Se calcula la cantidad de filmaciones y el retorno promedio se calcula solo de las filas en que el retorno es diferente a 0
    films_return = actor_films[actor_films["return"] != 0]
    avg_return = round(films_return["return"].mean(), 2)

    return {
        "actor": r_actor,
        "cantidad_filmaciones": len(actor_films),
        "retorno_total": actor_films["return"].sum(),
        "retorno_promedio": avg_return
    }


# Función para obtener el éxito de un director y detalles de sus películas
@app.get(
    "/get_director/{director}",
    name="Obtener éxito y películas del director",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def get_director(director: str):
    """
    Se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno.
    Devuelve el nombre de cada película con la fecha de lanzamiento, retorno individual, costo y ganancia de la misma.
    """

    director = director.lower()
    r_director = director.title()

    # Buscamos el id del director en el diccionario, si devuelve None es porque no existe
    director_id = directors.get(director, None)

    if director_id == None:
        return {
            "director": f"{r_director} no existe",
            "retorno_total_director": None,
            "peliculas": []
        }

    # Buscamos el director en el DataFrame de películas
    director_films = movies[movies["directors_id"].apply(
        lambda ids: director_id in ids)]

    if director_films.empty:
        return {
            "director": r_director,
            "retorno_total_director": 0,
            "peliculas": []
        }

    # Calculamos el éxito del director y los detalles de sus películas
    peliculas = []
    for _, row in director_films.iterrows():
        title = row["title"]
        release_date = row["release_year"]
        budget = row["budget"]
        revenue = row["revenue"]
        film_return = round(row["return"], 2)
        peliculas.append((title, release_date, budget, revenue, film_return))

    return {
        "director": r_director,
        "retorno_total_director": director_films["return"].sum(),
        "peliculas": [
            {
                "titulo": title,
                "anio": release_date,
                "budget_pelicula": budget,
                "revenue_pelicula": revenue,
                "retorno_pelicula": film_return
            }
            for title, release_date, budget, revenue, film_return in peliculas
        ]
    }


# Función para recomendar una lista de películas dada una película
@app.get(
    "/recomendacion/{title}",
    name="Obtener recomendación de películas",
    tags=["Películas"],
    status_code=status.HTTP_200_OK
)
def recomendation(title: str):
    """Ingresas un nombre de pelicula y te recomienda las similares en una lista"""
    title = title.lower()
    # Buscamos la película en el df de películas
    movie_id = movies.loc[movies["title"] == title].index

    # Si la a película no existe en el DataFrame se devuelve nulo
    if movie_id.empty:
        return {"lista recomendada": "No se encontró la película"}

    # Intentamos hacer un reshape para poder sacar la correlación con cosine_sim, si no se puede es porque la película no tiene suficente información para sacar alguna correlación
    try:
        movie = weight_matrix.loc[movie_id].iloc[0].to_numpy().reshape(1, -1)
    except KeyError:
        return {"lista recomendada": "No hay suficiente información de esta película para hacer alguna recomendación"}

    # Calculamos la similitud de coseno entre la película ingresada por el usuario y todas las demás películas
    cosine_sim = cosine_similarity(movie, weight_matrix)

    # Obtenemos los 5 índices de las películas más similares excluyendo la primera que es la que ingresa el usuario
    similar_movies = cosine_sim.argsort()[0][::-1][1:6]

    recomendation_list = []
    # Obtenemos los títulos de las películas similares y los añadimos a la lista de recomendación
    for i in similar_movies:
        recomendation_list.append((titles["title"].iloc[i]).title())

    return {"lista recomendada": sorted(recomendation_list)}


# Función para que no se apague el server de Render
@app.get("/healthz", include_in_schema=False)
def health_check():
    return status.HTTP_200_OK
