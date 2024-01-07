import datetime

import pytest

from db.add_record.create_expense import AddExpenseQuery
from db.add_record.create_revenue import AddRevenueQuery
from db.get_records.select_expenses import SelectExpensesQuery
from db.get_records.select_revenues import SelectRevenueQuery
from db.delete_data.delete_user_data import delete_user_data


class TestDeleteData:
    
    @pytest.mark.asyncio
    async def test_delete_data(self, get_asm):
        await AddExpenseQuery(user_id=100, category='cat', subcategory='sub', money_count=20, date_stamp=datetime.datetime.now(), async_session=get_asm).save_expense()
        await AddRevenueQuery(user_id=100, category='cat', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).save_revenue()
        await AddExpenseQuery(user_id=10, category='cat', subcategory='sub', money_count=20, date_stamp=datetime.datetime.now(), async_session=get_asm).save_expense()
        await AddRevenueQuery(user_id=10, category='cat', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=get_asm).save_revenue()
        
        res1 = await delete_user_data(session=get_asm, user_id=100)
        res2 = await delete_user_data(session=get_asm, user_id='fkj')
        
        user_10_expenses = await SelectExpensesQuery(target_user_id=10, async_session=get_asm).get_all()
        user_10_revenues = await SelectRevenueQuery(target_user_id=10, async_session=get_asm).get_all()
        user_100_expenses = await SelectExpensesQuery(target_user_id=100, async_session=get_asm).get_all()
        user_100_revenues = await SelectRevenueQuery(target_user_id=100, async_session=get_asm).get_all()
        
        assert user_100_expenses is None
        assert user_100_revenues is None
        assert len(user_10_expenses) == 1
        assert len(user_10_revenues) == 1
        assert res1 == True
        assert res2 == False
        