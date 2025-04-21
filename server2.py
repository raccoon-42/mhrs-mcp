from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

# Set up Firefox options for headless mode
#options.headless = True  # Enable headless mode
#options.add_argument("--headless")
os.environ["webdriver.gecko.driver"] = "/opt/homebrew/bin/geckodriver"
options = Options()

# Global driver and wait
driver = None
wait = None

# Initialize FastMCP for communication
mcp = FastMCP("mhrs")

# URL and credentials
url = "https://mhrs.gov.tr/vatandas/#/"
username = os.getenv("MHRS_USERNAME")
password = os.getenv("MHRS_PASSWORD")

is_logged_in = False
# Set up the driver and WebDriverWait globally
def initialize_driver():
    global driver, wait
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 30)  # You can adjust this timeout value as needed

def login():
    global is_logged_in
    try:
        initialize_driver()  # Initialize the driver and wait

        username_input = wait.until(EC.presence_of_element_located((By.ID, "LoginForm_username")))
        username_input.send_keys(username)

        password_input = wait.until(EC.presence_of_element_located((By.ID, "LoginForm_password")))
        password_input.send_keys(password)
        # Wait until spinner is gone
        wait_loading_screen()

        # Now click the login button
        click_button(".ant-btn.ant-btn-teal.ant-btn-block") #login button selector
        wait_loading_screen() # wait until loggin in
        click_button(".ant-modal-confirm-btns > button:nth-child(1)") #neyim var button
        is_logged_in = True
        return "Login is successful"
    except Exception as e:
        return f"Error: {e}"

# Tool for getting active appointments
@mcp.tool()
def get_active_appointments():
    """
    Fetches and returns a list of active appointments for the currently logged-in user from the MHRS system.

    This function navigates to the main page of the MHRS website, waits for appointment elements to load,
    and extracts key information such as date, status, hospital, doctor, and clinic details from each listed appointment.
    The results are formatted as a JSON string.

    Returns:
        str or None: A JSON-formatted string containing the user's active appointment data.
                     If no appointments are found or an error occurs, returns None and logs the error.

    Example:
        get_active_appointments()

    Output JSON Structure:
    [
        {
            "datetime": "18.04.2025 13:20",
            "status": "Randevu Alındı",
            "note": "MHRS",
            "hospital": "BERGAMA DEVLET HASTANESİ",
            "department": "GÖĞÜS HASTALIKLARI",
            "clinic": "BERGAMA",
            "doctor": "Uzm. Dr. Ali Konyar"
        },
        ...
    ]

    Notes:
        - Assumes the Selenium WebDriver session is active and the user is logged in.
        - Uses a short wait time (2 seconds) for detecting active appointments.
        - Prints both the list size and the resulting JSON to console for debugging.
    """
    global is_logged_in
    if not is_logged_in:
        login()
    try:
        driver.get("https://mhrs.gov.tr/vatandas/#/")
        
        wait_loading_screen() 
    
        appointments_list = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-list-items li"))
        )
        
        print("appointments_list size:", len(appointments_list))
        print(appointments_list)
        # Print out the text of each appointment
        appointments_data = []  # List to store all appointment data

        # Loop through each appointment and store its data
        for appointment in appointments_list:
            data = appointment.text.splitlines()
            appointment_data = {
                "datetime": data[0],
                "status": data[1],
                "note": data[2],
                "hospital": data[3],
                "department": data[4],
                "clinic": data[5],
                "doctor": data[6]
            }
            appointments_data.append(appointment_data)  # Add the appointment data to the list

        # Convert the list of appointment data into a JSON string
        appointments_json = json.dumps(appointments_data, ensure_ascii=False, indent=4)
        
        print("Appointments saved to JSON:")
        print(appointments_json)  # Print the JSON string (you can also return or save it)
        
        return appointments_json  # Return the JSON string
    except Exception as e:
        print("Cannot find any active appointments.")
       

@mcp.tool()
def list_available_doctors(city_name, town_name, clinic, hospital):
    """
    Attempts to list available doctors for medical appointment on the MHRS website using provided location and clinic details.

    This function navigates through the appointment booking interface via Selenium:
    - Selects the city, district, clinic, and hospital
    - Initiates a search for available appointments

    Args:
        city_name (str): Name of the city/province (e.g., "İZMİR")
        town_name (str): Name of the district/town (e.g., "bergama")
        clinic (str): Name or partial name of the clinic (e.g., "göğüs")
        hospital (str): Name or partial name of the hospital (e.g., "bergama")

    Returns:
        str or None: Returns a message string if appointment cannot be booked (e.g., no availability,
        doctor not found, date not found), otherwise None on successful attempt.
    
    Notes:
        - Assumes login has already been performed before this function is called.
        - Designed to be used within an automated session using Selenium WebDriver.
    """
    global is_logged_in
    if not is_logged_in:
        login()
        
    try:
        driver.get("https://mhrs.gov.tr/vatandas/#/")
        wait_loading_screen()

        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
        
        hasta_randevusu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.randevu-card-dissiz:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)")))
        hasta_randevusu_button.click()
        wait_loading_screen()
        
        genel_arama_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.randevu-turu-button:nth-child(1)")))
        genel_arama_button.click()
        #url="https://mhrs.gov.tr/vatandas/#/Randevu"
        #driver.get(url)
        select_city(city_name)
        select_ilce(town_name)
        select_clinic(clinic)
        select_hospital(hospital)

        click_on_appointment_search_button()

        if check_if_any_available_appointment():
            return fetch_all_available_doctor_names()
        else:
            return f"There are no available appointments to book for clinic {clinic}."
    except Exception as e:
        return e
   
 
@mcp.tool()
def cancel_appointment():
    return


def select_city(city_name):
    city_name = normalize_string_to_upper(city_name)
    
    wait_loading_screen()
    dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#il-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)")))
    wait_loading_screen()
    dropdown_span.click()  # Open the dropdown
    wait_loading_screen()

    city_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.ant-select-tree-treenode-switcher-open > span:nth-child(2)")))
    wait_loading_screen()

    for city in city_elements:
        print(city.text)
    
    # Use XPath to find the span with specific city name
    city_span = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{city_name}']")))
    wait_loading_screen()
    city_span.click()

def select_ilce(town_name):
    town_name = normalize_string_to_upper(town_name)

    wait_loading_screen()
    dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ant-select-selection__placeholder")))
    wait_loading_screen()
    dropdown_span.click()
    wait_loading_screen()
    
    selector = "li.ant-select-dropdown-menu-item"
    ilce_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
    for ilce in ilce_elements: 
        print(ilce.text)
    
    wait_loading_screen()
    town_span = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{town_name}']")))
    wait_loading_screen()
    town_span.click()
    
def normalize_string_to_lower(string):
    return string.strip().replace("İ","i").lower()

def normalize_string_to_upper(string):
    return string.strip().replace("i","İ").upper()

    #all_ilce_elements = wait.until(EC.presence_of_all_elements_located(()))
def select_clinic(clinic_name):
    try:
        wait_loading_screen()
        dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#klinik-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)")))
        wait_loading_screen()
        dropdown_span.click()
        
        #clinic_span = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//span[contains((text()), '{clinic_name}')]")))
        clinic_spans = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[starts-with(@id, 'klinik')]")))
        clinic_spans = clinic_spans[1:]
        #this prints webelement object
        normalized_target = normalize_string_to_lower(clinic_name)
        clinic_span = None
        
        for span in clinic_spans:
            # Get the text of each span and normalize it (lowercase)
            span_text = span.text.strip().lower()
            # If the target clinic name is found in the text of the current span, click it
            if normalized_target in span_text:
                clinic_span = span
                break  # Exit the loop once the clinic is found
            
        wait_loading_screen()
        if clinic_span:
            clinic_span.click()
    except Exception as e:
        return e
    
def select_hospital(hospital_name):
    dropdown_selector = "#hastane-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)"
    wait_loading_screen()
    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
    wait_loading_screen()
    dropdown.click()


    hospital_spans = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[starts-with(@id, 'hastane')]")))
    hospital_spans = hospital_spans[1:]
    wait_loading_screen()
    
    target_hospital_name = hospital_name.strip().lower()
    hospital_span = None

    for span in hospital_spans:
        normalized_hospital_name = span.text.strip().lower()
        if target_hospital_name in normalized_hospital_name:
            hospital_span = span
            break
    
    if hospital_span:
        wait_loading_screen()
        hospital_span.click()


def click_on_appointment_search_button():
    id = "randevu-ara-buton"
    appointment_search_button = wait.until(EC.element_to_be_clickable((By.ID, id)))
    wait_loading_screen()
    appointment_search_button.click()
    wait_loading_screen()


def check_if_any_available_appointment():
    try:
        wait_loading_screen()
        # tries to find the pop-up message that displays "no available appointment found"
        no_appintmount_available_button = driver.find_element(By.CSS_SELECTOR, ".ant-modal-confirm-btns > button:nth-child(1)")
        wait_loading_screen()
        wait.until(EC.element_to_be_clickable(no_appintmount_available_button))
        no_appintmount_available_button.click()
        return False
    except Exception as e:
        #available_appointments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ul_selector)))
        return True
    
def fetch_all_available_doctor_names():
    ul_selector = ".ant-list-items"
     # Wait for the <ul> element to be present in the DOM
    ul_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector)))
    
    # Find all <li> elements under the <ul> element
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")
    
    # Print the text of each <li> element
    for li in li_elements:
        print(li.text)
    
    # Return the list of <li> elements
    return li_elements

def wait_loading_screen():
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-spin-spinning")))
    #wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
    
# Placeholder for booking appointment (if needed in the future)
@mcp.tool()
def list_available_appointment_hours(doctor_name, appointment_date):
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"
    
    days = fetch_available_appointment_dates()

    day = select_day(appointment_date, days)
    if not day:
        return f"Could not find available appointments on the date you are looking for: {appointment_date}"
    
    click_on_a_day(day)
    list_all_available_hours_of_a_day() # assumes a day is clicked
    
    
    
    # decision making - separate this logic into another function - book_appointment() ?
    select_main_hour_slot()
    select_sub_hour_slot()
    accept_appointment() 
    if has_exceeded_max_appointment_count():
        return f"You exceeded maximum number of appointments (2) you can book at a given time. Cancel or wait for your future appointments."
    


def select_doctor(doctor_name):
    print("trying to select a doctor")
    # Wait for the list of doctor names to be present in the DOM
    wait_loading_screen()
    doctor_spans = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, "li.ant-list-item > div > div > span"
    )))
    
    print(f"Found {len(doctor_spans)} doctor(s). Looking for {doctor_name}...")

    # Normalize the doctor name to lowercase for case-insensitive matching
    doctor_name_normalized = doctor_name.strip().lower()

    # Iterate over each span and check if it contains the doctor name
    for doctor_span in doctor_spans:
        doctor_text = doctor_span.text.strip().lower()
        print(f"Checking doctor: {doctor_text}")
        
        if doctor_name_normalized in doctor_text:
            print(f"Found doctor: {doctor_text}")
            wait_loading_screen()
            doctor_span.click()  # Click the matching doctor
            print(f"Doctor {doctor_name} selected.")
            return True  # Exit the function once the doctor is selected

    # If no match was found
    print(f"Couldn't find a doctor matching: '{doctor_name}'")
    return False


def fetch_available_appointment_dates():
    print("Trying to fetch all appointment dates")
    
    # Parent container CSS selector
    parent_div_selector = "div.ant-tabs:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    
    # Wait for the parent div to be located
    parent_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, parent_div_selector)))
    
    # Now, find all the child divs (with date content) inside this parent container
    date_divs = parent_div.find_elements(By.CSS_SELECTOR, "div > div")  # Adjust the selector as needed
    
    print(f"Found {len(date_divs)} date divs inside the parent container.")

    # Iterate over each date div and print or interact with the content
    for date_div in date_divs:
        print(f"Appointment Date: {date_div.text}")
    
    # Optionally return the div elements if you need to interact further
    return date_divs

def select_day(day, date_divs):
    print("selecting day")
    target_day = day.strip().lower()
    for date_div in date_divs:
        normalized_date = date_div.text.lower()
        if target_day in normalized_date:
            print(f"found target day {target_day}")
            return date_div
    print(f"Could not find available appointments on the date you are looking for: {day}")
    return None



def click_on_a_day(day):
    print("trying to click on day")
    wait_loading_screen()
    day_div = wait.until(EC.element_to_be_clickable(day))
    wait_loading_screen()
    day_div.click()
    print(f"clicked on day {day.text}")

def select_clock_hourr(target_hour, clock_divs):
    for clock_div in clock_divs:
        if target_hour in clock_div.text:
            return clock_div
    return None

def select_main_hour_slot():
    #input clock=16:20
    clock = "13:00"
    target_clock_hour = clock.strip().split(':')[0]
    print(f"clock is {target_clock_hour}")
    clock_divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-collapse-item")))
    for clock_div in clock_divs:
        if target_clock_hour in clock_div.text:
            print(f"found target clock {target_clock_hour} in {clock_div.text}")
            wait_loading_screen()
            clock_div.click()
            return clock_div
    
    return None

def select_sub_hour_slot():
    target_clock = "13:20"
    clickable_clock_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-collapse-content-active > div")))
    for button in clickable_clock_buttons:
        print(f"current button is {button} and looking for {target_clock}")
        if target_clock in button.text:
            print(f"found target clock {target_clock}")
            button.click()
            wait_loading_screen()
            return button
    return None

def click_button(button_selector):
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, button_selector)))
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
    button.click()
    print(f"button {button.text} successfully clicked")
    wait_loading_screen()
    return


def accept_appointment():
    print("executing accept_appointment func")
    button_selector = ".ant-modal-confirm-btns > button:nth-child(2)"
    click_button(button_selector)
    print("appointment ACCEPT button successfully clicked")

    
    def verify_appointment():
        print("executing verify_appointment func")
        button_selector = ".ant-modal-footer > div:nth-child(1) > button:nth-child(2)"
        click_button(button_selector)
        print("appointment VERIFY button successfully clicked")
        
    verify_appointment()


def has_exceeded_max_appointment_count():
    # max # concurrent appointment count is by default 2
    exceeded_max_app_count_pop_up_selector = "div.ant-modal-body:nth-child(2)"
    try:
        driver.find_element(By.CSS_SELECTOR, exceeded_max_app_count_pop_up_selector)
        # assume pop up appeared
        ok_button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
        click_button(ok_button_selector)
        print("clicked ok on max app count exceeded button")
        return True
    except Exception:
        print("max count exceeded pop up did not appear")
        return False
        


def list_all_available_hours_of_a_day():
    # Wait for all the divs inside .ant-tabs-tabpane to be present
    wait_loading_screen()
    
    clock_divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-tabs-tabpane > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div")))
    
    print(f"Found {len(clock_divs)} tab pane divs.")
    wait_loading_screen()
    
    # Iterate over each tab pane div and print or interact with the content
    for clock_div in clock_divs:
        print(f"Tab content: {clock_div.text}")
        #clock_divs = tab.find_elements(By.CSS_SELECTOR, "div > div")
        #print(f"found {len(clock_divs)} clock divs inside of this parent container")
        #for clock_div in clock_divs:
         #   print(f"clock div: {clock_div.text}")
        click_on_a_clock_and_list_details(clock_div)
    
    # Optionally, return the div elements if you need to interact further
    return clock_divs

def click_on_a_clock_and_list_details(clock_div):
    wait_loading_screen()
    clock_div.click()
    print(f"clicked on clock {clock_div.text.strip().split()[0]}")
    
    clickable_buttons = clock_div.find_elements(By.CSS_SELECTOR, "div > button")
    for button in clickable_buttons:
        print(f"button text is {button.text}")

if __name__ == "__main__":
    print("server2 is running...")
    mcp.run(transport='stdio')