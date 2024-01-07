import datetime
import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from db.basic_funcs.query_base_class import SQLQuery
from db.basic_funcs.add_query import AddQuery
from db.basic_funcs.select_query import SelectQuery
from db.db_models import User, Expense, Revenue


class TestBasicQueries:
    
    @pytest.mark.asyncio
    async def test_basic_query(self, get_asm):
        query = SQLQuery(async_session=get_asm)
        assert not query.session is None
        assert isinstance(query.session, async_sessionmaker)
        async with query.session() as session:
            assert isinstance(session, AsyncSession)
        
        
    @pytest.mark.asyncio
    async def test_add_query(self, get_asm):       
        new_user = AddQuery(async_session=get_asm, new_item=User(user_id=1))
        await new_user.add_to_db()
        new_expense = AddQuery(async_session=get_asm, new_item=Expense(user_id=1, category='c', subcategory='s', money_count=200, datetime_stamp=datetime.datetime.now()))
        await new_expense.add_to_db()
        new_revenue = AddQuery(async_session=get_asm, new_item=Revenue(user_id=1, category='c', type_='t', money_count=500, datetime_stamp=datetime.datetime.now()))
        await new_revenue.add_to_db()
        
        async with get_asm() as session:
            async with session.begin():
                users = await session.scalars(select(User))
                users_list = users.all()
                expenses = await session.scalars(select(Expense))
                expenses_list = expenses.all()
                
                revenues = await session.scalars(select(Revenue))
                revenues_list = revenues.all()
        
        assert len(users_list) == 1
        assert users_list[0].user_id == 1
        assert len(expenses_list) == 1
        assert expenses_list[0].user_id == 1
        assert expenses_list[0].category == 'c'
        assert expenses_list[0].subcategory == 's'
        assert expenses_list[0].money_count == 200
        assert type(expenses_list[0].datetime_stamp) == datetime.datetime
        assert len(revenues_list) == 1
        assert revenues_list[0].user_id == 1
        assert revenues_list[0].category == 'c'
        assert revenues_list[0].type_ == 't'
        assert revenues_list[0].money_count == 500
        assert type(revenues_list[0].datetime_stamp) == datetime.datetime
                        
                
    @pytest.mark.asyncio
    async def test_add_duplicates(self, get_asm):
        try:
            await AddQuery(async_session=get_asm, new_item=User(user_id=1)).add_to_db()
        except IntegrityError:
            pytest.fail('Integrity error appeared')

    @pytest.mark.asyncio
    async def test_add_fake_item(self, get_asm):
        class FakeValue:
            val = 'item'
        fake_value_1 = FakeValue()
        fake_value_2 = datetime.date.today()
        fake_value_3 = None
            
        with pytest.raises(ValueError):
            assert await AddQuery(async_session=get_asm, new_item=fake_value_1).add_to_db()
        with pytest.raises(ValueError):
            assert await AddQuery(async_session=get_asm, new_item=fake_value_2).add_to_db()
        with pytest.raises(ValueError):
            assert await AddQuery(async_session=get_asm, new_item=fake_value_3).add_to_db()
            
    @pytest.mark.asyncio
    async def test_select_all_query(self, get_asm):
        users_result = await SelectQuery(async_session=get_asm, statement=select(User)).select_all()
        expenses_result = await SelectQuery(async_session=get_asm, statement=select(Expense)).select_all()
        revenues_result = await SelectQuery(async_session=get_asm, statement=select(Revenue)).select_all()
        
        async with get_asm() as session:
            async with session.begin():
                all_users = await session.scalars(select(User))
                users_expected = all_users.all()
                all_expenses = await session.scalars(select(Expense))
                expenses_expected = all_expenses.all()
                all_revenues = await session.scalars(select(Revenue))
                revenues_expected = all_revenues.all()
        
        assert len(users_result) == len(users_expected)
        assert all([a.user_id == b.user_id] for a, b in zip(users_result, users_expected))
        assert all([a.id == b.id] for a, b in zip(expenses_result, expenses_expected))
        assert all([a.id == b.id] for a, b in zip(revenues_result, revenues_expected))
        assert isinstance(users_result[0], User)
        assert isinstance(expenses_result[0], Expense)
        assert isinstance(revenues_result[0], Revenue)
    
    @pytest.mark.asyncio
    async def test_empty_statement(self, get_asm):
        assert await SelectQuery(async_session=get_asm, statement=None).select_all() is None
        assert await SelectQuery(async_session=get_asm, statement=None).select_one_or_none() is None
        
    @pytest.mark.asyncio
    async def test_select_one_or_none(self, get_asm):
        await AddQuery(async_session=get_asm, new_item=User(user_id=1)).add_to_db()
        user_result = await SelectQuery(async_session=get_asm, statement=select(User).where(User.user_id == 1)).select_one_or_none()
        
        async with get_asm() as session:
            async with session.begin():
                user = await session.scalars(select(User).where(User.user_id == 1))
                user_expected = user.one_or_none()
        
        assert not user_result is None
        assert not user_expected is None     
        assert user_result.registration_date == user_expected.registration_date
