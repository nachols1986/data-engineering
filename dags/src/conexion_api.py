import os
import requests
import pandas as pd
from dotenv import dotenv_values

path = os.environ['AIRFLOW_HOME']

try:
    # Leer las credenciales desde el archivo .env
    credentials = dotenv_values(f'{path}/dags/env/gcba_api_key.env')
    vclient_id = credentials.get('vclient_id')
    vclient_secret = credentials.get('vclient_secret')
    if not vclient_id or not vclient_secret:
        raise ValueError("Error: No se encontraron vclient_id o vclient_secret en el archivo .env.")
except FileNotFoundError:
    print("Error: No se encontró el archivo .env en la ruta especificada.")
    exit(1)
except ValueError as e:
    print(e)
    exit(1)

# Parámetros para las solicitudes HTTP
params = {'client_id': vclient_id, 'client_secret': vclient_secret}

def make_request(url):
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanzar una excepción si la solicitud no fue exitosa (código distinto de 200)
        return response.json()['data']['stations']  # Devolver los datos de las estaciones
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud HTTP: {e}")
        return None

# URL para la información de las estaciones
url_info = 'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/stationInformation'
data_info = make_request(url_info)
if data_info:
    df_info = pd.json_normalize(data_info)
    df_info.to_csv(f'{path}/dags/data/station_info.csv', index=False)
    print(f"Se ha guardado la información de las estaciones en station_info.csv")
else:
    print("No se pudieron obtener los datos de información de las estaciones.")

# URL para el estado de las estaciones
url_status = 'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/stationStatus'
data_status = make_request(url_status)
if data_status:
    df_status = pd.json_normalize(data_status)
    df_status.to_csv(f'{path}/dags/data/station_status.csv', index=False)
    print(f"Se ha guardado el estado de las estaciones en station_status.csv")
else:
    print("No se pudieron obtener los datos de estado de las estaciones.")

largo = len(df_info)
print(f'Descargada información de {largo} estaciones')