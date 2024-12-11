import os
import logging
import praw
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_reddit_instance():
    """
    Initialize and return a Reddit instance using credentials from environment variables.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not client_id or not client_secret or not user_agent:
        logging.error("Reddit API credentials are not set in environment variables.")
        raise Exception("Reddit API credentials are missing.")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    logging.info("Reddit instance created successfully.")
    return reddit

def search_subreddits(keyword, subreddit_names, limit=50):
    """
    Search for crypto-related pump-and-dump activity.

    :param keyword: The keyword or phrase to search for.
    :param subreddit_names: List of subreddits to search in.
    :param limit: Number of results to retrieve.
    :return: List of relevant posts.
    """
    try:
        reddit = get_reddit_instance()

        # Combine subreddits into a single query
        subreddit_query = "+".join(subreddit_names)
        subreddit = reddit.subreddit(subreddit_query)
        logging.info(f"Searching for pumps in subreddits: {subreddit_query}")

        # Perform the search
        search_results = subreddit.search(
            keyword,
            limit=limit,
            sort="new",  # Prioritize new posts
            time_filter="day"  # Posts from the last hour
        )
        logging.info(f"Search completed for keyword: '{keyword}'")

        # Collect relevant results
        posts = []
        for post in search_results:
            # Calculate engagement score
            engagement_score = post.score + len(post.comments)
            posts.append({
                "title": post.title,
                "url": post.url,
                "score": post.score,
                "num_comments": len(post.comments),
                "author": str(post.author),
                "created_utc": post.created_utc,
                "engagement_score": engagement_score,
            })

        logging.info(f"Total posts retrieved: {len(posts)}")
        return posts

    except Exception as e:
        logging.exception("An error occurred while searching subreddits.")
        return []


def calculate_engagement_score(post):
    upvotes = post.score
    comments = post.num_comments
    awards = getattr(post, 'total_awards_received', 0)
    
    # Calculate post age in hours
    post_age_seconds = datetime.now(timezone.utc).timestamp() - post.created_utc
    post_age_hours = post_age_seconds / 3600

    # Engagement score formula
    engagement_score = (upvotes * 1.5) + (comments * 2) + (awards * 3) - (post_age_hours * 0.1)
    return round(engagement_score, 2)

def redditposts(keyword,subreddit_input,limit_input):
    
    # Parse limit
    try:
        limit = int(limit_input)
    except ValueError:
        logging.error("Invalid input for limit. Defaulting to 10.")
        limit = 10

    # Parse subreddit names
    subreddit_names = [s.strip() for s in subreddit_input]

    # Perform search
    results = search_subreddits(keyword, subreddit_names, limit)

    # Display results
    return results


if __name__ == "__main__":
    keywords=["pump","moon","100x","buy now","HODL","FOMO","next big thing"]
    subreddits=["CryptoCurrency", "CryptoMoonShots", "altcoin"]
    print(redditposts(keywords,subreddits,"10"))
