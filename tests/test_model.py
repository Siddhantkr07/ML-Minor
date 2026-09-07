import numpy as np
import pandas as pd

from stock_predictor.model import chronological_split, train_and_evaluate


def _sample_dataset() -> tuple[pd.DataFrame, pd.Series]:
    index = pd.date_range("2023-01-01", periods=100, freq="B")
    close = np.linspace(100, 140, len(index))
    features = pd.DataFrame(
        {"current_close": close, "close_lag_1": np.roll(close, 1), "daily_return": 0.002}, index=index
    )
    target = pd.Series(close + 0.4, index=index)
    return features, target


def test_chronological_split_keeps_future_rows_out_of_training() -> None:
    features, target = _sample_dataset()
    x_train, x_test, y_train, y_test = chronological_split(features, target, test_size=0.2)

    assert x_train.index.max() < x_test.index.min()
    assert y_train.index.max() < y_test.index.min()


def test_training_returns_metrics_and_holdout_predictions() -> None:
    features, target = _sample_dataset()
    result = train_and_evaluate(features, target, test_size=0.2)

    assert result.test_rows == len(result.predictions)
    assert set(result.metrics) == {"ridge_regression", "naive_persistence"}
    assert result.predictions["ridge_prediction"].notna().all()
