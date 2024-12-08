import time
import nltk
import statistics
import requests
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def compute_sentiment_score(post_text):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(post_text)
    # VADER gives 'compound' in [-1,1]
    # Transform it to [0,1] for convenience
    sentiment = (scores['compound'] + 1) / 2.0  
    # If sentiment > 0.8, we consider it a strong indicator
    sentiment_score = 20 if sentiment > 0.8 else 0
    return sentiment_score, sentiment

def get_historical_klines(symbol="BTCUSDT", interval="1h", limit=100):
    """Fetch historical OHLC data from Binance."""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def analyze_historical_data(klines):
    """Analyze historical data to detect past pump patterns.
    
    This function will:
    - Compute % increases between open and close prices of each candle.
    - Identify candles with unusually large spikes in price and volume.
    
    You can customize this logic to identify 'pump' patterns.
    """
    price_increases = []
    volumes = []

    for candle in klines:
        open_time = candle[0]
        open_price = float(candle[1])
        high_price = float(candle[2])
        low_price = float(candle[3])
        close_price = float(candle[4])
        volume = float(candle[5])

        # Percentage increase in this interval
        if open_price > 0:
            pct_increase = ((close_price - open_price) / open_price) * 100
        else:
            pct_increase = 0
        
        price_increases.append(pct_increase)
        volumes.append(volume)

    # Basic Statistics
    avg_price_increase = statistics.mean(price_increases)
    max_price_increase = max(price_increases)
    avg_volume = statistics.mean(volumes)
    max_volume = max(volumes)

    # Simple Heuristic: If we found instances of large >20% candles historically, 
    # or volume spikes > 3x average, it might indicate historical pump behavior.
    # This is a placeholder; you should refine it with more nuanced logic.
    historical_pump_count = sum(1 for p in price_increases if p > 20)
    historical_volume_spikes = sum(1 for v in volumes if v > 3 * avg_volume)

    # Score based on historical pump tendencies
    # For example, if the coin had multiple >20% pumps in the last 100 intervals, 
    # we add some score.
    hist_pump_score = 10 if historical_pump_count > 2 else 0
    # If there were frequent volume spikes, add to the score
    hist_pump_score += 10 if historical_volume_spikes > 2 else 0

    return hist_pump_score, {
        "avg_price_increase": avg_price_increase,
        "max_price_increase": max_price_increase,
        "avg_volume": avg_volume,
        "max_volume": max_volume,
        "historical_pump_count": historical_pump_count,
        "historical_volume_spikes": historical_volume_spikes
    }
    
def assess_historical_pattern(coin_symbol="BTCUSDT"):
    # Fetch last 1000 1-hour candles for historical analysis
    klines_data = get_historical_klines(symbol=coin_symbol, interval="1h", limit=1000)
    hist_score, details = analyze_historical_data(klines_data)
    
    return hist_score


print(assess_historical_pattern())