import os
import json
import pandas as pd
from flask import Flask, render_template, send_from_directory


app = Flask(__name__)

DATA_FILE = "/app/data/dataset.csv"
QUALITY_REPORT = "/app/reports/quality_report.json"
RESEARCH_REPORT = "/app/reports/research_report.json"
PLOTS_DIR = "/app/plots"


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_dataset_preview():
    if not os.path.exists(DATA_FILE):
        return [], []

    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8-sig", engine="python")
    columns = list(df.columns)
    preview = df.head(10).fillna("").to_dict(orient="records")
    return columns, preview


@app.route("/")
def index():
    columns, df_preview = load_dataset_preview()
    quality_report = load_json(QUALITY_REPORT)
    research_report = load_json(RESEARCH_REPORT)

    quality_report_str = json.dumps(quality_report, indent=2, ensure_ascii=False)
    research_report_str = json.dumps(research_report, indent=2, ensure_ascii=False)

    plots = []
    if os.path.exists(PLOTS_DIR):
        plots = sorted([f for f in os.listdir(PLOTS_DIR) if f.endswith(".png")])

    return render_template(
        "index.html",
        columns=columns,
        df_preview=df_preview,
        quality_report=quality_report_str,
        research_report=research_report_str,
        plots=plots
    )


@app.route("/static_plot/<path:filename>")
def static_plot(filename):
    return send_from_directory(PLOTS_DIR, filename)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)