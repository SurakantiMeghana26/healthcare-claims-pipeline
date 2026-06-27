"""
Hello Healthcare DAG - My First Airflow DAG!
=============================================
This is a simple DAG that demonstrates basic Airflow concepts.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


# ============================================================
# DEFAULT ARGUMENTS for all tasks in this DAG
# ============================================================
default_args = {
    'owner': 'meghana',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


# ============================================================
# PYTHON FUNCTIONS for tasks
# ============================================================

def say_hello():
    """First task: Say hello!"""
    print("=" * 50)
    print("Hello from Airflow!")
    print("This is my first DAG!")
    print("=" * 50)


def fetch_healthcare_data():
    """Second task: Simulate fetching data."""
    print("Fetching healthcare claims data...")
    print("Records fetched: 1000 claims")
    print("Records fetched: 50 providers")
    print("Records fetched: 500 members")


def process_data():
    """Third task: Simulate processing."""
    print("Processing healthcare data...")
    print("Cleaning data...")
    print("Validating records...")
    print("Done!")


def send_notification():
    """Fourth task: Send completion notification."""
    print("Sending notification...")
    print("Pipeline completed successfully!")
    print("Time: " + str(datetime.now()))


# ============================================================
# DEFINE THE DAG
# ============================================================
with DAG(
    dag_id='hello_healthcare',
    default_args=default_args,
    description='My first Airflow DAG for healthcare project',
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=['healthcare', 'tutorial', 'first-dag'],
) as dag:
    
    # Task 1: Say hello
    task_hello = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello,
    )
    
    # Task 2: Fetch data (simulated)
    task_fetch = PythonOperator(
        task_id='fetch_healthcare_data',
        python_callable=fetch_healthcare_data,
    )
    
    # Task 3: Process data (simulated)
    task_process = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    # Task 4: Send notification
    task_notify = PythonOperator(
        task_id='send_notification',
        python_callable=send_notification,
    )
    
    # ============================================================
    # SET TASK ORDER (dependencies)
    # Tasks will run in this order!
    # ============================================================
    task_hello >> task_fetch >> task_process >> task_notify