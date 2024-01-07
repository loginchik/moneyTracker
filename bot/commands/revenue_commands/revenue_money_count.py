from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_structures import RevenueStates
from commands.data_validation import check_money_count
from .revenue_date import ask_revenue_is_now
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_revenue']['money']


async def ask_revenue_money_count(message: types.Message, state: FSMContext) -> None:
    await state.set_state(RevenueStates.waiting_for_money_count)
    await message.answer(message_texts['ask']['basic'])
    
    
async def get_revenue_money_count(message: types.Message, state: FSMContext) -> None:
    entered_money_count = message.text
    checked_money_count = check_money_count(entered_money_count)
    
    if not checked_money_count == False:
        await state.update_data(money_count=checked_money_count)
        await ask_revenue_is_now(message=message, state=state)
    else:
        await message.reply(message_texts['ask']['error'])