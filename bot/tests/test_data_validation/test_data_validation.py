import datetime
from commands.data_validation import check_date, check_money_count


def test_date_validation_with_correct_date():
    assert check_date('20-12-2023 14:00') == '2023-12-20 14:00'
    
    datetime_now = datetime.datetime.now()
    current_datetime = datetime.datetime.strftime(datetime_now, '%d-%m-%Y %H:%M')
    current_datetime_result = datetime.datetime.strftime(datetime_now, '%Y-%m-%d %H:%M')
    assert check_date(current_datetime) == current_datetime_result
    

def test_date_validation_with_incorrect_date():
    assert check_date('20-06-2030 14:00') == False  # doesn't happen yet
    assert check_date('20-06-2022') == False  # incomplete 
    assert check_date('20-20-2023 14:00') == False  # doesn't exist
    assert check_date('2023-20-06 14:00') == False  # wrong format
    assert check_date('20.05.2023 14:00') == False  # wrong format
    assert check_date(None) == False
    
    
def test_money_count_validation_with_correct():
    assert check_money_count('20.05') == float(20.05)
    assert check_money_count('100') == float(100)
    assert check_money_count('10,5') == float(10.5)
    

def test_money_count_validation_with_incorrect():
    assert check_money_count('10.0.0') == False
    assert check_money_count('-100') == False
    assert check_money_count('') == False
    assert check_money_count(None) == False
    