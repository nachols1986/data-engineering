# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 14:19:10 2024

@author: nacho

Data Engineering
Consigna de Primer Pre entregable

Ref: https://docs.google.com/presentation/d/1aMYWVltJAc8s2mnDt3LnB8lxYhdv4ts3jvawxxX8LlI/edit#slide=id.g1522af722c0_0_81

Generar un script (formato .py o .ipynb) que funcione como prototipo (MVP) de un ETL para el proyecto final
El script debería extraer datos desde una API en formato JSON para ser manipulado como diccionario utilizando el lenguaje Python
Generar una tabla para ser almacenada en una base de datos a partir de información una API.

El objetivo es tener un código inicial que será usado en el proyecto final como un MVP de ETL . El script debería extraer datos en JSON desde una API pública o gratuita para luego convertir estos datos en diccionario Python y posterior manipulación. Considera los siguientes puntos:

    1. La API seleccionada debería contener datos  en cambio constante: Es decir, elegir datos que estén cambiando día con día, como pueden ser reportes de clima, datos de finanzas, casos de criminalidad, etc.
    2. Revisa que la información de la API seleccionada pueda ser consultada por lo menos una vez al día: Es importante que tengas la capacidad de actualizar los datos constantemente y con un un rate de por lo menos una vez al día, sin que se limite su acceso.
    3. El Código o script debería extraer varios datos de diferentes categorías/variables: Por ejemplo, si se eligen acciones de bolsa, se pueden elegir diferentes acciones, o subdividir por ETFs, en caso de elegir, el clima, dividir por regiones, etc.
    4. Respecto a la estructura del script/código:
        Revisa que no tenga bugs
        Revisa que el código no sea redundante
        Cerciorate de que no haya datos sensibles que se muestren en el mismo, como pueden ser credenciales.
        Revisa que tu código sea eficiente, es decir, que ejecute lo que se propone de la forma más sencilla, clara y rápida posible.

A su vez, la entrega involucra la creación de una versión inicial de la tabla donde los datos serán cargados posteriormente. Considera los siguientes puntos para su elaboración:
    1. La tabla debería contener información corespondiente a la que se extrae de la API.
    2. Incluir una columna temporal para el control de ingesta de datos


ref: https://api-transporte.buenosaires.gob.ar/
API Transporte GCBA

"""
import requests
import pandas as pd
#import json
#import os
#import redshift_connector
from dotenv import dotenv_values
from sqlalchemy import create_engine


# Leo las credenciales guardadas localmente
user_Credential_from_envfile = dotenv_values('C:/Users/nacho/OneDrive - ITBA/Coder House/Data Engineering/gcba_api_key.env')
vclient_id = user_Credential_from_envfile['vclient_id']
vclient_secret = user_Credential_from_envfile['vclient_secret']

params = {'client_id': vclient_id, 'client_secret': vclient_secret}

# Info Estaciones
url = 'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/stationInformation'
response = requests.get(url, params=params)
data = response.json()
df_info = pd.json_normalize(data['data']['stations'])

# Status Estaciones
url = 'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/stationStatus'
response = requests.get(url, params=params)
data = response.json()
df_st = pd.json_normalize(data['data']['stations'])

# Limpiamos columnas que no interesan
df_info = df_info.iloc[:, 0:9]

df_info.drop(['physical_configuration',
              'altitude',
              'post_code'], 
           axis=1,
           inplace = True)

df_st.drop(['is_charging_station',
            'is_installed',
            'is_renting',
            'is_returning',
            'traffic',
            'num_bikes_available_types.mechanical',
            'num_bikes_available_types.ebike'], 
           axis=1,
           inplace = True)


# Limpiamos la info
# 1. Eliminamos duplicados
df_info.drop_duplicates(inplace = True)
df_st.drop_duplicates(inplace = True)

# 2. Chequeamos outliers (usando criterio boxplot)
def number_of_outliers(df):
    
    df = df.select_dtypes(exclude = 'object')
    
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    
    return ((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).sum()

number_of_outliers(df_info)
"""
Se ven outliers en lat (2) y en capacity. No parece ser nada grave... así que no los corrijo
"""

number_of_outliers(df_st)
"""
Se ven outliers en num_bikes_available y num_bikes_disabled como variables que más me interesan.
Sin embargo, entiendo que en un universo de muy pocas bicicletas disponibles, si una estación de pronto tiene 15 avaiable, esté será "outlier" pero no es erróneo.

stats = df_st.describe()
Por ejemplo el percentil 75% de num_bikes_available es 5

... Así que los dejo así
"""

# Convierto unix timestamp a datetime
df_st['last_reported'] = pd.to_datetime(df_st['last_reported'],
                                        origin = 'unix',
                                        unit = 's')

df_st['last_reported'] = df_st['last_reported'] + pd.Timedelta(hours = -3)

# Agrego fecha de reporte de la info --> para el df_info siempre se va a sobreescribir la tabla || para df_st se irá acumulando el status
df_info['last_refresh'] = pd.Timestamp.now()
df_st['last_refresh'] = pd.Timestamp.now()

# Genero algunas tablas con métricas adicionales
# 1. Cantidad de estaciones fuera de servicio por fecha
df_est_oos = df_st.groupby(['last_refresh','status'])['station_id'].count()
df_est_oos = df_est_oos.unstack(fill_value=0)

# 2. Quiero para cada estación (guardando por fecha) su % de bicicletas disponibles
df_merge = pd.merge(df_st, df_info, how = 'left', on = 'station_id')
df_merge['perc_libres'] = df_merge['num_bikes_available'] / df_merge['capacity']
df_merge= df_merge[['last_refresh_x', 'station_id', 'perc_libres']]


# Conexión a la base de datos RS
host = 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com'
database='data-engineer-database'
user = 'nacho_ls_coderhouse'
password = 'w7IkMu0Tb8'
port = 5439

# 3. Insertar todo el contenido del DataFrame df_info en la tabla stations_info
engine_prompt = f'postgresql://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(engine_prompt)

table_name = 'stations_info'
df_info.to_sql(table_name, 
               engine, 
               index=False, 
               if_exists = 'replace'
               #if_exists='append'
               )

table_name = 'stations_status'
df_st.to_sql(table_name, 
               engine, 
               index=False, 
               #if_exists = 'replace'
               if_exists='append'
               )

table_name = 'stations_availability'
df_est_oos.to_sql(table_name, 
               engine, 
               index=False, 
               #if_exists = 'replace'
               if_exists='append'
               )

table_name = 'stations_free_bikes'
df_merge.to_sql(table_name, 
               engine, 
               index=False, 
               #if_exists = 'replace'
               if_exists='append'
               )


"""
TODO ESTO NO FUNCIONÓ
conn = redshift_connector.connect(
    host = host,
    database = database,
    user = user,
    password = password
    #user=os.environ['redshift_user'],
    #password=os.environ['redshift_password']
 )
cursor = conn.cursor()

from sqlalchemy import create_engine

# Cargo data de df_info
table_name = 'stations_info'
cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')")
table_exists = cursor.fetchone()[0]

query_create = \"""
CREATE TABLE stations_info (
    station_id  INT,
    name        VARCHAR(200),
    lat         DECIMAL(10,2),
    lon         DECIMAL (10,2),
    address     VARCHAR(300),
    capacity    INT
    )
\"""

print(query_create)

if not table_exists:
    cursor.execute(query_create)
    print("Tabla creada")
else:
    cursor.execute(f"DELETE FROM {table_name}")
    print("Contenido de la tabla borrado")

conn.commit()
cursor.close()
conn.close()
"""