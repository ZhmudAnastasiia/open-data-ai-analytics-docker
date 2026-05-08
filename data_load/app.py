import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
CSV_FILE = os.getenv("CSV_FILE", "/app/data/dataset.csv")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")
DOWNLOAD_URL = os.getenv(
    "DOWNLOAD_URL",
    "https://data.gov.ua/dataset/sports-rules/resource/1208ea90-47e7-46a0-a5ad-b91c15bd3cd6/download/sports-rules.csv"
)


def get_engine():
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url)


def wait_for_db(max_retries=20, delay=3):
    engine = get_engine()
    for attempt in range(max_retries):
        try:
            with engine.connect():
                print("Database is ready.")
                return engine
        except Exception as e:
            print(f"Waiting for database... {attempt + 1}/{max_retries}. Error: {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to database.")


def ensure_csv_exists():
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

    if os.path.exists(CSV_FILE):
        print(f"CSV file already exists: {CSV_FILE}")
        return

    print("Local CSV not found. Downloading from source...")
    response = requests.get(DOWNLOAD_URL, timeout=60)
    response.raise_for_status()

    with open(CSV_FILE, "wb") as f:
        f.write(response.content)

    print(f"CSV downloaded successfully: {CSV_FILE}")


def load_dataset():
    print(f"Reading CSV file: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, sep=";", encoding="utf-8-sig", engine="python")

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    df = df.replace(r"^\s*$", pd.NA, regex=True)

    print(f"CSV loaded successfully. Rows: {len(df)}, Columns: {len(df.columns)}")
    print("Columns:", list(df.columns))
    return df


def main():
    ensure_csv_exists()
    df = load_dataset()
    engine = wait_for_db()

    print(f"Writing data to table '{TABLE_NAME}'...")
    df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)

    print("Data loaded into PostgreSQL not successfull.")


if __name__ == "__main__":
    main()