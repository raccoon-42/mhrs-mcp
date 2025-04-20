import unicodedata


s = "CİLDİYE"
print(s.lower())  # might be "ı" if Turkish locale
print(s.casefold())  # more consistent, often "i"
print(s.encode('ascii', 'ignore').decode().lower())

print(unicodedata.normalize("NFKD", s.casefold()).encode("ascii", "ignore").decode())
print("ÖÜĞÇŞİ".lower())
print("CİLDİYE".replace("İ", "i").lower())  # i

def normalize_string_to_lower(string):
    return string.strip().replace("İ","i").lower()

def normalize_string_to_upper(string):
    return string.strip().replace("i","İ").upper()

teststr = normalize_string_to_lower(s)
print(teststr)


city = "izmiröğüçşı"

print(city.upper())
print(normalize_string_to_upper(city))

clock_format = "  24;00"
import re
print(re.split(r'[:;,.]', clock_format.strip())[0])
