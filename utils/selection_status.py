from enum import Enum

class SelectionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    CITY_NOT_FOUND = "city_not_found"
    TOWN_NOT_FOUND = "town_not_found"
    SPECIALITY_NOT_FOUND = "speciality_not_found"
    HOSPITAL_NOT_FOUND = "hospital_not_found"
    CLINIC_NOT_FOUND = "clinic_not_found"
    DOCTOR_NOT_FOUND = "doctor_not_found"
    DATE_NOT_FOUND = "date_not_found"
    TIME_NOT_FOUND = "time_not_found"
    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"