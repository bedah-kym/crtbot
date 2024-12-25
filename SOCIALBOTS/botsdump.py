import asyncio
from .redditbot import redditposts
from .telegrambot2 import TelegramPosts
from .Xbot import Xposts
from .fbapi import search_posts
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


def parse_posts(posts):
    """
    Parses and prints the fetched posts.

    :param posts: List of dictionaries representing posts
    """
    parsed_posts = []
    for i, post in enumerate(posts, 1):
        parsed_posts.append(post)
    return parsed_posts
     
def compute_sentiment_score(post_text, analyzer):
    """
    Computes the sentiment score of a given text.

    :param post_text: Text to analyze
    :param analyzer: SentimentIntensityAnalyzer instance
    :return: Tuple of sentiment score and sentiment category
    """
    scores = analyzer.polarity_scores(post_text)
    sentiment = (scores['compound'] + 1) / 2.0  # Transform to [0, 1] range
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
    Analyzes sentiments of a list of posts, using engagement score as weight.

    :param posts: List of dictionaries representing posts
    :return: Weighted average sentiment score
    """
    analyzer = SentimentIntensityAnalyzer()
    total_weighted_sentiment = 0
    total_engagement = 0

    for post in posts:
        post_text = post.get('title', 'group_name') + ' ' + post.get('selftext', 'message') 
        sentiment, category = compute_sentiment_score(post_text, analyzer)

        # Normalize engagement score to [0, 1]
        engagement_score = post.get('engagement_score', 0)
        max_engagement = max([p.get('engagement_score', 0) for p in posts], default=1)
        normalized_engagement = engagement_score / max_engagement if max_engagement else 0

        weighted_sentiment = sentiment * normalized_engagement
        total_weighted_sentiment += weighted_sentiment
        total_engagement += normalized_engagement

        if 'title' in post and post['title']:
            print(f"Post: {post['title']}")
            
        elif 'message' in post and post['message']:
            print(f"Message: {post['message']}")
        else:
            print(f"Tweet: {post['Tweet']}")
             
        print(f"Sentiment Score: {sentiment:.2f} ({category}), Engagement Score: {engagement_score:.2f}\n")

    # Calculate weighted average sentiment
    average_sentiment = total_weighted_sentiment / total_engagement if total_engagement else 0
    return average_sentiment
    
     
async def sentiment_scores(keywords, subreddits, coin,group_id, cookies_file, fb_cookies):
    # Fetch posts
    telegram_posts = parse_posts(await TelegramPosts())
    reddit_posts = parse_posts(await redditposts(keywords, subreddits, 10))
    twitter_posts = parse_posts(await Xposts(keywords, cookies_file)) 
    facebook_posts = parse_posts(await search_posts(group_id, keywords, fb_cookies))

    # Combine posts
    parsed_posts = telegram_posts + reddit_posts + twitter_posts +facebook_posts

    # Filter posts containing the coin
    filtered_posts = [
        post for post in parsed_posts 
        if coin.lower() in post.get('selftext', '').lower() or coin.lower() in post.get('message', '').lower()
    ]

    # Find the post with the highest engagement
    highest_engagement_post = max(
        filtered_posts, 
        key=lambda x: x.get('engagement_score', 0), 
        default=None
    )

    if highest_engagement_post is None:
        print("No posts found with engagement scores for the given coin.")
        return 0, 'Neutral', None

    print(f"Highest Engagement Post: {highest_engagement_post}")

    # Analyze sentiments
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

if __name__ == "__main__":
    
    group_id = "1766546466973495"  # Example group ID
    fb_cookies = "SOCIALBOTS/fbcookies.json"
    cookies_file = "SOCIALBOTS/cookies.json"

    coin = "BTC"
    keywords=[coin,"pump","moon","100x","buy now","HODL","FOMO","next big thing"]
    subreddits=["CryptoCurrency", "CryptoMoonShots", "altcoin"]
    
    asyncio.run(sentiment_scores(keywords,subreddits,coin,group_id,cookies_file,fb_cookies))
