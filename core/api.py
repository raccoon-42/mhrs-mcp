from mcp.server.fastmcp import FastMCP
import sys
import os

# Add the project root to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.clients.auth_client import AuthClient

from utils.appointment_status import AppointmentStatus
from utils.selection_status import SelectionStatus

from core.services.appointment_service import (
    cancel_appointment, revert_appointment, get_active_appointments,
    appointment_doctor_available,
    appointment_doctor_available_dates,
    appointment_available_hours_on,
    appointment_book_time,
    accept_notification_modal,
    get_modal_text_if_present,
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
def appointment_book_tool(city, district, specialty, hospital, doctor_name, date, time):
    """
    Books an appointment with a specific doctor at a given time and date.

    This function performs a complete booking flow:
    1. Checks doctor availability in the specified location
    2. Verifies available dates for the doctor
    3. Checks available hours on the selected date
    4. Attempts to book the appointment at the specified time

    Args:
        city (str): City where the hospital is located (e.g., "İZMİR")
        district (str): District where the hospital is located (e.g., "URLA")
        specialty (str): Medical specialty (e.g., "CİLDİYE")
        hospital (str): Name of the hospital (e.g., "URLA")
        doctor_name (str): Doctor's name (e.g., "eylem")
        date (str): Appointment date in "DD.MM.YYYY" format (e.g., "09.05.2025")
        time (str): Appointment time in "HH:MM" format (e.g., "15:40")

    Returns:
        dict: A dictionary containing:
            - 'status' (Status): Result of the booking attempt
            - Additional fields may be present based on the status

    Example:
        >>> result = appointment_book_tool(
        ...     city="İZMİR",
        ...     district="URLA",
        ...     specialty="CİLDİYE",
        ...     hospital="URLA",
        ...     doctor_name="eylem",
        ...     date="09.05.2025",
        ...     time="15:40"
        ... )
        >>> print(result)
        {'status': Status.SUCCESS}
    """
    response = appointment_doctor_available(city, district, specialty, hospital)
    if not response["status"] == SelectionStatus.SUCCESS:
        return response

    if not appointment_doctor_available_dates(doctor_name):
        return {"status": AppointmentStatus.NO_DOCTOR_AVAILABLE}   

    if not appointment_available_hours_on(date):
        return {"status": AppointmentStatus.NO_DATE_AVAILABLE_FOR_DOCTOR}

    if not appointment_book_time(time):
        return {"status": AppointmentStatus.NO_AVAILABLE_HOURS_ON_DATE}

    return {"status": AppointmentStatus.SUCCESS}

@mcp.tool()
def appointment_check_hours_tool(city, district, specialty, hospital, doctor_name, date):
    """
    Checks available appointment hours for a specific doctor on a given date.

    This function:
    1. Verifies doctor availability in the specified location
    2. Checks if the doctor has available dates
    3. Retrieves all available time slots for the specified date

    Args:
        city (str): City where the hospital is located (e.g., "İZMİR")
        district (str): District where the hospital is located (e.g., "URLA")
        specialty (str): Medical specialty (e.g., "CİLDİYE")
        hospital (str): Name of the hospital (e.g., "URLA")
        doctor_name (str): Doctor's name (e.g., "eylem")
        date (str): Date to check in "DD.MM.YYYY" format (e.g., "09.05.2025")

    Returns:
        dict: A dictionary containing:
            - 'status' (Status): Result of the availability check
            - 'data' (list): Available time slots if successful

    Example:
        >>> result = appointment_check_hours_tool(
        ...     city="İZMİR",
        ...     district="URLA",
        ...     specialty="CİLDİYE",
        ...     hospital="URLA",
        ...     doctor_name="eylem",
        ...     date="09.05.2025"
        ... )
        >>> print(result)
        {
            'status': Status.SUCCESS,
            'data': ['09:00', '09:20', '09:40', '10:00']
        }
    """
    response = appointment_doctor_available(city, district, specialty, hospital)
    if not response["status"] == SelectionStatus.SUCCESS:
        return response

    if not appointment_doctor_available_dates(doctor_name):
        return {"status": AppointmentStatus.NO_DATE_AVAILABLE}

    available_hours = appointment_available_hours_on(date)
    if not available_hours:
        return {"status": AppointmentStatus.NO_DATE_AVAILABLE_FOR_DOCTOR}
    
    return {"status": AppointmentStatus.SUCCESS, "data": available_hours}
    
@mcp.tool()
def appointment_check_dates_tool(city, district, specialty, hospital, doctor_name):
    """
    Retrieves available appointment dates for a specific doctor.

    This function:
    1. Verifies doctor availability in the specified location
    2. Retrieves all available dates for the doctor

    Args:
        city (str): City where the hospital is located (e.g., "İZMİR")
        district (str): District where the hospital is located (e.g., "URLA")
        specialty (str): Medical specialty (e.g., "CİLDİYE")
        hospital (str): Name of the hospital (e.g., "URLA")
        doctor_name (str): Doctor's name (e.g., "eylem")

    Returns:
        dict: A dictionary containing:
            - 'status' (Status): Result of the date check
            - 'data' (list): Available dates if successful

    Example:
        >>> result = appointment_check_dates_tool(
        ...     city="İZMİR",
        ...     district="URLA",
        ...     specialty="CİLDİYE",
        ...     hospital="URLA",
        ...     doctor_name="eylem"
        ... )
        >>> print(result)
        {
            'status': Status.SUCCESS,
            'data': ['09.05.2025', '10.05.2025', '11.05.2025']
        }
    """
    response = appointment_doctor_available(city, district, specialty, hospital)
    if not response["status"] == SelectionStatus.SUCCESS:
        return response

    available_dates = appointment_doctor_available_dates(doctor_name)
    if not available_dates:
        return {"status": AppointmentStatus.NO_DATE_AVAILABLE_FOR_DOCTOR}
   
    return {"status": AppointmentStatus.SUCCESS, "data": available_dates}
    
@mcp.tool()
def appointment_check_doctor_tool(city, district, specialty, hospital):
    """
    Checks for available doctors in a specified location and specialty.

    This function:
    1. Verifies the location and specialty combination
    2. Retrieves a list of available doctors

    Args:
        city (str): City where the hospital is located (e.g., "İZMİR")
        district (str): District where the hospital is located (e.g., "URLA")
        specialty (str): Medical specialty (e.g., "CİLDİYE")
        hospital (str): Name of the hospital (e.g., "URLA")

    Returns:
        dict: A dictionary containing:
            - 'status' (Status): Result of the doctor check
            - 'data' (list): List of available doctors if successful
            - 'details' (str, optional): Error details if unsuccessful

    Example:
        >>> result = appointment_check_doctor_tool(
        ...     city="İZMİR",
        ...     district="URLA",
        ...     specialty="CİLDİYE",
        ...     hospital="URLA"
        ... )
        >>> print(result)
        {
            'status': Status.SUCCESS,
            'data': ['Dr. Eylem Yılmaz', 'Dr. Ali Kaya']
        }
    """
    result = appointment_doctor_available(city, district, specialty, hospital)
    
    return result
    
@mcp.tool()
def accept_notification_modal_tool():
    """
    Accepts the notification modal that appears when an appointment is not available.

    This function is usable when a status code with Status.NOTIFY_WHEN_AVAILABLE is returned.
    """
    return accept_notification_modal()

@mcp.tool()
def get_modal_text_if_present_tool():
    """
    Checks if a pop-up message (modal) is present on the page and returns the text if present.
    """
    return get_modal_text_if_present()

if __name__ == "__main__":
    """
    Runs the MCP server for handling appointment-related requests.
    """
    print("MHRS appointment server is running...")
    mcp.run(transport='stdio')
    #browser.wait_warping()
    #print(cancel_appointment_tool("eylem")) #works
    #print(revert_appointment_tool("eylem")) #works
    