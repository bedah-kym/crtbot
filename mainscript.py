from analysis import assess_historical_pattern
from SOCIALBOTS.botsdump import sentiment_scores
from decision import get_binance_data, assess_price_volume ,calculate_trade_amount,decide_to_buy
from indicators import mainscore
from execution import get_portfolio_balance, execute_trade
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
api_key = os.environ.get('TEST_API_KEY')
api_secret = os.environ.get('TEST_SECRET')


def initialize_testnet_client(api_key: str, api_secret: str) -> Client:
    """
    Initialize and return Binance Testnet client.
    """
    client = Client(api_key, api_secret)
    client.API_URL = 'https://testnet.binance.vision/api'  # Set the Binance testnet URL
    return client


def run_pump_detection_pipeline(post_text, post_price, post_time,coin_symbol="BTCUSDT"):
    """
    Main pipeline for detecting pump-and-dump schemes.

    Parameters:
    - post_text (str): The text content of the post.
    - post_price (float): The price mentioned in the post.
    - post_time (str): The timestamp of the post.
    - coin_symbol (str): Cryptocurrency symbol (default: "BTCUSDT").
    - portfolio_balance (float): User portfolio balance (default: 1000).

    Returns:
    - dict: Results of the pipeline analysis.
    """
    try:
        # 1. Engagement metrics (Placeholder for future implementation)
        engagement_score = len(post_text)  # Simplistic placeholder

        # 2. Price & Volume Analysis
        binance_price, price_change_percent, volume = get_binance_data(coin_symbol)
        price_score, volume_score, price_increase, volume_spike = assess_price_volume(post_price, post_time, coin_symbol)

        # 3. Sentiment Analysis
        sentiment_score, sentiment = sentiment_scores()

        # 4. Historical Data (Placeholder for future implementation)
        historical_score = 0  # Placeholder value
        
        # Aggregate results
        results = {
            "engagement_score": engagement_score,
            "price_analysis": {
                "binance_price": binance_price,
                "price_change_percent": price_change_percent,
                "volume": volume,
                "price_score": price_score,
                "volume_score": volume_score,
                "price_increase": price_increase,
                "volume_spike": volume_spike,
            },
            "sentiment_analysis": {
                "sentiment_score": sentiment_score,
                "sentiment": sentiment,
            },
            "historical_score": historical_score,
           
        }

        return results

    except Exception as e:
        print(f"Error in pipeline: {e}")
        return None

def trade_execution(client,hist_score, total_score):
    print('trading exection ....')
    portfolio_balance = get_portfolio_balance(client,'USDT') 
    trade_amount = calculate_trade_amount(hist_score, total_score, portfolio_balance,existing_positions_count=3)
    print("---------trade amount to stake",trade_amount)

    can_buy =decide_to_buy(hist_score,total_score,price_increase=955.535)
    print ("---------descision to buy is :",can_buy)
    if can_buy :
        execute_trade(
            client,
            amount=trade_amount,
            symbol = 'BTCUSDT'
        )
        
          
# Example call
if __name__ == "__main__":
    
    # Replace with real data for testing
    client = initialize_testnet_client(api_key, api_secret)
    post_text = "The price of Bitcoin  is skyrocketing! Time to buy."
    
    total_score = mainscore(symbol = 'BTCUSDT',interval = '1h',limit = 500)
    hist_score = assess_historical_pattern()
    
    post_price = 20000.0
    post_time = "2024-12-08T12:00:00Z"
    
    results = run_pump_detection_pipeline(post_text,post_price, post_time)
    print("analysis",results)
    
    trade = trade_execution(client,hist_score, total_score)
    print(trade)
