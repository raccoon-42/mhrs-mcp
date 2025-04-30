import re

def normalize_string_to_lower(string):
    return string.strip().replace("İ","i").lower()

def normalize_string_to_upper(string):
    return string.strip().replace("i","İ").upper()

def parse_main_hour(clock):
    return re.split(r'[:;,.]', clock.strip())[0]

def normalize_to_colon_format(time_str):
    parts = re.split(r'[:;,.]', time_str.strip())

    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0  # default to 0 if minute is missing

    return f"{hour:02d}:{minute:02d}"