import tweepy

# Replace these with your own API credentials
API_KEY = 'VMeJHtj4JGvK1X3MUtxdUgD73'
API_SECRET_KEY = 'g6dQCwILwnda2UCUqPB6DenBLtN7dZi6BmC8wgQQX2PAql0WSo'
ACCESS_TOKEN = '1418135869144412161-YqNybjOA6v7Un33pzjJwSDTVX419pX'
ACCESS_TOKEN_SECRET = 'L261VplHeWXiHlkGCRqeI98vDnDUVIV1LZInnPHl1f376'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAEfSxAEAAAAAyqAUEaxsNZOQtHj%2BY2VqXbq4ExU%3DGZaakLMNejvQUDKV27JvAQlOzOuqqE96Vx4k6xUyOXp1wlgNjT'

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








""""
# Set up your credentials
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEfSxAEAAAAAyqAUEaxsNZOQtHj%2BY2VqXbq4ExU%3DGZaakLMNejvQUDKV27JvAQlOzOuqqE96Vx4k6xUyOXp1wlgNjT"

# Initialize the client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def search_tweets_with_retry(keyword, max_results=10, retry_delay=60):
    try:
        # Search for tweets
        response = client.search_recent_tweets(query=keyword, max_results=max_results)
        tweets = response.data

        if tweets:
            print(f"Found {len(tweets)} tweets with keyword '{keyword}':\n")
            for tweet in tweets:
                print(f"Tweet ID: {tweet.id}")
                print(f"Tweet Text: {tweet.text}\n")
        else:
            print(f"No tweets found with keyword '{keyword}'.")

    except tweepy.errors.TooManyRequests as e:
        print("Rate limit exceeded. Waiting for reset...")
        reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + retry_delay))
        sleep_duration = max(reset_time - time.time(), retry_delay)
        time.sleep(sleep_duration)
        # Retry after waiting
        search_tweets_with_retry(keyword, max_results)
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
search_tweets_with_retry("crypto", max_results=15)"""