from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import json
import time 
import re

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

def check_login():
    global is_logged_in
    if not is_logged_in:
        login()
        
def search_doctor(doctor_name):
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"

@mcp.tool()
def cancel_appointment(appointment_identifier):
    """
    Cancels an existing appointment that matches the given identifier string.

    This function navigates to the MHRS main page (if not already there), searches through
    the user's active appointments, and attempts to cancel the one that matches the provided
    identifier (e.g., doctor name, clinic name, or any unique substring in the appointment text).
    It performs confirmation steps to complete the cancellation.

    Args:
        appointment_identifier (str): A string used to identify the appointment to cancel,
                                       e.g., a doctor's name like "eylem" or part of the appointment text.

    Returns:
        bool or str:
            - Returns True if the appointment was successfully cancelled.
            - Returns False if no matching appointment is found.
            - Returns a message string if an exception occurs (e.g., no appointments exist).

    Example:
        cancel_appointment("eylem")

    Notes:
        - Uses `normalize_string_to_lower()` for case-insensitive matching.
        - Assumes the user is already logged in and the Selenium driver is active.
        - Uses class selectors to click the Cancel, Confirm, and OK buttons in sequence.
        - Relies on appointment text containing the given identifier.
    """
    check_login()
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing cancel appointment func for identifier {appointment_identifier}")
    try:
    # navigate to mainpage
        if not driver.current_url == "https://mhrs.gov.tr/vatandas/#/":
            driver.get("https://mhrs.gov.tr/vatandas/#/")
            
        driver.find_element(By.CSS_SELECTOR, ".ant-list-items")
        
        appointments = driver.find_elements(By.CSS_SELECTOR, ".ant-list-items li")
        wait_loading_screen()
        for appointment in appointments:
            if appointment_identifier in normalize_string_to_lower(appointment.text):
                click_button(".ant-btn-danger") # cancel button
                click_button(".ant-btn-primary") # verify button
                click_button(".ant-btn-primary") # ok button
                return True
        return False
    except Exception as e:
        print(e)
        print("You don't have any appointments to cancel.")
        return "You don't have any appointments to cancel."
   
@mcp.tool()
def revert_appointment(appointment_identifier):
    """
    Reverts a pending or recently modified appointment that matches the given identifier.

    This function navigates to the MHRS main page, searches for appointments containing the
    provided identifier string (e.g., doctor's name), and performs a revert action if a match is found.
    It clicks the necessary confirmation buttons to finalize the revert.

    Args:
        appointment_identifier (str): A string used to identify the appointment to revert,
                                       such as a doctor's name, clinic, or any unique substring.

    Returns:
        bool or str:
            - Returns True if the revert action was successful.
            - Returns False if no matching appointment is found.
            - Returns a string message if an exception occurs or if no revertable appointment exists.

    Example:
        revert_appointment("eylem")

    Notes:
        - Performs case-insensitive matching using `normalize_string_to_lower()`.
        - Assumes a valid, logged-in Selenium session.
        - Designed for UI flows where appointments may be reverted via a confirm dialog.
        - Matching is done using substring matching inside appointment text.
    """
    check_login()
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing revert appointment func for identifier {appointment_identifier}")
    # navigate to mainpage
    
    try:
        if not driver.current_url == "https://mhrs.gov.tr/vatandas/#/":
            driver.get("https://mhrs.gov.tr/vatandas/#/")
            
        driver.find_element(By.CSS_SELECTOR, ".ant-list-items")
        
        appointments = driver.find_elements(By.CSS_SELECTOR, ".ant-list-items li")
        wait_loading_screen()
        for appointment in appointments:
            if appointment_identifier in normalize_string_to_lower(appointment.text):
                click_button(".ant-btn-primary") # cancel button
                click_button(".ant-modal-confirm-btns > button:nth-child(1)") # ok button
                return True
        return False
    except Exception as e:
        print(e)
        print("You dont have any revertable appointments.")
        return "You don't have any revertable appointments, sorry :/"
  
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
    check_login()
        
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
    Lists available doctors for a given location and clinic on the MHRS system.

    This function automates the process of navigating to the general appointment search page,
    selects the specified city, district, clinic, and hospital, and initiates a search to check
    for available appointment slots. If available, it fetches and prints the list of doctors.

    Args:
        city_name (str): Name of the city/province (e.g., "İZMİR")
        town_name (str): Name of the district/town (e.g., "URLA")
        clinic (str): Name or partial name of the clinic (e.g., "CİLDİYE")
        hospital (str): Name or partial name of the hospital (e.g., "URLA")

    Returns:
        str or None: A message if there are no available appointments, otherwise prints available doctors
        and returns None.

    Example:
        list_available_doctors("İZMİR", "URLA", "CİLDİYE", "URLA")

    Notes:
        - Assumes the user is already logged in via Selenium session.
        - Uses `wait_loading_screen()` and WebDriverWait to handle dynamic content loading.
        - Does not select a doctor or attempt to book; only lists available options.
    """
    check_login()
    
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
    
@mcp.tool()
def list_available_appointment_dates(doctor_name):
    """
    Lists all available appointment hours for a given doctor on a specific date.

    This function attempts to locate the specified doctor in the available appointment list,
    then fetches all available appointment dates. If the target date is found, it clicks on that day
    and lists all available time slots.

    Args:
        doctor_name (str): The name (or part of the name) of the doctor to search for (e.g., "eylem")
        appointment_date (str): The desired appointment date in "DD.MM.YYYY" format (e.g., "30.04.2025")

    Returns:
        str or None: Returns an error message string if the doctor or date is not found,
                     otherwise prints available time slots to the console and returns None.

    Example:
        list_available_appointment_hours("eylem", "30.04.2025")

    Notes:
        - Assumes clinic search and available appointments list are already displayed.
        - Requires an active Selenium session and prior login.
        - Uses `fetch_available_appointment_dates()` and `select_day()` to find valid dates.
        - Uses `list_all_available_hours_of_a_day()` to print time slots for the selected date.
    """
    check_login()
    
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"
    
    return fetch_available_appointment_dates()

@mcp.tool()
def list_available_appointment_time_slots(appointment_date):
    day = select_day(appointment_date)
    if not day:
        return f"Could not find available appointments on the date you are looking for: {appointment_date}"
    
    click_on_a_day(day)
    
    #list_all_available_hours_of_a_day(day)
    return fetch_all_available_time_slots_of_a_day()
    
@mcp.tool()
def book_appointment(appointment_hour):
    """
    Attempts to book an appointment at the specified hour.

    This function first selects the main hour block (e.g., "11") and then tries to select
    the specific sub-hour slot (e.g., "11:40"). If the slot is no longer available, it logs a message.
    If the slot is successfully selected, the function proceeds to confirm the appointment.

    Args:
        appointment_hour (str): The target appointment time in "HH:MM" format (e.g., "11:40")

    Returns:
        None

    Example:
        book_appointment("11:40")

    Notes:
        - Assumes that appointment date, doctor, and clinic have already been selected.
        - Assumes a logged-in Selenium session and that available appointment slots are visible.
        - Uses `select_main_hour_slot()` and `select_sub_hour_slot()` to find and select time.
        - Calls `accept_appointment()` only if the desired time slot is still available.
    """
    check_login()
    
    select_main_hour_slot(appointment_hour)
    if not select_sub_hour_slot(appointment_hour):
        print("Appointment booked by somebody else. Please choose another time slot.")
        return 
    accept_appointment()
    #if has_exceeded_max_appointments():
    #    print("it did exceed max count")
    #    return "You’ve reached the max number (2) of appointments. Please cancel one or wait for your next appointment before booking again."
    #else:
    #    return "Your appointment has been booked successfully."

def select_city(city_name):
    #city_name = unidecode(city_name).upper()  # Normalize and convert to uppercase
    city_name = normalize_string_to_upper(city_name)
    wait_loading_screen()

    city_found = False
    dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#il-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)")))
    wait_loading_screen()
    dropdown_span.click()  # Open the dropdown
    print("Dropdown clicked, waiting for options to appear")
    wait_loading_screen()

    city_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.ant-select-tree-treenode-switcher-open > span:nth-child(2)")))
    wait_loading_screen()

    for city in city_elements:
        print(city.text)
    
    print(f"looking for city {city_name}")
    # Use XPath to find the span with specific city name
    city_span = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{city_name}']")))
    wait_loading_screen()
    city_span.click()
    print(f"City {city_name} selected.")

def select_ilce(town_name):
    print("converting town to uppercase")
    town_name = normalize_string_to_upper(town_name)

    wait_loading_screen()
    print("trying to select dropdown")
    dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ant-select-selection__placeholder")))
    print("selected dropdown")
    wait_loading_screen()
    dropdown_span.click()
    print("Dropdown clicked, waiting for options to appear")
    wait_loading_screen()
    
    selector = "li.ant-select-dropdown-menu-item"
    print("selecting ilce elements")
    ilce_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
    print("selected ilce elements")
    for ilce in ilce_elements: 
        print(ilce.text)
    
    wait_loading_screen()
    town_span = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{town_name}']")))
    wait_loading_screen()
    town_span.click()
    print(f"Town {town_name} selected.")
    
    #all_ilce_elements = wait.until(EC.presence_of_all_elements_located(()))
def normalize_string_to_lower(string):
    return string.strip().replace("İ","i").lower()

def normalize_string_to_upper(string):
    return string.strip().replace("i","İ").upper()

def select_clinic(clinic_name):
    wait_loading_screen()
    print("selecting dropdown")
    dropdown_span = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#klinik-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)")))
    print("selected dropdown")
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "li.ant-select-dropdown-menu-item"))
    )

    wait_loading_screen()
    dropdown_span.click()
    print("clicked dropdown")
    
    print("trying to find out clinic span")        
    #clinic_span = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//span[contains((text()), '{clinic_name}')]")))
    clinic_spans = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[starts-with(@id, 'klinik')]")))
    clinic_spans = clinic_spans[1:]
    #this prints webelement object
    print(clinic_spans) 
    normalized_target = normalize_string_to_lower(clinic_name)
    print(f"looking for {normalized_target}")
    clinic_span = None
    
    for span in clinic_spans:
        # Get the text of each span and normalize it (lowercase)
        span_text = normalize_string_to_lower(span.text)
        print(f"Checking if '{normalized_target}' is in '{span_text}'")

        # If the target clinic name is found in the text of the current span, click it
        if normalized_target in span_text:
            clinic_span = span
            print(f"Found clinic: {span_text}")
            break  # Exit the loop once the clinic is found
        
    
    wait_loading_screen()
    print("trying to select clinic span")
    if clinic_span:
        print(f"found clinic span {clinic_span.text}")
        clinic_span.click()
        print(f"Clinic {clinic_name} selected.")
    else:
        print(f"Couldn't find a clinic matching '{clinic_name}'")


def select_hospital(hospital_name):
    print("trying to select hospital")
    dropdown_selector = "#hastane-tree-select > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)"
    wait_loading_screen()
    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
    wait_loading_screen()
    dropdown.click()
    print("clicked on dropdown")


    hospital_spans = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[starts-with(@id, 'hastane')]")))
    hospital_spans = hospital_spans[1:]
    print(f"found {len(hospital_spans)} amount of hospitals")
    wait_loading_screen()
    
    target_hospital_name = normalize_string_to_lower(hospital_name)
    hospital_span = None

    print(f"searching for target hospital {target_hospital_name}")    
    for span in hospital_spans:
        normalized_hospital_name = normalize_string_to_lower(span.text)
        if target_hospital_name in normalized_hospital_name:
            hospital_span = span
            break
    
    if hospital_span:
        wait_loading_screen()
        hospital_span.click()
        print(f"selected {hospital_span.text} hospital")
    else:
        print(f"failed to find target hospital {target_hospital_name}")


def click_on_appointment_search_button():
    id = "randevu-ara-buton"
    appointment_search_button = wait.until(EC.element_to_be_clickable((By.ID, id)))
    wait_loading_screen()
    appointment_search_button.click()
    wait_loading_screen()

def check_if_any_available_appointment():
    print("checking any available appointment")
    try:
        wait_loading_screen()
        # tries to find the pop-up message that displays "no available appointment found"
        no_appintmount_available_button = driver.find_element(By.CSS_SELECTOR, ".ant-modal-confirm-btns > button:nth-child(1)")
        print("found no appointment button")
        wait_loading_screen()
        wait.until(EC.element_to_be_clickable(no_appintmount_available_button))
        no_appintmount_available_button.click()
        print("no appointment found sorry")
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
    doctor_data = []
    
    # Print the text of each <li> element
    for li in li_elements:
        lines = li.text.strip().splitlines()
        doctor_info = {
                "doctor": lines[0],
                "earliest_date": lines[2],
                "days_left": lines[3],
                "hospital": lines[4],
                "department": lines[5],
                "clinic": lines[6]
            }
        doctor_data.append(doctor_info)

    doctors_json = json.dumps(doctor_data, ensure_ascii=False, indent=4)
    # Return the list of <li> elements
    return doctors_json

def select_doctor(doctor_name):
    print("trying to select a doctor")
    # Wait for the list of doctor names to be present in the DOM
    wait_loading_screen()
    doctor_spans = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, "li.ant-list-item > div > div > span"
    )))
    
    print(f"Found {len(doctor_spans)} doctor(s). Looking for {doctor_name}...")

    # Normalize the doctor name to lowercase for case-insensitive matching
    doctor_name_normalized = normalize_string_to_lower(doctor_name)

    # Iterate over each span and check if it contains the doctor name
    for doctor_span in doctor_spans:
        doctor_text = normalize_string_to_lower(doctor_span.text)
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

    available_dates_data = []
    # Iterate over each date div and print or interact with the content
    for date_div in date_divs:
        date_info = {
            "date": date_div.text.strip()
        }
        available_dates_data.append(date_info)

    dates_json = json.dumps(available_dates_data, ensure_ascii=False, indent=4)    
    print("DATES JSON:")
    print(dates_json)
    # Optionally return the div elements if you need to interact further
    return dates_json

def select_day(day):
    print("selecting day")
    parent_div_selector = "div.ant-tabs:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    parent_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, parent_div_selector)))
    date_divs = parent_div.find_elements(By.CSS_SELECTOR, "div > div")  # Adjust the selector as needed
    
    target_day = normalize_string_to_lower(day)
    for date_div in date_divs:
        normalized_date = normalize_string_to_lower(date_div.text)
        if target_day in normalized_date:
            print(f"found target day {target_day}")
            return date_div
    print(f"Could not find available appointments on the date you are looking for: {day}")
    return None

def fetch_all_available_time_slots_of_a_day():
    # Wait for all the divs inside .ant-tabs-tabpane to be present
    wait_loading_screen()
    
    clock_divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-tabs-tabpane > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div")))
    
    print(f"Found {len(clock_divs)} tab pane divs.")
    wait_loading_screen()
    
    full_hour_data = []
    # Iterate over each tab pane div and print or interact with the content
    for clock_div in clock_divs:
        main_hour_data = clock_div.text
        print(f"Tab content: {clock_div.text}")
        sub_hour_data = click_on_a_clock_and_list_details(clock_div)
        
        full_hour_info = {
            "main_hour": main_hour_data,    
            "sub_hours": sub_hour_data
        }
        full_hour_data.append(full_hour_info)
    
    full_hour_JSON = json.dumps(full_hour_data, ensure_ascii=False, indent=4)
    print("full hour JSON:")
    print(full_hour_JSON)
    # Optionally, return the div elements if you need to interact further
    return full_hour_JSON

def click_on_a_clock_and_list_details(clock_div):
    wait_loading_screen()
    clock_div.click()
    print(f"clicked on clock {clock_div.text.strip().split()[0]}")
    
    sub_hour_data = []
    clickable_buttons = clock_div.find_elements(By.CSS_SELECTOR, "div > button")
    for button in clickable_buttons:
        sub_hour_slot = {
            "sub_hour": button.text
        }
        print(f"button text is {button.text}")
        sub_hour_data.append(sub_hour_slot)
        
    return sub_hour_data
    


def click_on_a_day(day):
    print("trying to click on day")
    wait_loading_screen()
    day_div = wait.until(EC.element_to_be_clickable(day))
    wait_loading_screen()
    day_div.click()
    print(f"clicked on day {day.text}")

def select_clock_hour(target_hour, clock_divs):
    for clock_div in clock_divs:
        if target_hour in clock_div.text:
            return clock_div
    return None

def parse_main_hour(clock):
    return re.split(r'[:;,.]', clock.strip())[0]

def normalize_to_colon_format(time_str):
    parts = re.split(r'[:;,.]', time_str.strip())

    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0  # default to 0 if minute is missing

    return f"{hour:02d}:{minute:02d}"

# both clicks and returns the button
def select_main_hour_slot(target_clock):
    #input clock=16:20
    target_clock_hour = parse_main_hour(target_clock)
    print(f"clock is {target_clock_hour}")
    clock_divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-collapse-item")))
    for clock_div in clock_divs:
        if target_clock_hour in clock_div.text:
            print(f"found target clock {target_clock_hour} in {clock_div.text}")
            wait_loading_screen()
            clock_div.click()
            return clock_div
    
    return None

# both clicks and returns the button
def select_sub_hour_slot(target_clock):
    target_clock = normalize_to_colon_format(target_clock)
    #input clock=16:20
    #clickable_clock_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-collapse-content-active > div")))
    clickable_clock_buttons = driver.find_elements(By.CSS_SELECTOR, "div.ant-collapse-content-active button.slot-saat-button")
    print(f"found {len(clickable_clock_buttons)} time slot buttons")
    for button in clickable_clock_buttons:
        print(f"current button is {button.text} and looking for {target_clock}")
        if target_clock in button.text:
            print(f"found target clock {target_clock} in {button.text}")
            button.click()
            wait_loading_screen()
            return button
    return None

def click_button(button_selector):
    for attempt in range(3):
        try:
            wait_loading_screen()  # Ensure loading screen is gone first
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))).click()
            wait_loading_screen()  # Wait after click
            break

        except Exception as e:
            print(f"[!] Attempt {attempt + 1}: {type(e).__name__} - {e}")
            time.sleep(0.5)

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
    click_button(".ant-modal-confirm-btns > button:nth-child(1)") # ok button
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
    
    

def reject_appointment():
    print("executing reject_appointment func")
    button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
    click_button(button_selector)
    print("appointment REJECT button successfully clicked")


# appointment accept and max apponitment count buttons conflict. need a separator.
def has_exceeded_max_appointments():
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
        

def wait_loading_screen():
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ant-spin-spinning")))
    #wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-spin-spinning")))
    #wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-spin")))    
    #wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
def wait_warping():
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
    
def no_available_appointments():
    print("no available appointmens func started running")
    selector = ".ant-modal-confirm-btns > button:nth-child(1)"
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    wait_loading_screen()
    button.click()
    wait_loading_screen()
    print("no available appointmens func stopped running")

if __name__ == "__main__":
    print("server2 is running...")
    mcp.run(transport='stdio')