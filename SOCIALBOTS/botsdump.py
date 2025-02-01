import asyncio
from .redditbot import redditposts
from .telegrambot2 import TelegramPosts, send_notification
from .Xbot import Xposts
from .fbapi import search_posts
import nltk
import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def parse_posts(posts):
    """
    Parses and prints the fetched posts.
    """
    parsed_posts = []
    for i, post in enumerate(posts, 1):
        parsed_posts.append(post)
    return parsed_posts

def compute_sentiment_score(post_text, analyzer):
    """
    Computes the sentiment score of a given text.
    """
    scores = analyzer.polarity_scores(post_text)
    sentiment = (scores['compound'] + 1) / 2.0  # range [0, 1]
    if sentiment >= 0.75:
        sentiment_category = 'Very Positive'
    elif sentiment >= 0.5:
        sentiment_category = 'Positive'
    elif sentiment <= 0.25:
        sentiment_category = 'Very Negative'
    elif sentiment <= 0.5:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Neutral'
    return sentiment, sentiment_category

def analyze_sentiments(posts):
    """
    Analyzes sentiments of a list of posts using engagement score as weight.
    """
    analyzer = SentimentIntensityAnalyzer()
    total_weighted_sentiment = 0
    total_engagement = 0

    # For normalization
    max_engagement = max([p.get('engagement_score', 0) for p in posts], default=1)

    for post in posts:
        post_text = post.get('title', 'group_name') + ' ' + post.get('selftext', 'message')
        sentiment, category = compute_sentiment_score(post_text, analyzer)

        engagement_score = post.get('engagement_score', 0)
        normalized_engagement = engagement_score / max_engagement if max_engagement else 0

        weighted_sentiment = sentiment * normalized_engagement
        total_weighted_sentiment += weighted_sentiment
        total_engagement += normalized_engagement

        # Print info for debug
        if 'title' in post and post['title']:
            print(f"Post: {post['title']}")
        elif 'message' in post and post['message']:
            print(f"Message: {post['message']}")
        else:
            print(f"Tweet: {post.get('Tweet', '')}")

        print(f"Sentiment Score: {sentiment:.2f} ({category}), Engagement Score: {engagement_score:.2f}\n")

    if total_engagement == 0:
        return 0
    average_sentiment = total_weighted_sentiment / total_engagement
    return average_sentiment

async def sentiment_scores(keywords, subreddits, coin, group_id, cookies_file, fb_cookies):
    """
    Runs each bot in sequence (Telegram, Reddit, X/Twitter, Facebook), 
    combines all posts, writes to a file, sends file to Telegram, 
    and returns sentiment info.
    """

    # 1) Run bots one by one instead of all at once
    print("Running Telegram bot...")
    telegram_data = await TelegramPosts()
    telegram_posts = parse_posts(telegram_data)
    print("Telegram bot finished.\n")

    print("Running Reddit bot...")
    reddit_data = await redditposts(keywords, subreddits, 10)
    reddit_posts_parsed = parse_posts(reddit_data)
    print("Reddit bot finished.\n")

    print("Running X (Twitter) bot...")
    twitter_data = await Xposts(keywords, cookies_file)
    twitter_posts = parse_posts(twitter_data)
    print("X bot finished.\n")

    print("Running Facebook bot...")
    facebook_data = await search_posts(group_id, keywords, fb_cookies)
    facebook_posts = parse_posts(facebook_data)
    print("Facebook bot finished.\n")

    # 2) Combine posts
    parsed_posts = telegram_posts + reddit_posts_parsed + twitter_posts + facebook_posts

    # 3) Write all posts to a text file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"POSTDATA/{timestamp}.txt"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            for post in parsed_posts:
                f.write(str(post) + "\n")
        print(f"All posts saved to {file_name}")
    except Exception as e:
        print(f"Failed to write posts to file: {e}")

    # 4) Send file name to Telegram
    """try:
        await send_notification(file_name)
        print(f"Post lists File {file_name} sent to Telegram bot.")
    except Exception as e:
        print(f"Failed to send file to Telegram: {e}")"""

    # 5) Filter posts containing the coin
    filtered_posts = [
        post for post in parsed_posts
        if coin.lower() in post.get('selftext', '').lower()
           or coin.lower() in post.get('message', '').lower()
    ]

    # 6) Find the post with the highest engagement
    highest_engagement_post = max(
        filtered_posts,
        key=lambda x: x.get('engagement_score', 0),
        default=None
    )

    if highest_engagement_post is None:
        print(f"No posts found mentioning {coin} with engagement scores.")
        return 0, 'Neutral', None

    print(f"Highest Engagement Post: {highest_engagement_post}")

    # 7) Analyze sentiment
    sentiment = analyze_sentiments(parsed_posts)
    if sentiment >= 0.80:
        sentiment_category = 'Very Positive'
    elif sentiment >= 0.60:
        sentiment_category = 'Positive'
    elif sentiment >= 0.40:
        sentiment_category = 'Neutral'
    elif sentiment >= 0.20:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Very Negative'

    return sentiment, sentiment_category, highest_engagement_post

# Example usage
if __name__ == "__main__":
    group_id = "1766546466973495"
    fb_cookies = "SOCIALBOTS/fbcookies.json"
    cookies_file = "SOCIALBOTS/cookies.json"

    coin = "BTC"
    keywords = [coin, "pump", "moon", "100x", "buy now", "HODL", "FOMO", "next big thing"]
    subreddits = ["CryptoCurrency", "CryptoMoonShots", "altcoin"]

    asyncio.run(sentiment_scores(keywords, subreddits, coin, group_id, cookies_file, fb_cookies))
