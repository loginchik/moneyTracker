import datetime

import aiohttp

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_structures import RevenueStates, make_binary_keyboard
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_revenue']['confirm']


async def ask_revenue_confirmation(message: types.Message, state: FSMContext) -> None:
    await state.set_state(RevenueStates.waiting_for_results_confirmation)
    inline_keyboard_markup = make_binary_keyboard(message_texts['ask']['buttons']['yes'], message_texts['ask']['buttons']['no'])
    
    key_names = {
        'category': message_texts['ask']['report_keys']['cat'], 
        'revenue_type': message_texts['ask']['report_keys']['typ'], 
        'money_count': message_texts['ask']['report_keys']['mon'], 
        'revenue_date': message_texts['ask']['report_keys']['dat']
    }
    
    current_data = await state.get_data()
    try:
        report_lines = [f'{key_names[k]}: {current_data[k]}' for k in key_names.keys()]
        report = '\n'.join(report_lines)
        message_text = message_texts['ask']['basic'] + '\n\n' + report
        await message.answer(message_text, reply_markup=inline_keyboard_markup)
    except KeyError:
        await state.clear()
        await state.set_data({})
        await message.answer(message_texts['ask']['error'])
        
    
async def get_revenue_confirmation_callback(callback: types.CallbackQuery, state: FSMContext, db_url: str, db_apikey: str, bot: Bot) -> None:
    if callback.data == 'yes':
        await bot.edit_message_text(text=callback.message.text + '\n\n' + message_texts['callback']['yes']['addition'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        user_entered_data = await state.get_data()
        try:
            category = user_entered_data['category']
            type_ = user_entered_data['revenue_type']
            money_count = user_entered_data['money_count']
            r_date = user_entered_data['revenue_date']
        except KeyError:
            await state.set_data({})
            await state.clear()
            return await bot.edit_message_text(text=message_texts['callback']['yes']['error'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)

        async with aiohttp.ClientSession() as session:
            add_response = await session.post(f'{db_url}/revenues/new/?user_id={callback.from_user.id}&category={category}&type_={type_}&money_count={money_count}&r_date={r_date}&apikey={db_apikey}')
            if add_response.status == 201:
                await state.set_data({})
                await state.clear()
                return await callback.message.answer(message_texts['callback']['yes']['success'])
            else:
                await state.set_data({})
                await state.clear()
                return await bot.edit_message_text(text=message_texts['callback']['yes']['error'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
    else:
        await state.set_data({})
        await state.clear()
        return await bot.edit_message_text(message_texts['callback']['no']['success'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)

    