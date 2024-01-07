import datetime
import re


def check_date(entered: str) -> str | bool:
    """Checks if received from user date can be turned into a datetime format and has already passed."""
    if entered is None: return False
    
    if re.match(pattern=r'\d{1,2}\-\d{1,2}-\d{4} \d{1,2}:\d{1,2}', string=entered):
        try:
            converted_to_datetime = datetime.datetime.strptime(entered, '%d-%m-%Y %H:%M')
            converted_back = datetime.datetime.strftime(converted_to_datetime, '%Y-%m-%d %H:%M')
            return converted_back if converted_to_datetime <= datetime.datetime.now() else False
        except ValueError: return False
        except: return False
    else: return False