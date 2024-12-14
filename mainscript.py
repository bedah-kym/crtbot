import asyncio
import nest_asyncio
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *
from analysis import assess_historical_pattern
from SOCIALBOTS.botsdump import sentiment_scores
from decision import (
    get_binance_data,
    assess_price_volume,
    calculate_trade_amount,
    decide_to_buy
)
from indicators import mainscore
from execution import get_portfolio_balance, execute_trade, get_open_positions
from SOCIALBOTS.telegrambot2 import send_notification

# Apply nested asyncio compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv()
API_KEY = os.getenv('TEST_API_KEY')
API_SECRET = os.getenv('TEST_SECRET')

async def initialize_testnet_client(api_key: str, api_secret: str) -> Client:
    """
    Initialize Binance testnet client.
    """
    client = Client(api_key, api_secret)
    client.API_URL = 'https://testnet.binance.vision/api'
    return client


def get_market_precision(client: Client, symbol: str) -> int:
    """
    Fetch the precision for a given trading pair.
    """
    exchange_info = client.get_exchange_info()
    for symbol_info in exchange_info['symbols']:
        if symbol_info['symbol'] == symbol:
            lot_size_filter = next(
                filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']),
                None
            )
            if lot_size_filter:
                step_size = float(lot_size_filter['stepSize'])
                return len(str(step_size).split('.')[-1].rstrip('0'))
    return 0  # Default precision


def round_quantity(quantity: float, precision: int) -> float:
    """
    Round the trade quantity to the appropriate precision.
    """
    return round(quantity, precision)


async def run_pump_detection_pipeline(
    keywords: list, subreddits: list ,coin_symbol: str, searchcoin:str
) -> dict:
    """
    Main pipeline for detecting pump-and-dump schemes.
    """
    try:
        # Sentiment Analysis
        sentiment_score, sentiment, influencial_post = await sentiment_scores(keywords,subreddits,searchcoin)

        if influencial_post:
            engagement_score = influencial_post.get('engagement_score', 0)
            post_time = influencial_post.get('date','created_utc')
            
        else:
            print("No influential post found.")
            engagement_score = 0   
            post_time = "2024-12-08T12:00:00Z" #placeholder    
         # Price & Volume Analysis
        binance_price, price_change_percent, volume = get_binance_data(coin_symbol)
        price_score, volume_score, price_increase, volume_spike = assess_price_volume(
            post_time, coin_symbol
        )
        
        
        # Historical Data Analysis
        historical_score = assess_historical_pattern()

        return {
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

    except Exception as e:
        print(f"Error in pipeline: {e}")
        return None


async def trade_execution(
    client: Client, historical_score: float, total_score: float, coin_symbol: str, price_increase: float
):
    """
    Execute trade based on analysis results.
    """
    try:
        open_positions = get_open_positions(client) or 0
        portfolio_balance = get_portfolio_balance(client, "USDT")
        precision = get_market_precision(client, coin_symbol)

        trade_amount = calculate_trade_amount(
            historical_score, total_score, portfolio_balance,open_positions
        )
        trade_amount = round_quantity(trade_amount, precision)

        can_buy = decide_to_buy(historical_score, total_score, price_increase=price_increase)

        if can_buy:
            order = execute_trade(client, trade_amount, coin_symbol)
            print("Trade executed:", order)
            await send_notification(f"Trade executed: {order}")
        else:
            await send_notification(f"No buy signal detected for {coin_symbol}.")

    except Exception as e:
        print(f"Trade execution failed: {e}")
        await send_notification(f"Trade execution failed: {e}")


async def main():
    """
    Main function to execute the pipeline and trade decisions.
    """
    coin_symbol = "BTCUSDT"
    
    searchcoin = "bitcoin"
    
    keywords=[searchcoin,"pump","moon","100x","buy now","HODL","FOMO","next big thing"]
    
    subreddits=["CryptoCurrency", "CryptoMoonShots", "altcoin"]

    client = await initialize_testnet_client(API_KEY, API_SECRET)

    
    # Run analysis pipeline
    results = await run_pump_detection_pipeline(
        keywords,subreddits,coin_symbol,searchcoin
    )
    print("Pipeline Results:", results)

    if results:
        total_score = mainscore(symbol=coin_symbol, interval="1h", limit=500)
        historical_score = results["historical_score"]

        await trade_execution(client, historical_score, total_score, coin_symbol, results['price_analysis']['price_increase'])


if __name__ == "__main__":
    asyncio.run(main())
