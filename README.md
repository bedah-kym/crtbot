# **Bot Documentation: CRTBot**

---

## **Overview**
**CRTBot** is a powerful cryptocurrency analysis bot designed to detect potential pump-and-dump schemes and assist users in making informed decisions. It analyzes data from multiple sources, including social media, market trends, and historical records, using advanced sentiment evaluation and market insights.

---

## **Core Components**

### **1. Main Script (`mainscript.py`)**
**Purpose:** Serves as the primary pipeline for running all bot functionalities.

#### **Key Function:**
- **`run_pump_detection_pipeline`**
  - Integrates multiple modules to detect market anomalies and analyze social media trends.

#### **Pipeline Steps:**
1. **Engagement Metrics:** Analyzes post engagement to flag potential manipulative content.
2. **Price & Volume Analysis:** Examines cryptocurrency price and trading volume for anomalies.
3. **Sentiment Analysis:** Assesses post sentiment to identify manipulation signals.
4. **Historical Data Analysis:** Compares data with historical trends for unusual activity detection.

#### **Inputs:**
- **`post_text`**: Content of social media or forum posts.
- **`post_price`**: Cryptocurrency price mentioned in the post.
- **`post_time`**: Timestamp of the post.
- **`coin_symbol`** (default: `BTCUSDT`): Target cryptocurrency pair.
- **`portfolio_balance`** (default: `1000`): User's portfolio balance.

---

### **2. Decision Module (`decision.py`)**
**Purpose:** Fetches market data and applies decision logic.

#### **Key Features:**
- **Binance API Integration:**
  - Fetches live cryptocurrency data (price, volume, price change percentage).
- **Price & Volume Assessment:**
  - Validates post data against real-time market conditions.

#### **Main Functions:**
- **`get_binance_data(symbol="BTCUSDT")`**
- **`assess_price_volume(post_price, post_time, symbol="BTCUSDT")`**

---

### **3. Analysis Module (`analysis.py`)**
**Purpose:** Conducts sentiment and statistical analysis.

#### **Key Features:**
- **Sentiment Analysis:**
  - Uses NLTK's VADER for text sentiment scoring.
  - Flags extreme sentiment posts for potential manipulation.
- **Statistical Analysis:**
  - Detects anomalies and normalizes data using Python's `statistics` module.

---

### **4. Database (`db.sqlite3`)**
**Purpose:** Stores and manages structured data.

#### **Usage:**
- Logs historical data for trend analysis.
- Tracks detected anomalies and flagged posts.

---

### **5. Configuration Files**
- **`.env`:** Contains sensitive configuration data (API keys, bot settings).
- **`.gitignore`:** Ensures sensitive files are excluded from version control.

---

### **6. Social Media Integration (`SOCIAL-BOTS` Directory)**
**Purpose:** Scrapes and analyzes social media data in real-time.

#### **Capabilities:**
- Post scraping and engagement tracking.
- Analysis of social media trends.

---

## **Features**
1. **Real-Time Market Analysis:** Continuously analyzes cryptocurrency market data.
2. **Social Media Monitoring:** Tracks and evaluates social media sentiment and trends.
3. **Alert System:** Notifies users of potential market manipulation based on:
   - Abnormal price/volume changes.
   - Strong sentiment spikes.
4. **Decision Support:** Provides actionable insights for user portfolio management.

---

## **How to Run the Bot Locally**

### **Prerequisites**
1. **Python Installation:** Ensure Python 3.8 or later is installed.
2. **Virtual Environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:** Create a `.env` file and set the following:
   - API keys for Binance, Twitter, Facebook, Reddit, Telegram.
   - Cookies for Facebook and Twitter (saved in `SOCIAL-BOTS/cookies.json` and `SOCIAL-BOTS/fb_cookies.json`).
   - Telegram credentials (e.g., `BOT_TOKEN`, `CHAT_ID`, etc.).
   - Database path (`DB_PATH`).

### **Setup Binance Tokens**
- Use testnet credentials for testing or mainnet credentials for real trades.

---

### **Run the Bot**
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/betaways01/crt-bot
   cd crt-bot
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **Initialize the Database:** Ensure `db.sqlite3` exists in the project root.
3. **Run the Bot:**
   ```bash
   python mainscript.py
   ```
4. **Monitor Output:** Observe the console for real-time logs and alerts.

---

## **Customization**
Modify the following parameters in `mainscript.py`:
- **Social Media:**
  - `group_id`: Facebook group ID.
  - `cookies_file`: Path to Twitter cookies.
  - `fb_cookies`: Path to Facebook cookies.
- **Cryptocurrency:**
  - `coin_symbol`: Target cryptocurrency pair (e.g., `ADAUSDT`).
  - `searchcoin`: Coin to monitor in social media posts.
- **Keywords:** Add or update keywords for post analysis.
- **Subreddits:** Add subreddits to monitor (e.g., `CryptoMoonShots`).

---

## **Areas for Future Development**
1. **User Interface:**
   - Add a web dashboard for monitoring and customization.
2. **Advanced Analytics:**
   - Incorporate machine learning models for anomaly detection.
3. **Scalability:**
   - Optimize for handling multiple users and data streams.

---
