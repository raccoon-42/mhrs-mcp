from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re
from core.clients.browser_client import BrowserClient
from utils.string_utils import normalize_string_to_lower, normalize_string_to_upper, parse_main_hour, normalize_to_hour_format

from utils.selection_status import SelectionStatus
browser = BrowserClient()

def select_city(city_name):
    # Normalize and convert to uppercase
    city_name = normalize_string_to_upper(city_name)
    try:
        # Select the div container for the city dropdown
        browser.wait_loading_screen()
        city_selection = browser.wait.until(EC.element_to_be_clickable((By.ID, 'il-tree-select'))).click()
        browser.wait_loading_screen()

        # Find list items within the dropdown
        city_items = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ant-select-tree li')))
        
        print("traversing city names")
        # Click on the city that matches our criteria
        for city in city_items:
            print(f"city name is {city.text}")
            if city_name in normalize_string_to_upper(city.text):
                city.click()
                print(f"Selected city: {city.text}")
                browser.wait_loading_screen()
                return SelectionStatus.SUCCESS
        
        print(f"City not found: {city_name}")
        return SelectionStatus.CITY_NOT_FOUND
    except Exception as e:
        print(f"Error selecting city: {e}")
        return SelectionStatus.ERROR

def select_ilce(town_name):
    # Normalize and convert to uppercase
    town_name = normalize_string_to_upper(town_name)
    try:
        # Select the div container for the town dropdown
        browser.wait_loading_screen()
        town_selection = browser.wait.until(EC.element_to_be_clickable((By.ID, 'randevuAramaForm_ilce'))).click()
        browser.wait_loading_screen()

        # Find list items within the dropdown
        town_items = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ant-select-dropdown-menu li')))
        
        # Click on the town that matches our criteria
        for town in town_items:
            print(f"town name is {town.text}")
            if town_name in normalize_string_to_upper(town.text):
                town.click()
                print(f"Selected town: {town.text}")
                browser.wait_loading_screen()
                return SelectionStatus.SUCCESS
        
        print(f"Town not found: {town_name}")
        return SelectionStatus.TOWN_NOT_FOUND
    except Exception as e:
        print(f"Error selecting town: {e}")
        return SelectionStatus.ERROR

def select_clinic(clinic_name):
    # Normalize and convert to uppercase
    clinic_name = normalize_string_to_upper(clinic_name)
    try:
        # Select the div container for the clinic dropdown
        browser.wait_loading_screen()
        clinic_selection = browser.wait.until(EC.element_to_be_clickable((By.ID, 'klinik-tree-select'))).click()
        browser.wait_loading_screen()

        # Find list items within the dropdown
        clinic_items = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#rc-tree-select-list_2 > ul:nth-child(2) > li')))
        
        # Debug print
        print(f"Found {len(clinic_items)} clinic options")
        # Click on the clinic that matches our criteria
        for clinic in clinic_items:
            print(f"Clinic : {clinic.text}")
            print(f"trying to find: {normalize_string_to_upper(clinic.text)} for {clinic_name}")
            if clinic_name in normalize_string_to_upper(clinic.text):
                clinic.click()
                print(f"Selected clinic: {clinic.text}")
                browser.wait_loading_screen()
                return SelectionStatus.SUCCESS
        
                
        print(f"Clinic not found: {clinic_name}")
        return SelectionStatus.CLINIC_NOT_FOUND
    except Exception as e:
        print(f"Error selecting clinic: {e}")
        return SelectionStatus.ERROR

def select_hospital(hospital_name):
    hospital_name = normalize_string_to_upper(hospital_name)
    try:
        # Set the hospital dropdown to be focused
        browser.wait_loading_screen()
        hospital_selection = browser.wait.until(EC.element_to_be_clickable((By.ID, 'hastane-tree-select'))).click()
        browser.wait_loading_screen()

        # Find list items within the dropdown
        hospital_items = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#rc-tree-select-list_3 > ul:nth-child(2) > li')))
        
        # Debug print
        print(f"Found {len(hospital_items)} hospital options")
        for h in hospital_items:
            print(f"Hospital option: {h.text}")
            
        # Click on the hospital that matches our criteria
        for hospital in hospital_items:
            if hospital_name in normalize_string_to_upper(hospital.text):
                hospital.click()
                print(f"Selected hospital: {hospital.text}")
                browser.wait_loading_screen()
                return SelectionStatus.SUCCESS 
                
        print(f"Hospital not found: {hospital_name}")
        return SelectionStatus.HOSPITAL_NOT_FOUND
    except Exception as e:
        print(f"Error selecting hospital: {e}")
        return SelectionStatus.ERROR
    
def genel_randevu_arama():
    browser.wait_loading_screen()

    browser.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
    
    hasta_randevusu_button = browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.randevu-card-dissiz:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)")))
    hasta_randevusu_button.click()
    browser.wait_loading_screen()
    
    genel_arama_button = browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.randevu-turu-button:nth-child(1)")))
    genel_arama_button.click()

def click_on_appointment_search_button():
    button_selector = "#randevu-ara-buton"
    browser.click_button(button_selector)
    browser.wait_loading_screen()
    return True

def check_if_any_available_appointment():
    try:
        browser.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ant-list-items")))
        return True
    except Exception:
        return False

def fetch_all_available_doctor_names():
    try:
        print("fetching available doctors")
        ul_selector = ".ant-list-items"
        # Wait for the <ul> element to be present in the DOM
        ul_element = browser.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector)))
        
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
        print("Doctors (JSON):")
        print(doctors_json)
        # Return the list of <li> elements
        return doctor_data
    except Exception as e:
        print(f"Error fetching doctor names: {e}")
        return False
        #return json.dumps([], ensure_ascii=False)

def select_doctor(doctor_name):
    try:
        print(f"selecting doctor: {doctor_name}")
        doctor_name = normalize_string_to_lower(doctor_name)
        doctor_list = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-list-items li")))
        
        for doctor_item in doctor_list:
            #doctor_name_div = doctor_item.find_element(By.CSS_SELECTOR, "div:nth-child(3) > div:nth-child(1)")
            if doctor_name in normalize_string_to_lower(doctor_item.text):
                doctor_item.click()
                print(f"Selected doctor: {doctor_item.text}")
                browser.wait_loading_screen()
                return True
        
        print(f"Doctor not found: {doctor_name}")
        return False
    except Exception as e:
        print(f"Error selecting doctor: {e}")
        return False

def fetch_available_appointment_dates():
    try:
        browser.wait_loading_screen()
        # Select all date divs within the appointment calendar
        date_divs = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-tabs-tab")))
        print(f"found {len(date_divs)} date divs")
        available_dates_data = []
        for date_div in date_divs:
            date_text = date_div.text
            if date_text.strip():  # Only process non-empty date divs
                date_info = {
                    "date": date_text
                }
                available_dates_data.append(date_info)

        dates_json = json.dumps(available_dates_data, ensure_ascii=False, indent=4)    
        print("DATES JSON:")
        print(dates_json)
        return available_dates_data
    except Exception as e:
        print(f"Error fetching appointment dates: {e}")
        return json.dumps([], ensure_ascii=False)

def select_day(day):
    print("selecting day")
    parent_div_selector = "div.ant-tabs:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    parent_div = browser.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, parent_div_selector)))
    date_divs = parent_div.find_elements(By.CSS_SELECTOR, "div > div")  # Adjust the selector as needed
    
    target_day = normalize_string_to_lower(day)
    for date_div in date_divs:
        normalized_date = normalize_string_to_lower(date_div.text)
        if target_day in normalized_date:
            print(f"found target day {target_day}")
            return date_div
    print(f"Could not find available appointments on the date you are looking for: {day}")
    return None

def click_on_a_day(day):
    print("trying to click on day")
    browser.wait_loading_screen()
    day_div = browser.wait.until(EC.element_to_be_clickable(day))
    browser.wait_loading_screen()
    day_div.click()
    print(f"clicked on day {day.text}")

def fetch_all_available_time_slots_of_a_day():
    # Wait for all the divs inside .ant-tabs-tabpane to be present
    browser.wait_loading_screen()
    
    clock_divs = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-tabs-tabpane > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div")))
    
    print(f"Found {len(clock_divs)} tab pane divs.")
    browser.wait_loading_screen()
    
    full_hour_data = []
    # Iterate over each tab pane div and print or interact with the content
    for clock_div in clock_divs:
        main_hour_data = clock_div.text
        print(f"Tab content: {clock_div.text}")
        sub_hour_data = click_on_a_clock_and_list_details(clock_div)
        
        if not sub_hour_data:
            continue
        
        full_hour_info = {
            "main_hour": main_hour_data,    
            "sub_hours": sub_hour_data
        }
        full_hour_data.append(full_hour_info)
    
    full_hour_JSON = json.dumps(full_hour_data, ensure_ascii=False, indent=4)
    print("full hour JSON:")
    print(full_hour_JSON)
    return full_hour_data

def click_on_a_clock_and_list_details(clock_div):
    browser.wait_loading_screen()
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

def select_clock_hour(target_hour, clock_divs):
    for clock_div in clock_divs:
        if target_hour in clock_div.text:
            return clock_div
    return None

# both clicks and returns the button
def select_main_hour_slot(target_clock):
    #input clock=16:20
    target_clock_hour = parse_main_hour(target_clock)
    print(f"clock is {target_clock_hour}")
    clock_divs = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ant-collapse-item")))
    for clock_div in clock_divs:
        if target_clock_hour in clock_div.text:
            print(f"found target clock {target_clock_hour} in {clock_div.text}")
            browser.wait_loading_screen()
            clock_div.click()
            return clock_div
    
    return None

# both clicks and returns the button
def select_sub_hour_slot(target_clock):
    target_clock = normalize_to_hour_format(target_clock)
    #input clock=16:20
    #clickable_clock_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-collapse-content-active > div")))
    clickable_clock_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "div.ant-collapse-content-active button.slot-saat-button")
    print(f"found {len(clickable_clock_buttons)} time slot buttons")
    for button in clickable_clock_buttons:
        print(f"current button is {button.text} and looking for {target_clock}")
        if target_clock in button.text:
            print(f"found target clock {target_clock} in {button.text}")
            button.click()
            browser.wait_loading_screen()
            return button
    return None 