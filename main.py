from fastapi import FastAPI
import pandas as pd
import json 
import ast
from fastapi import HTTPException

app = FastAPI()

peliculas = pd.read_csv('movies_dataset_desanidada.csv')

# Conversion de release date a datetime
peliculas['release_date'] = pd.to_datetime(peliculas['release_date'], errors='coerce')

# Nueva columna para el mes de estreno
meses_espanol = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
peliculas['release month'] = peliculas['release_date'].apply(lambda x: meses_espanol[x.month-1] if pd.notnull(x) else None)

# Nueva columna para el dia de estreno
dias_espanol = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
peliculas['release_day'] = peliculas['release_date'].apply(lambda x: dias_espanol[x.weekday()] if pd.notnull(x) else None)

### Funcion que te permite obetener el numero de filmaciones estrenadas cierto mes

@app.get('/cantidad-filmaciones1/{mes}')
def cantidad_filmaciones_mes(mes:str):
    cantidad = peliculas['release month'].value_counts().get(mes,0)
    texto = '{0} Películas fueron estrenadas en el mes de {1}'.format(cantidad,mes)
    return texto

### Funcion que te permite obtener el numero de filmacion estrenadas cierto dia

@app.get('/cantidad-filmaciones2/{dia}')
def cantidad_filmaciones_dia(dia:str):
    cantidad = peliculas['release_day'].value_counts().get(dia,0)
    texto = '{} Películas fueron estrenadas el dia {}'.format(cantidad, dia)
    return texto

### Funcion que al ingresar el titulo de una pelicula te permite conseguir el título, el año de estreno y el score.

@app.get('/score-Peliculas/{peli}')
def score_titulo(peli):
    filtro = peliculas['title'] == peli
    if filtro.sum() == 0:
        return 'Pelicula no encontrada'
    score = peliculas.loc[filtro, 'popularity'].values[0]
    f_lanzamiento = peliculas.loc[filtro, 'release_date'].dt.year.values[0]
    texto = 'La película {0} fue estrenada en el año {1} con una popularidad de {2}'.format(peli,f_lanzamiento,score)
    return texto

### Funcion que al ingrear el titulo de una pelicula te permite conseguir  el título, la cantidad de votos 
# y el valor promedio de las votaciones, debe existir al menos 2000 valoraciones para que se de un valor, caso contrario se devuelve none

@app.get('/votos-Peliculas/{peli}')

def votos_titulo(peli):
    filtro = peliculas['title'] == peli
    if filtro.sum() == 0:
        return 'Pelicula no encontrada'
    votos = peliculas.loc[filtro,'vote_count'].values[0]
    avg_votos=peliculas.loc[filtro,'vote_average'].values[0]
    f_lanzamiento = peliculas.loc[filtro, 'release_date'].dt.year.values[0]
    if votos < 2000:
        return None
    texto = 'La Pelicula {0} fue estrenada en el año {1} con un total de {2} votaciones y un promedio de {3}'.format(peli,f_lanzamiento,votos,avg_votos)
    
    return texto 
