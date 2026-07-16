import os
import requests
import pandas as pd
from google.cloud import bigquery
from datetime import datetime

# --- Config ---
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
PROJECT_ID = "moviepipeline-de"      # <-- replace with your actual GCP project ID
DATASET_ID = "Raw"
TABLE_ID = "movies_raw"

def fetch_popular_movies(pages=5):
    """Pull popular movies from TMDB, a few pages worth."""
    all_movies = []
    for page in range(1, pages + 1):
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {"api_key": TMDB_API_KEY, "page": page}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        all_movies.extend(data["results"])
    return all_movies

def to_dataframe(movies):
    df = pd.DataFrame(movies)
    # keep it simple — just the fields we care about, plus a load timestamp
    keep_cols = [
        "id", "title", "release_date", "genre_ids",
        "vote_average", "vote_count", "popularity", "overview"
    ]
    df = df[keep_cols]
    df["loaded_at"] = datetime.utcnow().isoformat()
    return df

def load_to_bigquery(df, project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # overwrite each run for now
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # wait for it to finish
    print(f"Loaded {len(df)} rows into {table_ref}")

if __name__ == "__main__":
    movies = fetch_popular_movies(pages=5)
    df = to_dataframe(movies)
    load_to_bigquery(df, PROJECT_ID, DATASET_ID, TABLE_ID)
