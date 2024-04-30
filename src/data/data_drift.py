import os

import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

if __name__ == "__main__":
    report = Report(metrics=[DataDriftPreset()])

    current = pd.read_csv("data/current_data.csv")
    reference = pd.read_csv("data/reference_data.csv")

    report.run(reference_data=reference, current_data=current)

    # if directory doesn't exist create one
    if not os.path.exists("reports/sites"):
        os.makedirs("reports/sites")

    report.save_html("reports/sites/data_drift.html")