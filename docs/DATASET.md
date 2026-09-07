# Dataset Documentation

## Dataset used for the verified experiment

The verified experiment uses daily Apple Inc. stock-price history with ticker `AAPL`. The project retrieves the data through the `yfinance` Python package, which requests historical market data from Yahoo Finance.

## Experiment period

- Requested range: 2020-01-01 to 2025-01-01
- Observed range: recorded automatically in `artifacts/dataset_summary.json` after each run
- Frequency: trading days
- Prediction target: closing price one trading day ahead

## Fields used

The model validates a `Date` field and a positive numeric `Close` field. From closing prices it derives lagged closes, daily return, rolling means, rolling standard deviations, and the relative distance from rolling means.

## Cleaning and quality checks

The data loader sorts records by date, removes duplicate dates while retaining the final value, converts close values to numeric form, drops invalid dates or missing closes, and rejects non-positive closes. A minimum of 40 valid observations is required before feature construction.

## Reproduce the dataset

From the project root, run:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m stock_predictor.cli train --ticker AAPL --start 2020-01-01 --end 2025-01-01
```

The cleaned data used for that run is written locally to `artifacts/price_history.csv`. The `artifacts` directory is deliberately excluded from version control so that each experiment can record its own data snapshot without committing generated data or model files.

## Alternative CSV source

A CSV from Kaggle or another source can be used when it provides a date column and a `Close` column. Place the file in `data/` and run:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m stock_predictor.cli train --csv data\your_dataset.csv
```
