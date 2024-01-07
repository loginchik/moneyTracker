import datetime
from unittest.mock import AsyncMock

import pytest 

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from db.add_record.create_revenue import AddRevenueQuery
from db.add_record.create_user import AddUserQuery
from tests.test_handlers.conftest import TEST_HANDLERS_USER
from bot_structures import RevenueStates, make_binary_keyboard, make_category_keyboard
from commands.revenue_commands.revenue_category import (
    ask_new_revenue_category_name, 
    select_revenue_category, 
    get_revenue_category_callback, 
    save_new_revenue_category_name
)
from commands.revenue_commands.revenue_type import (
    ask_new_revenue_type_name,
    ask_revenue_type, 
    get_revenue_type_callback, 
    save_new_revenue_type_name
)
from commands.revenue_commands.revenue_money_count import (
    ask_revenue_money_count, 
    get_revenue_money_count
)
from commands.revenue_commands.revenue_date import (
    ask_revenue_is_now, 
    get_revenue_isnow_callback, 
    save_specific_revenue_date
)
from commands.revenue_commands.revenue_confirmation import (
    ask_revenue_confirmation, 
    get_revenue_confirmation_callback
)
from bot_inner_texts import load_message_texts_json


message_expected_texts = load_message_texts_json()['edit_db']['new_revenue']


class Test_askNewRevenueCategoryName:
    @pytest.mark.asyncio
    async def test_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['category']['new_category_name']['initial'] + message_expected_texts['category']['new_category_name']['basic']
        await ask_new_revenue_category_name(message=message, state=setup_state, from_initial=True)
        new_state = await setup_state.get_state()
        
        message.answer.assert_called_with(expected_text)
        assert new_state == RevenueStates.waiting_for_new_category_name
    
    @pytest.mark.asyncio
    async def test_not_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['category']['new_category_name']['basic']

        await ask_new_revenue_category_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        message.answer.assert_called_with(expected_text)
        assert new_state == RevenueStates.waiting_for_new_category_name
    

class Test_selectRevenueCategory:
    
    @pytest.mark.asyncio
    async def test_select_empty_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock()
        
        await select_revenue_category(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
       
        assert new_state == RevenueStates.waiting_for_new_category_name
        message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_select_full_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddRevenueQuery(user_id=TEST_HANDLERS_USER.id, category='c', type_='s', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_revenue()
        expected_keyboard: types.InlineKeyboardMarkup = make_category_keyboard(['c'])
        expected_text = message_expected_texts['category']['select_category']['basic']

        await select_revenue_category(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_category_choice
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)        
        

class Test_getRevenueCategoryCallback:
    
    @pytest.mark.asyncio
    async def test_new_category(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='new_category')
        
        await get_revenue_category_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_data.get('category', None) is None
        assert new_state == RevenueStates.waiting_for_new_category_name
        call.message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_other_category_full_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='some category', from_user=TEST_HANDLERS_USER)
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddRevenueQuery(user_id=TEST_HANDLERS_USER.id, category='c', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_revenue()
        
        await get_revenue_category_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == RevenueStates.waiting_for_type_choice
        assert new_data.get('category', None) == 'some category'
    
    @pytest.mark.asyncio
    async def test_other_category_empty_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='some category', from_user=TEST_HANDLERS_USER)
        
        await get_revenue_category_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == RevenueStates.waiting_for_new_type_name
        assert new_data.get('category', None) == 'some category'
    
    @pytest.mark.asyncio
    async def test_empty_callback(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        call = AsyncMock(data=None)
        
        await get_revenue_category_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('category', None) is None
        
        
class Test_saveNewRevenueCategoryName:
    
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(text=None)
        expected_text = message_expected_texts['category']['new_category_name']['error']

        await save_new_revenue_category_name(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('category', None) is None
        message.answer.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_correct_input(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(text='new category name')
        
        await save_new_revenue_category_name(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert not new_state is None
        assert new_data.get('category', None) == 'new category name'
        
        
class Test_askRevenueType:
    
    @pytest.mark.asyncio
    async def test_ask_empty_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        
        await ask_revenue_type(message=message, state=setup_state, async_session_maker=setup_session, target_user_id=TEST_HANDLERS_USER.id)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_new_type_name
        message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_ask_full_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddRevenueQuery(user_id=TEST_HANDLERS_USER.id, category='c', type_='t', money_count=200, date_stamp=datetime.datetime.now(), async_session=setup_session).save_revenue()
        expected_keyboard = make_category_keyboard(['t'])
        expected_text = message_expected_texts['type']['select_type']['basic']

        await ask_revenue_type(message=message, state=setup_state, async_session_maker=setup_session, target_user_id=TEST_HANDLERS_USER.id)
        new_state = await setup_state.get_state()

        assert new_state == RevenueStates.waiting_for_type_choice
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)
                

class Test_askNewRevenueTypeName:
    
    @pytest.mark.asyncio
    async def test_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['type']['new_type_name']['initial'] + message_expected_texts['type']['new_type_name']['basic']

        await ask_new_revenue_type_name(message=message, state=setup_state, from_initial=True)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_new_type_name
        message.answer.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_not_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['type']['new_type_name']['basic']

        await ask_new_revenue_type_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_new_type_name
        message.answer.assert_called_with(expected_text)

        
class Test_getRevenueTypeCallback:
    
    @pytest.mark.asyncio
    async def test_new_category(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='new_category')
        
        await get_revenue_type_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_new_type_name
        call.message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_other_category(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='some category')
        
        await get_revenue_type_callback(callback=call, state=setup_state, bot=bot)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        assert new_data.get('revenue_type', None) == 'some category'
        assert new_state == RevenueStates.waiting_for_money_count
        
    @pytest.mark.asyncio
    async def test_empty_callback(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data=None)
        
        await get_revenue_type_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        
        assert new_state is None
        call.message.answer.assert_not_called()
        

class Test_saveNewRevenueTypeName:
    
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text=None)
        expected_text = message_expected_texts['type']['new_type_name']['error']

        await save_new_revenue_type_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('revenue_type', None) is None
        message.answer.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_correct_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='some type')
        
        await save_new_revenue_type_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == RevenueStates.waiting_for_money_count
        assert new_data.get('revenue_type', None) == 'some type'
        
        
class Test_askRevenueMoneyCount:
   
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        
        await ask_revenue_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_money_count
        message.answer.assert_called()
        

class Test_getRevenueMoneyCount:
    
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text=None)
        expected_text = message_expected_texts['money']['ask']['error']

        await get_revenue_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None        
        assert new_data.get('money_count', '') == ''
        message.reply.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_correct_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='600')
        
        await get_revenue_money_count(message=message, state=setup_state)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        assert new_data.get('money_count', None) == 600
        assert new_state == RevenueStates.waiting_for_date_isnow_choice
        
    @pytest.mark.asyncio
    async def test_incorrect_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='-700')
        expected_text = message_expected_texts['money']['ask']['error']

        await get_revenue_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('money_count', None) is None
        message.reply.assert_called_with(expected_text)    
        
        
class Test_askRevenueIsNow:
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_keyboard = make_binary_keyboard(message_expected_texts['date']['ask']['buttons']['yes'], message_expected_texts['date']['ask']['buttons']['no'])
        expected_text = message_expected_texts['date']['ask']['basic']

        await ask_revenue_is_now(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_date_isnow_choice
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)
        

class Test_getRevenueIsNowCallback:
    @pytest.mark.asyncio
    async def test_yes(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='yes')
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 200, 
        })
        
        await get_revenue_isnow_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == RevenueStates.waiting_for_results_confirmation
        assert not new_data.get('revenue_date', None) is None
        
    @pytest.mark.asyncio
    async def test_no(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='no')
        
        await get_revenue_isnow_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == RevenueStates.waiting_for_specific_date
        assert new_data.get('revenue_date', None) is None
        call.message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_other_callback(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='other')
        
        await get_revenue_isnow_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('revenue_date', None) is None
        call.message.answer.assert_not_called()
        
    
class Test_saveSpecificRevenueDate:
    
    @pytest.mark.asyncio
    async def test_correct_date(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='20-12-2023 14:50')
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 200
        })
        
        await save_specific_revenue_date(message=message, state=setup_state)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        assert new_data.get('revenue_date', None) == '2023-12-20 14:50'
        assert new_state == RevenueStates.waiting_for_results_confirmation
        
    
    @pytest.mark.asyncio
    async def test_incorrect_date(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='2023-20-20 50:67')
        expected_text = message_expected_texts['date']['ask']['error']

        await save_specific_revenue_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('revenue_date', None) is None
        message.reply.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text=None)
        expected_text = message_expected_texts['date']['ask']['error']

        await save_specific_revenue_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('revenue_date', None) is None
        message.reply.assert_called_with(expected_text)

class Test_askRevenueConfirmation:
    
    @pytest.mark.asyncio
    async def test_ask_correct_data(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 500, 
            'revenue_date': '2023-12-20 14:50'
        })
        
        await ask_revenue_confirmation(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == RevenueStates.waiting_for_results_confirmation
        message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_incorrect_data(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        
        await ask_revenue_confirmation(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data == {}
        message.answer.assert_called()


class Test_getRevenueConfirmationCallback:
    
    @pytest.mark.asyncio
    async def test_yes_user_exists(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='text')
        call: types.CallbackQuery = AsyncMock(data='yes', **{'message': message}, from_user=TEST_HANDLERS_USER)
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 500, 
            'revenue_date': '2023-12-20 14:59'
        })
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        expected_text = message_expected_texts['confirm']['callback']['yes']['success']

        await get_revenue_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        call.message.answer.assert_called_with(expected_text)
        assert new_state is None
        assert new_data == {}
        
    @pytest.mark.asyncio
    async def test_yes_user_not_exists(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='text')
        call: types.CallbackQuery = AsyncMock(data='yes', **{'message': message})
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 500, 
            'revenue_date': '2023-12-20 14:59'
        })
        expected_text = message_expected_texts['confirm']['callback']['yes']['success']
        
        await get_revenue_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        call.message.answer.assert_called_with(expected_text)
        assert new_state is None
        assert new_data == {}
     
    @pytest.mark.asyncio
    async def test_yes_incorrect_data(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='text')
        call: types.CallbackQuery = AsyncMock(data='yes', **{'message': message})
        await setup_state.set_data({
            'category': 'c', 
            'revenue_type': 't', 
            'money_count': 500, 
            'revenue_date': '2023-20-20 14:59'
        })
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        
        await get_revenue_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        call.message.answer.assert_not_called()
        assert new_state is None
        assert new_data == {}
        
    @pytest.mark.asyncio
    async def test_no(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='text')
        call: types.CallbackQuery = AsyncMock(data='no', kwargs={'message': message})
        
        await get_revenue_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        call.message.answer.assert_not_called()
        assert new_state is None
        assert new_data == {}
        