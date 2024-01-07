import aiohttp

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from bot_structures import make_category_keyboard
from bot_structures import ExpenseStates
from .expense_subcategory import ask_expense_subcategory_choice
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_expense']['category']


async def ask_new_expense_category_name(message: types.Message, state: FSMContext, from_initial: bool = False):
    await state.set_state(ExpenseStates.waiting_for_new_category_name)
    message_text = message_texts['new_category_name']['basic']
    if from_initial:
        message_text = message_texts['new_category_name']['initial'] + message_text
    await message.answer(message_text)
    

async def select_expense_category(message: types.Message, state: FSMContext, db_url: str, db_apikey: str) -> None:
    async with aiohttp.ClientSession() as session:
        cat_response = await session.get(f'{db_url}/expenses/categories/?user_id={message.from_user.id}&apikey={db_apikey}')
        if cat_response.status == 200:
            user_categories = await cat_response.json()
        else:
            user_categories = []
            
    if not len(user_categories) == 0:
        user_unique_categories = sorted(set(user_categories))
        inline_reply_markup = make_category_keyboard(categories_list=user_unique_categories)
        await state.set_state(ExpenseStates.waiting_for_category_choice)
        await message.answer(message_texts['select_category']['basic'], reply_markup=inline_reply_markup)
    else:
        await ask_new_expense_category_name(message=message, state=state, from_initial=True)

    
async def get_expense_category_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot, db_url: str, db_apikey: str) -> None:
    if callback.data == 'new_category':
        await bot.edit_message_text(text=message_texts['callback']['new'], message_id=callback.message.message_id, chat_id=callback.message.chat.id, reply_markup=None)
        await ask_new_expense_category_name(message=callback.message, state=state)
    elif not callback.data is None:
        chosen_category = callback.data
        await state.update_data(category=chosen_category)
        await bot.edit_message_text(text=f"{message_texts['callback']['chosen']} {chosen_category}", message_id=callback.message.message_id, chat_id=callback.message.chat.id, reply_markup=None)
        await ask_expense_subcategory_choice(message=callback.message, state=state, target_user_id=callback.from_user.id, db_url=db_url, db_apikey=db_apikey)
    else:
        pass


async def save_new_category_name(message: types.Message, state: FSMContext, db_url: str, db_apikey: str) -> None:
    new_category_name = message.text
    
    if not new_category_name is None and 0 < len(new_category_name) <= 50:
        await state.update_data(category=new_category_name)
        await ask_expense_subcategory_choice(message=message, state=state, target_user_id=message.from_user.id, db_url=db_url, db_apikey=db_apikey)
    else:
        await message.answer(message_texts['new_category_name']['error'])
        
           