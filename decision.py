import requests

def get_binance_data(symbol="BTCUSDT"):
    # Fetch current ticker data
    response = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=" + symbol)
    data = response.json()
    # Extract relevant fields
    current_price = float(data["lastPrice"])
    price_change_percent = float(data["priceChangePercent"])
    volume = float(data["volume"])
    return current_price, price_change_percent, volume


def assess_price_volume(post_price, post_time, symbol="BTCUSDT"):
    current_price, price_change_percent, current_volume = get_binance_data(symbol)
    
    # Hypothetical: If >10% increase since post_time, but we need the actual time logic:
    # For simplicity, assume we fetched post_price at post_time earlier.
    price_increase = ((current_price - post_price) / post_price) * 100
    
    # Fetch historical volume data (could be cached or from DB)
    # For a simple example, assume avg_24h_volume is from a previous call or a DB.
    # To get a 24h average volume, you can rely on "volume" in the 24hr ticker and compare to some baseline.
    _, _, avg_24h_volume = get_binance_data(symbol)  # Normally you'd store this reference before and after some interval
    
    volume_spike = current_volume / avg_24h_volume if avg_24h_volume else 1
    
    price_score = 0
    if price_increase > 10:
        # Add score for a significant price pump
        price_score += 30  # Example weighting

    volume_score = 0
    if volume_spike > 3:
        volume_score += 30  # Example weighting

    return price_score, volume_score, price_increase, volume_spike
#print(compute_sentiment_score(text))

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
