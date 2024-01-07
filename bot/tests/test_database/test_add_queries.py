import datetime

import pytest

from sqlalchemy import select

from db.db_models import User, Expense, Revenue
from db.basic_funcs.add_query import AddQuery
from db.basic_funcs.select_query import SelectQuery
from db.add_record.create_expense import AddExpenseQuery
from db.add_record.create_user import AddUserQuery
from db.add_record.create_revenue import AddRevenueQuery


class Test_addQueries:
    
    very_long_text = 'text' * 100
    now = datetime.datetime.now()
    future_date = datetime.datetime(year=now.year + 10, month=now.month, day=now.day, hour=now.hour, minute=now.minute)
    
    @pytest.mark.asyncio
    async def test_check_user_id(self, get_asm):
        await AddQuery(async_session=get_asm, new_item=User(user_id=110)).add_to_db()
        new_user_result = await SelectQuery(async_session=get_asm, statement=select(User).where(User.user_id == 100)).select_one_or_none()
        user_100_exists = not new_user_result is None              
                
        new_user_query_id = await AddUserQuery(user_id=100, async_session=get_asm).check_new_user_id()
        exists_user_query_id = await AddUserQuery(user_id=110, async_session=get_asm).check_new_user_id()  
        
        assert user_100_exists == False
        assert new_user_query_id == 100
        assert exists_user_query_id is None
        
    @pytest.mark.asyncio
    async def test_save_user(self, get_asm):
        await AddUserQuery(user_id=100, async_session=get_asm).save_user()
        new_user = await SelectQuery(async_session=get_asm, statement=select(User).where(User.user_id == 100)).select_one_or_none()
        
        assert not new_user is None
        assert (datetime.datetime.now() - new_user.registration_date).total_seconds() < 100
        
        with pytest.raises(ValueError):
            await AddUserQuery(user_id=100, async_session=get_asm).save_user()
            
    @pytest.mark.asyncio
    async def test_add_expense_to_existent_user(self, get_asm):
        new_expense_check_result = await AddExpenseQuery(user_id=100,  category='c', subcategory='s', money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_expense_data()
        new_expense_check_result_false = await AddExpenseQuery(user_id=100, category=self.very_long_text, subcategory=self.very_long_text, money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_expense_data()
        new_expense_check_result_fake_money_count = await AddExpenseQuery(user_id=100, category='c', subcategory='s', money_count=0, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_expense_data()
        new_expense_check_result_fake_date = await AddExpenseQuery(user_id=100, category='c', subcategory='s', money_count=200, date_stamp=self.future_date, async_session=get_asm).check_new_expense_data()
        
        assert new_expense_check_result == True
        assert new_expense_check_result_false == False
        assert new_expense_check_result_fake_money_count == False
        assert new_expense_check_result_fake_date == False
        
        await AddExpenseQuery(user_id=100, category='c', subcategory='s', money_count=2000, date_stamp=datetime.datetime.now(), async_session=get_asm).save_expense()
        
        expense = await SelectQuery(async_session=get_asm, statement=select(Expense).where(Expense.user_id == 100).where(Expense.money_count == 2000)).select_one_or_none()
        assert not expense is None
        
    @pytest.mark.asyncio
    async def test_add_expense_to_new_user(self, get_asm):
        await AddExpenseQuery(user_id=1000, category='cat', subcategory='sub', money_count=230, date_stamp=datetime.datetime.now(),async_session=get_asm).save_expense()

        new_user = await SelectQuery(async_session=get_asm, statement=select(User).where(User.user_id == 1000)).select_one_or_none()
        new_expense = await SelectQuery(async_session=get_asm, statement=select(Expense).where(Expense.user_id == 1000).where(Expense.category == 'cat')).select_one_or_none()
        
        assert not new_user is None
        assert not new_expense is None
        
    @pytest.mark.asyncio 
    async def test_add_revenue_for_existent_user(self, get_asm):
        new_revenue_check_result = await AddRevenueQuery(user_id=100, category='c', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_revenue_data()
        new_revenue_check_result_fake_text = await AddRevenueQuery(user_id=100, category=self.very_long_text, type_=self.very_long_text, money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_revenue_data()
        new_revenue_check_result_fake_money = await AddRevenueQuery(user_id=100, category='c', type_='t', money_count=0, date_stamp=datetime.datetime.now(), async_session=get_asm).check_new_revenue_data()
        new_revenue_check_result_fake_date = await AddRevenueQuery(user_id=100, category='c', type_='t', money_count=200, date_stamp=self.future_date, async_session=get_asm).check_new_revenue_data()
        
        assert new_revenue_check_result == True
        assert new_revenue_check_result_fake_text == False
        assert new_revenue_check_result_fake_money == False
        assert new_revenue_check_result_fake_date == False
        
        await AddRevenueQuery(user_id=100, category='c', type_='t', money_count=3500, date_stamp=datetime.datetime.now(), async_session=get_asm).save_revenue()
        
        revenue = await SelectQuery(async_session=get_asm, statement=select(Revenue).where(Revenue.user_id == 100).where(Revenue.money_count == 3500)).select_one_or_none()
        assert not revenue is None
        
    @pytest.mark.asyncio
    async def test_add_revenue_to_new_user(self, get_asm):
        await AddRevenueQuery(user_id=450, category='categ', type_='ty', money_count=5000, date_stamp=datetime.datetime.now(), async_session=get_asm).save_revenue()
        
        new_user = await SelectQuery(async_session=get_asm, statement=select(User).where(User.user_id == 450)).select_one_or_none()
        new_revenue = await SelectQuery(async_session=get_asm, statement=select(Revenue).where(Revenue.user_id == 450).where(Revenue.money_count == 5000)).select_one_or_none()
        
        assert not new_user is None
        assert not new_revenue is None
