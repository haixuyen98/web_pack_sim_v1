from .string_helper import lower_text
from .constant import DEFAULT_SIM_TT, DEFAULT_SIM_TS

def detectPack(input_str):
    if bool(input_str) is False:
        return None
    
    input_str = lower_text(input_str)
    if input_str in DEFAULT_SIM_TT:
        return 1
    if input_str in DEFAULT_SIM_TS:
        return 2
    
    split_strings = input_str.split()
    last_word =  split_strings[-1]
    if "s" in last_word:
        return 2
    return 1
    
