from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random

def load_cookies_from_file(file_path):
    """Load cookies from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def inject_cookies(driver, cookies):
    """Inject cookies into the browser session."""
    driver.get("https://twitter.com")  # Navigate to Twitter to match the cookie domain
    for cookie in cookies:
        cookie.pop("domain", None)  # Remove domain to let Selenium handle it
        if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            cookie.pop("sameSite")  # Remove invalid sameSite value
        driver.add_cookie(cookie)
    time.sleep(random.uniform(3, 5))  # Random delay for human-like behavior
    driver.refresh()  # Refresh to apply cookies

def login_to_twitter(driver, username, password):
    """Automates Twitter login."""
    driver.get("https://twitter.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "session[username_or_email]")))

    driver.find_element(By.NAME, "session[username_or_email]").send_keys(username)
    time.sleep(random.uniform(1, 2))  # Mimic typing delay
    driver.find_element(By.NAME, "session[password]").send_keys(password)
    time.sleep(random.uniform(1, 2))  # Mimic typing delay
    driver.find_element(By.CSS_SELECTOR, "div[data-testid=\"LoginForm_Login_Button\"]").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))  # Wait until logged in

def scroll_to_load(driver, pause_time=2):
    """Scrolls down the page to load more content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(pause_time, pause_time + 1))  # Randomize scrolling intervals
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

service = Service("C:/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

def calculate_engagement_score(metrics):
    """Calculate the engagement score from metrics."""
    try:
        comments = int(metrics.get("comments", "0").replace("K", "000").replace("M", "000000"))
        retweets = int(metrics.get("retweets", "0").replace("K", "000").replace("M", "000000"))
        likes = int(metrics.get("likes", "0").replace("K", "000").replace("M", "000000"))
        return comments + retweets + likes
    except ValueError:
        return 0

def search_tweets_with_selenium(keywords_list, cookies_path=None, username=None, password=None, max_results=10):
    try:
        if cookies_path:
            cookies = load_cookies_from_file(cookies_path)
            inject_cookies(driver, cookies)
        elif username and password:
            login_to_twitter(driver, username, password)

        query = ' OR '.join(keywords_list)
        url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
        driver.get(url)

        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))

        # Retry logic for loading tweets
        for _ in range(3):
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
                break
            except:
                print("Retrying to load tweets...")
                driver.refresh()
                time.sleep(random.uniform(5, 7))

        # Scroll to load more tweets
        scroll_to_load(driver)

        tweets_data = []
        tweets = driver.find_elements(By.CSS_SELECTOR, "article")[:max_results]
        for tweet in tweets:
            try:
                time.sleep(random.uniform(1, 2))  # Mimic human reading time per tweet
                text = tweet.find_element(By.CSS_SELECTOR, "div[lang]").text

                # Extract engagement metrics using aria-label
                aria_label = tweet.find_element(By.CSS_SELECTOR, "div[role='group']").get_attribute("aria-label")
                metrics = {
                    "comments": "0",
                    "retweets": "0",
                    "likes": "0",
                }
                if aria_label:
                    parts = aria_label.split(", ")
                    for part in parts:
                        if "replies" in part:
                            metrics["comments"] = part.split()[0]
                        elif "reposts" in part:
                            metrics["retweets"] = part.split()[0]
                        elif "likes" in part:
                            metrics["likes"] = part.split()[0]

                engagement_score = calculate_engagement_score(metrics)

                tweets_data.append({
                    "Tweet": text,
                    "metrics": metrics,
                    "engagement_score": engagement_score
                })
            except Exception as e:
                print(f"Error extracting tweet: {e}")

        return tweets_data

    except Exception as e:
        import traceback
        print(f"Error during Selenium scraping: {e}")
        print(traceback.format_exc())
        return []

    finally:
        driver.quit()

async def Xposts(keywords, cookies_path, username=None, password=None):
    
    keywords = list(set(keyword.strip() for keyword in keywords))

    # Define cookies file path or login credentials
    cookies_path = "SOCIALBOTS/cookies.json"
    username = None
    password = None

    tweets = search_tweets_with_selenium(
        keywords,
        cookies_path=cookies_path,
        username=username,
        password=password,
        max_results=10
    )

    return tweets  # Return the fetched tweets

if __name__ == '__main__':
    Xposts()
