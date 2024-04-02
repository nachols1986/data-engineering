### Instructivo para ejecutar el proceso ETL en Airflow con Docker

#### Paso 1: Preparación de archivos

1. Descarga todos los archivos originales necesarios para el proceso ETL, incluyendo los scripts Python y los archivos `.env`.
2. Coloca los archivos descargados en una carpeta llamada `C:\ecobici` en tu sistema.

#### Paso 2: Organización de archivos

1. Copia el archivo Dockerfile, docker-compose.yaml y requirements.txt en la carpeta `C:\ecobici`.
2. Copia el archivo dag.py y la carpeta `src` (que contiene los scripts `.py` necesarios) en una subcarpeta llamada `dags` dentro de `C:\ecobici`.
3. También dentro de la carpeta `dags`, crea una subcarpeta llamada `env` y coloca dentro los archivos gcba_api_key.env y redshift_key.env.

La estructura que debería quedar es la siguiente:

/
├── ecobici
├── dags
│   ├── src
│   │   ├── conexion_api.py
│   │   ├── process_ecobici_data.py
│   │   ├── create_aggregated_tables.py
│   │   └── upload_to_redshift.py
│   ├── env
│   │   ├── gcba_api_key.env
│   │   └── redshift_key.env
│   └── dag.py
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt

#### Paso 3: Construcción de la imagen Docker

1. Abre PowerShell en tu sistema.
2. Navega hasta la carpeta `C:\ecobici` usando el comando `cd C:\ecobici`.
3. Ejecuta el siguiente comando para construir la imagen Docker: `docker build -t ecobici_elt .`.

#### Paso 4: Ejecución del contenedor Docker

1. Una vez que la imagen Docker se haya construido correctamente, ejecuta el siguiente comando para iniciar el contenedor: `docker-compose up`.
2. Esto iniciará Airflow y lo hará accesible a través del navegador web en `http://localhost:8080`.

#### Paso 5: Acceso a Airflow

1. Abre un navegador web y navega a `http://localhost:8080`.
2. Inicia sesión en Airflow con las siguientes credenciales:
   - **Usuario**: ecobici
   - **Contraseña**: ecobici

#### Paso 6: Verificación del proceso ETL

1. Una vez iniciada la sesión en Airflow, verás el DAG `ecobici_dag` en la lista de DAG disponibles.
2. Activa el DAG haciendo clic en el botón de encendido.
3. Airflow comenzará automáticamente a ejecutar el DAG según la programación definida en el mismo.
