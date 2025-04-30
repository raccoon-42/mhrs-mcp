from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
from core.clients.browser_client import BrowserClient
from utils.string_utils import normalize_string_to_lower
from core.clients.auth_client import AuthClient

browser = BrowserClient()
client = AuthClient()

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
    browser.click_button(".ant-modal-confirm-btns > button:nth-child(1)") # ok button
    browser.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))

def reject_appointment():
    print("executing reject_appointment func")
    button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
    browser.click_button(button_selector)
    print("appointment REJECT button successfully clicked")

def has_exceeded_max_appointments():
    exceeded_max_app_count_pop_up_selector = "div.ant-modal-body:nth-child(2)"
    try:
        browser.driver.find_element(By.CSS_SELECTOR, exceeded_max_app_count_pop_up_selector)
        # assume pop up appeared
        ok_button_selector = ".ant-modal-confirm-btns > button:nth-child(1)"
        browser.click_button(ok_button_selector)
        print("clicked ok on max app count exceeded button")
        return True
    except Exception:
        print("max count exceeded pop up did not appear")
        return False

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
    """
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing cancel appointment func for identifier {appointment_identifier}")
    try:
    # navigate to mainpage
        if not browser.driver.current_url == "https://mhrs.gov.tr/vatandas/#/":
            browser.driver.get("https://mhrs.gov.tr/vatandas/#/")
            
        browser.driver.find_element(By.CSS_SELECTOR, ".ant-list-items")
        
        appointments = browser.driver.find_elements(By.CSS_SELECTOR, ".ant-list-items li")
        browser.wait_loading_screen()
        for appointment in appointments:
            if appointment_identifier in normalize_string_to_lower(appointment.text):
                browser.click_button(".ant-btn-danger") # cancel button
                browser.click_button(".ant-btn-primary") # verify button
                browser.click_button(".ant-btn-primary") # ok button
                return True
        return False
    except Exception as e:
        print(e)
        print("You don't have any appointments to cancel.")
        return "You don't have any appointments to cancel."

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
    """
    
    appointment_identifier = normalize_string_to_lower(appointment_identifier)
    print(f"executing revert appointment func for identifier {appointment_identifier}")
    # navigate to mainpage
    
    try:
        if not browser.driver.current_url == "https://mhrs.gov.tr/vatandas/#/":
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
        print("You dont have any revertable appointments.")
        return "You don't have any revertable appointments, sorry :/"

def get_active_appointments():
    """
    Fetches and returns a list of active appointments for the currently logged-in user from the MHRS system.

    Returns:
        str or None: A JSON-formatted string containing the user's active appointment data.
                     If no appointments are found or an error occurs, returns None and logs the error.
    """
    client.check_login()
    print("logged in")
        
    try:
        
        browser.driver.get("https://mhrs.gov.tr/vatandas/#/")
        
        browser.wait_loading_screen() 
    
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
        return json.dumps([], ensure_ascii=False) 