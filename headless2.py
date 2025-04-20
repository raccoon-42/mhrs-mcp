from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import os
from dotenv import load_dotenv
import json 
import re
# Set the locale to Turkish
# Load environment variables
load_dotenv()

os.environ["webdriver.gecko.driver"] = "/opt/homebrew/bin/geckodriver"

# Set up Firefox options for headless mode
options = Options()
#options.headless = True  # Enable headless mode
#options.add_argument("--headless")

# URL and credentials
url = "https://mhrs.gov.tr/vatandas/#/"
username = os.getenv("MHRS_USERNAME")
password = os.getenv("MHRS_PASSWORD")

# Set up Firefox WebDriver with headless option
#driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
#driver = webdriver.Firefox(service=Service("/opt/homebrew/bin/geckodriver"), options=options)
driver = webdriver.Firefox(options=options)
driver.get(url)

print("Waiting for driver")
wait = WebDriverWait(driver, 30)

def test():
    def login():
        username_input = wait.until(EC.presence_of_element_located((By.ID, "LoginForm_username")))
        username_input.send_keys(username)
        print("Entered username")

        password_input = wait.until(EC.presence_of_element_located((By.ID, "LoginForm_password")))
        password_input.send_keys(password)
        print("Entered password")
        # Wait until spinner is gone
        print("Waiting for button to become clickable")
        wait_loading_screen()

        # Now click the login button
        click_button(".ant-btn.ant-btn-teal.ant-btn-block") #login button selector
        print("Login button clicked")
        wait_loading_screen() # wait until loggin in
    
    login()
    # ?
    click_button(".ant-modal-confirm-btns > button:nth-child(1)") #neyim var button
    print("neyim var button clicked to refuse")
    
    print("----------------------------------")
    print("TESTING")
   
    print("----------------------------------")
    list_available_doctors("İZMİR", "URLA", "CİLDİYE", "URLA")
    print("----------------------------------")
    list_available_appointment_hours("eylem", "30.04.2025")
    print("----------------------------------")
    book_appointment("11.40")


    #wait_warping() # did not work
    
    print("trying to get active appointments")
    get_active_appointments()
    #print("trying to cancel an appointments")
    #cancel_appointment("eylem")
    #print("run cancel app func")
    
    #revert_appointment("eylem")
    
    
def search_doctor(doctor_name):
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"

def cancel_appointment(appointment_identifier):
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
   

def revert_appointment(appointment_identifier):    
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
  

def get_active_appointments():
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
    

def list_available_doctors(city_name, town_name, clinic, hospital):
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
        fetch_all_available_doctor_names()
    else:
        return f"There are no available appointments to book for clinic {clinic}."
    
def list_available_appointment_hours(doctor_name, appointment_date):
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"
    
    days = fetch_available_appointment_dates()

    day = select_day(appointment_date, days)
    if not day:
        return f"Could not find available appointments on the date you are looking for: {appointment_date}"
    
    click_on_a_day(day)
    
    #list_all_available_hours_of_a_day(day)
    list_all_available_hours_of_a_day()
    
def book_appointment(appointment_hour):
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
        span_text = span.text.strip().lower()
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
        normalized_hospital_name = span.text.strip().lower()
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
    print("fetching available doctors")
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
print
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

import time 

def click_button(button_selector):
    for attempt in range(3):
        try:
            wait_loading_screen()  # Ensure loading screen is gone first

            # Re-fetch element each time
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
            
            button.click()
            print(f"[✓] Button '{button.text}' successfully clicked.")
            
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

# Close the browser
print("Opening website")
test()
#driver.quit()