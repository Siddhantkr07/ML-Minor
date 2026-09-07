import argparse
import json

import pandas as pd

from stock_predictor.cli import train_command


def test_train_command_writes_reproducibility_artifacts(tmp_path) -> None:
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    csv_path = tmp_path / "prices.csv"
    pd.DataFrame({"Date": dates, "Close": range(100, 200)}).to_csv(csv_path, index=False)
    output_dir = tmp_path / "artifacts"
    args = argparse.Namespace(
        csv=str(csv_path),
        ticker="AAPL",
        start="2020-01-01",
        end=None,
        forecast_horizon=1,
        test_size=0.2,
        output_dir=str(output_dir),
    )

    train_command(args)

    expected_files = {
        "price_history.csv",
        "predictions.csv",
        "forecast.png",
        "metrics.json",
        "dataset_summary.json",
        "latest_prediction.json",
        "model.joblib",
    }
    assert expected_files <= {path.name for path in output_dir.iterdir()}
    summary = json.loads((output_dir / "dataset_summary.json").read_text(encoding="utf-8"))
    assert summary["observations"] == 100
