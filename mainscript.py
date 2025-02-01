import asyncio
import nest_asyncio
import sqlite3
import os
import time
from datetime import datetime
import requests
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

nest_asyncio.apply()
load_dotenv()

# Binance testnet API keys
API_KEY = os.getenv('TEST_API_KEY')
API_SECRET = os.getenv('TEST_SECRET')

DB_PATH = "db.sqlite3"
# CoinMarketCap API key
CMC_API_KEY = os.getenv("CMC_API_KEY")

async def initialize_testnet_client(api_key: str, api_secret: str) -> Client:
    client = Client(api_key, api_secret)
    client.API_URL = 'https://testnet.binance.vision/api'  # Testnet
    return client

def synchronize_time(client: Client):
    try:
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_offset = server_time['serverTime'] - local_time
        client.time_offset = time_offset
    except Exception as e:
        print(f"Time sync error: {e}")

def get_market_precision(client: Client, symbol: str) -> int:
    exchange_info = client.get_exchange_info()
    for symbol_info in exchange_info['symbols']:
        if symbol_info['symbol'] == symbol:
            for f in symbol_info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
                    return len(str(step_size).split('.')[-1].rstrip('0'))
    return 0

def round_quantity(quantity: float, precision: int) -> float:
    return round(quantity, precision)

def get_top_100_coins():
    """
    Get top 100 coins from CoinMarketCap.
    """
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }
    params = {"limit": 10, "convert": "USD"}
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        top_100 = []
        for item in data["data"]:
            symbol = item["symbol"]
            top_100.append(symbol)
        return top_100
    except Exception as e:
        print(f"Error fetching coins from CoinMarketCap: {e}")
        return []

async def run_pump_detection_pipeline(
    keywords: list,
    subreddits: list,
    coin_symbol: str,
    searchcoin: str,
    group_id: str,
    cookies_file: str,
    fb_cookies: str
) -> dict:
    """
    Detect possible pump signals for a specific coin.
    """
    try:
        # Sentiment
        sentiment_score, sentiment, influencial_post = await sentiment_scores(
            keywords, subreddits, searchcoin, group_id, cookies_file, fb_cookies
        )
        
        if influencial_post:
            engagement_score = influencial_post.get('engagement_score', 0)
            post_time = influencial_post.get('date', 'created_utc')
        else:
            engagement_score = 0
            post_time = "2024-12-08T12:00:00Z"  # example

        # Price & Volume
        binance_price, price_change_percent, volume = get_binance_data(coin_symbol)
        price_score, volume_score, price_increase, volume_spike = assess_price_volume(
            post_time, coin_symbol
        )

        # Historical
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
        print(f"Error in pipeline for {coin_symbol}: {e}")
        return None

def save_trade_to_db(db_path, symbol, side, amount, price, realized_pnl=0.0):
    """
    Create 'trades' table if it doesn't exist,
    then save a trade record to the database.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create table if needed (adjust columns as you prefer)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        amount REAL,
        price REAL,
        timestamp TEXT,
        realized_pnl REAL
    )
    """
    cur.execute(create_table_query)

    # Insert a new row for the trade
    insert_query = """
    INSERT INTO trades (symbol, side, amount, price, timestamp, realized_pnl)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(insert_query, (symbol, side, amount, price, timestamp_str, realized_pnl))
    conn.commit()
    conn.close()
    
    
async def trade_execution(
    client: Client,
    historical_score: float,
    total_score: float,
    coin_symbol: str,
    price_increase: float
):
    """
    Execute trade if final check says "buy," then save trade info to database.
    """
    try:
        open_positions = 1 #get_open_positions(client) or 1
        if not isinstance(open_positions, (int, float)):
            print("open_positions is not a number. Default to 0.")
            open_positions = 1

        portfolio_balance = get_portfolio_balance(client, "USDT")
        if not isinstance(portfolio_balance, (int, float)):
            raise ValueError("Portfolio balance is not valid.")

        # Figure out how many coins to buy
        trade_amount = calculate_trade_amount(
            historical_score, total_score, portfolio_balance, open_positions
        )
        if not isinstance(trade_amount, (int, float)):
            raise ValueError("Trade amount is not valid.")

        # Decide if we actually buy
        can_buy = decide_to_buy(historical_score, total_score, price_increase=price_increase)
        if can_buy:
            # Execute the buy trade
            order = execute_trade(client, trade_amount, coin_symbol)
            print("Trade executed:", order)
            await send_notification(f"Trade executed: {order}")

            # Extract details to store in DB.
            # Here, we assume it's always a "BUY," but adapt for SELL if you do short trades.
            traded_symbol = coin_symbol
            side = "BUY"
            amount = trade_amount

            # We try to get a fill price from order data. If unavailable, default to 0.0
            price = 0.0
            if order and "fills" in order and len(order["fills"]) > 0:
                price = float(order["fills"][0].get("price", 0))

            # Now save the trade info to the SQLite database
            save_trade_to_db(DB_PATH, traded_symbol, side, amount, price, realized_pnl=0.0)

        else:
            await send_notification(f"No buy signal for {coin_symbol}.")
    except Exception as e:
        print(f"Trade execution failed: {e}")
        await send_notification(f"Trade execution failed: {e}")

import asyncio

async def main():
    # Constants
    group_id = "565383300477194"
    cookies_file = "SOCIALBOTS/cookies.json"
    fb_cookies = "SOCIALBOTS/fbcookies.json"
    
    # Fetch coin list
    coin_list = get_top_100_coins() or ["pump", "moon", "100x", "buy now", "HODL", "FOMO", "next big thing"]
    subreddits = ["CryptoCurrency", "CryptoMoonShots", "altcoin"]
    
    # Initialize Binance client
    client = await initialize_testnet_client(API_KEY, API_SECRET)
    synchronize_time(client)

    pumped_coins = {}
    
    print("Checking each coin for a pump signal. Please wait...")
    
    async def process_coin(symbol):
        try:
            coin_symbol = symbol + "USDT"
            results = await run_pump_detection_pipeline(
                coin_list, subreddits, coin_symbol, symbol, group_id, cookies_file, fb_cookies
            )
            if results:
                total_score = mainscore(symbol=coin_symbol, interval="1h", limit=500)
                price_increase = results["price_analysis"]["price_increase"]
                if total_score > 10 or price_increase > 10:
                    return {
                        "symbol": symbol,
                        "results": results,
                        "total_score": total_score,
                        "price_increase": price_increase,
                    }
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
        return None

    # Process all coins concurrently
    tasks = [process_coin(symbol) for symbol in coin_list]
    results = await asyncio.gather(*tasks)
    
    # Filter out None results
    pumped_coins = {res["symbol"]: res for res in results if res}

    if not pumped_coins:
        print("No pumps detected.")
        return

    print("Pumped coins found:")
    for coin in pumped_coins:
        print(f" - {coin}")
    
    # Auto-trade concurrently
    async def auto_trade(symbol, coin_data):
        try:
            coin_symbol = symbol + "USDT"
            print(f"\nAuto-trading for {coin_symbol} ...")
            await trade_execution(
                client,
                coin_data["results"]["historical_score"],
                coin_data["total_score"],
                coin_symbol,
                coin_data["price_increase"],
            )
        except Exception as e:
            print(f"Error auto-trading {symbol}: {e}")

    trade_tasks = [auto_trade(symbol, data) for symbol, data in pumped_coins.items()]
    await asyncio.gather(*trade_tasks)

    print("Done auto-trading all pumped coins!")

if __name__ == "__main__":
    asyncio.run(main())
