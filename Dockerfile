# Utiliza una imagen de Python como base
FROM python:3.9-slim

# Establece variables de entorno para Airflow y configuración de autenticación
ENV AIRFLOW_HOME=/airflow
ENV PYTHONPATH=/airflow
ENV AIRFLOW__WEBSERVER__AUTHENTICATE=True
ENV AIRFLOW__WEBSERVER__AUTH_BACKEND=airflow.contrib.auth.backends.password_auth
ENV AIRFLOW__WEBSERVER__USERNAME=airflow
ENV AIRFLOW__WEBSERVER__PASSWORD=airflow

# Instala Airflow con pip
RUN pip install apache-airflow

# Copia los archivos .env al contenedor
COPY gcba_api_key.env /airflow/gcba_api_key.env
COPY redshift_key.env /airflow/redshift_key.env

# Copia el script y el archivo DAG a la carpeta de Airflow
COPY script_ecobici.py /airflow/dags/script_ecobici.py
COPY dag_etl_ecobici.py /airflow/dags/dag_etl_ecobici.py

# Configura Airflow para que use SQLite como backend de la base de datos
RUN airflow db init

# Inicia Airflow
CMD ["airflow", "webserver", "--port", "8080"]
