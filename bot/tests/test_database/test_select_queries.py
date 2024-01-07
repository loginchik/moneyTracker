import datetime

import pytest

from db.get_records.select_users import SelectUserQuery
from db.get_records.select_expenses import SelectExpensesQuery
from db.get_records.select_revenues import SelectRevenueQuery
from db.add_record.create_user import AddUserQuery
from db.add_record.create_expense import AddExpenseQuery
from db.add_record.create_revenue import AddRevenueQuery
from db.db_models import User, Expense, Revenue


class TestSelectQueries:
    
    def test_return_none_or_all(self, get_asm):
        user_result_full = SelectUserQuery(async_session=get_asm).return_none_or_all(['a', 'b'])
        user_result = SelectUserQuery(async_session=get_asm).return_none_or_all([])
        user_none_result = SelectUserQuery(async_session=get_asm).return_none_or_all(None)
        user_int_result = SelectUserQuery(async_session=get_asm).return_none_or_all(15)
        
        expense_result_full = SelectExpensesQuery(async_session=get_asm, target_user_id=100).return_none_or_all(['b', 'c'])
        expense_result = SelectExpensesQuery(async_session=get_asm, target_user_id=100).return_none_or_all([])
        expense_none_result = SelectExpensesQuery(async_session=get_asm, target_user_id=100).return_none_or_all(None)
        expense_int_result = SelectExpensesQuery(async_session=get_asm, target_user_id=100).return_none_or_all(15)
        
        revenue_result_full = SelectRevenueQuery(async_session=get_asm, target_user_id=100).return_none_or_all(['d', 'e'])
        revenue_result = SelectRevenueQuery(async_session=get_asm, target_user_id=100).return_none_or_all([])
        revenue_none_result = SelectRevenueQuery(async_session=get_asm, target_user_id=100).return_none_or_all(None)
        revenue_int_result = SelectRevenueQuery(async_session=get_asm, target_user_id=100).return_none_or_all(15)
        
        assert user_result_full == ['a', 'b']
        assert user_result is None
        assert user_none_result is None
        assert user_int_result is None
        
        assert expense_result_full == ['b', 'c']
        assert expense_result is None
        assert expense_none_result is None
        assert expense_int_result is None
        
        assert revenue_result_full == ['d', 'e']
        assert revenue_result is None
        assert revenue_none_result is None
        assert revenue_int_result is None        
    
    @pytest.mark.asyncio
    async def test_select_user_query(self, get_asm):
        await AddUserQuery(user_id=100, async_session=get_asm).save_user()
        
        all_users = await SelectUserQuery(async_session=get_asm).select_all()
        user_by_id_exists = await SelectUserQuery(async_session=get_asm).by_id(user_id=100)
        user_by_id_not_exists = await SelectUserQuery(async_session=get_asm).by_id(user_id=1500)
        user_exists_exists = await SelectUserQuery(async_session=get_asm).check_exists(user_id=100)
        user_exists_not_exists = await SelectUserQuery(async_session=get_asm).check_exists(user_id=1500)
        
        assert len(all_users) == 1
        assert isinstance(all_users[0], User)
        assert not user_by_id_exists is None
        assert isinstance(user_by_id_exists, User)
        assert user_by_id_not_exists is None
        assert user_exists_exists == True
        assert user_exists_not_exists == False
        
    @pytest.mark.asyncio
    async def test_select_expense_query(self, get_asm):
        # Expense now
        now = datetime.datetime.now()
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat11', money_count=100, date_stamp=now, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat12', money_count=100, date_stamp=now, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat21', money_count=100, date_stamp=now, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat22', money_count=100, date_stamp=now, async_session=get_asm).save_expense()
        # Two days ago
        two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat11', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat12', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat21', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat22', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_expense()
        # Three days ago
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat11', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat12', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat21', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat22', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_expense()
        # More than week ago
        more_that_week_ago = datetime.datetime.now() - datetime.timedelta(days=9)
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat11', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat1', subcategory='subcat12', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat21', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_expense()
        await AddExpenseQuery(user_id=100, category='cat2', subcategory='subcat22', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_expense()
        # Other users
        await AddExpenseQuery(user_id=110, category='cat1', subcategory='subcat11', money_count=200, date_stamp=now, async_session=get_asm).save_expense()
        
        all_expenses = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_all()
        in_period = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).in_period(period_start=three_days_ago, period_end=two_days_ago)
        in_last_two_days = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).in_last_n_days(2)
        today_ = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).specific_date(datetime.date.today())
        
        user_categories = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_user_expense_categories()
        user_subcategories = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_user_expense_subcategories(category_name='cat1')
        user_subcategories_no_category = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_user_expense_subcategories(category_name=None)
        user_subcategories_no_category_2 = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_user_expense_subcategories(category_name='')
        
        assert len(all_expenses) == 16
        assert isinstance(all_expenses[0], Expense)
        assert len(in_period) == 8
        assert isinstance(in_period[0], Expense)
        assert len(in_last_two_days) == 8
        assert isinstance(in_last_two_days[0], Expense)
        assert len(today_) == 4
        assert isinstance(today_[0], Expense)
        assert sorted(set(user_categories)) == ['cat1', 'cat2']
        assert sorted(set(user_subcategories)) == ['subcat11', 'subcat12']
        assert user_subcategories_no_category is None
        assert user_subcategories_no_category_2 is None
    
    @pytest.mark.asyncio
    async def test_select_revenue_query(self, get_asm):
        # Expense now
        now = datetime.datetime.now()
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat11', money_count=100, date_stamp=now, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat12', money_count=100, date_stamp=now, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat21', money_count=100, date_stamp=now, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat22', money_count=100, date_stamp=now, async_session=get_asm).save_revenue()
        # Two days ago
        two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat11', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat12', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat21', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat22', money_count=100, date_stamp=two_days_ago, async_session=get_asm).save_revenue()
        # Three days ago
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat11', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat12', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat21', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat22', money_count=100, date_stamp=three_days_ago, async_session=get_asm).save_revenue()
        # More than week ago
        more_that_week_ago = datetime.datetime.now() - datetime.timedelta(days=9)
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat11', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat1', type_='subcat12', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat21', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_revenue()
        await AddRevenueQuery(user_id=100, category='cat2', type_='subcat22', money_count=100, date_stamp=more_that_week_ago, async_session=get_asm).save_revenue()
        # Other users
        await AddRevenueQuery(user_id=110, category='cat1', type_='subcat11', money_count=200, date_stamp=now, async_session=get_asm).save_revenue()
        
        all_revenues = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).get_all()
        in_period = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).in_period(period_start=three_days_ago, period_end=two_days_ago)
        in_last_2_days = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).in_last_n_days(days_delta=2)
        today_ = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).specific_date(specific_date=datetime.date.today())
        us_cats = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).user_categories()
        us_types = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).user_types()
        
        assert len(all_revenues) == 16
        assert isinstance(all_revenues[0], Revenue)
        assert len(in_period) == 8
        assert isinstance(in_period[0], Revenue)
        assert len(in_last_2_days) == 8
        assert isinstance(in_last_2_days[0], Revenue)
        assert len(today_) == 4
        assert isinstance(today_[0], Revenue)
        assert sorted(set(us_cats)) == ['cat1', 'cat2']
        assert sorted(set(us_types)) == ['subcat11', 'subcat12', 'subcat21', 'subcat22']