import os
import requests
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine

# Leo las credenciales
user_Credential_from_envfile = dotenv_values('gcba_api_key.env')
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

# 1. Eliminamos duplicados
df_info.drop_duplicates(inplace = True)
df_st.drop_duplicates(inplace = True)

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
df_est_oos.reset_index()

# 2. Quiero para cada estación (guardando por fecha) su % de bicicletas disponibles
df_merge = pd.merge(df_st, df_info, how = 'left', on = 'station_id')
df_merge['perc_libres'] = df_merge['num_bikes_available'] / df_merge['capacity']
df_merge= df_merge[['last_refresh_x', 'station_id', 'perc_libres']]


# Conexión a la base de datos RS

# Leo las credenciales
user_Credential_from_envfile = dotenv_values('redshift_key.env')

host = 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com'
database='data-engineer-database'
user = user_Credential_from_envfile['user']
password = user_Credential_from_envfile['password']
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