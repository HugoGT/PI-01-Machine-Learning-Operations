# Data for the api

import pandas as pd


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
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12
}
