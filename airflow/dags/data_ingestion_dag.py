"""
Healthcare Data Ingestion DAG
==============================
Automates the daily data pipeline:
1. Generate synthetic healthcare data
2. Load to Snowflake RAW_DATA schema
3. Verify the load
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


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
# TASK FUNCTIONS
# ============================================================

def start_pipeline():
    """Log pipeline start."""
    print("=" * 60)
    print("HEALTHCARE DATA INGESTION PIPELINE STARTED")
    print(f"Started at: {datetime.now()}")
    print("=" * 60)


def check_data_files():
    """Verify all CSV files exist."""
    import os
    
    data_dir = '/opt/airflow/data'
    required_files = [
        'providers.csv',
        'members.csv',
        'procedures.csv',
        'diagnoses.csv',
        'claims.csv'
    ]
    
    print(f"Checking data directory: {data_dir}")
    
    missing_files = []
    for file in required_files:
        file_path = f'{data_dir}/{file}'
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"  Found: {file} ({size:.2f} KB)")
        else:
            print(f"  MISSING: {file}")
            missing_files.append(file)
    
    if missing_files:
        raise FileNotFoundError(f"Missing files: {missing_files}")
    
    print("All files verified!")


def report_metrics():
    """Report pipeline metrics."""
    print("=" * 60)
    print("PIPELINE METRICS")
    print("=" * 60)
    print(f"Completed at: {datetime.now()}")
    print("Data successfully ingested!")
    print("=" * 60)


def end_pipeline():
    """Log pipeline completion."""
    print("=" * 60)
    print("HEALTHCARE DATA INGESTION COMPLETED!")
    print(f"Finished at: {datetime.now()}")
    print("=" * 60)


# ============================================================
# DEFINE THE DAG
# ============================================================
with DAG(
    dag_id='healthcare_data_ingestion',
    default_args=default_args,
    description='Daily ingestion of healthcare claims data',
    schedule='@daily',  # Runs once per day
    catchup=False,
    tags=['healthcare', 'ingestion', 'production'],
) as dag:
    
    # Task 1: Start pipeline
    task_start = PythonOperator(
        task_id='start_pipeline',
        python_callable=start_pipeline,
    )
    
    # Task 2: Generate healthcare data
    task_generate_data = BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow/src && python generate_healthcare_data.py',
    )
    
    # Task 3: Verify data files
    task_verify_files = PythonOperator(
        task_id='verify_data_files',
        python_callable=check_data_files,
    )
    
    # Task 4: Load to Snowflake
    task_load_snowflake = BashOperator(
        task_id='load_to_snowflake',
        bash_command='cd /opt/airflow/src && python load_to_snowflake.py',
    )
    
    # Task 5: Report metrics
    task_metrics = PythonOperator(
        task_id='report_metrics',
        python_callable=report_metrics,
    )
    
    # Task 6: End pipeline
    task_end = PythonOperator(
        task_id='end_pipeline',
        python_callable=end_pipeline,
    )
    
    # ============================================================
    # SET TASK DEPENDENCIES
    # ============================================================
    task_start >> task_generate_data >> task_verify_files >> task_load_snowflake >> task_metrics >> task_end