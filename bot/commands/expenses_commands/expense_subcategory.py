import aiohttp

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_structures import ExpenseStates, make_category_keyboard
from .expense_money_count import ask_for_expense_money_count
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_expense']['subcategory']


async def ask_expense_subcategory_choice(message: types.Message, state: FSMContext, db_url: str, db_apikey: str, target_user_id: int = None) -> None:
    current_data = await state.get_data()
    chosen_category = current_data.get('category', None)
    
    if not chosen_category is None:
        async with aiohttp.ClientSession() as session:
            subcat_response = await session.get(f'{db_url}/expenses/subcategories/?user_id={target_user_id}&category={chosen_category}&apikey={db_apikey}')
            user_subcategories = await subcat_response.json()

        if not len(user_subcategories) == 0:
            user_unique_subcategories = sorted(set(user_subcategories))
            inline_reply_markup = make_category_keyboard(categories_list=user_unique_subcategories)
            await state.set_state(ExpenseStates.waiting_for_subcategory_choice)
            await message.answer(message_texts['select_subcategory']['basic'], reply_markup=inline_reply_markup)
        else:
            await ask_new_expense_subcategory_name(message=message, state=state, from_initial=True)
    else:
        await state.set_state(ExpenseStates.waiting_for_category_choice)


async def ask_new_expense_subcategory_name(message: types.Message, state: FSMContext, from_initial: bool = False) -> None:
    await state.set_state(ExpenseStates.waiting_for_new_subcategory_name)
    message_text = message_texts['new_subcategory_name']['basic']
    if from_initial:
        message_text = message_texts['new_subcategory_name']['initial'] + message_text
    await message.answer(message_text)


async def get_expense_subcategory_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.data == 'new_category':
        await bot.edit_message_text(text=message_texts['callback']['new'], message_id=callback.message.message_id, chat_id=callback.message.chat.id)
        await ask_new_expense_subcategory_name(message=callback.message, state=state)
    elif not callback.data is None:
        subcategory_name = callback.data
        await state.update_data(subcategory=subcategory_name)
        await bot.edit_message_text(text=f"{message_texts['callback']['chosen']} {subcategory_name}", chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await ask_for_expense_money_count(message=callback.message, state=state)
    else:
        pass
     
        
async def save_new_expense_subcategory_name(message: types.Message, state: FSMContext) -> None:
    new_subcategory_name = message.text
    if not new_subcategory_name is None and 0 < len(new_subcategory_name) <= 50:
        await state.update_data(subcategory=new_subcategory_name)
        await ask_for_expense_money_count(message=message, state=state)
    else:
        await message.reply(message_texts['new_subcategory_name']['error'])