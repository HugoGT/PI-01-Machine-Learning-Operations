# API

import pandas as pd
from fastapi import FastAPI


# Cargar los datasets como dataframes de pandas
movies = pd.read_csv("movies.csv", index_col='id')
genres = pd.read_csv("genres.csv", index_col='id').to_dict(
    orient='dict')['genre']
actors = pd.read_csv("actors.csv", index_col='id').to_dict(
    orient='dict')['actor']
directors = pd.read_csv("directors.csv", index_col='id').to_dict(
    orient='dict')['director']


app = FastAPI()


@app.get("/")
def home():

    return genres
