import asyncio
from .redditbot import redditposts
from .telegrambot2 import TelegramPosts
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
        else:
            print(f"Message: {post['message']}")
        print(f"Sentiment Score: {sentiment:.2f} ({category}), Engagement Score: {engagement_score:.2f}\n")

    # Calculate weighted average sentiment
    average_sentiment = total_weighted_sentiment / total_engagement if total_engagement else 0
    return average_sentiment
    
     
async def sentiment_scores():
    keywords=["pump","moon","100x","buy now","HODL","FOMO","next big thing"]
    subreddits=["CryptoCurrency", "CryptoMoonShots", "altcoin"]
    
    telegram_posts = parse_posts(await TelegramPosts())
    reddit_posts = parse_posts(redditposts(keywords,subreddits, 10))

    # Combine posts and ensure engagement scores are included
    parsed_posts = telegram_posts + reddit_posts

    sentiment = analyze_sentiments(parsed_posts)

    if sentiment > 0.56:
        sentiment_category = 'Positive'
    elif sentiment < 0.34:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Neutral'

    # Return both sentiment score and category
    return sentiment, sentiment_category

if __name__ == "__main__":
    asyncio.run(sentiment_scores())
