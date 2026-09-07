# Stock Price Prediction

A reproducible machine-learning project that predicts the next trading day's closing price from recent price history. It was built for the Minor Project brief and supports either Yahoo Finance data or a CSV exported from Kaggle or another source.

> **Important:** This project is for educational use. Stock forecasts are uncertain and must not be treated as investment advice.

## What this project does

- Downloads historical data for any stock ticker through Yahoo Finance, or reads a local CSV.
- Builds lag, return, and rolling-window features without looking into the future.
- Uses a chronological holdout set so the evaluation resembles real forecasting.
- Compares a Ridge Regression model with a naive baseline that assumes the next close equals today's close.
- Saves the trained model, metrics, holdout predictions, forecast plot, and latest prediction locally.

## Project structure

```text
.
├── data/                         # Optional local CSV data (not committed)
├── docs/PROJECT_REPORT_TEMPLATE.md
├── src/stock_predictor/
│   ├── data.py                   # Data loading and validation
│   ├── features.py               # Leakage-safe feature engineering
│   ├── model.py                  # Train, baseline, and evaluation logic
│   └── cli.py                    # Command-line entry point
├── tests/                        # Automated checks
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment, then install the required packages.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run a training experiment

Use Yahoo Finance data for Apple from 2020 onward:

```powershell
$env:PYTHONPATH = "src"
python -m stock_predictor.cli train --ticker AAPL --start 2020-01-01
```

Or train from a Kaggle-style CSV. The CSV needs a date column and a `Close` column (case-insensitive):

```powershell
$env:PYTHONPATH = "src"
python -m stock_predictor.cli train --csv data\your_dataset.csv
```

The command writes results into `artifacts/`, which is intentionally excluded from Git so that generated models and downloaded data do not bloat the repository.

## Read the results

After a run, inspect these files:

- `artifacts/metrics.json` - Ridge and baseline MAE, RMSE, and R-squared scores.
- `artifacts/predictions.csv` - Actual and predicted prices for the final chronological test period.
- `artifacts/forecast.png` - Visual comparison of actual and predicted holdout prices.
- `artifacts/latest_prediction.json` - The model's next-close estimate based on the latest available row.
- `artifacts/model.joblib` - Saved pipeline and feature list for reuse.

For a credible conclusion, report whether the model beats the naive baseline. A model that does not beat the baseline should be described honestly; that is still a valid experimental result.

## Methodology

The target is the closing price after the selected forecast horizon (one trading day by default). Features use only data available on or before the prediction date:

- Current close and lagged closing prices (1, 2, 3, 5, 10, and 20 days)
- Daily percentage return
- Rolling price averages and standard deviations (5, 10, and 20 days)
- Relative distance between the current close and rolling averages

The newest 20% of eligible observations is reserved as a test set; the model never trains on it. This avoids the random shuffling that causes future information to leak into time-series evaluations.

## Quality checks

Run the automated tests after setup:

```powershell
$env:PYTHONPATH = "src"
pytest -q
```

## GitHub publication checklist

1. Run the tests and one real experiment locally.
2. Review `artifacts/metrics.json` and use the exact values in your report.
3. Add a short screenshot of `artifacts/forecast.png` to the repository only if your instructor expects it.
4. Make sure local datasets, virtual environments, and `artifacts/` are not staged.
5. Create a GitHub repository, add it as `origin`, commit, and push.

The report template in `docs/PROJECT_REPORT_TEMPLATE.md` lists the evidence to capture after your first successful experiment.
