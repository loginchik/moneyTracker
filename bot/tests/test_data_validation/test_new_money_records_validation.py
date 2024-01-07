import datetime
from db.add_record.new_record_check_funcs import check_money_count, check_varchar, check_datetime_stamp


def test_check_money_count():
    assert check_money_count('6,7') is None
    assert check_money_count('6.7') == 6.7
    assert check_money_count(None) is None
    assert check_money_count(-199) is None
    assert check_money_count('-300') is None
    assert check_money_count('200') == 200

    
def test_check_varchar():
    assert check_varchar(200) is None
    assert check_varchar('200') == '200'
    assert check_varchar('Some string', 5) is None
    assert check_varchar(None) is None
    
    
def test_check_datetime_stamp():
    d1 = datetime.datetime(2000, 10, 20)
    assert check_datetime_stamp(d1) == d1
    assert check_datetime_stamp('date') is None
    assert check_datetime_stamp(None) is None
    assert check_datetime_stamp(100) is None
    d2 = datetime.datetime(2050, 10, 10)
    assert check_datetime_stamp(d2) is None