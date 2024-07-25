from fastapi import FastAPI
import pandas as pd
import json 
import ast
import uvicorn


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Usa el puerto por defecto 8000 si PORT no está disponible
    uvicorn.run(app, host="0.0.0.0", port=port)

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


data_set = pd.read_csv('Union.csv')


# Función para extraer los nombres de los actores del campo 'cast'
def obtener_nombres_actores(cadena_cast):
    try:
        cast_list = json.loads(cadena_cast.replace("'", "\""))
        return [actor['name'] for actor in cast_list]
    except json.JSONDecodeError:
        return []

# Aplicar la función para obtener una columna con los nombres de los actores
data_set['actores'] = data_set['cast'].apply(obtener_nombres_actores)

# Expandir la lista de actores en filas separadas
df_actores = data_set.explode('actores')

### Esta funcion recibe el nombre del actor obtiene la cantidad de películas en las que ha participado y el promedio de retorno.

@app.get('/actores/{nombre}')

def get_actor(nombre):

    peliculas_actor = df_actores[df_actores['actores'] == nombre]

    dimensiones = peliculas_actor.shape

    num_pelis = dimensiones[0]

    retorno_total = peliculas_actor['revenue'].sum()

    promedio_retorno = peliculas_actor['revenue'].mean()

    texto = 'El actor {0} ha participado de {1} cantidad de peliculas, el mimso ha conseguido un retorno de {2} con un promedio {3} por filamcion'.format(nombre,num_pelis,retorno_total,promedio_retorno)

    return texto


#Esta funcion opbtiene los nombres de los directores

def obtener_nombres_directores(cadena_crew):
    try:
        crew_list = json.loads(cadena_crew.replace("'", "\""))
        return [persona['name'] for persona in crew_list if persona['job'] == 'Director']
    except json.JSONDecodeError:
        return []
data_set['Directores'] = data_set['crew'].apply(obtener_nombres_directores)


### Esta funcion obtiene el retorno generado por un director, ademas devuelve el nombre de cada pelicula en la que ha trabajado, incluyendo fecha de lanzamiento retorno individual , costo y ganancia

@app.get('/director-films/{director}')
def get_director(director):
    df_director = data_set[data_set['Directores'].apply(lambda x: director in x)]
    dimensiones = df_director.shape
    cantidad = dimensiones[0]
    cantidad = int(cantidad)
    df_director['budget'] = pd.to_numeric(df_director['budget'], errors='coerce').fillna(0).astype(int)
    df_director['revenue'] = pd.to_numeric(df_director['revenue'], errors='coerce').fillna(0).astype(int)
    df_director['release_date'] = pd.to_datetime(df_director['release_date'], errors='coerce')
    texto = 'El numero de peliculas en las que el director a trabajado es: {0}'.format(cantidad)
    resultado = df_director[['title', 'release_date', 'budget', 'revenue']].to_dict(orient='records')
    return texto, resultado
