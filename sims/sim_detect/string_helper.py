from unidecode import unidecode


def lower_text(input_str):
    return unidecode(input_str).lower()
