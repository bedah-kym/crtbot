import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import random

def calculate_engagement_score(likes, comments, shares, reactions):
    """Calculate engagement score based on weights."""
    return likes * 1 + comments * 2 + shares * 3 + reactions * 1.5

def load_cookies(driver, cookies_file):
    """Load cookies from a JSON file into the Selenium driver."""
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                cookie.pop("sameSite")
            driver.add_cookie(cookie)

def is_logged_in(driver):
    """Check if the user is logged in by looking for a unique element on the homepage."""
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MainFeed']")))
        #print("Login successful.")
        return True
    except TimeoutException:
        #print("Not logged in. Checking again...")
        return True

def dismiss_notification_prompt(driver):
    """Dismiss notification prompt if it appears."""
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Close']")))
        close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
        close_button.click()
        print("Notification prompt dismissed.")
    except TimeoutException:
        print("No notification prompt found.")

def wait_for_page_load(driver):
    """Wait for the document.readyState to be 'complete'."""
    WebDriverWait(driver, 60).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("Page loaded completely.")

def is_placeholder(element):
    """Check if the element is a loading placeholder."""
    try:
        if "loading" in element.get_attribute("aria-label") or "loading-state" in element.get_attribute("data-visualcompletion"):
            return True
        return False
    except Exception:
        return False

async def scrape_group_or_page(driver, group_id, keywords):
    """Scrape posts from a specific group or page URL for keywords and engagement metrics."""
    url = f"https://www.facebook.com/groups/{group_id}"

    for attempt in range(3):
        try:
            print(f"Attempting to load: {url}")
            driver.get(url)
            print(f"Current URL after load: {driver.current_url}")
            wait_for_page_load(driver)
            print("Page loaded successfully.")
            break
        except TimeoutException:
            print(f"Retrying page load ({attempt + 1}/3)...")
    else:
        print("Failed to load the page after retries.")
        return []

    # Scroll and collect posts
    posts = []
    scroll_attempts = 0
    max_scroll_attempts = 10  # Adjust this limit as needed
    last_height = driver.execute_script("return document.body.scrollHeight")

    while scroll_attempts < max_scroll_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(random.uniform(5, 7))  # Random delay to mimic human behavior

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No new content loaded, stopping scroll.")
            break

        last_height = new_height
        print(f"Scroll attempt {scroll_attempts + 1}")

        elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet^='FeedUnit']")
        #print(f"Found {len(elements)} posts in this scroll attempt.")

        if len(elements) == 0:
            print("No posts detected using primary selector. Checking alternative selectors.")
            elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")  # Alternative selector
            #print(f"Found {len(elements)} posts using alternative selector.")

        for element in elements:
            try:
                if is_placeholder(element):
                    print("Skipping loading placeholder.")
                    continue

                message = element.find_element(By.CSS_SELECTOR, "div[dir='auto']").text.lower()

                try:
                    likes_text = element.find_element(By.CSS_SELECTOR, "span.x1e558r4").text.replace('K', '000').replace(',', '')
                    likes = int(likes_text) if likes_text.isdigit() else 0
                except NoSuchElementException:
                    likes = 0

                try:
                    reactions_div = element.find_element(By.CSS_SELECTOR, "div.x1n2onr6")
                    reactions_text = reactions_div.find_element(By.CSS_SELECTOR, "span.x1e558r4").text.replace('K', '000').replace(',', '')
                    reactions = int(reactions_text) if reactions_text.isdigit() else likes  # Fallback to likes if reactions missing
                except NoSuchElementException:
                    reactions = likes

                try:
                    comments_text = element.find_element(By.CSS_SELECTOR, "span[aria-label*='comment']").text.replace('K', '000').replace(',', '')
                    comments = int(comments_text) if comments_text.isdigit() else 0
                except NoSuchElementException:
                    comments = 0

                try:
                    shares_text = element.find_element(By.CSS_SELECTOR, "span[aria-label*='share']").text.replace('K', '000').replace(',', '')
                    shares = int(shares_text) if shares_text.isdigit() else 0
                except NoSuchElementException:
                    shares = 0

                engagement_score = calculate_engagement_score(likes, comments, shares, reactions)

                if any(keyword.lower() in message for keyword in keywords):
                    posts.append({
                        "message": message,
                        "likes": likes,
                        "comments": comments,
                        "shares": shares,
                        "reactions": reactions,
                        "engagement_score": engagement_score
                    })

            except NoSuchElementException:
                continue  # Skip elements that do not match the expected structure

        scroll_attempts += 1

    return posts

async def search_posts(group_id, keywords, cookies_file):
    """Search posts for keywords using Selenium."""
    service = Service("C:/chromedriver-win64/chromedriver.exe")  # Update with your ChromeDriver path
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.facebook.com/")
        load_cookies(driver, cookies_file)

        # Refresh to apply cookies with retry logic
        for attempt in range(3):
            try:
                driver.refresh()
                print("Page refreshed successfully.")
                break
            except TimeoutException:
                print(f"Retrying refresh ({attempt + 1}/3)...")
                await asyncio.sleep(5)
        else:
            print("Failed to refresh after retries.")
            return []

        await asyncio.sleep(10)  # Allow time for cookies to take effect

        # Check login status with retries
        for attempt in range(3):
            if is_logged_in(driver):
                break
            print(f"Retrying login check ({attempt + 1}/3)...")
            await asyncio.sleep(5)
        else:
            print("Failed to log in after retries. Please check your cookies.")
            return []

        dismiss_notification_prompt(driver)
        wait_for_page_load(driver)

        posts = await scrape_group_or_page(driver, group_id, keywords)
        return posts

    finally:
        driver.quit()

if __name__ == "__main__":
    async def fbposts():
        group_id = "1766546466973495"  # Example group ID
        keywords = ["crypto", "blockchain", "bitcoin", "ethereum"]
        cookies_file = "SOCIALBOTS/fbcookies.json"

        posts = await search_posts(group_id, keywords, cookies_file)
        print(f"Found {len(posts)} posts:")
        for post in posts:
            print(json.dumps(post, indent=2))

    asyncio.run(fbposts(keywords,cookies_file,group_id))
