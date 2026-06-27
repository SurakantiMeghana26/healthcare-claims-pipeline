"""
dbt Transformation DAG
======================
Automatically runs dbt transformations after data ingestion:
1. dbt deps (install dependencies)
2. dbt run (build all models)
3. dbt test (validate data quality)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


# ============================================================
# DEFAULT ARGUMENTS
# ============================================================
default_args = {
    'owner': 'meghana',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# ============================================================
# PATHS
# ============================================================
DBT_PROJECT_DIR = '/opt/airflow/dbt_project/healthcare_analytics'
DBT_PROFILES_DIR = '/opt/airflow/config'


# ============================================================
# PYTHON FUNCTIONS
# ============================================================

def start_transformation():
    """Log start of transformation."""
    print("=" * 60)
    print("dbt TRANSFORMATION PIPELINE STARTED")
    print(f"Started at: {datetime.now()}")
    print(f"Project: {DBT_PROJECT_DIR}")
    print(f"Profiles: {DBT_PROFILES_DIR}")
    print("=" * 60)


def report_success():
    """Log successful completion."""
    print("=" * 60)
    print("dbt TRANSFORMATION COMPLETED SUCCESSFULLY!")
    print(f"Finished at: {datetime.now()}")
    print("All 12 models built and tested!")
    print("=" * 60)


# ============================================================
# DEFINE THE DAG
# ============================================================
with DAG(
    dag_id='dbt_transformation',
    default_args=default_args,
    description='Run dbt transformations on healthcare data',
    schedule='@daily',
    catchup=False,
    tags=['healthcare', 'dbt', 'transformation', 'production'],
) as dag:
    
    # Task 1: Start
    task_start = PythonOperator(
        task_id='start_transformation',
        python_callable=start_transformation,
    )
    
    # Task 2: dbt debug (verify connection)
    task_dbt_debug = BashOperator(
        task_id='dbt_debug',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt debug --profiles-dir {DBT_PROFILES_DIR}',
    )
    
    # Task 3: dbt run (build all models)
    task_dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --profiles-dir {DBT_PROFILES_DIR}',
    )
    
    # Task 4: dbt test (validate data quality)
    task_dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --profiles-dir {DBT_PROFILES_DIR}',
    )
    
    # Task 5: Success notification
    task_success = PythonOperator(
        task_id='report_success',
        python_callable=report_success,
    )
    
    # ============================================================
    # SET TASK DEPENDENCIES
    # ============================================================
    task_start >> task_dbt_debug >> task_dbt_run >> task_dbt_test >> task_success