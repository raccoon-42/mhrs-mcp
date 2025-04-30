from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.clients.browser_client import BrowserClient

# Load environment variables
load_dotenv()

# URL and credentials
url = "https://mhrs.gov.tr/vatandas/#/"
username = os.getenv("MHRS_USERNAME")
password = os.getenv("MHRS_PASSWORD")

browser = BrowserClient()

class AuthClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthClient, cls).__new__(cls)
            cls._instance.is_logged_in = False
        return cls._instance
    
    def login(self):
        try:
            browser.initialize_driver()  # Initialize the driver and wait

            print("entering username")
            username_input = browser.wait.until(EC.presence_of_element_located((By.ID, "LoginForm_username")))
            username_input.send_keys(username)
            print("entered password")

            print("entering password")
            password_input = browser.wait.until(EC.presence_of_element_located((By.ID, "LoginForm_password")))
            password_input.send_keys(password)
            print("entered password")
            # Wait until spinner is gone
            browser.wait_loading_screen()


            # Now click the login button
            print("clicking login button")
            browser.click_button(".ant-btn.ant-btn-teal.ant-btn-block") #login button selector
            print("clicked login button")
            browser.wait_loading_screen() # wait until loggin in
            print("waiting for login")
            browser.click_button(".ant-modal-confirm-btns > button:nth-child(1)") #neyim var button
            print("clicked neyim var button")
            self.is_logged_in = True
            return "Login is successful"
        except Exception as e:
            return f"Error: {e}"

    def check_login(self):
        if not self.is_logged_in:
            self.login() 