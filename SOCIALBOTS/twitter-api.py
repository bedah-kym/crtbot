import tweepy 
from dotenv import load_dotenv
import os

load_dotenv()

# Replace these with your own API credentials
API_KEY = os.environ.get("XAPI_KEY")
API_SECRET_KEY = os.environ.get("XAPI_SECRET_KEY")
ACCESS_TOKEN = os.environ.get("XACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("XACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("XBEARER_TOKEN")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def search_tweets_with_metrics(keywords_list, max_results=10):
    try:
        # Construct the query by joining keywords with 'OR'
        query = ' OR '.join(keywords_list)
        # Optionally, exclude retweets and replies
        query += ' -is:retweet -is:reply lang:en'
        # Search recent tweets containing any of the keywords
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['id', 'text', 'public_metrics', 'created_at', 'author_id', 'lang']
        )
        return response.data
    except tweepy.TweepyException as e:
        print(f"Error searching tweets: {e}")
        return []

def main():
    # Define your list of keywords
    keywords = ['crypto', 'bitcoin', 'ethereum', 'blockchain', '#crypto']
    # Remove duplicates and strip whitespace
    keywords = list(set(keyword.strip() for keyword in keywords))
    
    # Adjust max_results as needed (maximum 100)
    tweets = search_tweets_with_metrics(keywords, max_results=10)
    
    if tweets:
        for tweet in tweets:
            metrics = tweet.public_metrics
            print(f"Tweet ID: {tweet.id}")
            print(f"Author ID: {tweet.author_id}")
            print(f"Created At: {tweet.created_at}")
            print(f"Tweet Text: {tweet.text}")
            print("Engagement Metrics:")
            print(f"  Retweet Count: {metrics['retweet_count']}")
            print(f"  Reply Count: {metrics['reply_count']}")
            print(f"  Like Count: {metrics['like_count']}")
            print(f"  Quote Count: {metrics['quote_count']}")
            print("-" * 50)
    else:
        print("No tweets found.")

if __name__ == '__main__':
    main()

