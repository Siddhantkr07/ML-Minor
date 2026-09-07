"""Chronological model fitting and transparent evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class TrainingResult:
    model: Pipeline
    predictions: pd.DataFrame
    metrics: dict[str, dict[str, float]]
    train_rows: int
    test_rows: int


def chronological_split(
    features: pd.DataFrame, target: pd.Series, test_size: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Reserve the newest observations for testing without shuffling."""
    if not 0.1 <= test_size < 0.5:
        raise ValueError("test_size must be between 0.1 and 0.5.")
    split_index = int(len(features) * (1 - test_size))
    if split_index < 20 or len(features) - split_index < 5:
        raise ValueError("The dataset is too small for the selected chronological split.")
    return (
        features.iloc[:split_index],
        features.iloc[split_index:],
        target.iloc[:split_index],
        target.iloc[split_index:],
    )


def _metric_values(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(mean_squared_error(actual, predicted) ** 0.5),
        "r2": float(r2_score(actual, predicted)),
    }


def train_and_evaluate(features: pd.DataFrame, target: pd.Series, test_size: float = 0.2) -> TrainingResult:
    """Fit Ridge Regression and compare it against the persistence baseline."""
    x_train, x_test, y_train, y_test = chronological_split(features, target, test_size)
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=1.0)),
        ]
    )
    model.fit(x_train, y_train)
    model_prediction = model.predict(x_test)
    baseline_prediction = x_test["current_close"].to_numpy()

    predictions = pd.DataFrame(
        {
            "actual_close": y_test,
            "ridge_prediction": model_prediction,
            "naive_prediction": baseline_prediction,
        },
        index=x_test.index,
    )
    metrics = {
        "ridge_regression": _metric_values(y_test, model_prediction),
        "naive_persistence": _metric_values(y_test, baseline_prediction),
    }
    return TrainingResult(model, predictions, metrics, len(x_train), len(x_test))
