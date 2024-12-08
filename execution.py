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


def check_connectivity(client: Client) -> bool:
    """
    Check server connectivity by pinging the endpoint.
    Returns True if successful, False otherwise.
    """
    try:
        client.ping()
        return True
    except Exception as e:
        print(f"Connectivity check failed: {e}")
        return False


def get_portfolio_balance(client: Client, coin: str) -> float:
    """
    Fetch and return the balance of a specific coin from the Binance Testnet account.
    :param client: Binance client object
    :param coin: The coin symbol to check the balance for (e.g., 'USDT')
    :return: Balance as a float
    """
    try:
        account_info = client.get_account()
        balances = account_info.get('balances', [])
        # Filter the specific coin balance
        for balance in balances:
            if balance['asset'] == coin:
                print(f"--------Account Balance for {coin}: {float(balance['free'])}")
                return float(balance['free'])
        print(f"No balance found for {coin}.")
        return 0.0
    except Exception as e:
        print(f"Failed to fetch portfolio balance for {coin}: {e}")
        return 0.0


def get_open_positions(client: Client) -> dict:
    """
    Fetch and return the current open positions from Binance Futures Testnet.
    """
    try:
        # Fetch account futures positions
        positions = client.get_open_orders()
        
        # Extract and filter non-zero positions
        open_positions = [
            {
                "symbol": position['symbol'],
                "positionAmt": float(position['positionAmt']),
                "entryPrice": float(position['entryPrice']),
                "unRealizedProfit": float(position['unRealizedProfit'])
            }
            for position in positions['positions']
            if float(position['positionAmt']) != 0
        ]
        
        print(f"Open Positions: {open_positions}")
        return open_positions
    except Exception as e:
        print(f"Failed to fetch open positions: {e}")
        return {"error": str(e)}


def execute_trade(
    client: Client, 
    symbol: str = "BTCUSDT", 
    amount: float = 0.001, 
    side=SIDE_BUY, 
    order_type=ORDER_TYPE_MARKET
) -> dict:
    """
    Executes a market order for a given symbol and amount on Binance Testnet.
    Handles exceptions and returns either the order response or error details.
    """
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=amount
        )
        return order
    except Exception as e:
        print(f"Order execution failed: {e}")
        return {"error": str(e)}


def main():
    """
    Main driver function to initialize the client, check connectivity,
    execute a trade, fetch portfolio balance and open positions.
    """
    # Initialize Binance Testnet client
    client = initialize_testnet_client(api_key, api_secret)

    # Check connectivity
    if not check_connectivity(client):
        return {"error": "Cannot connect to Binance Testnet."}

    # Fetch portfolio balance
    print("\nFetching portfolio balance...")
    portfolio_balance = get_portfolio_balance(client,'USDT')

    # Fetch open positions
    print("\nFetching open positions...")
    open_positions = get_open_positions(client)

    # Execute a test trade
    print("\nExecuting a test trade...")
    trade_response = execute_trade(
        client,
        symbol="BTCUSDT",
        amount=0.001
    )
    print(f"Trade Response: {trade_response}")

    # Return results
    return {
        "portfolio_balance": portfolio_balance,
        "open_positions": open_positions,
        "trade_response": trade_response
    }


if __name__ == "__main__":
    main()
