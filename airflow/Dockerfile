FROM apache/airflow:3.0.4

USER airflow

RUN pip install --no-cache-dir \
    dbt-snowflake==1.8.0 \
    faker==25.0.0 \
    pandas==2.2.2 \
    snowflake-connector-python==3.10.0