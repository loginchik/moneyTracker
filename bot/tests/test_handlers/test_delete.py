import datetime
from unittest.mock import AsyncMock

import pytest

from aiogram import types
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from commands.delete_all_data_command import ask_delete_all_confirmaion, delete_all_data_message
from bot_structures import DeleteDataStates
from db.add_record.create_expense import AddExpenseQuery
from bot_inner_texts import load_message_texts_json


message_expected_texts = load_message_texts_json()['edit_db']['delete_data']


class TestDeleteDataMessage:
    
    user = types.User(id=12345678, is_bot=False, first_name='FM')
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message = AsyncMock(from_user=self.user)
        
        await ask_delete_all_confirmaion(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == DeleteDataStates.waiting_confirmation
        message.answer.assert_called()
        
    
    @pytest.mark.asyncio
    async def test_get_confirmaion_correct(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message = AsyncMock(from_user=self.user, text=message_expected_texts['confirm']['user_text'])
        await AddExpenseQuery(user_id=self.user.id, category='cat', subcategory='sub', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        
        await delete_all_data_message(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        
        assert new_state is None
        message.answer.assert_called_with(message_expected_texts['result']['success'])
        
    @pytest.mark.asyncio
    async def test_get_confirmaion_incorrect(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message1 = AsyncMock(from_user=self.user, text='Я хочу удалить все    данные')
        message2 = AsyncMock(from_user=self.user.id, text=None)
        await AddExpenseQuery(user_id=self.user.id, category='cat', subcategory='sub', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        
        await delete_all_data_message(message=message1, state=setup_state, async_session_maker=setup_session)
        await delete_all_data_message(message=message2, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        
        assert new_state is None
        message1.answer.assert_called_with(message_expected_texts['result']['cancel'])
        message2.answer.assert_called_with(message_expected_texts['result']['cancel'])