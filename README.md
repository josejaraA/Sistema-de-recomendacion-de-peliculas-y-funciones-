# Funciones y Sistema de recomendación de películas 

Este proyecto implementa un sistema de recomendación de películas utilizando técnicas de procesamiento de lenguaje natural (NLP) y algoritmos de aprendizaje automático. El sistema recomienda películas basándose en la similitud de contenido utilizando la similitud del coseno y un modelo KNN.

## Descripcón del proyecto

El objetivo principal de este proyecto es desplegar una aplicación con FastApi que permita recomendar a los usuarios películas similares y tener acceso a la data de las peliculas, actores y directores

## Extacción, transformación y carga (ETL)
Leer el jupyter notebook 'ETL' para un mejor entendimiento
### ETL para movies_dataset.csv
- Al revisar el contenido de las columnas podemos notar que que hay muchas columnas que no necesitamos, por lo tanto las eliminamos
- Cambiamos el tipo de dato de la columna release_date a datetime
- Convertimos el tipo id a un entero natural de python
- Creamos nuevas columnas para el mes de estreno y para el dia de estreno en español
- Desanidamos la columana genres 
- Guardamos el dataset en un nuevo archivo

### ETL para credits.csv
- Al revisar los datos nos damos cuenta que estan anidadas las columnas cast y crew
- Extraemos el nombre de los actores en una nueva columna
- Extraemos el nombre del director en una nueva columna 
- Eliminamos las columnas cast y crew
- Finalmente unificamos los datasets de movies y credits en uno solo

## Analisis exploratorio de datos 
Leer el jupyter notebook 'EDA' para un mejor entendimiento
### Resumen Estadístico 
- El DataFrame tiene 45538 entradas con 19 columnas.
- Tipos de datos: 5 columnas float64, 2 columnas int64, y 12 columnas
- La columna tagline tiene una cantidad significativa de valores nulos (20,439 de 45,538).
- El presupuesto (budget) tiene un valor medio de aproximadamente $21,579,880 con un máximo de $380,000,000.
- La popularidad (popularity) tiene una media de 2.926 y un máximo de 547.49, mostrando una amplia dispersión.
- Los ingresos (revenue) muestran una gran variabilidad con una media de $111,986,000 y un máximo de $2,787,965,000.
- La duración (runtime) de las películas varía considerablemente, con un máximo de 1256 minutos (siendo este un valor atípico).
- La puntuación promedio (vote_average) tiene una media de 6.015 con un rango de 0.5 a 10
- El número de votos (vote_count) también muestra una amplia dispersión, con un máximo de 14,075.
### Análisis de Relaciones de datos numéricos 
- Existe una tendencia general de que un mayor presupuesto se asocia con mayores ingresos.
- Hay una gran cantidad de puntos con presupuestos e ingresos bajos, y pocos puntos con presupuestos e ingresos extremadamente altos. La dispersión sugiere que aunque un mayor presupuesto puede llevar a mayores ingresos, no siempre es así, y hay una considerable variabilidad.
- La mayoría de las películas tienen una popularidad baja (menos de 100) y una puntuación promedio entre 4 y 8.
- Algunas películas tienen una popularidad muy alta pero no necesariamente una puntuación promedio alta esto sugiere que puede deberse a que los usuarios en la mayoría de casos no votan a las películas por lo que la correlación entre la popularidad y el promedio de votación no parece ser fuerte.
- La mayoría de las películas tienen una diración de entre 90 y 200 minutos, siendo también las más populares. La dispersión sugiere que no hay una clara relación lineal entre la duración y la popularidad.
### Conclusiones 
- Los estudios de cine pueden considerar la asignación de presupuestos más altos a proyectos con potencial de alta recaudación, pero también deben ser conscientes de la alta variabilidad en los resultados financieros.
- Invertir en géneros populares como Drama, Comedia y Thriller puede ser una estrategia segura para maximizar el éxito comercial.  
- Las películas con duraciones estándar parecen ser más comunes y aceptadas; las duraciones extremas no necesariamente atraen más audiencia.
- Debido a la baja relación que existe entre las variables numéricas se verán descartadas para el entrenamiento del modelo.
## Funciones Requeridas 
Se crea las funciones:
- cantidad_filmaciones_mes, la cual te permite obetener el número de filmaciones estrenadas cierto mes.
- cantidad_filmaciones_dia, la cual te permite obtener el número de filmcaiones estrenadas en cierto día.
- score_titulo, la cual te permite obtener el título, el año de estreno y el score.
- votos_titulo, la cual te permite obtener el título, la cantidad de votos  y el valor promedio de las votaciones, debe existir al menos 2000 valoraciones para que se de un valor, caso contrario se devuelve none.
- get_actor, la cual te permite obtener la cantidad de películas en las que ha participado y el promedio de retorno.
- get_director, la cual te permite obtener el retorno generado por un director, además devuelve el nombre de cada película en la que ha trabajado, incluyendo fecha de lanzamiento retorno individual , costo y ganancia.
## Entrenamiento del Modelo para el sistema de recomendación de películas 
### Filtración de datos
- Para que las recomendaciones sean de las películas más relevantes posibles solo se tendrá en cuanta a aquellas que tienen más de 5 puntos en promedio de votos.
- Existen películas que no fueron hechas en inglés, las descartamos.
- Las características que se tendrán en cuenta son: Género, Descripción, Companías productoras, Actores y Directores.
### Entrenamiento y desarrollo de las funciones para el sistema
- Combinamos todas estas características en una sola columna.
- Utilizando el vectorizador TFIDF convertimos la nueva columna en un vector y las guardamos en TFIDF_matrix.
- Usando el modelo K-vecinos mediendo la similitud del coseno entrenamos el modelo.
- Con el modelo entrenado creamos una función que obtenga una lista de películas con mayor cercanía respecto a las características.
- Creamos otra función que llame a la anterior para dar el resultado.
















