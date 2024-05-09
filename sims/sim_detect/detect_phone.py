import re

def detect_phone(phone):
    if not re.match(r'^0', phone):
        phone = '0' + phone
    check_phone = re.findall(r'\b\d{10,11}\b', phone) and phone is not None
    if bool(check_phone) == False:
        return None
    return phone
    
