from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os


# Define la configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 3, 28),  # Fecha de inicio del DAG
    'schedule_interval': '0 */6 * * *',  # Ejecutar cada 6 horas
}

# Define el DAG
dag = DAG(
    'ecobici_etl',
    default_args=default_args,
    description='ETL para procesar datas de Ecobici Bs As',
    catchup=True
)

def run_etl():
    os.system("python /airflow/dags/script_ecobici.py")

run_etl_task = PythonOperator(
    task_id='run_etl_task',
    python_callable=run_etl,
    dag=dag,
)

run_etl_task
