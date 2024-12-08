from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('TEST_API_KEY')
api_secret = os.environ.get('TEST_SECRET')

def execute_trade(symbol="BTCUSDT", amount=0.001, api_key="", api_secret=""):
    client = Client(api_key, api_secret)
    # Market buy order
    order = client.create_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=amount
    )
    return order

def execute_trade_testnet(api_key, api_secret,symbol="BTCUSDT", amount=0.001):
    # Initialize client for Testnet
    client = Client(api_key, api_secret)
    client.API_URL = 'https://testnet.binance.vision/api'  # Testnet URL
    
    # Check server time synchronization
    try:
        client.ping() 
    except Exception as e:
        return {"error": f"Connectivity issue: {str(e)}"}
    
    # Attempt the trade
    try:
        order = client.create_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=amount
        )
        return order
    except Exception as e:
        return {"error": str(e)}

print(execute_trade_testnet(api_key,api_secret))

