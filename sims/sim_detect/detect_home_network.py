from .string_helper import lower_text
from .constant import DEFAULT_HOME_NETWORK, DEFAULT_NUMBER_PREFIX


def detectTelco(phone):
    value = getValueWithPrefix(phone)
    return value

def getTelcoInput(input_str):
    input_str = lower_text(input_str)
    value = getValue(input_str)
    # neu value = 0 thi join cac string lai va check tiep
    if value == None:
        join_str = joinText(input_str)
        value = getValue(join_str)
    # neu value = 0 thi lay tu viet tat check tiep 
    if value == None:
        short_str = shortText(input_str)
        value = getValue(short_str)
    return value 


def getValue(input_str):
    if input_str in DEFAULT_HOME_NETWORK["VIETTEL"]:
        return 1
    if input_str in DEFAULT_HOME_NETWORK["VINAPHONE"]:
        return 2
    if input_str in DEFAULT_HOME_NETWORK["MOBIPHONE"]:
        return 3
    if input_str in DEFAULT_HOME_NETWORK["VIETNAMMOBILE"]:
        return 4
    if input_str in DEFAULT_HOME_NETWORK["GMOBILE"]:
        return 5
    if input_str in DEFAULT_HOME_NETWORK["ITEL"]:
        return 8
    if input_str in DEFAULT_HOME_NETWORK["WINTEL"]:
        return 9
    if input_str in DEFAULT_HOME_NETWORK["MAY BAN"]:
        return 7
    return None


def shortText(input_str):
    words = input_str.split()
    first_characters = [word[0] for word in words]
    return "".join(first_characters)


def joinText(input_str):
    words = input_str.split()
    return "".join(words)


def getValueWithPrefix(phone):
    if phone[:3] in DEFAULT_NUMBER_PREFIX["VIETTEL"]:
        return 1
    if phone[:3] in DEFAULT_NUMBER_PREFIX["VINAPHONE"]:
        return 2
    if phone[:3] in DEFAULT_NUMBER_PREFIX["MOBIPHONE"]:
        return 3
    if phone[:3] in DEFAULT_NUMBER_PREFIX["VIETNAMMOBILE"]:
        return 4
    if phone[:3] in DEFAULT_NUMBER_PREFIX["GMOBILE"]:
        return 5
    if phone[:3] in DEFAULT_NUMBER_PREFIX["ITEL"]:
        return 8
    if phone[:3] in DEFAULT_NUMBER_PREFIX["WINTEL"]:
        return 9
    if phone[:4] in DEFAULT_NUMBER_PREFIX["DESKTOP_PHONE"]:
        return 7
    return None
