from sqlalchemy import create_engine
from dotenv import dotenv_values
import os
import pandas as pd

path = os.environ['AIRFLOW_HOME']

# Leo las credenciales
user_Credential_from_envfile = dotenv_values(f'{path}/dags/env/redshift_key.env')

host = 'data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com'
database='data-engineer-database'
user = user_Credential_from_envfile['user']
password = user_Credential_from_envfile['password']
port = 5439

# Conexión a la base de datos RS
engine_prompt = f'postgresql://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(engine_prompt)

# Leer los archivos CSV creados en las partes anteriores y cargarlos en Redshift
df_info =       pd.read_csv(f'{path}/dags/data/station_info_procesada.csv')
df_st =         pd.read_csv(f'{path}/dags/data/station_status_procesada.csv')
df_est_oos =    pd.read_csv(f'{path}/dags/data/station_availability.csv')
df_merge =      pd.read_csv(f'{path}/dags/data/station_free_bikes.csv')

# Insertar todo el contenido de los DataFrames en las tablas correspondientes en Redshift
table_name = 'stations_info'
df_info.to_sql(table_name, engine, index=False, if_exists='append')

table_name = 'stations_status'
df_st.to_sql(table_name, engine, index=False, if_exists='append')

table_name = 'stations_availability'
df_est_oos.to_sql(table_name, engine, index=False, if_exists='append')

table_name = 'stations_free_bikes'
df_merge.to_sql(table_name, engine, index=False, if_exists='append')

print("Todo subido a Redshift!! =)")