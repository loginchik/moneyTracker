import datetime

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from bot_structures import RevenueStates, make_binary_keyboard
from commands.data_validation import check_date
from .revenue_confirmation import ask_revenue_confirmation
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_revenue']['date']


async def ask_revenue_is_now(message: types.Message, state: FSMContext) -> None:
    await state.set_state(RevenueStates.waiting_for_date_isnow_choice)
    inline_reply_markup = make_binary_keyboard(message_texts['ask']['buttons']['yes'], message_texts['ask']['buttons']['no'])
    await message.answer(message_texts['ask']['basic'], reply_markup=inline_reply_markup)
    
    
async def ask_revenue_specific_date(message: types.Message, state: FSMContext) -> None:
    await state.set_state(RevenueStates.waiting_for_specific_date)
    await message.answer(message_texts['ask']['specific'])
    
    
async def get_revenue_isnow_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.data == 'yes':
        current_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
        await state.update_data(revenue_date=current_date)
        await bot.edit_message_text(text=f"{message_texts['callback']['chosen']} {current_date}", chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        await ask_revenue_confirmation(message=callback.message, state=state)
    elif callback.data == 'no':
        await bot.edit_message_text(text=message_texts['callback']['new'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        await ask_revenue_specific_date(message=callback.message, state=state)
    else:
        pass
  
        
async def save_specific_revenue_date(message: types.Message, state: FSMContext) -> None:
    entered_date = message.text
    validated_date = check_date(entered_date)
    
    if not validated_date == False:
        await state.update_data(revenue_date=validated_date)
        await ask_revenue_confirmation(message=message, state=state)
    else:
        await message.reply(message_texts['ask']['error'])