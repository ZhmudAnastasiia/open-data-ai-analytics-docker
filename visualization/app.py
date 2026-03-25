import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")
PLOTS_DIR = "/app/plots"


def get_engine():
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url)


def clean_dataframe(df):
    df = df.copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    df = df.replace(r"^\s*$", np.nan, regex=True)

    df["dateAccepted"] = pd.to_datetime(df["dateAccepted"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["dateAccepted"])
    df["year"] = df["dateAccepted"].dt.year.astype("Int64")

    today = pd.Timestamp.today()
    df["age_years"] = ((today - df["dateAccepted"]).dt.days / 365).astype(float)

    return df


def save_top_sports(df):
    sport_counts = df["sportName"].value_counts()

    plt.figure(figsize=(12, 5))
    sport_counts.head(15).plot(kind="bar")
    plt.title("Top-15 sports by number of regulations")
    plt.xlabel("Sport")
    plt.ylabel("Number of documents")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/top_15_sports.png")
    plt.close()


def save_documents_by_year(df):
    year_counts = df["year"].value_counts().sort_index()

    plt.figure(figsize=(12, 5))
    plt.plot(year_counts.index.astype(int), year_counts.values, marker="o")
    plt.title("Number of approved documents by year")
    plt.xlabel("Year")
    plt.ylabel("Number of documents")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/documents_by_year.png")
    plt.close()


def save_status_distribution(df):
    status_counts = df["status"].value_counts()

    plt.figure(figsize=(8, 5))
    status_counts.plot(kind="bar")
    plt.title("Document status distribution")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/status_distribution.png")
    plt.close()


def save_age_distribution(df):
    plt.figure(figsize=(10, 5))
    plt.hist(df["age_years"].dropna(), bins=20)
    plt.title("Distribution of document age")
    plt.xlabel("Years since approval")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/document_age_distribution.png")
    plt.close()


def main():
    os.makedirs(PLOTS_DIR, exist_ok=True)

    engine = get_engine()
    raw_df = pd.read_sql_table(TABLE_NAME, engine)
    df = clean_dataframe(raw_df)

    save_top_sports(df)
    save_documents_by_year(df)
    save_status_distribution(df)
    save_age_distribution(df)

    print("Plots saved successfully.")


if __name__ == "__main__":
    main()