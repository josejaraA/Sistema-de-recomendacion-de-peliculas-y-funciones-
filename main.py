from fastapi import FastAPI
import pandas as pd
import json 
import ast
import uvicorn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from fastapi import FastAPI, HTTPException

app = FastAPI()

peliculas = pd.read_csv("Dataset_LimpioV.csv")


#Limpiar datos nulos
peliculas['overview'] = peliculas['overview'].fillna('')

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
peliculas['release_date'] = pd.to_datetime(peliculas['release_date'], errors='coerce')

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


# Expandir la lista de actores en filas separadas
df_actores = peliculas.explode('actores')

### Esta funcion recibe el nombre del actor obtiene la cantidad de películas en las que ha participado y el promedio de retorno.
peliculas['actores'] = peliculas['actores'].apply(ast.literal_eval)
@app.get('/actores/{nombre}')

def get_actor(nombre):

    peliculas_actor = df_actores[df_actores['actores'] == nombre]

    dimensiones = peliculas_actor.shape

    num_pelis = dimensiones[0]

    retorno_total = peliculas_actor['revenue'].sum()

    promedio_retorno = peliculas_actor['revenue'].mean()

    texto = 'El actor {0} ha participado en {1} peliculas, el mimso ha conseguido un retorno de {2} con un promedio {3} por filamcion'.format(nombre,num_pelis,retorno_total,promedio_retorno)

    return texto



### Esta funcion obtiene el retorno generado por un director, ademas devuelve el nombre de cada pelicula en la que ha trabajado, incluyendo fecha de lanzamiento retorno individual , costo y ganancia

@app.get('/director-films/{director}')
def get_director(director):

        # Asegúrate de que las listas de directores estén en el formato correcto
    peliculas['Directores'] = peliculas['Directores'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Filtra las películas por el director
    df_director = peliculas[peliculas['Directores'].apply(lambda x: director in x if x else False)]

    dimensiones = df_director.shape
    cantidad = dimensiones[0]
    cantidad = int(cantidad)
    df_director['budget'] = pd.to_numeric(df_director['budget'], errors='coerce').fillna(0).astype(int)
    df_director['revenue'] = pd.to_numeric(df_director['revenue'], errors='coerce').fillna(0).astype(int)
    texto = 'El numero de peliculas en las que el director a trabajado es: {0}'.format(cantidad)
    resultado = df_director[['title', 'release_date', 'budget', 'revenue']].to_dict(orient='records')
    return texto, resultado



# Filtracion de datos
peliculas_filtradas = peliculas[peliculas['vote_average'] > 5]
peliculas_filtradas = peliculas_filtradas[peliculas_filtradas['original_language'] == 'en']
peliculas_filtradas = peliculas_filtradas.drop_duplicates(subset='title')
peliculas_filtradas.reset_index(drop=True, inplace=True)


# Combinar características relevantes
def combinar_caracteristicas(row):
    return f"{row['genres']} {row['overview']} {row['tagline']} {row['production_companies']} {row['actores']}"
peliculas_filtradas['combined_features'] = peliculas_filtradas.apply(combinar_caracteristicas, axis=1)

# Vectorización TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(peliculas_filtradas['combined_features'])

# Modelo K-Vecinos
knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(tfidf_matrix)

# Mapeo de títulos a índices
indices = pd.Series(peliculas_filtradas.index, index=peliculas_filtradas['title']).drop_duplicates()

# Función de recomendación
def obtener_recomendaciones_knn(titulo, n_recommendations=6):
    if titulo not in indices:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    idx = indices[titulo]
    distances, indices_knn = knn.kneighbors(tfidf_matrix[idx], n_neighbors=n_recommendations)
    similar_movies = peliculas_filtradas.iloc[indices_knn[0][1:]]['title']
    
    return similar_movies.tolist()

@app.get('/Recomendaciones/{titulo}')
def recomendaciones(titulo: str):
    try:
        recomendaciones_knn = obtener_recomendaciones_knn(titulo)
        return recomendaciones_knn
    except HTTPException as e:
        return {"Pelicula no encontrada"}
