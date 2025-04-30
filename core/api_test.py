from mcp.server.fastmcp import FastMCP
import sys
import os

# Add the project root to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.clients.auth_client import AuthClient
from core.services.user_service import (
    select_city, select_ilce, select_clinic, select_hospital, 
    click_on_appointment_search_button, fetch_all_available_doctor_names,
    select_doctor, fetch_available_appointment_dates, 
    select_day, click_on_a_day, fetch_all_available_time_slots_of_a_day,
    select_main_hour_slot, select_sub_hour_slot
)
from core.services.appointment_service import (
    accept_appointment, reject_appointment, has_exceeded_max_appointments,
    cancel_appointment, revert_appointment, get_active_appointments
)
from core.clients.browser_client import BrowserClient

auth_client = AuthClient()
browser = BrowserClient()

def cancel_appointment_tool(appointment_identifier):
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
    return cancel_appointment(appointment_identifier)
   
def revert_appointment_tool(appointment_identifier):
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
    return revert_appointment(appointment_identifier)
  
def get_active_appointments_tool():
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
    return get_active_appointments()

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
    print(f"list_available_doctors city={city_name}, town={town_name}, clinic={clinic}, hospital={hospital}")
    browser.genel_randevu_arama()
    if select_city(city_name) and select_ilce(town_name) and select_clinic(clinic) and select_hospital(hospital):
        print("PASS")
        click_on_appointment_search_button()
        try:
            return fetch_all_available_doctor_names()
        except Exception as e:
            print(f"Error after search: {e}")
            try:
                browser.no_available_appointments()
                return "No available appointments found"
            except Exception:
                return "Error occurred during doctor search"
    return "Unable to select search criteria"

def list_available_appointment_dates(doctor_name):
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
    if select_doctor(doctor_name):
        try:
            return fetch_available_appointment_dates()
        except Exception as e:
            print(f"Error fetching dates: {e}")
            return "Error fetching appointment dates"
    return f"Could not find doctor: {doctor_name}"

def list_available_appointment_time_slots(appointment_date):
    """
    Lists all available time slots for a specified appointment date.

    Args:
        appointment_date (str): The date to check availability for

    Returns:
        str: JSON string containing available time slots
    
    Example:
        list_available_appointment_time_slots("30.04.2025")
        
    Notes:
        - Assumes the user is already logged in via Selenium session.
        - Assumes doctor and clinic are already selected.
    """
    day_div = select_day(appointment_date)
    
    if day_div:
        click_on_a_day(day_div)
        return fetch_all_available_time_slots_of_a_day()
    return f"Could not find available appointments on date: {appointment_date}"

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
    
    if select_main_hour_slot(appointment_hour) and select_sub_hour_slot(appointment_hour):
        if has_exceeded_max_appointments():
            return "You have exceeded the maximum number of appointments"
        accept_appointment()
        return f"Successfully booked appointment at {appointment_hour}"
    return f"Could not book appointment at {appointment_hour}"

def list_available_appointment_dates_for_a_doctor(doctor_name):
    auth_client.check_login()
    if not select_doctor(doctor_name):
        return f"Could not find the doctor you are looking for: {doctor_name}"
    
    return fetch_available_appointment_dates()

def list_available_appointment_hours(appointment_date):
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
    auth_client.check_login()
    
    day = select_day(appointment_date)
    if not day:
        return f"Could not find available appointments on the date you are looking for: {appointment_date}"
    
    click_on_a_day(day)
    
    #list_all_available_hours_of_a_day(day)
    return fetch_all_available_time_slots_of_a_day()

if __name__ == "__main__":
    """
    Runs the MCP server for handling appointment-related requests.
    """
    print("MHRS appointment server is running...")
    get_active_appointments()
    list_available_doctors("İZMİR", "URLA", "CİLDİYE", "URLA")
    list_available_appointment_dates_for_a_doctor("eylem")
    #list_available_appointment_hours("06.05.2025")
    #book_appointment("13.20")
