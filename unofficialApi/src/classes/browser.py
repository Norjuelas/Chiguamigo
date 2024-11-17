from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options

import json
import os
import random
import time


class Browser:

    def __init__(self, driver: webdriver.Chrome):
        self.driver = self.init_driver()
        self.cookie_file_location = 'src/storage/cookies.json'

    def init_driver(self):
        """Inicializa el WebDriver con las opciones necesarias."""
        #options = Options() 
        #options.add_argument("--headless")
        #options=options
        return webdriver.Firefox()    

    def random_int(self, min_val: int, max_val: int):
        return random.randint(min_val, max_val)

    def get_driver(self):
        return self.driver

    def go_to_page(self, url: str, waitby: str = "", waitarg: str = "", timeout: int = 10):
        self.driver.get(url)
        if waitby:
            if waitby == "css":
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, waitarg))
                )
    
    def wait_for_page_load(self, seconds=3, element=None, by=By.CLASS_NAME):
        """
        Espera a que la página cargue completamente o hasta que un elemento específico esté presente.
        
        :param seconds: Tiempo máximo de espera (en segundos).
        :param element: Nombre del elemento a esperar (opcional).
        :param by: Tipo de localizador de elementos (opcional, predeterminado By.CLASS_NAME).
        :return: True si se encuentra el elemento o si la página carga dentro del tiempo, False si ocurre un Timeout.
        """
        try:
            if element is None:
                # Espera hasta que expire el tiempo indicado
                WebDriverWait(self.driver, seconds).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            else:
                # Espera hasta que el elemento esté presente en el DOM
                WebDriverWait(self.driver, seconds).until(EC.presence_of_element_located((by, element)))
            return True
        except TimeoutException:
            print(f"Tiempo de espera agotado después de {seconds} segundos.")
            return False
        
    def scroll_page(self, scroll_max: int = 1000, scroll_unit: int = 10, sleep_after: int = 0):
        scrolled_amount = 0
        sleep_max = scroll_max / sleep_after if sleep_after > 0 else 0
        sleep_amount = 0

        for index in range(scroll_max // scroll_unit):
            scrolled_amount = index * scroll_unit

            if sleep_after > 0 and sleep_amount < sleep_max:
                if scrolled_amount - (sleep_after * sleep_amount) >= sleep_after:
                    time.sleep(self.random_int(1, 2))
                    sleep_amount += 1

            self.driver.execute_script(f"window.scrollBy(0, {scroll_unit})")

    def send_keys(self, selector_by: str, selector_by_arg: str, keys: str):
        element = self.get_element(selector_by, selector_by_arg)
        element.send_keys(keys)

    def get_element(self, by: str, arg: str):
        if by == "css":
            return self.driver.find_element(By.CSS_SELECTOR, arg)

    def get_elements(self, by: str, arg: str):
        if by == "css":
            return self.driver.find_elements(By.CSS_SELECTOR, arg)

    def find_button_and_click(self, button_text: str):
        script = f"""
        let buttons = document.querySelectorAll("[role='button']");
        for (let index = 0; index < buttons.length; index++) {{
            const element = buttons[index];
            if (element.innerText == "{button_text}") {{
                element.click();
                break;
            }}
        }}
        """
        self.driver.execute_script(script)

    def get_current_window_handle(self):
        return self.driver.current_window_handle

    def ctrl_click_element(self, element, current_window_handle):
        webdriver.ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        WebDriverWait(self.driver, 10).until(
            lambda _: len(self.driver.window_handles) > 1
        )
        handles = self.driver.window_handles
        return [handle for handle in handles if handle != current_window_handle][0]

    def switch_tab(self, handle: str):
        self.driver.switch_to.window(handle)

    def wait_for_element(self, waitby: str, waitarg: str, timeout: int = 10):
        if waitby == "css":
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, waitarg))
            )

    def sync_execute_js(self, script: str):
        return self.driver.execute_script(script)

    def save_cookies(self, store: bool = False):
        all_cookies = self.driver.get_cookies()
        if store:
            os.makedirs(os.path.dirname(self.cookie_file_location), exist_ok=True)
            with open(self.cookie_file_location, 'w', encoding='utf-8') as file:
                json.dump(all_cookies, file)
        return all_cookies

    def retrieve_cookies(self, cookies: list = None):
        if not os.path.exists(self.cookie_file_location):
            return False

        try:
            if cookies is None:
                with open(self.cookie_file_location, 'r', encoding='utf-8') as file:
                    cookies = json.load(file)

            for cookie in cookies:
                self.driver.add_cookie(cookie)

            return True
        except Exception as e:
            print(e)
            return False

    def sleep_default(self, min_time: int, max_time: int):
        sleep_time = self.random_int(min_time, max_time)
        time.sleep(sleep_time)

    def sleep(self, min_time: int, max_time: int):
        sleep_time = self.random_int(min_time, max_time)
        time.sleep(sleep_time)

    def scroll_screen(self):
        self.sync_execute_js("window.scrollTo(0,document.body.scrollHeight)")
        self.sleep(1, 3)

    def finished_scrolling(self, threshold: int = 97):
        return self.sync_execute_js(f"return (window.scrollY / document.body.scrollHeight) * 100 >= {threshold}")
