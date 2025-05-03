from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import json
from core.clients.browser_client import BrowserClient
from utils.string_utils import normalize_string_to_lower
from core.clients.auth_client import AuthClient

from core.services.user_service import (
    select_city, select_ilce, select_clinic, select_hospital, 
    click_on_appointment_search_button, fetch_all_available_doctor_names,
    select_doctor, fetch_available_appointment_dates, 
    select_day, click_on_a_day, fetch_all_available_time_slots_of_a_day,
    select_main_hour_slot, select_sub_hour_slot
)

browser = BrowserClient()
auth_client = AuthClient()

def accept_appointment():
    print("executing accept_appointment func")
    button_selector = ".ant-modal-confirm-btns > button:nth-child(2)"
    browser.click_button(button_selector)
    print("appointment ACCEPT button successfully clicked")

    # Inner function to verify appointment
    def verify_appointment():
        print("executing verify_appointment func")
        button_selector = ".ant-modal-footer > div:nth-child(1) > button:nth-child(2)"
        browser.click_button(button_selector)
        print("appointment VERIFY button successfully clicked")
        
    verify_appointment()
    force_appointment()

def has_successfully_booked_appointment():
    success_code = "RND5036"
    div_selector = ".ant-modal-confirm > div:nth-child(2)"
    try:
        element = browser.driver.find_element(By.CSS_SELECTOR, div_selector)
        if success_code in element.text:
            #click ok
            ok_button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
            browser.click_button(ok_button_selector)
            print("successfully booked appointment")
            return True
        else:
            print("failed to book appointment")
            return False
    except Exception as e:
        print("failed to book appointment with error", e)
        return False

def has_available_appointment():
    NO_APPOINTMENT_CODE = "RND4010"
    MODAL_SELECTOR = ".ant-modal-body"
    OK_BUTTON_SELECTOR = ".ant-modal-confirm-btns > button:nth-child(1)"

    try:
        element = browser.driver.find_element(By.CSS_SELECTOR, MODAL_SELECTOR)
        if NO_APPOINTMENT_CODE in element.text:
            browser.click_button(OK_BUTTON_SELECTOR)
            print("No available appointments (RND4010).")
            return False
        else:
            print("Modal found but RND4010 not in message. Appointments may be available.")
            return True

    except NoSuchElementException:
        print("No modal found — assuming appointments may be available.")
        return True

    except Exception as e:
        print("Unexpected error checking appointments:", e)
        return False  # or raise, depending on desired behavior

def reject_appointment():
    print("executing reject_appointment func")
    button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
    browser.click_button(button_selector)
    print("appointment REJECT button successfully clicked")

# if exceeded max appointment    count, enforce replacement appointment taking
def force_appointment():
    randevu_degistirme_pop_up_code = "RND5015"
    exceeded_max_app_count_pop_up_selector = "div.ant-modal-body:nth-child(2)"
    try:
        element = browser.driver.find_element(By.CSS_SELECTOR, exceeded_max_app_count_pop_up_selector)
        if randevu_degistirme_pop_up_code in element.text:
            print("found text", element.text)
            ok_button_selector = ".ant-modal-confirm-btns > button:nth-child(2)"
            browser.click_button(ok_button_selector)
            return True
        else:
            print("max count exceeded pop up did not appear")
            return False
    except Exception:
        print("max count exceeded pop up did not appear")
        return False

def cancel_appointment(appointment_identifier):
    auth_client.check_login()
    
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
    """
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing cancel appointment func for identifier {appointment_identifier}")
    try:
    # navigate to mainpage
        browser.driver.get("https://mhrs.gov.tr/vatandas/#/")
            
        browser.driver.find_element(By.CSS_SELECTOR, ".ant-list-items")
        
        appointments = browser.driver.find_elements(By.CSS_SELECTOR, ".ant-list-items li")
        browser.wait_loading_screen()
        for appointment in appointments:
            if appointment_identifier in normalize_string_to_lower(appointment.text) and "Geri Alınabilir Randevu" not in appointment.text:
                browser.click_button(".ant-btn-danger") # cancel button
                browser.click_button(".ant-btn-primary") # verify button
                browser.click_button(".ant-btn-primary") # ok button
                return True
        return False
    except Exception as e:  
        print(e)
        print(f"You don't have any appointments to cancel for identifier {appointment_identifier}.")
        return False

def revert_appointment(appointment_identifier):
    auth_client.check_login()
    
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
    """
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing revert appointment func for identifier {appointment_identifier}")
    # navigate to mainpage
    
    try:
        browser.driver.get("https://mhrs.gov.tr/vatandas/#/")
            
        browser.driver.find_element(By.CSS_SELECTOR, ".ant-list-items")
        
        appointments = browser.driver.find_elements(By.CSS_SELECTOR, ".ant-list-items li")
        browser.wait_loading_screen()
        for appointment in appointments:
            if appointment_identifier in normalize_string_to_lower(appointment.text):
                browser.click_button(".ant-btn-primary") # cancel button
                browser.click_button(".ant-modal-confirm-btns > button:nth-child(1)") # ok button
                return True
        return False
    except Exception as e:
        print(e)
        print(f"You don't have any revertable appointments for identifier {appointment_identifier}, sorry :/")
        return False

def get_active_appointments():
    """
    Fetches and returns a list of active appointments for the currently logged-in user from the MHRS system.

    Returns:
        str or None: A JSON-formatted string containing the user's active appointment data.
                     If no appointments are found or an error occurs, returns None and logs the error.
    """
    auth_client.check_login()
    print("logged in")
        
    try:
        
        browser.driver.get("https://mhrs.gov.tr/vatandas/#/")
        
        browser.wait_loading_screen() 
    
        browser.driver.find_element(By.CSS_SELECTOR, ".ant-list-items li")
        appointments_list = browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-list-items li")))
        
        print("appointments_list size:", len(appointments_list))
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
        print(appointments_json)
        
        return appointments_json
    except Exception as e:
        print(f"Error fetching active appointments: {e}")
        return False
        #return json.dumps([], ensure_ascii=False) 
        
def appointment_doctor_available(city_name, town_name, clinic, hospital):
    auth_client.check_login()
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
    print(f"list_available_doctors city={city_name}, town={town_name}, clinic={clinic}, hospital={hospital}")
    browser.genel_randevu_arama()
    browser.wait_warping() #works
    if select_city(city_name) and select_ilce(town_name) and select_clinic(clinic) and select_hospital(hospital):
        print("PASS")
        click_on_appointment_search_button()
        if has_available_appointment():
            try:
                return fetch_all_available_doctor_names()
            except Exception as e:
                print(f"Error after search: {e}")
                return False
    return False

def appointment_book_time(appointment_hour):
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
    
    if select_main_hour_slot(appointment_hour) and select_sub_hour_slot(appointment_hour):
        accept_appointment()
        return has_successfully_booked_appointment()
    print(f"Could not book appointment at {appointment_hour}")
    return False

def appointment_doctor_available_dates(doctor_name):
    """
    Lists all available appointment dates for a given doctor.

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
    auth_client.check_login()
    if not select_doctor(doctor_name):
        print(f"Could not find the doctor you are looking for: {doctor_name}")
        return False
    
    return fetch_available_appointment_dates()

def appointment_available_hours_on(appointment_date):
    auth_client.check_login()
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
        list_available_appointment_hours("30.04.2025")

    Notes:
        - Assumes clinic search and available appointments list are already displayed.
        - Requires an active Selenium session and prior login.
        - Uses `fetch_available_appointment_dates()` and `select_day()` to find valid dates.
        - Uses `list_all_available_hours_of_a_day()` to print time slots for the selected date.
    """
    
    day = select_day(appointment_date)
    if not day:
        print(f"Could not find available appointments on the date you are looking for: {appointment_date}")
        return False
    
    click_on_a_day(day)
    
    #list_all_available_hours_of_a_day(day)
    return fetch_all_available_time_slots_of_a_day()