from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

from browser import Browser  # Asumimos que la clase Browser ya está implementada en Python
from Chiguamigo.unofficialApi.src.classes.constants import username, password, fetchTweetsMinTimeout, fetchTweetsMaxTimeout, waitForElTimeout, sendKeyMinTimeout, sendKeyMaxTimeout


class TwitterClient:
    def __init__(self):
        self.driver = None
        self.browser = None

    def get_client(self):
        self.driver = webdriver.Chrome()  # Cambia esto según tu configuración de WebDriver
        self.browser = Browser(self.driver)
        return self.login()

    def login(self, cookies=None):
        try:
            print("[+] Trying login method 1: Cookies 🍪")
            self.browser.go_to_page("https://twitter.com/")
            result = self.browser.retrieve_cookies(cookies)

            if result:
                self.browser.sleep_default()
                self.browser.go_to_page("https://twitter.com/")
            else:
                print("[+] Cookies not found 😥, Trying login method 2: Credentials 🔐")
                self.browser.go_to_page("https://twitter.com/i/flow/login")

                self.browser.wait_for_element(By.CSS_SELECTOR, "[autocomplete='username']", waitForElTimeout)
                print(f"[+] Inputting username... {username}")
                self.browser.send_keys(By.CSS_SELECTOR, "input[autocomplete='username']", username, sendKeyMinTimeout, sendKeyMaxTimeout)
                self.browser.sleep_default()
                self.browser.find_button_and_click("Next")

                print(f"[+] Inputting password... {password}")
                self.browser.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]', waitForElTimeout)
                self.browser.send_keys(By.CSS_SELECTOR, 'input[type="password"]', password, sendKeyMinTimeout, sendKeyMaxTimeout)
                self.browser.sleep_default()
                self.browser.find_button_and_click("Log in")

            self.browser.wait_for_element(By.CSS_SELECTOR, '[aria-label="Tweet"]', waitForElTimeout)
            tweet_button = self.browser.get_element(By.CSS_SELECTOR, '[aria-label="Tweet"]')

            if tweet_button:
                print("Login success... saving cookies")
                self.get_cookies(True)
                return True
            else:
                print("Login failed")
                return False
        except Exception as e:
            print(e)
            return False

    def get_trends(self):
        try:
            self.browser.go_to_page("https://twitter.com/i/trends", By.CSS_SELECTOR, '[aria-label="Timeline: Trends"]')
            self.browser.wait_for_element(By.CSS_SELECTOR, "[data-testid='trend']", waitForElTimeout)
            self.browser.scroll_page(1000, 10, 50)

            trends_script = """
            let rawTrends = document.querySelectorAll('[data-testid="trend"]');
            let allTrends = [];
            rawTrends.forEach(t => {
                let tList = t.innerText.split(String.fromCharCode(0x0A));
                allTrends.push({ details: tList[0], name: tList[1], tweets: tList[2] });
            });
            return allTrends;
            """

            trends_list = self.browser.sync_execute_js(trends_script)
            return trends_list
        except Exception as e:
            print(e)
            return []

    def tweet(self, tweet):
        try:
            tweet_element = self.browser.get_element(By.CSS_SELECTOR, '[aria-label="Tweet"]')
            tweet_element.click()

            self.browser.wait_for_element(By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']", waitForElTimeout)
            self.browser.send_keys(By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']", tweet, sendKeyMinTimeout, sendKeyMaxTimeout)
            self.browser.sleep_default()
            tweet_button = self.browser.get_element(By.CSS_SELECTOR, "[data-testid='tweetButton']")
            tweet_button.click()
        except Exception as e:
            print(e)

    def fetch_tweets(self, source, amount):
        try:
            self.browser.go_to_page(source)
            self.browser.sleep(fetchTweetsMinTimeout, fetchTweetsMaxTimeout)
            self.browser.wait_for_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]', waitForElTimeout)

            current_window_handle = self.browser.get_current_window_handle()
            final_tweets = []
            found_tweets = 0

            while found_tweets < amount:
                tweets = self.browser.get_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                for tweet in tweets:
                    try:
                        new_tab_handle = self.browser.ctrl_click_element(tweet, current_window_handle)
                        self.browser.switch_tab(new_tab_handle)

                        is_tweet = self.browser.sync_execute_js(
                            "return window.location.href.includes('https://twitter.com/') && window.location.href.includes('status')"
                        )

                        if not is_tweet:
                            print("[!] Ad found....skipping!")
                            self.driver.close()
                            self.browser.switch_tab(current_window_handle)
                            continue

                        self.browser.wait_for_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]', waitForElTimeout)
                        tweet_data = self.scrape_tweet()
                        final_tweets.append(tweet_data)
                        found_tweets += 1
                        print(f"[!] Scrapped Tweets {found_tweets}/{amount}")

                        if found_tweets >= amount:
                            return final_tweets
                    except Exception as e:
                        print(e)
                        continue

                self.browser.sync_execute_js("document.querySelectorAll('article[data-testid=\"tweet\"]').forEach(tweet => tweet.remove());")
                self.browser.scroll_page(1000, 200, 0)
                self.browser.wait_for_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]', waitForElTimeout)
        except Exception as e:
            print(e)
            return []

    def scrape_tweet(self):
        scrape_tweet_script = """
        // JavaScript logic here...
        """
        return self.browser.sync_execute_js(scrape_tweet_script)

    def get_cookies(self, store=False):
        return self.browser.save_cookies(store)

    def retrieve_cookies(self, cookies):
        return self.browser.retrieve_cookies(cookies)
