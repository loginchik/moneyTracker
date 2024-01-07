import aiohttp

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_structures import make_category_keyboard, RevenueStates
from .revenue_money_count import ask_revenue_money_count
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_revenue']['type']


async def ask_new_revenue_type_name(message: types.Message, state: FSMContext, from_initial: bool = False) -> None:
    await state.set_state(RevenueStates.waiting_for_new_type_name)
    message_text = message_texts['new_type_name']['basic']
    if from_initial:
        message_text = message_texts['new_type_name']['initial'] + message_text
    await message.answer(message_text)


async def ask_revenue_type(message: types.Message, state: FSMContext, db_url: str, db_apikey: str, target_user_id: int = None) -> None:
    async with aiohttp.ClientSession() as session:
        types_resp = await session.get(f'{db_url}/revenues/types/?user_id={target_user_id}&apikey={db_apikey}')
        if types_resp.status == 200:
            user_types = await types_resp.json()
        else:
            user_types = []

    if not len(user_types) == 0:
        user_unique_types = sorted(set(user_types))
        await state.set_state(RevenueStates.waiting_for_type_choice)
        inline_reply_markup = make_category_keyboard(categories_list=user_unique_types)
        await message.answer(message_texts['select_type']['basic'], reply_markup=inline_reply_markup)
    else:
        await ask_new_revenue_type_name(message=message, state=state, from_initial=True)


async def get_revenue_type_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.data == 'new_category':
        await bot.edit_message_text(text=message_texts['callback']['new'], message_id=callback.message.message_id, chat_id=callback.message.chat.id, reply_markup=None)
        await ask_new_revenue_type_name(message=callback.message, state=state, from_initial=False)
    elif not callback.data is None:
        revenue_type = callback.data
        await state.update_data(revenue_type=revenue_type)
        await bot.edit_message_text(text=f"{message_texts['callback']['chosen']} {revenue_type}", message_id=callback.message.message_id, chat_id=callback.message.chat.id, reply_markup=None)
        await ask_revenue_money_count(message=callback.message, state=state)
    else:
        pass    


async def save_new_revenue_type_name(message: types.Message, state: FSMContext) -> None:
    new_revenue_type = message.text
    if not new_revenue_type is None and 0 < len(new_revenue_type) <= 50:
        await state.update_data(revenue_type=new_revenue_type)
        await ask_revenue_money_count(message=message, state=state)
    else:
        await message.answer(message_texts['new_type_name']['error'])