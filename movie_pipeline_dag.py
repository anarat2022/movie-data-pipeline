from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append("/usr/local/airflow/include")

default_args = {
    "owner": "anarat",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="movie_pipeline",
    default_args=default_args,
    description="Extract TMDB movies, load to BigQuery, transform with dbt",
    schedule="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["data-engineering", "bigquery", "dbt"],
) as dag:

    def run_extract_load():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/airflow/include/movie_pipeline/gcp_key.json"
        from extract_load import fetch_popular_movies, to_dataframe, load_to_bigquery
        movies = fetch_popular_movies(pages=5)
        df = to_dataframe(movies)
        load_to_bigquery(df, "moviepipeline-de", "Raw", "movies_raw")

    extract_and_load = PythonOperator(
        task_id="extract_and_load",
        python_callable=run_extract_load,
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "export GOOGLE_APPLICATION_CREDENTIALS=/usr/local/airflow/include/movie_pipeline/gcp_key.json && "
            "cd /usr/local/airflow/include/movie_pipeline && "
            "dbt build --profiles-dir ."
        ),
    )

    extract_and_load >> run_dbt
