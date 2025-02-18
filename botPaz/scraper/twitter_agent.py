#twitter_agent.py

import os
import sys
import pandas as pd

from progress import Progress
from scroller import Scroller
from tweet import Tweet
 
from datetime import datetime
from fake_headers import Headers
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # Si usas teclas como PAGE_DOWN


TWITTER_LOGIN_URL = "https://twitter.com/i/flow/login"

class TwitterAgent:

    def __init__(
        self,
        mail,
        username,
        password,
        max_tweets=50,
        scrape_username=None,
        scrape_hashtag=None,
        scrape_query=None,
        scrape_poster_details=False,
        scrape_latest=True,
        scrape_top=False,
        proxy=None,
    ):
        print("Initializing Twitter Scraper...")
        self.mail = mail
        self.username = username
        self.password = password
        self.interrupted = False
        self.tweet_ids = set()
        self.data = []
        self.tweet_cards = []
        self.scraper_details = {
            "type": None,
            "username": None,
            "hashtag": None,
            "query": None,
            "tab": None,
            "poster_details": False,
        }
        self.max_tweets = max_tweets
        self.progress = Progress(0, max_tweets)
        self.router = self.go_to_home
        self.driver = self._get_driver(proxy)
        self.actions = ActionChains(self.driver)
        self.scroller = Scroller(self.driver)
        self._config_scraper(
            max_tweets,
            scrape_username,
            scrape_hashtag,
            scrape_query,
            scrape_latest,
            scrape_top,
            scrape_poster_details,
        )

    def _config_scraper(
        self,
        max_tweets=50,
        scrape_username=None,
        scrape_hashtag=None,
        scrape_query=None,
        scrape_latest=True,
        scrape_top=False,
        scrape_poster_details=False,
    ):
        self.tweet_ids = set()
        self.data = []
        self.tweet_cards = []
        self.max_tweets = max_tweets
        self.progress = Progress(0, max_tweets)
        self.scraper_details = {
            "type": None,
            "username": scrape_username,
            "hashtag": str(scrape_hashtag).replace("#", "")
            if scrape_hashtag is not None
            else None,
            "query": scrape_query,
            "tab": "Latest" if scrape_latest else "Top" if scrape_top else "Latest",
            "poster_details": scrape_poster_details,
        }
        self.router = self.go_to_home
        self.scroller = Scroller(self.driver)

        if scrape_username is not None:
            self.scraper_details["type"] = "Username"
            self.router = self.go_to_profile
        elif scrape_hashtag is not None:
            self.scraper_details["type"] = "Hashtag"
            self.router = self.go_to_hashtag
        elif scrape_query is not None:
            self.scraper_details["type"] = "Query"
            self.router = self.go_to_search
        else:
            self.scraper_details["type"] = "Home"
            self.router = self.go_to_home
        pass

    def _get_driver(
        self,
        proxy=None,
    ):
        print("Setup WebDriver...")
        header = Headers().generate()["User-Agent"]

        # browser_option = ChromeOptions()
        browser_option = FirefoxOptions()
        browser_option.add_argument("--no-sandbox")
        browser_option.add_argument("--disable-dev-shm-usage")
        browser_option.add_argument("--ignore-certificate-errors")
        browser_option.add_argument("--disable-gpu")
        browser_option.add_argument("--log-level=3")
        browser_option.add_argument("--disable-notifications")
        browser_option.add_argument("--disable-popup-blocking")
        browser_option.add_argument("--user-agent={}".format(header))
        if proxy is not None:
            browser_option.add_argument("--proxy-server=%s" % proxy)

        # For Hiding Browser
        #browser_option.add_argument("--headless")

        try:
            # print("Initializing ChromeDriver...")
            # driver = webdriver.Chrome(
            #     options=browser_option,
            # )

            print("Initializing FirefoxDriver...")
            driver = webdriver.Firefox(
                options=browser_option,
            )

            print("WebDriver Setup Complete")
            return driver
        except WebDriverException:
            try:
                # print("Downloading ChromeDriver...")
                # chromedriver_path = ChromeDriverManager().install()
                # chrome_service = ChromeService(executable_path=chromedriver_path)

                print("Downloading FirefoxDriver...")
                firefoxdriver_path = GeckoDriverManager().install()
                firefox_service = FirefoxService(executable_path=firefoxdriver_path)

                # print("Initializing ChromeDriver...")
                # driver = webdriver.Chrome(
                #     service=chrome_service,
                #     options=browser_option,
                # )

                print("Initializing FirefoxDriver...")
                driver = webdriver.Firefox(
                    service=firefox_service,
                    options=browser_option,
                )

                print("WebDriver Setup Complete")
                return driver
            except Exception as e:
                print(f"Error setting up WebDriver: {e}")
                sys.exit(1)
        pass

    def login(self):
        print()
        print("Logging in to Twitter...")

        try:
            self.driver.maximize_window()
            self.driver.get(TWITTER_LOGIN_URL)
            sleep(3)

            self._input_username()
            self._input_unusual_activity()
            self._input_password()

            cookies = self.driver.get_cookies()

            auth_token = None

            for cookie in cookies:
                if cookie["name"] == "auth_token":
                    auth_token = cookie["value"]
                    break

            if auth_token is None:
                raise ValueError(
                    """This may be due to the following:

- Internet connection is unstable
- Username is incorrect
- Password is incorrect
"""
                )

            print()
            print("Login Successful")
            print()
        except Exception as e:
            print()
            print(f"Login Failed: {e}")
            sys.exit(1)

        pass

    def _input_username(self):
        input_attempt = 0

        while True:
            try:
                username = self.driver.find_element(
                    "xpath", "//input[@autocomplete='username']"
                )

                username.send_keys(self.username)
                username.send_keys(Keys.RETURN)
                sleep(3)
                break
            except NoSuchElementException:
                input_attempt += 1
                if input_attempt >= 3:
                    print()
                    print(
                        """There was an error inputting the username.

It may be due to the following:
- Internet connection is unstable
- Username is incorrect
- Twitter is experiencing unusual activity"""
                    )
                    self.driver.quit()
                    sys.exit(1)
                else:
                    print("Re-attempting to input username...")
                    sleep(2)

    def _input_unusual_activity(self):
        input_attempt = 0

        while True:
            try:
                unusual_activity = self.driver.find_element(
                    "xpath", "//input[@data-testid='ocfEnterTextTextInput']"
                )
                unusual_activity.send_keys(self.mail)
                unusual_activity.send_keys(Keys.RETURN)
                sleep(3)
                break
            except NoSuchElementException:
                input_attempt += 1
                if input_attempt >= 3:
                    break

    def _input_password(self):
        input_attempt = 0

        while True:
            try:
                password = self.driver.find_element(
                    "xpath", "//input[@autocomplete='current-password']"
                )

                password.send_keys(self.password)
                password.send_keys(Keys.RETURN)
                sleep(3)
                break
            except NoSuchElementException:
                input_attempt += 1
                if input_attempt >= 3:
                    print()
                    print(
                        """There was an error inputting the password.

It may be due to the following:
- Internet connection is unstable
- Password is incorrect
- Twitter is experiencing unusual activity"""
                    )
                    self.driver.quit()
                    sys.exit(1)
                else:
                    print("Re-attempting to input password...")
                    sleep(2)

    def go_to_home(self):
        self.driver.get("https://twitter.com/home")
        sleep(3)
        pass

    def go_to_tweet(self,username,tweet_id):
        if not tweet_id or not isinstance(tweet_id, str):
            raise ValueError("El tweet_id no es válido o no se ha proporcionado.")

        try:
            self.driver.get(f"https://twitter.com/{username}/status/{tweet_id}")
            sleep(3)
        except Exception as e:
            print(f"Error al intentar navegar al tweet: {e}")
            pass

    def go_to_profile(self):
        if (
            self.scraper_details["username"] is None
            or self.scraper_details["username"] == ""
        ):
            print("Username is not set.")
            sys.exit(1)
        else:
            self.driver.get(f"https://twitter.com/{self.scraper_details['username']}")
            sleep(3)
        pass
    
    def scrape_tweets(
        self,
        max_tweets=50,
        no_tweets_limit=False,
        scrape_username=None,
        scrape_hashtag=None,
        scrape_query=None,
        scrape_latest=True,
        scrape_top=False,
        scrape_poster_details=False,
        router=None,
    ):
        self._config_scraper(
            max_tweets,
            scrape_username,
            scrape_hashtag,
            scrape_query,
            scrape_latest,
            scrape_top,
            scrape_poster_details,
        )

        if router is None:
            router = self.router

        router()

        if self.scraper_details["type"] == "Username":
            print(
                "Scraping Tweets from @{}...".format(self.scraper_details["username"])
            )
        elif self.scraper_details["type"] == "Hashtag":
            print(
                "Scraping {} Tweets from #{}...".format(
                    self.scraper_details["tab"], self.scraper_details["hashtag"]
                )
            )
        elif self.scraper_details["type"] == "Query":
            print(
                "Scraping {} Tweets from {} search...".format(
                    self.scraper_details["tab"], self.scraper_details["query"]
                )
            )
        elif self.scraper_details["type"] == "Home":
            print("Scraping Tweets from Home...")

        # Accept cookies to make the banner disappear
        try:
            accept_cookies_btn = self.driver.find_element(
            "xpath", "//span[text()='Refuse non-essential cookies']/../../..")
            accept_cookies_btn.click()
        except NoSuchElementException:
            pass

        self.progress.print_progress(0, False, 0, no_tweets_limit)

        refresh_count = 0
        added_tweets = 0
        empty_count = 0
        retry_cnt = 0

        while self.scroller.scrolling:
            try:
                self.get_tweet_cards()
                added_tweets = 0

                for card in self.tweet_cards[-15:]:
                    try:
                        tweet_id = str(card)

                        if tweet_id not in self.tweet_ids:
                            self.tweet_ids.add(tweet_id)

                            if not self.scraper_details["poster_details"]:
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView();", card
                                )

                            tweet = Tweet(
                                card=card,
                                driver=self.driver,
                                actions=self.actions,
                                scrape_poster_details=self.scraper_details[
                                    "poster_details"
                                ],
                            )

                            if tweet:
                                if not tweet.error and tweet.tweet is not None:
                                    if not tweet.is_ad:
                                        self.data.append(tweet.tweet)
                                        added_tweets += 1
                                        self.progress.print_progress(len(self.data), False, 0, no_tweets_limit)

                                        if len(self.data) >= self.max_tweets and not no_tweets_limit:
                                            self.scroller.scrolling = False
                                            break
                                    else:
                                        continue
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                    except NoSuchElementException:
                        continue

                if len(self.data) >= self.max_tweets and not no_tweets_limit:
                    break

                if added_tweets == 0:
                    # Check if there is a button "Retry" and click on it with a regular basis until a certain amount of tries
                    try:
                        while retry_cnt < 15:
                            retry_button = self.driver.find_element(
                            "xpath", "//span[text()='Retry']/../../..")
                            self.progress.print_progress(len(self.data), True, retry_cnt, no_tweets_limit)
                            sleep(58)
                            retry_button.click()
                            retry_cnt += 1
                            sleep(2)
                    # There is no Retry button so the counter is reseted
                    except NoSuchElementException:
                        retry_cnt = 0
                        self.progress.print_progress(len(self.data), False, 0, no_tweets_limit)

                    if empty_count >= 5:
                        if refresh_count >= 3:
                            print()
                            print("No more tweets to scrape")
                            break
                        refresh_count += 1
                    empty_count += 1
                    sleep(1)
                else:
                    empty_count = 0
                    refresh_count = 0
            except StaleElementReferenceException:
                sleep(2)
                continue
            except KeyboardInterrupt:
                print("\n")
                print("Keyboard Interrupt")
                self.interrupted = True
                break
            except Exception as e:
                print("\n")
                print(f"Error scraping tweets: {e}")
                break

        print("")

        if len(self.data) >= self.max_tweets or no_tweets_limit:
            print("Scraping Complete")
        else:
            print("Scraping Incomplete")

        if not no_tweets_limit:
            print("Tweets: {} out of {}\n".format(len(self.data), self.max_tweets))

        pass

    def get_tweet_cards(self):
        self.tweet_cards = self.driver.find_elements(
            "xpath", '//article[@data-testid="tweet" and not(@disabled)]'
        )
        pass
    
    def make_pd(self):
            
        data = {
            "Name": [tweet[0] for tweet in self.data],
            "Handle": [tweet[1] for tweet in self.data],
            "Timestamp": [tweet[2] for tweet in self.data],
            "Verified": [tweet[3] for tweet in self.data],
            "Content": [tweet[4] for tweet in self.data],
            "Comments": [tweet[5] for tweet in self.data],
            "Retweets": [tweet[6] for tweet in self.data],
            "Likes": [tweet[7] for tweet in self.data],
            "Analytics": [tweet[8] for tweet in self.data],
            "Tags": [tweet[9] for tweet in self.data],
            "Mentions": [tweet[10] for tweet in self.data],
            "Emojis": [tweet[11] for tweet in self.data],
            "Profile Image": [tweet[12] for tweet in self.data],
            "Tweet Link": [tweet[13] for tweet in self.data],
            "Tweet ID": [tweet[14] for tweet in self.data],
        }

        if self.scraper_details["poster_details"]:
            data["Tweeter ID"] = [f"user_id:{tweet[15]}" for tweet in self.data]
            data["Following"] = [tweet[16] for tweet in self.data]
            data["Followers"] = [tweet[17] for tweet in self.data]
        
        df = pd.DataFrame(data)
        
        return df

    def save_to_csv(self):
        print("Saving Tweets to CSV...")
        now = datetime.now()
        folder_path = "./tweets/"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print("Created Folder: {}".format(folder_path))

        data = {
            "Name": [tweet[0] for tweet in self.data],
            "Handle": [tweet[1] for tweet in self.data],
            "Timestamp": [tweet[2] for tweet in self.data],
            "Verified": [tweet[3] for tweet in self.data],
            "Content": [tweet[4] for tweet in self.data],
            "Comments": [tweet[5] for tweet in self.data],
            "Retweets": [tweet[6] for tweet in self.data],
            "Likes": [tweet[7] for tweet in self.data],
            "Analytics": [tweet[8] for tweet in self.data],
            "Tags": [tweet[9] for tweet in self.data],
            "Mentions": [tweet[10] for tweet in self.data],
            "Emojis": [tweet[11] for tweet in self.data],
            "Profile Image": [tweet[12] for tweet in self.data],
            "Tweet Link": [tweet[13] for tweet in self.data],
            "Tweet ID": [{tweet[14]} for tweet in self.data],
        }

        if self.scraper_details["poster_details"]:
            data["Tweeter ID"] = [f"user_id:{tweet[15]}" for tweet in self.data]
            data["Following"] = [tweet[16] for tweet in self.data]
            data["Followers"] = [tweet[17] for tweet in self.data]

        df = pd.DataFrame(data)

        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{folder_path}{current_time}_tweets_1-{len(self.data)}.csv"
        pd.set_option("display.max_colwidth", None)
        df.to_csv(file_path, index=False, encoding="utf-8")

        print("CSV Saved: {}".format(file_path))

        pass

    def get_tweets(self):
        return self.data
    
    def reply(self, message: str, tweet_id=None, tweet_url=None):
        """
        Reply to a specific tweet with the given message.
        """
        try:
            # Navega al tweet usando su URL o ID
            if tweet_url:
                self.driver.get(tweet_url)
            elif tweet_id:
                self.driver.get(f"https://twitter.com/anybody/status/{tweet_id}")
            
            sleep(3)  # Espera para cargar la página

            # Esperar y localizar la caja de texto para el mensaje
            print("Buscando caja de texto para respuesta...")
            reply_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']"))
            )
            print("Caja de texto encontrada, escribiendo mensaje...")
            reply_box.send_keys(message)

            # Esperar y localizar el botón de enviar tweet
            print("Buscando botón de tweet...")
            tweet_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='tweetButtonInline']"))
            )
            print("Botón de tweet encontrado, intentando hacer clic...")
            self.driver.execute_script("arguments[0].click();", tweet_button)

            
            print("Respuesta enviada exitosamente.")
            return True

        except Exception as e:
            print(f"Error al responder el tweet: {e}")
            return False
        
    def scrape_replys(self,username, tweet_id: int, max_tweets: int = 50):
        """
        Scrapea respuestas de un tweet dado su ID.
        
        Args:
            tweet_id (int): ID del tweet del que se desea obtener respuestas.
            max_tweets (int): Número máximo de respuestas a scrapear.
        """
        try:
            # Navegar al tweet utilizando su ID
            print(f"Navegando al tweet con ID {tweet_id}...")
            self.go_to_tweet(username,str(tweet_id))

            # Inicializar variables para el scraping
            replies = []
            added_tweets = 0

            # Asegurarse de que el banner de cookies no interrumpa el scraping
            try:
                accept_cookies_btn = self.driver.find_element(
                    "xpath", "//span[text()='Refuse non-essential cookies']/../../.."
                )
                accept_cookies_btn.click()
            except NoSuchElementException:
                pass

            # Iniciar el proceso de scraping
            while len(replies) < max_tweets:
                try:
                    self.get_tweet_cards()
                    for card in self.tweet_cards[-15:]:
                        try:
                            # Crear un objeto Tweet para cada respuesta
                            reply = Tweet(
                                card=card,
                                driver=self.driver,
                                actions=self.actions,
                                scrape_poster_details=False,
                            )

                            # Validar que la respuesta sea válida y no un anuncio
                            if reply and not reply.error and reply.tweet and not reply.is_ad:
                                replies.append(reply.tweet)
                                added_tweets += 1
                                print(f"Respuestas scrapeadas: {len(replies)}/{max_tweets}")

                                # Detener si alcanzamos el límite de respuestas
                                if len(replies) >= max_tweets:
                                    break
                        except NoSuchElementException:
                            continue

                    # Hacer scroll para cargar más respuestas
                    self.scroller.scroll()

                except StaleElementReferenceException:
                    print("Elemento desactualizado, intentando nuevamente...")
                    continue

            print(f"Scraping completado. Total de respuestas obtenidas: {len(replies)}")
            return replies

        except Exception as e:
            print(f"Error durante el scraping de respuestas: {e}")
            return []


