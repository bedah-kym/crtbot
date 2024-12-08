# Bot Documentation: crtbot

## Overview
**crtbot** is designed to analyze cryptocurrency-related data from various sources, such as social media posts, market data, and historical trends, to detect potential pump-and-dump schemes and assist users in making informed decisions. The bot integrates multiple components for data analysis, sentiment evaluation, and market insights.

---

## Core Components

### 1. **mainscript.py**
**Main Pipeline:**
- **Function:** `run_pump_detection_pipeline`
- **Purpose:** Executes the entire detection process, integrating data collection, sentiment analysis, and market evaluation.
- **Pipeline Steps:**
  1. **Engagement Metrics:** Calculates engagement scores based on the text content of posts.
  2. **Price & Volume Analysis:** Analyzes cryptocurrency price and volume trends to detect anomalies.
  3. **Sentiment Analysis:** Evaluates the sentiment of social media posts.
  4. **Historical Data Analysis:** Compares current data against historical trends to detect unusual activity.
- **Inputs:**
  - `post_text`: Social media or forum post content.
  - `post_price`: The price mentioned in the post.
  - `post_time`: Timestamp of the post.
  - `coin_symbol` (default: `BTCUSDT`): Cryptocurrency pair.
  - `portfolio_balance` (default: `1000`): User's portfolio balance.

---

### 2. **decision.py**
**Data Retrieval and Decision Logic:**
- **Binance API Integration:**
  - `get_binance_data(symbol="BTCUSDT")` fetches live market data, including:
    - Current price.
    - Price change percentage.
    - Trading volume.
- **Price & Volume Assessment:**
  - `assess_price_volume(post_price, post_time, symbol="BTCUSDT")`
  - Compares reported prices in posts with live market data to validate authenticity and detect significant movements.

---

### 3. **analysis.py**
**Sentiment and Statistical Analysis:**
- **Sentiment Analysis:**
  - Utilizes NLTK's VADER for analyzing text sentiment.
  - `compute_sentiment_score(post_text)` outputs a normalized sentiment score (`0-1`).
  - Flags posts with strong positive or negative sentiments as potential indicators of manipulation.
- **Statistical Tools:**
  - References to Python's `statistics` module suggest it supports data normalization and anomaly detection.

---

### 4. **Database (db.sqlite3)**
Stores structured data for:
- Historical analysis.
- Tracking detected anomalies and flagged posts.
- User interactions or bot decisions.

---

### 5. **Configuration Files**
- `.env`: Contains environment variables, such as API keys and configuration details.
- `.gitignore`: Specifies files to exclude from version control (e.g., sensitive information).

---

## Additional Features
### Social Media Bots (SOCIAL-BOTS Directory)
Likely contains modules for integrating social media data, enabling:
- Post scraping.
- Real-time engagement tracking.
- Social trend analysis.

---

## Expected Functionality When Completed
1. **Real-Time Market Analysis:** Continuously fetch and analyze market data.
2. **Social Media Monitoring:** Scrape posts, evaluate sentiment, and detect anomalies in engagement patterns.
3. **Alert System:** Notify users of potential pump-and-dump schemes based on:
   - Abnormal price and volume spikes.
   - Overly positive/negative sentiment.
4. **Decision Support:** Provide actionable insights for user portfolio management.

---

## How to Run the Bot Locally

### Prerequisites
1. **Python Installation:** Ensure Python 3.8 or later is installed on your machine.
2. **Virtual Environment:** (Optional) Set up a virtual environment for the project:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. **Dependencies:** Install required Python packages. Use the `requirements.txt` file (if available) or install packages manually:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   - Create a `.env` file in the project directory with the necessary environment variables, such as API keys for Binance and other configurations.

### Steps to Run
1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd X-API
   ```
2. **Database Setup:** Ensure `db.sqlite3` is in the project root. If not, initialize the database (if a migration script is available).
3. **Run the Main Script:** Execute `mainscript.py` to start the bot:
   ```bash
   python mainscript.py
   ```
4. **Monitor Output:** Check logs or terminal output for real-time analysis results and any alerts.

### Additional Notes
- If using social media integrations, ensure required tokens or API credentials are configured.
- Test the pipeline with sample inputs to validate functionality before deployment.

---

## Areas for Development
1. **User Interface:**
   - Add a dashboard for real-time updates and alerts.
   - Implement input forms for user-defined parameters.
2. **Enhanced Analytics:**
   - Integrate machine learning models for advanced anomaly detection.
   - Expand historical data analysis capabilities.
3. **Scalability:**
   - Ensure the bot can handle multiple users and a variety of cryptocurrency pairs.
   - Optimize performance for large-scale data ingestion.



