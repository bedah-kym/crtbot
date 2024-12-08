

def run_pump_detection_pipeline(post_text, post_price, post_time, coin_symbol="BTCUSDT", portfolio_balance=1000):
    # 1. Engagement metrics
    engagement_score = get_engagement_score(post_text)
    
    # 2. Price & Volume Analysis
    price_score, volume_score, price_increase, volume_spike = assess_price_volume(post_price, post_time, coin_symbol)
    
    # 3. Sentiment Analysis
    sentiment_score, sentiment = compute_sentiment_score(post_text)
    
    # 4. Historical Data
    hist_score = assess_historical_pattern(coin_symbol)
    
    # Aggregate scores
    total_score = engagement_score + price_score + volume_score + sentiment_score + hist_score
    
    # Decide to buy
    should_buy = decide_to_buy(total_score, hist_score, price_increase)
    
    # Risk Management: Calculate trade amount based on hist_score
    trade_amount = calculate_trade_amount(hist_score, portfolio_balance) if should_buy else 0
    
    # Execute trade if conditions met
    if should_buy:
        try:
            order_response = execute_trade(symbol=coin_symbol, amount=trade_amount, api_key="your_api_key", api_secret="your_secret")
            log(f"Buy Order Placed: {order_response}")
        except Exception as e:
            log(f"Error placing order: {e}")
    else:
        log("No trade executed.")
