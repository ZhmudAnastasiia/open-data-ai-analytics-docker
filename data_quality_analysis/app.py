import os
import json
import pandas as pd
from sqlalchemy import create_engine


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")
REPORT_PATH = "/app/reports/quality_report.json"


def get_engine():
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url)


def main():
    engine = get_engine()
    df = pd.read_sql_table(TABLE_NAME, engine)

    required_cols = [
        "identifier", "sportName", "type", "publisherName",
        "title", "dateAccepted", "number", "status", "url"
    ]

    missing_count = df.isna().sum().sort_values(ascending=False)
    missing_pct = (df.isna().mean() * 100).sort_values(ascending=False)

    quality_missing = []
    for col in missing_count.index:
        quality_missing.append({
            "column": col,
            "missing_count": int(missing_count[col]),
            "missing_pct": round(float(missing_pct[col]), 2)
        })

    duplicate_rows = int(df.duplicated().sum())
    identifier_duplicates = None
    identifier_missing = None

    if "identifier" in df.columns:
        identifier_duplicates = int(df["identifier"].duplicated().sum())
        identifier_missing = int(df["identifier"].isna().sum())

    invalid_dates = None
    min_date = None
    max_date = None

    if "dateAccepted" in df.columns:
        dates = pd.to_datetime(df["dateAccepted"], dayfirst=True, errors="coerce")
        invalid_dates = int(dates.isna().sum())
        valid_dates = dates.dropna()
        if not valid_dates.empty:
            min_date = str(valid_dates.min().date())
            max_date = str(valid_dates.max().date())

    status_distribution = {}
    if "status" in df.columns:
        status_distribution = {
            str(k): int(v) for k, v in df["status"].fillna("NULL").value_counts(dropna=False).to_dict().items()
        }

    top_sports = {}
    if "sportName" in df.columns:
        top_sports = {
            str(k): int(v) for k, v in df["sportName"].fillna("NULL").value_counts().head(20).to_dict().items()
        }

    present_required = [c for c in required_cols if c in df.columns]
    missing_required = [c for c in required_cols if c not in df.columns]

    column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

    if duplicate_rows == 0 and (identifier_duplicates in [0, None]) and not missing_required:
        overall_conclusion = (
            "Структура даних загалом коректна: усі обов’язкові поля присутні, "
            "повних дублікатів записів не виявлено, ідентифікатори переважно унікальні. "
            "Основні проблеми пов’язані з пропусками в окремих полях і некоректним розпізнаванням частини дат."
        )
    else:
        overall_conclusion = (
            "У наборі даних виявлено структурні або якісні проблеми, які потребують очищення "
            "перед подальшим аналізом."
        )

    report = {
        "dataset_overview": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1])
        },
        "required_columns": {
            "present": present_required,
            "missing": missing_required
        },
        "missing_values": quality_missing,
        "duplicates": {
            "full_duplicate_rows": duplicate_rows,
            "identifier_duplicates": identifier_duplicates,
            "identifier_missing": identifier_missing
        },
        "date_quality": {
            "invalid_or_missing_dateAccepted": invalid_dates,
            "min_dateAccepted": min_date,
            "max_dateAccepted": max_date
        },
        "column_types": column_types,
        "status_distribution": status_distribution,
        "top_sports_by_frequency": top_sports,
        "summary_text": overall_conclusion
    }

    os.makedirs("/app/reports", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Quality report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()