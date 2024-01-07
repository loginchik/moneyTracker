import datetime
import logging
from unittest.mock import AsyncMock

import pytest

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.add_record.create_user import AddUserQuery
from db.add_record.create_expense import AddExpenseQuery

from commands.expenses_commands.expense_category import (
    ask_new_expense_category_name,
    select_expense_category, 
    get_expense_category_callback, 
    save_new_category_name
)
from commands.expenses_commands.expense_subcategory import (
    ask_expense_subcategory_choice, 
    ask_new_expense_subcategory_name, 
    get_expense_subcategory_callback,
    save_new_expense_subcategory_name
)
from commands.expenses_commands.expense_money_count import (
    ask_for_expense_money_count, 
    get_expense_money_count, 
)
from commands.expenses_commands.expense_date import (
    ask_expense_date_is_now, 
    ask_expense_specific_date, 
    get_expense_date_is_now_callback, 
    save_expense_specific_date
)
from commands.expenses_commands.expense_confirmation import (
    ask_expense_confirmation, 
    get_expense_confirmation_callback
)
from tests.test_handlers.conftest import TEST_HANDLERS_USER
from bot_structures import ExpenseStates, make_category_keyboard, make_binary_keyboard
from bot_inner_texts import load_message_texts_json


message_expected_texts = load_message_texts_json()['edit_db']['new_expense']


test_results_logger = logging.getLogger('test_results_logger')
test_results_logger.setLevel(logging.WARNING)


class Test_askNewExpenseCategoryName:
    
    @pytest.mark.asyncio
    async def test_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text: str = message_expected_texts['category']['new_category_name']['initial'] + message_expected_texts['category']['new_category_name']['basic']

        await ask_new_expense_category_name(message=message, state=setup_state, from_initial=True)
        current_state = await setup_state.get_state()
        
        message.answer.assert_called_with(expected_text)
        assert current_state == ExpenseStates.waiting_for_new_category_name
    
    @pytest.mark.asyncio
    async def test_not_from_initial(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text: str = message_expected_texts['category']['new_category_name']['basic']

        await ask_new_expense_category_name(message=message, state=setup_state)
        current_state = await setup_state.get_state()
        
        message.answer.assert_called_with(expected_text)
        assert current_state == ExpenseStates.waiting_for_new_category_name



class Test_selectExpenseCategory:
    
    @pytest.mark.asyncio
    async def test_select_expense_category_with_expenses(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, database_url: str, database_apikey: str):
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddExpenseQuery(user_id=TEST_HANDLERS_USER.id, category='Category', subcategory='Subcategory', money_count=1000, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        expected_keyboard: types.InlineKeyboardMarkup = make_category_keyboard(categories_list=['Category'])
        expected_text: str = message_expected_texts['category']['select_category']['basic']

        await select_expense_category(message=message, state=setup_state, async_session_maker=setup_session)
        current_state = await setup_state.get_state()
       
        assert current_state == ExpenseStates.waiting_for_category_choice 
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)
    
    @pytest.mark.asyncio
    async def test_select_expense_category_no_expenses(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        expected_text: str = message_expected_texts['category']['new_category_name']['initial'] + message_expected_texts['category']['new_category_name']['basic']

        await select_expense_category(message=message, state=setup_state, async_session_maker=setup_session)
        current_state = await setup_state.get_state()
        
        assert current_state == ExpenseStates.waiting_for_new_category_name 
        message.answer.assert_called_with(expected_text)
        

class Test_getExpenseCategoryCallback:
    
    @pytest.mark.asyncio
    async def test_correct_input_from_buttons_full_db(self, setup_state: FSMContext, bot: Bot, setup_session: AsyncSession, create_empty_tables_data: None):
        callback: types.CallbackQuery = AsyncMock(data='some_category', from_user=TEST_HANDLERS_USER)
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddExpenseQuery(user_id=TEST_HANDLERS_USER.id, category='Category', subcategory='Subcategory', money_count=1000, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        await setup_state.set_state(ExpenseStates.waiting_for_category_choice)
        
        await get_expense_category_callback(callback=callback, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_current_state = await setup_state.get_state()
        
        assert new_data['category'] == 'some_category'
        assert new_current_state != ExpenseStates.waiting_for_category_choice
        callback.message.answer.assert_called()  
        
    @pytest.mark.asyncio
    async def test_correct_input_from_buttons_empty_db(self, setup_state: FSMContext, bot: Bot, setup_session: AsyncSession, create_empty_tables_data: None):
        callback: types.CallbackQuery = AsyncMock(data='some_category', from_user=TEST_HANDLERS_USER)
        await setup_state.set_state(ExpenseStates.waiting_for_category_choice)
        
        await get_expense_category_callback(callback=callback, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_current_state = await setup_state.get_state()
        
        assert new_data['category'] == 'some_category'
        assert new_current_state == ExpenseStates.waiting_for_new_subcategory_name
        callback.message.answer.assert_called()  

    @pytest.mark.asyncio
    async def test_correct_new_category_button(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot): 
        callback: types.CallbackQuery = AsyncMock(data='new_category')
        
        await get_expense_category_callback(callback=callback, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_current_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_data.get('category', None) is None
        assert new_current_state == ExpenseStates.waiting_for_new_category_name
        callback.message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_empty_data(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        await setup_state.set_state(ExpenseStates.waiting_for_category_choice)
        callback: types.CallbackQuery = AsyncMock(data=None)
        
        await get_expense_category_callback(callback=callback, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_current_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_data.get('category', None) is None
        assert new_current_state == ExpenseStates.waiting_for_category_choice
        callback.message.answer.assert_not_called()


class Test_saveNewExpenseCategoryName:

    @pytest.mark.asyncio
    async def test_save_name(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(text='new_cat_name')
        await setup_state.set_state(ExpenseStates.waiting_for_new_category_name)
        
        await save_new_category_name(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state != ExpenseStates.waiting_for_new_category_name
        assert new_data.get('category', None) == 'new_cat_name'
        message.answer.assert_called()
    
    @pytest.mark.asyncio    
    async def test_empty_text(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(text=None)
        await setup_state.set_state(ExpenseStates.waiting_for_new_category_name)
        expected_text: str = message_expected_texts['category']['new_category_name']['error']

        await save_new_category_name(message=message, state=setup_state, async_session_maker=setup_session)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_new_category_name
        assert new_data.get('category', None) is None
        message.answer.assert_called_with(expected_text)
        
        
class Test_askExpenseSubcategoryChoice:
    
    @pytest.mark.asyncio
    async def test_ask_full_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await AddExpenseQuery(user_id=TEST_HANDLERS_USER.id, category='Category', subcategory='Subcategory', money_count=1000, date_stamp=datetime.datetime.now(), async_session=setup_session).save_expense()
        expected_keyboard = make_category_keyboard(['Subcategory'])
        await setup_state.set_data({'category': 'Category'})
        expected_text = message_expected_texts['subcategory']['select_subcategory']['basic']

        await ask_expense_subcategory_choice(message=message, state=setup_state, async_session_maker=setup_session, target_user_id=TEST_HANDLERS_USER.id)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_subcategory_choice
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)
        
    @pytest.mark.asyncio
    async def test_ask_empty_db(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER)
        await setup_state.set_data({'category': 'Category'})
        
        await ask_expense_subcategory_choice(message=message, state=setup_state, async_session_maker=setup_session, target_user_id=TEST_HANDLERS_USER.id)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_new_subcategory_name
        message.answer.assert_called()
        
        
class Test_askNewExpenseSubcategoryName:
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['subcategory']['new_subcategory_name']['basic']

        await ask_new_expense_subcategory_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_new_subcategory_name
        message.answer.assert_called_with(expected_text)
        
        
class Test_getExpenseSubcategoryCallback:
    
    @pytest.mark.asyncio
    async def test_choice_from_buttons(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='some_category')
        
        await get_expense_subcategory_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_data.get('subcategory') == 'some_category'
        assert new_state == ExpenseStates.waiting_for_money_count
        
    @pytest.mark.asyncio
    async def test_choice_new_subcategory(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='new_category')
        
        await get_expense_subcategory_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_new_subcategory_name
        assert new_data.get('subcategory', None) is None
    
    @pytest.mark.asyncio
    async def test_choice_empty_callback(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data=None)
        
        await get_expense_subcategory_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('subcategory', '') == ''
        
        
class Test_saveNewExpenseSubcategoryName:
    
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext):
        await setup_state.set_state(ExpenseStates.waiting_for_new_subcategory_name)
        message: types.Message = AsyncMock(text=None)
        expected_text = message_expected_texts['subcategory']['new_subcategory_name']['error']

        await save_new_expense_subcategory_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_new_subcategory_name
        assert new_data.get('subcategory', '') == ''
        message.reply.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_normal_save(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='new category name')
        
        await save_new_expense_subcategory_name(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_money_count
        assert new_data.get('subcategory', None) == 'new category name'
        
        
class Test_askExpenseMoneyCount:
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        
        await ask_for_expense_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_money_count
        message.answer.assert_called()
        
        
class Test_getExpenseMoneyCount:
    
    @pytest.mark.asyncio
    async def test_correct_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='600')
        
        await get_expense_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_date_isnow_choice
        assert new_data.get('money_count', None) == 600
        
    @pytest.mark.asyncio
    async def test_no_text(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text=None)
        await setup_state.set_state(ExpenseStates.waiting_for_money_count)
        expected_text = message_expected_texts['money']['ask']['error']

        await get_expense_money_count(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_money_count
        assert new_data.get('money_count', None) is None
        message.reply.assert_called_with(expected_text)
        
        
class Test_askExpenseIsNow:
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_keyboard: types.InlineKeyboardMarkup = make_binary_keyboard(message_expected_texts['date']['ask']['buttons']['yes'], message_expected_texts['date']['ask']['buttons']['no'])
        expected_text = message_expected_texts['date']['ask']['basic']

        await ask_expense_date_is_now(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_date_isnow_choice
        message.answer.assert_called_with(expected_text, reply_markup=expected_keyboard)
        
        
class Test_askExpenseSpecificDate:
    
    @pytest.mark.asyncio
    async def test_ask(self, setup_state: FSMContext):
        message: types.Message = AsyncMock()
        expected_text = message_expected_texts['date']['ask']['specific']

        await ask_expense_specific_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_specific_date
        message.answer.assert_called_with(expected_text)
        

class Test_getExpenseDateIsNowCallback:
    @pytest.mark.asyncio
    async def test_yes(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='yes')
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcategory', 
            'money_count': 2000, 
        })
        
        await get_expense_date_is_now_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_results_confirmation
        assert not new_data.get('expense_date', None) is None
             
    @pytest.mark.asyncio
    async def test_no(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='no')
        
        await get_expense_date_is_now_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_specific_date
        assert new_data.get('expense_date', None) is None
        
    @pytest.mark.asyncio
    async def test_other_callback(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='some_data')
        
        await get_expense_date_is_now_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('expense_date', None) is None
    
    @pytest.mark.asyncio
    async def test_empty_callback(self, setup_state: FSMContext, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data=None)
        
        await get_expense_date_is_now_callback(callback=call, state=setup_state, bot=bot)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data.get('expense_date', None) is None
        
        
class Test_saveExpenseSpecificDate:
    @pytest.mark.asyncio
    async def test_correct_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='20-12-2023 14:50')
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcategory', 
            'money_count': 2000, 
        })
        
        await save_expense_specific_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_results_confirmation
        assert new_data.get('expense_date', None) == '2023-12-20 14:50'
        
    @pytest.mark.asyncio
    async def test_empty_message(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text=None)
        await setup_state.set_state(ExpenseStates.waiting_for_specific_date)
        expected_text = message_expected_texts['date']['ask']['error']

        await save_expense_specific_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_specific_date
        assert new_data.get('expense_date', None) is None
        message.reply.assert_called_with(expected_text)
        
    @pytest.mark.asyncio
    async def test_incorrect_input(self, setup_state: FSMContext):
        message: types.Message = AsyncMock(text='2023-20-12 23:69')
        await setup_state.set_state(ExpenseStates.waiting_for_specific_date)
        expected_text = message_expected_texts['date']['ask']['error']

        await save_expense_specific_date(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state == ExpenseStates.waiting_for_specific_date
        assert new_data.get('expense_date', None) is None
        message.reply.assert_called_with(expected_text)
        
        
class Test_askExpenseConfirmation:
    
    @pytest.mark.asyncio
    async def test_ask_correct_data(self, setup_state: FSMContext):
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcategory', 
            'money_count': 2000, 
            'expense_date': '2023-12-20 14:50'
        })
        message: types.Message = AsyncMock() 
        
        await ask_expense_confirmation(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        
        assert new_state == ExpenseStates.waiting_for_results_confirmation
        message.answer.assert_called()
        
    @pytest.mark.asyncio
    async def test_ask_incorrect_data(self, setup_state: FSMContext):
        message = AsyncMock() 
        await setup_state.set_data({'category': None})
        expected_text = message_expected_texts['confirm']['ask']['error']

        await ask_expense_confirmation(message=message, state=setup_state)
        new_state = await setup_state.get_state()
        new_data = await setup_state.get_data()
        
        assert new_state is None
        assert new_data == {}
        message.answer.assert_called_with(expected_text)
        
        
class Test_getExpenseConfirmationCallback:
    
    @pytest.mark.asyncio
    async def test_yes_correct_data(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='some text')
        call: types.CallbackQuery = AsyncMock(data='yes', from_user=TEST_HANDLERS_USER, **{'message': message})
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcat', 
            'money_count': 100, 
            'expense_date': '2023-12-20 14:59'
        })
        
        await get_expense_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        call.message.answer.assert_called()
        assert new_data == {}
        assert new_state is None
        
    @pytest.mark.asyncio
    async def test_yes_incorrect_data(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='some text')
        call: types.CallbackQuery = AsyncMock(data='yes', from_user=TEST_HANDLERS_USER, **{'message': message})
        await AddUserQuery(user_id=TEST_HANDLERS_USER.id, async_session=setup_session).save_user()
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcat', 
            'money_count': 100, 
            'expense_date': '2023-20-20 14:59'
        })
        
        await get_expense_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        call.message.answer.assert_not_called()
        assert new_data == {}
        assert new_state is None
    
    @pytest.mark.asyncio 
    async def test_yes_no_user(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        message: types.Message = AsyncMock(from_user=TEST_HANDLERS_USER, text='some text')
        call: types.CallbackQuery = AsyncMock(data='yes', from_user=TEST_HANDLERS_USER, **{'message': message})
        await setup_state.set_data({
            'category': 'Category', 
            'subcategory': 'Subcat', 
            'money_count': 100, 
            'expense_date': '2023-12-20 14:59'
        })
        await setup_state.set_state(ExpenseStates.waiting_for_results_confirmation)
        
        await get_expense_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        call.message.answer.assert_called()
        assert new_data == {}
        assert new_state is None 

        
    @pytest.mark.asyncio
    async def test_no(self, setup_state: FSMContext, setup_session: AsyncSession, create_empty_tables_data: None, bot: Bot):
        call: types.CallbackQuery = AsyncMock(data='no', text='text')
        await setup_state.set_data({
            'category': 'some', 
            'subcategory': 'some', 
            'money_count': 500, 
            'expense_date': '2023-12-20 14:50'
            })
        await setup_state.set_state(ExpenseStates.waiting_for_results_confirmation)
        
        await get_expense_confirmation_callback(callback=call, state=setup_state, async_session_maker=setup_session, bot=bot)
        new_data = await setup_state.get_data()
        new_state = await setup_state.get_state()
        
        call.message.answer.assert_not_called()
        assert new_data == {}
        assert new_state is None
