# Model Card

## Model summary

This project predicts the next trading day's closing price from recent historical closing-price information. It is an educational time-series regression project and not an investment system.

## Inputs and target

- Input: current closing price, 1/2/3/5/10/20-day lagged closes, daily return, and 5/10/20-day rolling statistics.
- Target: closing price after one trading day by default.
- Output: numeric next-close estimate.

## Model pipeline

The model uses median imputation, standard scaling, and Ridge Regression with `alpha=1.0`. It is compared against a persistence baseline that predicts the next close as the current close.

## Evaluation design

The newest 20% of complete observations is held out as a chronological test set. No random shuffle is used. This means every training observation precedes every evaluation observation and reduces the risk of future information leaking into the model.

## Verified AAPL experiment

For AAPL data requested from 2020-01-01 through 2025-01-01, the verified run uses 989 training rows and 248 test rows after feature engineering. The exact metrics are retained in `artifacts/metrics.json` and reported in the final report.

## Limitations and responsible use

- A single historical price series does not represent news, fundamentals, macroeconomics, or intraday market activity.
- Financial markets can change regime, so past performance does not guarantee future accuracy.
- The project does not assess trading costs, portfolio risk, or investment suitability.
- Model output must not be used as financial advice or an automated trading signal.
