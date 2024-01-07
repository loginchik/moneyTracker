import datetime

import aiohttp

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_structures import ExpenseStates, make_binary_keyboard
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['new_expense']['confirm']


async def ask_expense_confirmation(message: types.Message, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.waiting_for_results_confirmation)
    inline_reply_markup = make_binary_keyboard(message_texts['ask']['buttons']['yes'], message_texts['ask']['buttons']['no'])
    key_names = {
        'category': message_texts['ask']['report_keys']['cat'], 
        'subcategory': message_texts['ask']['report_keys']['subcat'], 
        'money_count': message_texts['ask']['report_keys']['mon'], 
        'expense_date': message_texts['ask']['report_keys']['dat']
    }
    
    current_data = await state.get_data()
    try:
        report_lines = [f'{key_names[k]}: {current_data[k]}' for k in key_names.keys()]
        report = '\n'.join(report_lines)
        message_text = message_texts['ask']['basic'] + '\n\n' + report
        await message.answer(text=message_text, reply_markup=inline_reply_markup)
    except KeyError:
        await state.clear()
        await state.set_data({})
        await message.answer(message_texts['ask']['error'])
    
    
async def get_expense_confirmation_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot, db_url: str, db_apikey: str) -> None:
    if callback.data == 'yes':
        new_text = callback.message.text + '\n\n' + message_texts['callback']['yes']['addition']
        await bot.edit_message_text(text=new_text, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        user_entered_data = await state.get_data()

        try:
            category = user_entered_data['category']
            subcategory = user_entered_data['subcategory']
            money_count = user_entered_data['money_count']
            expense_date_str = user_entered_data['expense_date']
        except KeyError:
            await state.set_data({})
            await state.clear()
            return await bot.edit_message_text(text=message_texts['callback']['yes']['error'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        
        async with aiohttp.ClientSession() as session:
            add_response = await session.post(f'{db_url}/expenses/new/?apikey={db_apikey}&user_id={callback.from_user.id}&category={category}&subcategory={subcategory}&money_count={money_count}&e_date={expense_date_str}')
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
        return await bot.edit_message_text(text=message_texts['callback']['no']['success'], chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)

    
    
        