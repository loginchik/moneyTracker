import datetime

from db.export.csv_generator import generate_csv
from db.export import generate_expenses_csv, generate_revenues_csv
from db.db_models import Expense, Revenue

class TestExport:
    
    def test_generator(self):
        records_list = ['record1;rec2', 'record2;rec2']
        header = ['record', 'subrecord']
        
        result = generate_csv(records_list=records_list, header=header)
        assert type(result) == bytes
    
    def test_expenses_csv_export(self):
        result_if_no_expenses = generate_expenses_csv([])
        expenses = [
            Expense(user_id=100, category='cat1', subcategory='subcat1', money_count=500, datetime_stamp=datetime.datetime.now()),
            Expense(user_id=100, category='cat2', subcategory='subcat2', money_count=300, datetime_stamp=datetime.datetime.now())
        ]
        result = generate_expenses_csv(expenses=expenses)
        
        assert result_if_no_expenses is None
        assert type(result) == bytes

    def test_revenues_csv_export(self):
        result_if_no_revenues = generate_revenues_csv([])
        revenues = [
            Revenue(user_id=100, category='cat', type_='t', money_count=400, datetime_stamp=datetime.datetime.now()), 
            Revenue(user_id=100, category='cat2', type_='t', money_count=500, datetime_stamp=datetime.datetime.now())
        ]
        result = generate_revenues_csv(revenues=revenues)
        
        assert result_if_no_revenues is None
        assert type(result) == bytes
