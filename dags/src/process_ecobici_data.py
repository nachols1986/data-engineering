import pandas as pd
import os

path = os.environ['AIRFLOW_HOME']

# Cargar los datos previamente descargados
df_info = pd.read_csv(f'{path}/dags/data/station_info.csv')
df_st = pd.read_csv(f'{path}/dags/data/station_status.csv')

# Limpiamos columnas que no interesan
df_info = df_info.iloc[:, 0:9]
df_info.drop(['physical_configuration', 'altitude', 'post_code'], axis=1, inplace=True)

df_st.drop(['is_charging_station', 'is_installed', 'is_renting', 'is_returning', 'traffic',
            'num_bikes_available_types.mechanical', 'num_bikes_available_types.ebike'], axis=1, inplace=True)

# 1. Eliminamos duplicados
df_info.drop_duplicates(inplace=True)
df_st.drop_duplicates(inplace=True)

# Convierto unix timestamp a datetime
df_st['last_reported'] = pd.to_datetime(df_st['last_reported'], origin='unix', unit='s')
df_st['last_reported'] = df_st['last_reported'] + pd.Timedelta(hours=-3)

# Agrego fecha de reporte de la info --> para el df_info siempre se va a sobreescribir la tabla || para df_st se irá acumulando el status
df_info['last_refresh'] = pd.Timestamp.now()
df_st['last_refresh'] = pd.Timestamp.now()

# Guardar los DataFrames en archivos CSV o en una base de datos temporal
df_info.to_csv(f'{path}/dags/data/station_info_procesada.csv', index=False)
df_st.to_csv(f'{path}/dags/data/station_status_procesada.csv', index=False)

print("Se preprocesaron los datos de los archivos station_info.csv y station_status.csv")
#print(df_info.head(3))
#print(df_st.head(3))