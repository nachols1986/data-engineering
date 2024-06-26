import os
import pandas as pd

path = os.environ['AIRFLOW_HOME']

# Cargar los datos previamente descargados
df_info = pd.read_csv(f'{path}/dags/data/station_info_procesada.csv')
df_st = pd.read_csv(f'{path}/dags/data/station_status_procesada.csv')

# Genero algunas tablas con métricas adicionales

# 1. Cantidad de estaciones fuera de servicio por fecha
df_est_oos = df_st.groupby(['last_refresh','status'])['station_id'].count()
df_est_oos = df_est_oos.unstack(fill_value=0)
df_est_oos.reset_index(inplace=True)

# Calcular el porcentaje de END_OF_LIFE sobre el total (EOL + IS)
df_est_oos['%_END_OF_LIFE'] = round((df_est_oos['END_OF_LIFE'] / (df_est_oos['END_OF_LIFE'] + df_est_oos['IN_SERVICE'])) * 100, 2)

# 2. Quiero para cada estación (guardando por fecha) su % de bicicletas disponibles
df_merge = pd.merge(df_st, df_info, how='left', on='station_id')
df_merge['perc_libres'] = df_merge['num_bikes_available'] / df_merge['capacity']
df_merge = df_merge[['last_refresh_x', 'station_id', 'perc_libres']]

# Guardar los DataFrames en archivos CSV o en una base de datos temporal
df_est_oos.to_csv(f'{path}/dags/data/station_availability.csv', index=False)
df_merge.to_csv(f'{path}/dags/data/station_free_bikes.csv', index=False)

print("Se guardaron los datos de métricas de estaciones fuera de servicio y porcentaje de disponibilidad")
#print(df_merge.head(3))