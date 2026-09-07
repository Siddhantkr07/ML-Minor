# Stock Price Prediction Project Report

Use this as a submission outline after running the project. Replace every bracketed item with your own verified result; do not invent metric values.

## 1. Title

**Stock Price Prediction Using Ridge Regression and Technical Time-Series Features**

## 2. Abstract

State the stock/ticker, date range, prediction horizon, model, evaluation approach, and whether the model outperformed the naive baseline. Keep this to 150-200 words.

## 3. Problem Statement

Predict the next trading day's closing price from historical closing-price information. Explain that this is a regression task and that financial markets are noisy, so the project evaluates rather than guarantees forecast accuracy.

## 4. Dataset

- Source: [Yahoo Finance / Kaggle dataset name and URL]
- Ticker: [e.g., AAPL]
- Period: [start date] to [end date]
- Observations after cleaning: [number]
- Key field: daily `Close` price

Describe missing values, duplicate dates, and any cleaning you performed.

## 5. Feature Engineering

List the project features: current close, 1/2/3/5/10/20-day lags, daily return, 5/10/20-day rolling mean, rolling standard deviation, and distance from rolling mean. Explain that each row's target is the close on the next trading day and that the features were calculated only from present or past values.

## 6. Model and Evaluation Design

Describe the Ridge Regression pipeline: median imputation, standard scaling, and Ridge Regression. Explain why the most recent 20% was held out chronologically rather than randomly shuffled. Include the naive persistence baseline, which predicts the next close to be equal to the current close.

## 7. Results

Copy exact values from `artifacts/metrics.json`.

| Model | MAE | RMSE | R-squared |
|---|---:|---:|---:|
| Ridge Regression | [value] | [value] | [value] |
| Naive persistence baseline | [value] | [value] | [value] |

Insert the holdout chart generated at `artifacts/forecast.png` and give it a clear caption.

## 8. Discussion

State whether Ridge Regression beat the baseline on MAE/RMSE. If it did not, explain that the result shows how difficult short-horizon price prediction is. Discuss limitations: a single price series, no news or macroeconomic data, changing market regimes, and no trading-cost analysis.

## 9. Conclusion and Future Work

Summarise the evaluated result without promising investment profitability. Reasonable extensions include walk-forward validation, additional market indicators, different assets, and models such as Random Forest, XGBoost, or LSTM, evaluated against the same baseline.

## 10. Reproducibility

Link your GitHub repository and include the exact command you ran. Example:

```powershell
$env:PYTHONPATH = "src"
python -m stock_predictor.cli train --ticker AAPL --start 2020-01-01
```
