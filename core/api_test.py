from mcp.server.fastmcp import FastMCP
import sys
import os

# Add the project root to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.clients.auth_client import AuthClient

from core.services.appointment_service import (
    cancel_appointment, revert_appointment, get_active_appointments,
    appointment_doctor_available,
    appointment_doctor_available_dates,
    appointment_available_hours_on,
    appointment_book_time,
)
from core.clients.browser_client import BrowserClient

auth_client = AuthClient()
browser = BrowserClient()

mcp = FastMCP("mhrs")

@mcp.tool()
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
   
@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
def appointment_book_tool(city="İZMİR", district="URLA", specialty="CİLDİYE", hospital="URLA", doctor_name="eylem", date="09.05.2025", time="15.40"):
    if not appointment_doctor_available(city, district, specialty, hospital):
        print("No doctors available.")
        return False

    if not appointment_doctor_available_dates(doctor_name):
        print("No available dates for the doctor.")
        return False

    if not appointment_available_hours_on(date):
        print("No available hours on the selected date.")
        return False

    if not appointment_book_time(time):
        print("Failed to book appointment at the selected time.")
        return False

    print("Appointment successfully booked!")
    return True

@mcp.tool()
def appointment_check_hours_tool(city="İZMİR", district="URLA", specialty="CİLDİYE", hospital="URLA", doctor_name="eylem", date="09.05.2025"):
    if not appointment_doctor_available(city, district, specialty, hospital):
        print("No doctors available.")
        return False

    if not appointment_doctor_available_dates(doctor_name):
        print("No available dates for the doctor.")
        return False

    if not appointment_available_hours_on(date):
        print("No available hours on the selected date.")
        return False
    return True
    
@mcp.tool()
def appointment_check_dates_tool(city="İZMİR", district="URLA", specialty="CİLDİYE", hospital="URLA", doctor_name="eylem"):
    if not appointment_doctor_available(city, district, specialty, hospital):
        print("No doctors available.")
        return False

    if not appointment_doctor_available_dates(doctor_name):
        print("No available dates for the doctor.")
        return False
    return True
    
@mcp.tool()
def appointment_check_doctor_tool(city="İZMİR", district="URLA", specialty="CİLDİYE", hospital="URLA"):
    if not appointment_doctor_available(city, district, specialty, hospital):
        print("No doctors available.")
        return False
    return True
    
if __name__ == "__main__":
    """
    Runs the MCP server for handling appointment-related requests.
    """
    print("MHRS appointment server is running...")
    print(appointment_book_tool())
    #browser.wait_warping()
    #print(cancel_appointment_tool("eylem")) #works
    #print(revert_appointment_tool("eylem")) #works
    