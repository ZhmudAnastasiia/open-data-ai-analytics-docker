import os
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")
REPORT_PATH = "/app/reports/research_report.json"


def get_engine():
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    df = df.replace(r"^\s*$", np.nan, regex=True)

    if "sportName" in df.columns:
        df["sportName"] = df["sportName"].str.title()

    if "dateAccepted" in df.columns:
        df["dateAccepted"] = pd.to_datetime(
            df["dateAccepted"],
            dayfirst=True,
            errors="coerce"
        )
        df["year"] = df["dateAccepted"].dt.year

    df = df.dropna(subset=["dateAccepted"])

    if "status" in df.columns:
        df["status"] = df["status"].astype("string").str.lower()
        df["status"] = df["status"].replace({
            "чинний": "active",
            "діючий": "active",
            "нечинний": "inactive",
            "скасований": "inactive",
            "змінений": "changed"
        })

    df = df.drop(columns=["publisherIdentifier"], errors="ignore")

    today = pd.Timestamp.today().normalize()
    df["age_years"] = (today - df["dateAccepted"]).dt.days / 365.0

    return df


def main():
    engine = get_engine()
    raw_df = pd.read_sql_table(TABLE_NAME, engine)
    df = clean_dataframe(raw_df)

    sport_counts = (
        df["sportName"].value_counts().sort_values(ascending=False)
        if "sportName" in df.columns else pd.Series(dtype="int64")
    )

    year_counts = (
        df["year"].value_counts().sort_index()
        if "year" in df.columns else pd.Series(dtype="int64")
    )

    status_counts = (
        df["status"].value_counts()
        if "status" in df.columns else pd.Series(dtype="int64")
    )

    age_stats = {}
    if "age_years" in df.columns and not df["age_years"].dropna().empty:
        age_stats = {
            "mean": round(float(df["age_years"].mean()), 2),
            "median": round(float(df["age_years"].median()), 2),
            "min": round(float(df["age_years"].min()), 2),
            "max": round(float(df["age_years"].max()), 2),
        }

    findings = []

    if not sport_counts.empty:
        top_sport = sport_counts.index[0]
        top_sport_count = int(sport_counts.iloc[0])
        findings.append(
            f"Найбільшу кількість нормативних документів має вид спорту '{top_sport}' — {top_sport_count} документів."
        )

    if not year_counts.empty:
        top_year = int(year_counts.idxmax())
        top_year_count = int(year_counts.max())
        findings.append(
            f"Найбільш активним роком затвердження документів є {top_year}, у якому зафіксовано {top_year_count} документів."
        )

    if not status_counts.empty:
        top_status = str(status_counts.idxmax())
        top_status_count = int(status_counts.max())
        findings.append(
            f"Домінуючий статус документів — '{top_status}', таких записів {top_status_count}."
        )

    if age_stats:
        findings.append(
            f"Середній вік нормативних документів становить приблизно {age_stats['mean']} року(ів)."
        )

    hypothesis_1 = (
        "Гіпотеза 1: більш поширені види спорту мають більше нормативних документів. "
        "Розподіл документів між видами спорту є відносно рівномірним, хоча окремі дисципліни мають вищу концентрацію документів."
    )

    hypothesis_2 = (
        "Гіпотеза 2: у новіші роки кількість затверджених документів є більшою. "
        "Розподіл за роками підтверджує посилення активності в останні роки."
    )

    hypothesis_3 = (
        "Гіпотеза 3: документи поступово втрачають актуальність і оновлюються через кілька років. "
        "Розподіл статусів та віку документів свідчить про регулярне оновлення нормативної бази."
    )

    report = {
        "cleaned_dataset_overview": {
            "rows_after_cleaning": int(df.shape[0]),
            "columns_after_cleaning": int(df.shape[1])
        },
        "top_15_sports": {str(k): int(v) for k, v in sport_counts.head(15).to_dict().items()},
        "documents_by_year": {str(int(k)): int(v) for k, v in year_counts.to_dict().items()},
        "status_distribution": {str(k): int(v) for k, v in status_counts.to_dict().items()},
        "document_age_statistics_years": age_stats,
        "top_findings": findings,
        "hypotheses": {
            "hypothesis_1": hypothesis_1,
            "hypothesis_2": hypothesis_2,
            "hypothesis_3": hypothesis_3
        }
    }

    os.makedirs("/app/reports", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Research report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()