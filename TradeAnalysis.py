#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta

# Change this to the path of your SQLite database
DB_PATH = "db.sqlite3"

def get_recent_trades(db_path, hours=24):
    """
    Fetch all trades made in the last `hours` hours (default: 24).
    Adjust column names and timestamp storage based on how your DB is set up.
    """
    # Calculate the cutoff time (for example, 24 hours ago)
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Convert to string if your 'timestamp' column is stored as text in ISO format
    # If your timestamp is stored as an integer (epoch), adjust this query
    cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Example table structure: trades(symbol TEXT, side TEXT, amount REAL, price REAL, timestamp TEXT, realized_pnl REAL)
    # The query checks for trades where the timestamp is newer than `cutoff_str`
    query = """
    SELECT symbol, side, amount, price, timestamp, realized_pnl
    FROM trades
    WHERE timestamp >= ?
    ORDER BY timestamp ASC
    """
    cur.execute(query, (cutoff_str,))
    trades = cur.fetchall()

    con.close()
    return trades

def analyze_trades(trades):
    """
    Compute total PnL (profit/loss), number of trades, etc. 
    Customize to your own needs.
    """
    total_pnl = 0.0
    for trade in trades:
        # If your realized_pnl can be None or missing, handle that
        # Example: trade = (symbol, side, amount, price, timestamp, realized_pnl)
        realized_pnl = trade[5] if trade[5] else 0.0
        total_pnl += realized_pnl

    total_trades = len(trades)
    return total_pnl, total_trades

def print_trade_summary(trades, total_pnl, total_trades, hours=24):
    """
    Print a summary of trades and profit/loss in the terminal.
    """
    print(f"Trade Summary for Last {hours} Hours")
    print("-" * 40)

    if total_trades == 0:
        print("No trades found in this period.")
        return

    for trade in trades:
        symbol, side, amount, price, tstamp, pnl = trade
        print(f"Time: {tstamp} | {symbol} | {side} | Amount: {amount} | Price: {price} | PnL: {pnl}")

    print("-" * 40)
    print(f"Total Trades: {total_trades}")
    print(f"Total PnL: {total_pnl:.2f}")
    print("-" * 40)

def save_summary_to_file(trades, total_pnl, total_trades, filename="daily_trade_report.txt", hours=24):
    """
    Write the summary to a text file.
    """
    with open(filename, "w") as f:
        f.write(f"Trade Summary for Last {hours} Hours\n")
        f.write("-" * 40 + "\n")

        if total_trades == 0:
            f.write("No trades found in this period.\n")
            return

        for trade in trades:
            symbol, side, amount, price, tstamp, pnl = trade
            line = (
                f"Time: {tstamp} | {symbol} | {side} | "
                f"Amount: {amount} | Price: {price} | PnL: {pnl}\n"
            )
            f.write(line)

        f.write("-" * 40 + "\n")
        f.write(f"Total Trades: {total_trades}\n")
        f.write(f"Total PnL: {total_pnl:.2f}\n")
        f.write("-" * 40 + "\n")

    print(f"Summary written to {filename}.")

def main():
    # 1) Fetch trades from the last 24 hours
    trades = get_recent_trades(DB_PATH, hours=24)

    # 2) Analyze trades
    total_pnl, total_trades = analyze_trades(trades)

    # 3) Print summary in terminal
    print_trade_summary(trades, total_pnl, total_trades, hours=24)

    # 4) Save summary to a text file
    save_summary_to_file(trades, total_pnl, total_trades)

    # 5) Optionally, you can send this file via Telegram/email
    #    For example, if you have a function send_notification(file_name),
    #    you could do: send_notification("daily_trade_report.txt")

if __name__ == "__main__":
    main()
