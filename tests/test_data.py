import pandas as pd

from stock_predictor.data import validate_price_history


def test_validation_sorts_rows_removes_duplicate_dates_and_keeps_close() -> None:
    dates = pd.date_range("2024-01-01", periods=41, freq="B")
    raw = pd.DataFrame(
        {
            "Date": list(reversed(dates)) + [dates[0]],
            "Close": list(range(100, 141))[::-1] + [999],
        }
    )

    cleaned = validate_price_history(raw)

    assert cleaned.index.is_monotonic_increasing
    assert len(cleaned) == 41
    assert cleaned.loc[dates[0], "Close"] == 999
