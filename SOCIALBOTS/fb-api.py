import requests

# Base URL for Facebook Graph API
BASE_URL = "https://graph.facebook.com/v21.0/{object_id}/posts"

def search_posts(object_ids, keywords, access_token):
    for object_id in object_ids:
        print(f"Scanning ID: {object_id}")
        url = BASE_URL.format(object_id=object_id)
        params = {
            "fields": (
                "id,message,created_time,"
                "likes.summary(true),comments.summary(true),"
                "shares,reactions.summary(true)"
            ),
            "access_token": access_token,
            "limit": 100,
        }

        filtered_posts = []

        while True:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                posts = data.get("data", [])

                for post in posts:
                    message = post.get("message", "").lower()
                    if any(keyword.lower() in message for keyword in keywords):
                        filtered_posts.append(post)

                paging = data.get("paging", {})
                next_url = paging.get("next")
                if next_url:
                    url = next_url
                    params = {}  # Params are included in next_url
                else:
                    break

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                if 'response' in locals():
                    print(f"Response: {response.text}")
                break
            except requests.exceptions.RequestException as req_err:
                print(f"Request error occurred: {req_err}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        if filtered_posts:
            print(f"Found {len(filtered_posts)} posts containing the keywords {keywords}:")
            for post in filtered_posts:
                print(f"Post ID: {post['id']}")
                print(f"Message: {post.get('message', 'No message')}")
                print(f"Created Time: {post['created_time']}")
                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = post.get('shares', {}).get('count', 0)
                reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
                print(f"Likes: {likes}, Comments: {comments}, Shares: {shares}, Reactions: {reactions}\n")
        else:
            print(f"No posts found containing the keywords {keywords}.")

# Example usage
if __name__ == "__main__":
    OBJECT_IDS = ["61550477913097", "user_profile_id_1"]  # Replace with the IDs of Pages or Profiles you want to scan
    KEYWORDS = ["funny", "interesting"]  # Replace with your list of keywords
    ACCESS_TOKEN = " "
    
    
    search_posts(OBJECT_IDS, KEYWORDS, ACCESS_TOKEN)


