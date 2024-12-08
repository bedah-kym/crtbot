from .redditbot import redditposts
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


def parse_posts(posts):
    """
    Parses and prints the fetched posts.

    :param posts: List of dictionaries representing Reddit posts
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
    # VADER's 'compound' score ranges from -1 (negative) to +1 (positive)
    # Transform it to [0,1] range
    sentiment = (scores['compound'] + 1) / 2.0  
    # Example categorization
    if sentiment > 0.66:
        sentiment_category = 'Positive'
    elif sentiment < 0.34:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Neutral'
    return sentiment, sentiment_category


def analyze_sentiments(posts):
    """
    Analyzes sentiments of a list of Reddit posts.

    :param posts: List of dictionaries representing Reddit posts
    :return: Average sentiment score
    """
    analyzer = SentimentIntensityAnalyzer()
    total_sentiment = 0
    for post in posts:
        # Concatenate the title and any additional text (if available)
        post_text = post.get('title', '') + ' ' + post.get('selftext', '')
        sentiment, category = compute_sentiment_score(post_text, analyzer)
        print(f"Post: {post['title']}")
        print(f"Sentiment Score: {sentiment:.2f} ({category})\n")
        total_sentiment += sentiment
    average_sentiment = total_sentiment / len(posts) if posts else 0
    return average_sentiment
    
     
def sentiment_scores():
    parsed_posts=parse_posts(redditposts("bitcoin","CryptoCurrency",10))
    sentiment = analyze_sentiments(parsed_posts)
    if sentiment > 0.66:
        sentiment_category = 'Positive'
    elif sentiment < 0.34:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Neutral'

    # Return both sentiment score and category
    return sentiment, sentiment_category

#sentiment_scores()