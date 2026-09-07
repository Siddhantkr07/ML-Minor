"""Feature construction that preserves time ordering and avoids target leakage."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FeatureConfig:
    """Feature windows used by the experiment."""

    lags: tuple[int, ...] = (1, 2, 3, 5, 10, 20)
    rolling_windows: tuple[int, ...] = (5, 10, 20)
    forecast_horizon: int = 1


def create_feature_frame(prices: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Create inputs and a future-close target for every eligible date.

    The row dated *t* contains only the close and indicators known at the end
    of date *t*. Its target is the close at *t + forecast_horizon*.
    """
    if config.forecast_horizon < 1:
        raise ValueError("forecast_horizon must be at least 1.")

    close = prices["Close"].astype(float).copy()
    frame = pd.DataFrame(index=prices.index)
    frame["current_close"] = close
    frame["daily_return"] = close.pct_change()

    for lag in config.lags:
        if lag < 1:
            raise ValueError("All lags must be positive integers.")
        frame[f"close_lag_{lag}"] = close.shift(lag)

    for window in config.rolling_windows:
        if window < 2:
            raise ValueError("Rolling windows must be at least 2.")
        average = close.rolling(window=window, min_periods=window).mean()
        frame[f"rolling_mean_{window}"] = average
        frame[f"rolling_std_{window}"] = close.rolling(window=window, min_periods=window).std()
        frame[f"close_to_mean_{window}"] = close / average - 1.0

    frame["target"] = close.shift(-config.forecast_horizon)
    return frame.dropna(subset=[column for column in frame.columns if column != "target"])


def supervised_dataset(feature_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split eligible features from the known future-price target."""
    eligible = feature_frame.dropna(subset=["target"]).copy()
    if len(eligible) < 30:
        raise ValueError("Not enough complete rows remain after feature engineering.")
    return eligible.drop(columns="target"), eligible["target"]
