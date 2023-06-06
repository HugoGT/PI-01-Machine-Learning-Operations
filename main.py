# API

import pandas as pd
from fastapi import FastAPI


# Cargar el dataset de películas como un dataframe de pandas
movies = pd.read_csv("movies.csv", index_col='id')

# Cargar los datasets como diccionarios para un fácil acceso
genres = pd.read_csv("genres.csv", index_col='id').to_dict(
    orient='dict')['genre']
actors = pd.read_csv("actors.csv", index_col='id').to_dict(
    orient='dict')['actor']
directors = pd.read_csv("directors.csv", index_col='id').to_dict(
    orient='dict')['director']

# Se crea el diccionario de meses para la ruta get months
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
        return {"message": f"El día {day} no existe, revise el dato enviado"}

    return {"message": f"{amount} películas fueron estrenadas el día {day}"}
