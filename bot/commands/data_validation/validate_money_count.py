import re


def check_money_count(entered: str) -> float | bool:
    """Checks if received from user amount of money can be turned into a positive float."""
    
    if entered is None: return False
    else:
        try:
            entered = entered.strip()
            if re.match(pattern=r'\d+([\.,]\d+)?$', string=entered):
                entered_float = float(entered.replace(',', '.'))
                return entered_float if entered_float > 0 else False
            else: return False
        except ValueError: return False
        except: return False