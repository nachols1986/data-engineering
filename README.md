## Descripción del trabajo

El proyecto se enfoca en la construcción de un robusto pipeline de ETL (Extract, Transform, Load) utilizando tecnologías modernas como Docker, Airflow, Python y una base de datos en Amazon Redshift. El objetivo principal es automatizar el flujo de datos desde la API Transporte del Gobierno de la Ciudad de Buenos Aires hasta una base de datos centralizada, permitiendo su posterior análisis y visualización.

El proceso comienza con la descarga de datos en tiempo real desde la API, la cual proporciona información detallada sobre el estado de las estaciones de las bicicletas públicas, así como datos generales sobre las mismas. Estos datos se adquieren periódicamente y se almacenan localmente para su posterior procesamiento.

Una vez obtenidos, los datos pasan por un proceso de transformación en Python, donde se aplican diferentes operaciones para limpiar, estructurar y enriquecer la información. Esto incluye la generación de métricas agregadas relevantes, como la disponibilidad de bicicletas en cada estación y la cantidad de estaciones fuera de servicio en un determinado período de tiempo.

Finalmente, los datos transformados se cargan en una base de datos en Amazon Redshift, que sirve como repositorio centralizado para almacenar grandes volúmenes de datos de forma escalable y eficiente. Esta base de datos permite realizar consultas analíticas complejas y generar visualizaciones que ayuden a comprender mejor el comportamiento del sistema de bicicletas públicas en la ciudad. 

Adicionalmente, se envía por email a los destinatarios que uno quisiera, un informe diario con el % de bicicletas fuera de servicio sobre el activo total. Se define un umbral máximo tolerable para dicho % y, en caso de superarlo, se envía un email de alerta.

Todo el proceso está orquestado mediante Airflow, una plataforma de flujo de trabajo y programación de tareas que facilita la automatización de los procesos ETL. Airflow permite definir, programar y monitorear fácilmente los diferentes pasos del pipeline, garantizando su ejecución de manera confiable y eficiente.

En resumen, este proyecto ofrece una solución completa para la extracción, transformación y carga de datos de la API de Transporte del Gobierno de la Ciudad de Buenos Aires en una base de datos en Amazon Redshift, utilizando tecnologías modernas y probadas en la industria para garantizar la eficacia y escalabilidad del pipeline de datos.

---
### Instructivo para ejecutar el proceso ETL en Airflow con Docker

#### Paso 1: Preparación de archivos

1. Descarga todos los archivos originales necesarios para el proceso ETL, incluyendo los scripts Python y los archivos `.env`.
2. Coloca los archivos descargados en una carpeta llamada `C:\ecobici` en tu sistema.

#### Paso 2: Organización de archivos

1. Copia el archivo Dockerfile, docker-compose.yaml y requirements.txt en la carpeta `C:\ecobici`.
2. Copia el archivo dag.py y la carpeta `src` (que contiene los scripts `.py` necesarios) en una subcarpeta llamada `dags` dentro de `C:\ecobici`.
3. También dentro de la carpeta `dags`, crea una subcarpeta llamada `env` y coloca dentro los archivos gcba_api_key.env y redshift_key.env.
4. La carpeta `data` crearla y dejarla vacía (ahí se irán guardando los .csv que luego se cargarán en Redshift)

La estructura que debería quedar es la siguiente:

```
/ ecobici
├── dags
│   ├── src
│   │   ├── conexion_api.py
│   │   ├── process_ecobici_data.py
│   │   ├── create_aggregated_tables.py
│   │   ├── send_mails.py
│   │   └── upload_to_redshift.py
│   ├── env
│   │   ├── gcba_api_key.env
│   │   ├── email_key.env
│   │   └── redshift_key.env
│   ├── params
│   │   ├── destinatarios.txt --> en este archivo, armar la lista de destinatarios para el informe diario y alertas
│   │   └── umbral.env --> aquí definir el valor (0-100) para el máximo % tolerable de bicicletas fuera de servicio
│   ├── data
│   └── dag.py
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
````

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

---
### Tablas de la Base de Datos

#### 1. `stations_info`

Esta tabla almacena información sobre las estaciones de bicicletas.

| station_id | name             | lat             | lon              | address                                          | capacity | last_refresh             |
|------------|------------------|-----------------|------------------|--------------------------------------------------|----------|--------------------------|
| 2          | 002 - Retiro I   | -34.59242413    | -58.37470989     | AV. Dr. José María Ramos Mejía 1300            | 40       | 2024-04-02 22:07:39.765015 |
| 3          | 003 - ADUANA     | -34.61220714255728 | -58.36912906378899 | Av. Paseo Colón 380                          | 28       | 2024-04-02 22:07:39.765015 |
| 4          | 004 - Plaza Roma | -34.6030082348981 | -58.36885646243477 | Av. Corrientes 100                           | 20       | 2024-04-02 22:07:39.765015 |

#### 2. `stations_status`

Esta tabla registra el estado de las estaciones de bicicletas.

| station_id | num_bikes_available | num_bikes_disabled | num_docks_available | num_docks_disabled | last_reported       | status      | last_refresh             |
|------------|---------------------|--------------------|---------------------|--------------------|---------------------|-------------|--------------------------|
| 2          | 4                   | 2                  | 34                  | 0                  | 2024-04-02 16:45:15 | IN_SERVICE  | 2024-04-02 19:47:09.568037 |
| 3          | 9                   | 1                  | 19                  | 0                  | 2024-04-02 16:45:32 | IN_SERVICE  | 2024-04-02 19:47:09.568037 |
| 4          | 5                   | 1                  | 14                  | 0                  | 2024-04-02 16:46:33 | IN_SERVICE  | 2024-04-02 19:47:09.568037 |

#### 3. `stations_availability`

Esta tabla muestra la disponibilidad de las estaciones.

| last_refresh            | end_of_life | in_service |
|-------------------------|-------------|------------|
| 2024-04-02 19:47:09.568037 | 15          | 352        |

#### 4. `stations_free_bikes`

Esta tabla indica la cantidad de bicicletas libres en las estaciones.

| last_refresh_x          | station_id | perc_libres |
|-------------------------|------------|-------------|
| 2024-04-02 19:47:09.568037 | 2          | 0.1         |
| 2024-04-02 19:47:09.568037 | 3          | 0.3214285714285714 |
| 2024-04-02 19:47:09.568037 | 4          | 0.25        |

