from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Set up Firefox options for headless mode
os.environ["webdriver.gecko.driver"] = "/opt/homebrew/bin/geckodriver"
options = Options()

class BrowserClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserClient, cls).__new__(cls)
            cls._instance.driver = None
            cls._instance.wait = None
        return cls._instance

    def initialize_driver(self):
        if self.driver is None:
            self.driver = webdriver.Firefox(options=options)
            self.driver.get("https://mhrs.gov.tr/vatandas/#/")
            self.wait = WebDriverWait(self.driver, 30)  # You can adjust this timeout value as needed 

    def click_button(self, button_selector):
        for attempt in range(3):
            try:
                self.wait_loading_screen()  # Ensure loading screen is gone first
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))).click()
                self.wait_loading_screen()  # Wait after click
                break
            except Exception as e:
                print(f"[!] Attempt {attempt + 1}: {type(e).__name__} - {e}")
                time.sleep(0.5)
    
    def wait_loading_screen(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ant-spin-spinning")))

    def wait_warping(self):
        self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
        
    def genel_randevu_arama(self):
        self.wait_loading_screen()

        self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
        
        hasta_randevusu_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.randevu-card-dissiz:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)")))
        hasta_randevusu_button.click()
        self.wait_loading_screen()
        
        genel_arama_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.randevu-turu-button:nth-child(1)")))
        genel_arama_button.click()