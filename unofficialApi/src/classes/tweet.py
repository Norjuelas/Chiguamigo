from selenium.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import List
from selenium.webdriver.remote.webelement import WebElement


class Tweet:
    def __init__(self, driver: WebDriver, tweet_url: str):
        self.driver = driver
        self.tweet_url = tweet_url
        self.on_tweet_page = False
        self.browser = Browser(self.driver)

    async def get_to_tweet(self):
        if not self.on_tweet_page:
            await self.browser.go_to_page(
                self.tweet_url, 
                "css", 
                "[data-testid='tweet']", 
                10  # waitForElTimeout
            )
            self.on_tweet_page = True

    async def like(self):
        await self.get_to_tweet()
        await self.driver.execute_script(
            "document.querySelectorAll(\"[data-testid='like']\")[0].click()"
        )

    async def unlike(self):
        await self.get_to_tweet()
        await self.driver.execute_script(
            "document.querySelectorAll(\"[data-testid='unlike']\")[0].click()"
        )

    async def retweet(self):
        await self.get_to_tweet()
        print(f"[i] Retweeting tweet {self.tweet_url}")
        await self.driver.execute_script(
            "document.querySelectorAll(\"[data-testid='retweet']\")[0].click()"
        )
        sleep(2)
        await self.driver.execute_script(
            "document.querySelectorAll(\"[data-testid='retweetConfirm']\")[0].click()"
        )

    async def unretweet(self):
        await self.get_to_tweet()
        await self.driver.