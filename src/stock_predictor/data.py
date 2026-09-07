"""Data loading and validation helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _standardise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Flatten provider-specific columns and normalise common OHLC names."""
    cleaned = frame.copy()
    if isinstance(cleaned.columns, pd.MultiIndex):
        cleaned.columns = ["_".join(str(value) for value in column if value) for column in cleaned.columns]

    rename_map: dict[str, str] = {}
    for column in cleaned.columns:
        normalised = str(column).strip().lower().replace("_", " ")
        if normalised in {"date", "datetime", "timestamp"}:
            rename_map[column] = "Date"
        elif normalised == "close" or normalised.startswith("close "):
            rename_map[column] = "Close"
        elif normalised in {"adj close", "adjusted close"}:
            rename_map[column] = "Adj Close"
    return cleaned.rename(columns=rename_map)


def validate_price_history(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a clean, dated Close series table or raise a helpful error."""
    prepared = _standardise_columns(frame)
    if "Close" not in prepared.columns:
        raise ValueError("The dataset must include a 'Close' column.")

    if "Date" in prepared.columns:
        prepared["Date"] = pd.to_datetime(prepared["Date"], errors="coerce")
        prepared = prepared.set_index("Date")
    elif not isinstance(prepared.index, pd.DatetimeIndex):
        raise ValueError("The dataset must include a Date column or a datetime index.")

    prepared.index = pd.to_datetime(prepared.index, errors="coerce")
    prepared = prepared.loc[~prepared.index.isna()].sort_index()
    prepared = prepared.loc[~prepared.index.duplicated(keep="last")]
    prepared["Close"] = pd.to_numeric(prepared["Close"], errors="coerce")
    prepared = prepared.dropna(subset=["Close"])

    if len(prepared) < 40:
        raise ValueError("At least 40 valid closing-price observations are required.")
    if (prepared["Close"] <= 0).any():
        raise ValueError("Closing prices must be positive values.")

    return prepared[["Close"]].copy()


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load and validate a local CSV with date and closing-price columns."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    return validate_price_history(pd.read_csv(csv_path))


def download_history(ticker: str, start: str, end: str | None = None) -> pd.DataFrame:
    """Download daily historical data from Yahoo Finance."""
    try:
        import yfinance as yf
    except ImportError as error:  # pragma: no cover - depends on environment setup
        raise ImportError("Install dependencies with 'pip install -r requirements.txt'.") from error

    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty.")
    history = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if history.empty:
        raise ValueError(f"No daily price data was returned for ticker '{ticker}'.")
    return validate_price_history(history)
