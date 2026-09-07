import pandas as pd

from stock_predictor.features import FeatureConfig, create_feature_frame, supervised_dataset


def test_target_is_the_next_observed_close() -> None:
    index = pd.date_range("2024-01-01", periods=50, freq="B")
    prices = pd.DataFrame({"Close": range(100, 150)}, index=index)

    frame = create_feature_frame(prices, FeatureConfig(lags=(1, 2), rolling_windows=(3,), forecast_horizon=1))

    first_date = frame.index[0]
    assert frame.loc[first_date, "target"] == prices.loc[index[index.get_loc(first_date) + 1], "Close"]


def test_supervised_dataset_excludes_unknown_future_target() -> None:
    index = pd.date_range("2024-01-01", periods=50, freq="B")
    prices = pd.DataFrame({"Close": range(100, 150)}, index=index)
    frame = create_feature_frame(prices, FeatureConfig(lags=(1,), rolling_windows=(3,), forecast_horizon=1))

    features, target = supervised_dataset(frame)

    assert features.index.max() < frame.index.max()
    assert target.notna().all()
