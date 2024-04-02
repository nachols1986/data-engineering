# dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
import os

path = os.environ['AIRFLOW_HOME']

from datetime import timedelta, datetime

default_args = {
                'owner': 'airflow',
                'email': ['ji.lopez.saez@email.com'],
                'depends_on_past': False,
                'email_on_failure': False,
                'email_on_retry': False,
                'retries': 1,
                'retry_delay': timedelta(minutes=5),
                'start_date': datetime(2024, 4, 1),    # Fecha de inicio del DAG
                'schedule_interval': '0 */6 * * *',    # Ejecutar cada 6 horas
                }

# Define the DAG, its ID and when should it run.
dag = DAG(
            dag_id='ecobici_dag',
            description='ETL para procesar datas de Ecobici Bs As',
            default_args=default_args,
            catchup=True
            )

# Conexión a la API del GCBA
task1 = BashOperator(
                    task_id='conexion_api',
                    bash_command=f'python {path}/dags/src/conexion_api.py',
                    dag=dag
                    )

# Preprocesamiento de los datos
task2 = BashOperator(
                    task_id='process_ecobici_data',
                    bash_command=f'python {path}/dags/src/process_ecobici_data.py',
                    dag=dag
                    )

# Crea tablas agregadas con kpis
task3 = BashOperator(
                    task_id='create_aggregated_tables',
                    bash_command=f'python {path}/dags/src/create_aggregated_tables.py',
                    dag=dag
                    )

# Carga los datos en amz redshift
task4 = BashOperator(
                    task_id='upload_to_redshift',
                    bash_command=f'python {path}/dags/src/upload_to_redshift.py',
                    dag=dag
                    )

task1 >> task2 >> task3 >> task4