from dateutil import parser
import requests

def get_binance_data(symbol):
    # Fetch current ticker data
    response = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=" + symbol)
    data = response.json()
    # Extract relevant fields
    current_price = float(data["lastPrice"])
    price_change_percent = float(data["priceChangePercent"])
    volume = float(data["volume"])
    return current_price, price_change_percent, volume

def get_historical_data(symbol, start_time, end_time, interval="1m"):
    """
    Fetch historical OHLC data from Binance.

    :param symbol: Cryptocurrency symbol (e.g., 'BTCUSDT').
    :param start_time: Start time in UNIX timestamp.
    :param end_time: End time in UNIX timestamp.
    :param interval: Time interval for the data (e.g., '1m', '1h').
    :return: List of historical data points.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time * 1000),  # Convert to milliseconds
        "endTime": int(end_time * 1000)      # Convert to milliseconds
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{"open_time": k[0], "close": float(k[4])} for k in data]  # Extract close prices
    else:
        raise ValueError(f"Failed to fetch historical data: {response.text}")


def get_price_at_time(symbol, timestamp):
    """
    Fetch the price of the cryptocurrency at a specific timestamp.

    :param symbol: Cryptocurrency symbol (e.g., 'BTCUSDT').
    :param timestamp: Unix timestamp for the desired price.
    :return: Price at the specified timestamp.
    """
    historical_data = get_historical_data(symbol, timestamp, timestamp + 60, interval="1m")
    if historical_data:
        return historical_data[0]['close']  # Return the close price of the first candle
    else:
        raise ValueError(f"Could not fetch historical price for {symbol} at {timestamp}")


def assess_price_volume(post_time, symbol):
    # Convert post time to timestamp
    post_timestamp = parser.parse(post_time).timestamp()

    # Fetch price at the time of the post
    try:
        price_at_post_time = get_price_at_time(symbol, post_timestamp)
    except ValueError as e:
        print(e)
        return 0, 0, 0, 0

    # Fetch current price and volume data
    current_price, price_change_percent, current_volume = get_binance_data(symbol)

    # Calculate price increase
    price_increase = ((current_price - price_at_post_time) / price_at_post_time) * 100

    # Fetch historical volume data
    _, _, avg_24h_volume = get_binance_data(symbol)
    volume_spike = current_volume / avg_24h_volume if avg_24h_volume else 1

    # Score calculation
    price_score = 30 if price_increase > 10 else 0
    volume_score = 30 if volume_spike > 3 else 0

    return price_score, volume_score, price_increase, volume_spike

def calculate_trade_amount(hist_score, total_score, portfolio_balance, existing_positions_count, max_allocation=0.05):
    """
    Calculate the trade amount based on historical confidence, total score, and portfolio balance.
    
    Parameters:
    - hist_score (int): Historical pump score (0, 10, 20).
    - total_score (int): Combined score from all indicators.
    - portfolio_balance (float): Total portfolio value in USD.
    - existing_positions_count (int): Number of current open positions.
    - max_allocation (float): Maximum allocation per trade (default 5%).
    
    Returns:
    - float: Amount in USD to allocate for the trade.
    """
    # Base allocation based on historical confidence
    if hist_score >= 20:
        base_allocation = 0.02  # 2%
    elif hist_score == 10:
        base_allocation = 0.01  # 1%
    else:
        base_allocation = 0.005  # 0.5%
    
    # Adjust allocation based on total_score
    # Higher total_score can slightly increase allocation
    if total_score > 90:
        score_multiplier = 1.2
    elif total_score > 80:
        score_multiplier = 1.1
    else:
        score_multiplier = 1.0
    
    # Adjust for existing positions to maintain diversification
    diversification_factor = 1 / (existing_positions_count + 1)  # More positions, smaller allocation
    
    # Calculate final allocation
    allocation = base_allocation * score_multiplier * diversification_factor
    
    # Ensure allocation does not exceed max_allocation
    allocation = min(allocation, max_allocation)
    
    # Calculate trade amount
    trade_amount = portfolio_balance * allocation
    
    # Ensure a minimum trade amount (e.g., $10) to avoid negligible trades
    min_trade_amount = 10.0
    trade_amount = max(trade_amount, min_trade_amount)
    
    return trade_amount


def decide_to_buy(total_score, hist_score, price_increase):
    SCORE_THRESHOLD = 70
    HIST_SCORE_THRESHOLD = 10
    
    signals = sum([price_increase > 10, hist_score > 0])
    
    if total_score > SCORE_THRESHOLD and signals >= 2 and price_increase < 50 and hist_score >= HIST_SCORE_THRESHOLD:
        return True
    return False
