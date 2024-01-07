import datetime
from unittest.mock import AsyncMock

import pytest

from aiogram import types, Bot
from aiogram.methods.send_document import SendDocument

from sqlalchemy.ext.asyncio import AsyncSession

from db.add_record.create_expense import AddExpenseQuery
from db.add_record.create_revenue import AddRevenueQuery
from commands.export_commands import export_expenses_message, export_revenues_message
from .conftest import TEST_HANDLERS_USER
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['export']


class TestExportCommands:
    
    @pytest.mark.asyncio
    async def test_export_expenses(self, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        await AddExpenseQuery(user_id=TEST_HANDLERS_USER.id, category='cat1', subcategory='subcat1', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        message1 = AsyncMock(from_user=TEST_HANDLERS_USER)
        message2 = AsyncMock(from_user=types.User(id=2345678, is_bot=False, first_name='FN'))
        
        result1 = await export_expenses_message(message=message1, async_session_maker=setup_session, bot=bot)
        result2 = await export_expenses_message(message=message2, async_session_maker=setup_session, bot=bot)
        
        message2.answer.assert_called_with(message_texts['expense']['no_data'])
        message1.answer.assert_not_called()
        
        assert isinstance(result1, SendDocument)
        assert not isinstance(result2, SendDocument)
        
    @pytest.mark.asyncio
    async def test_export_revenues(self, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        await AddRevenueQuery(user_id=TEST_HANDLERS_USER.id, category='cat', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_revenue()
        message1 = AsyncMock(from_user=TEST_HANDLERS_USER)
        message2 = AsyncMock(from_user=types.User(id=123567897654, is_bot=False, first_name='FM'))
        
        result1 = await export_revenues_message(message=message1, async_session_maker=setup_session, bot=bot)
        result2 = await export_revenues_message(message=message2, async_session_maker=setup_session, bot=bot)
        
        message2.answer.assert_called_with(message_texts['revenue']['no_data'])
        message1.answer.assert_not_called()
        
        assert isinstance(result1, SendDocument)
        assert not isinstance(result2, SendDocument)
    
        