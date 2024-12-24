import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

# Date ranges for Super League weeks
date_ranges = [
    {"start": "2024-08-09", "end": "2024-08-15"},
    {"start": "2024-08-16", "end": "2024-08-22"},
    {"start": "2024-08-23", "end": "2024-08-29"},
    {"start": "2024-08-30", "end": "2024-09-13"},
    {"start": "2024-09-14", "end": "2024-09-19"},
    {"start": "2024-09-20", "end": "2024-09-26"},
    {"start": "2024-09-27", "end": "2024-10-03"},
    {"start": "2024-10-04", "end": "2024-10-18"},
    {"start": "2024-10-19", "end": "2024-10-24"},
    {"start": "2024-10-25", "end": "2024-10-31"},
    {"start": "2024-11-01", "end": "2024-11-07"},
    {"start": "2024-11-08", "end": "2024-11-22"},
    {"start": "2024-11-23", "end": "2024-11-28"},
    {"start": "2024-11-29", "end": "2024-12-05"},
    {"start": "2024-12-06", "end": "2024-12-12"},
    {"start": "2024-12-13", "end": "2024-12-19"}
]

def scrape_tweets():
    # Load existing progress
    progress_file = "progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            checked_ranges = json.load(f)
    else:
        checked_ranges = {}

    # Set up Chrome with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://twitter.com/login")
    time.sleep(30)  # Wait for manual login

    for i, date_range in enumerate(date_ranges):
        date_key = f"{date_range['start']}_to_{date_range['end']}"
        week_file = f"week{i+1}.json"

        # Skip already checked ranges
        if date_key in checked_ranges and checked_ranges[date_key]:
            print(f"Skipping already checked range: {date_key}")
            continue

        print(f"Scraping tweets from {date_range['start']} to {date_range['end']}...")
        tweets = set()
        url = f"https://twitter.com/search?q=mourinho%20lang%3Atr%20since%3A{date_range['start']}%20until%3A{date_range['end']}&src=typed_query&f=live"
        driver.get(url)
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        while len(tweets) < 500:
            # Collect tweets
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            for tweet in tweet_elements:
                tweets.add(tweet.text)

            print(f"Collected {len(tweets)} tweets so far.")

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 5))  # Random delay between scrolls

            # Check if scrolling has stopped
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                print(f"No new tweets loaded. Scroll attempts: {scroll_attempts}")
                if scroll_attempts >= 3:  # Pause if too many failed scrolls
                    print("Pausing to mimic human behavior...")
                    time.sleep(random.uniform(10, 20))  # Long pause
                    scroll_attempts = 0
            else:
                scroll_attempts = 0

            last_height = new_height

        print(f"Finished scraping {len(tweets)} tweets for {date_range['start']} to {date_range['end']}")
        with open(week_file, "w", encoding="utf-8") as f:
            json.dump(list(tweets), f, ensure_ascii=False, indent=2)

        # Mark this range as checked
        checked_ranges[date_key] = True
        with open(progress_file, "w") as f:
            json.dump(checked_ranges, f, ensure_ascii=False, indent=2)

    print("All weeks processed.")
    driver.quit()

# Run the script
scrape_tweets()
