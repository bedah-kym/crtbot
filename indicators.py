import pandas as pd
import numpy as np
from ta import trend, momentum
from typing import Optional
from binance.client import Client
from binance.enums import *

def calculate_rsi(close_prices: pd.Series, window: int = 14) -> float:
    """
    Calculate the Relative Strength Index (RSI) and return the latest valid value.
    If not enough data is available, return NaN.
    """
    if len(close_prices) < window:
        print("Not enough data to calculate RSI.")
        return float('nan')
    
    rsi_series = momentum.RSIIndicator(close=close_prices, window=window).rsi()
    non_nan_rsi = rsi_series.dropna()
    if non_nan_rsi.empty:
        print("RSI calculation returned no valid values.")
        return float('nan')
    
    latest_rsi = non_nan_rsi.iloc[-1]
    return latest_rsi

def calculate_macd(close_prices: pd.Series) -> float:
    macd = trend.MACD(close=close_prices)
    macd_hist = macd.macd_diff().dropna()
    if macd_hist.empty:
        print("Not enough data to calculate MACD.")
        return float('nan')
    return macd_hist.iloc[-1]

def calculate_sma_crossover(short_window: int, long_window: int, close_prices: pd.Series) -> float:
    if len(close_prices) < max(short_window, long_window):
        print("Not enough data to calculate SMA crossover.")
        return 0.5  # Neutral by default

    sma_short = trend.SMAIndicator(close=close_prices, window=short_window).sma_indicator()
    sma_long = trend.SMAIndicator(close=close_prices, window=long_window).sma_indicator()

    # Drop NaN values if any
    if sma_short.dropna().empty or sma_long.dropna().empty:
        print("Not enough data to compute SMA values.")
        return 0.5
    
    if sma_short.iloc[-2] < sma_long.iloc[-2] and sma_short.iloc[-1] > sma_long.iloc[-1]:
        return 1.0
    elif sma_short.iloc[-2] > sma_long.iloc[-2] and sma_short.iloc[-1] < sma_long.iloc[-1]:
        return 0.0
    else:
        return 0.5

def calculate_ema_crossover(short_window: int, long_window: int, close_prices: pd.Series) -> float:
    if len(close_prices) < max(short_window, long_window):
        print("Not enough data to calculate EMA crossover.")
        return 0.5

    ema_short = trend.EMAIndicator(close=close_prices, window=short_window).ema_indicator()
    ema_long = trend.EMAIndicator(close=close_prices, window=long_window).ema_indicator()

    # Drop NaN values if any
    if ema_short.dropna().empty or ema_long.dropna().empty:
        print("Not enough data to compute EMA values.")
        return 0.5

    if ema_short.iloc[-2] < ema_long.iloc[-2] and ema_short.iloc[-1] > ema_long.iloc[-1]:
        return 1.0
    elif ema_short.iloc[-2] > ema_long.iloc[-2] and ema_short.iloc[-1] < ema_long.iloc[-1]:
        return 0.0
    else:
        return 0.5

def calculate_volume_spike(current_volume: float, average_volume: float, threshold: float = 3.0) -> float:
    if np.isnan(current_volume) or np.isnan(average_volume):
        print("Volume data is invalid.")
        return 0.0

    if current_volume >= threshold * average_volume:
        return 1.0
    elif current_volume >= 1.5 * average_volume:
        return 0.5
    else:
        return 0.0

def calculate_sentiment_score(sentiment: float, threshold: float = 0.8) -> float:
    if np.isnan(sentiment):
        return 0.0
    if sentiment >= threshold:
        return 1.0
    else:
        return sentiment / threshold

def calculate_hist_score(hist_score: int, max_hist_score: int = 20) -> float:
    if hist_score < 0:
        hist_score = 0
    return min(hist_score / max_hist_score, 1.0)

def get_total_score(
    close_prices: pd.Series,
    current_volume: float,
    average_volume: float,
    sentiment: float,
    hist_score: int,
    rsi_window: int = 14,
    macd_window_short: int = 12,
    macd_window_long: int = 26,
    sma_short_window: int = 20,
    sma_long_window: int = 50,
    ema_short_window: int = 12,
    ema_long_window: int = 26,
    volume_threshold: float = 3.0,
    sentiment_threshold: float = 0.8,
    hist_max_score: int = 20
) -> float:
    weights = {
        'RSI': 0.15,
        'MACD': 0.15,
        'SMA_Crossover': 0.15,
        'EMA_Crossover': 0.15,
        'Volume_Spike': 0.15,
        'Sentiment': 0.15,
        'Historical': 0.10
    }

    latest_rsi = calculate_rsi(close_prices, window=rsi_window)
    if np.isnan(latest_rsi):
        rsi_score = 0.5  # Default neutral if RSI can't be calculated
    else:
        rsi_score = 1.0 if latest_rsi < 30 else (0.5 if latest_rsi < 50 else 0.0)

    macd_hist = calculate_macd(close_prices)
    if np.isnan(macd_hist):
        macd_score = 0.5
    else:
        macd_score = 1.0 if macd_hist > 0 else 0.0

    sma_score = calculate_sma_crossover(short_window=sma_short_window, long_window=sma_long_window, close_prices=close_prices)
    ema_score = calculate_ema_crossover(short_window=ema_short_window, long_window=ema_long_window, close_prices=close_prices)
    volume_spike_score = calculate_volume_spike(current_volume, average_volume, threshold=volume_threshold)
    sentiment_score = calculate_sentiment_score(sentiment, threshold=sentiment_threshold)
    hist_score_normalized = calculate_hist_score(hist_score, max_hist_score=hist_max_score)

    weighted_rsi = weights['RSI'] * rsi_score
    weighted_macd = weights['MACD'] * macd_score
    weighted_sma = weights['SMA_Crossover'] * sma_score
    weighted_ema = weights['EMA_Crossover'] * ema_score
    weighted_volume = weights['Volume_Spike'] * volume_spike_score
    weighted_sentiment = weights['Sentiment'] * sentiment_score
    weighted_hist = weights['Historical'] * hist_score_normalized

    total_score = (
        weighted_rsi +
        weighted_macd +
        weighted_sma +
        weighted_ema +
        weighted_volume +
        weighted_sentiment +
        weighted_hist
    ) * 100

    return total_score

def mainscore(symbol,interval,limit):
    client = Client()  # Public data
    symbol = 'BTCUSDT'
    interval = '1h'
    limit = 500
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    close_prices = df['close']
    current_volume = df['volume'].iloc[-1] if len(df) > 0 else float('nan')
    average_volume = df['volume'].mean() if len(df) > 0 else float('nan')

    sentiment = 0.85
    hist_score = 15

    total = get_total_score(
        close_prices=close_prices,
        current_volume=current_volume,
        average_volume=average_volume,
        sentiment=sentiment,
        hist_score=hist_score
    )

    print(f"Total Score: {total:.2f}/100")
    return total
