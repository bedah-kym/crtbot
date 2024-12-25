import os
import logging
import asyncio
from datetime import datetime, timezone
import asyncpraw
import nest_asyncio

# Apply nest_asyncio to prevent event loop conflicts
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def get_reddit_instance():
    """
    Initialize and return an async Reddit instance using credentials from environment variables.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not client_id or not client_secret or not user_agent:
        logging.error("Reddit API credentials are not set in environment variables.")
        raise Exception("Reddit API credentials are missing.")

    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    logging.info("Async Reddit instance created successfully.")
    return reddit


def calculate_engagement_score(post):
    """
    Calculate the engagement score for a post.

    :param post: Reddit post object
    :return: Engagement score
    """
    upvotes = post['score']
    comments = post['num_comments']
    awards = post.get('total_awards_received', 0)

    # Calculate post age in hours
    post_age_seconds = datetime.now(timezone.utc).timestamp() - post['created_utc']
    post_age_hours = post_age_seconds / 3600

    # Engagement score formula
    engagement_score = (upvotes * 1.5) + (comments * 2) + (awards * 3) - (post_age_hours * 0.1)
    return round(engagement_score, 2)


async def search_subreddits(keywords, subreddit_names, limit=50):
    """
    Search for crypto-related pump-and-dump activity using async PRAW.

    :param keyword: The keyword or phrase to search for.
    :param subreddit_names: List of subreddits to search in.
    :param limit: Number of results to retrieve.
    :return: List of relevant posts.
    """
    async with await get_reddit_instance() as reddit:
        try:
            # Combine subreddits into a single query
            subreddit_query = "+".join(subreddit_names)
            subreddit = await reddit.subreddit(subreddit_query)
            logging.info(f"Searching for pumps in subreddits: {subreddit_query}")

            # Perform the search
            search_results = subreddit.search(
                keywords,
                limit=limit,
                sort="new",  # Prioritize new posts
                time_filter="day"  # Posts from the last day
            )
            logging.info(f"Search completed for keywords: '{keywords}'")

            # Collect relevant results
            posts = []
            async for post in search_results:
                engagement_score = calculate_engagement_score({
                    "score": post.score,
                    "num_comments": len(post.comments),
                    "total_awards_received": post.total_awards_received,
                    "created_utc": post.created_utc
                })
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


async def redditposts(keyword, subreddit_input, limit_input):
    """
    Search for Reddit posts using keywords and return results with engagement scores.

    :param keyword: The keyword to search for.
    :param subreddit_input: List of subreddit names.
    :param limit_input: Limit on the number of posts to fetch.
    :return: List of posts with details and engagement scores.
    """
    try:
        limit = int(limit_input)
    except ValueError:
        logging.error("Invalid input for limit. Defaulting to 10.")
        limit = 10

    subreddit_names = [s.strip() for s in subreddit_input]
    results = await search_subreddits(keyword, subreddit_names, limit)
    return results


async def main():
    keywords = ["pump", "moon", "100x", "buy now", "HODL", "FOMO", "next big thing"]
    subreddits = ["CryptoCurrency", "CryptoMoonShots", "altcoin"]
    try:
        results = await redditposts(keywords, subreddits, 10)
        print(results)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())