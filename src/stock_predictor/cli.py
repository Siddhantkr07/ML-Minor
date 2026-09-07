"""Command-line entry point for the stock prediction experiment."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import joblib

# Training can run on servers and GitHub Actions where no desktop display exists.
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "stock_price_prediction_matplotlib")
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .data import download_history, load_csv
from .features import FeatureConfig, create_feature_frame, supervised_dataset
from .model import train_and_evaluate


def _write_plot(predictions, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(11, 5))
    axis.plot(predictions.index, predictions["actual_close"], label="Actual close", linewidth=2)
    axis.plot(predictions.index, predictions["ridge_prediction"], label="Ridge prediction", linewidth=1.8)
    axis.plot(predictions.index, predictions["naive_prediction"], label="Naive baseline", linestyle="--")
    axis.set_title("Chronological holdout predictions")
    axis.set_xlabel("Date")
    axis.set_ylabel("Price")
    axis.legend()
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def train_command(args: argparse.Namespace) -> None:
    prices = load_csv(args.csv) if args.csv else download_history(args.ticker, args.start, args.end)
    config = FeatureConfig(forecast_horizon=args.forecast_horizon)
    feature_frame = create_feature_frame(prices, config)
    features, target = supervised_dataset(feature_frame)
    result = train_and_evaluate(features, target, test_size=args.test_size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.predictions.to_csv(output_dir / "predictions.csv", index_label="Date")
    _write_plot(result.predictions, output_dir / "forecast.png")

    latest_features = feature_frame.drop(columns="target").iloc[[-1]]
    latest_prediction = float(result.model.predict(latest_features)[0])
    source = str(args.csv) if args.csv else args.ticker.upper()
    metadata = {
        "source": source,
        "forecast_horizon_trading_days": args.forecast_horizon,
        "feature_columns": list(features.columns),
        "train_rows": result.train_rows,
        "test_rows": result.test_rows,
        "metrics": result.metrics,
    }
    (output_dir / "metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (output_dir / "latest_prediction.json").write_text(
        json.dumps(
            {
                "prediction_date": str(latest_features.index[0].date()),
                "predicted_next_close": latest_prediction,
                "forecast_horizon_trading_days": args.forecast_horizon,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    joblib.dump(
        {"model": result.model, "feature_columns": list(features.columns), "config": config},
        output_dir / "model.joblib",
    )

    print(f"Saved experiment results to {output_dir.resolve()}")
    for name, metric in result.metrics.items():
        print(f"{name}: MAE={metric['mae']:.4f}, RMSE={metric['rmse']:.4f}, R2={metric['r2']:.4f}")
    print(f"Latest next-close estimate: {latest_prediction:.4f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a leakage-aware stock-price prediction experiment.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    train = subparsers.add_parser("train", help="Train and evaluate a chronological time-series model.")
    source = train.add_mutually_exclusive_group()
    source.add_argument("--ticker", default="AAPL", help="Yahoo Finance ticker symbol (default: AAPL).")
    source.add_argument("--csv", help="Local CSV containing Date and Close columns.")
    train.add_argument("--start", default="2020-01-01", help="Start date for Yahoo Finance data (YYYY-MM-DD).")
    train.add_argument("--end", help="Optional end date for Yahoo Finance data (YYYY-MM-DD).")
    train.add_argument("--forecast-horizon", type=int, default=1, help="Trading days ahead to predict.")
    train.add_argument("--test-size", type=float, default=0.2, help="Newest fraction reserved for testing.")
    train.add_argument("--output-dir", default="artifacts", help="Directory for generated results.")
    train.set_defaults(handler=train_command)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
