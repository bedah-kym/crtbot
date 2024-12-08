import os
import logging
import praw

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

def search_subreddits(keyword, subreddit_names=["all"], limit=10):
    """
    Search for posts containing a keyword in specific subreddits.

    :param keyword: The keyword to search for.
    :param subreddit_names: List of subreddits to search in.
    :param limit: The number of results to retrieve.
    :return: List of posts containing the keyword.
    """
    try:
        reddit = get_reddit_instance()

        # Combine subreddits into a single query
        if "all" in subreddit_names:
            subreddit_query = "all"
        else:
            subreddit_query = "+".join(subreddit_names)

        subreddit = reddit.subreddit(subreddit_query)
        logging.info(f"Searching in subreddits: {subreddit_query}")

        # Search for the keyword
        search_results = subreddit.search(keyword, limit=limit)
        logging.info(f"Search completed for keyword: '{keyword}'")

        # Collect results
        posts = []
        for post in search_results:
            posts.append({
                "title": post.title,
                "url": post.url,
                "score": post.score,
                "author": str(post.author),
                "created_utc": post.created_utc
            })

        logging.info(f"Total posts retrieved: {len(posts)}")
        return posts

    except Exception as e:
        logging.exception("An error occurred while searching subreddits.")
        return []

def redditposts(keyword,subreddit_input,limit_input):
    
    # Parse limit
    try:
        limit = int(limit_input)
    except ValueError:
        logging.error("Invalid input for limit. Defaulting to 10.")
        limit = 10

    # Parse subreddit names
    subreddit_names = [s.strip() for s in subreddit_input.split(',')]

    # Perform search
    results = search_subreddits(keyword, subreddit_names, limit)

    # Display results
    return results


if __name__ == "__main__":
    redditposts()
