import aiohttp

from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_structures import DeleteDataStates
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['edit_db']['delete_data']


async def ask_delete_all_confirmaion(message: types.Message, state: FSMContext) -> None:
    await state.set_state(DeleteDataStates.waiting_confirmation)
    await message.answer(f'{message_texts["confirm"]["basic"]} "{message_texts["confirm"]["user_text"]}"')


async def delete_all_data_message(message: types.Message, state: FSMContext, db_url: str, db_apikey: str) -> None:
    if not message.text is None and message.text.lower() == 'я хочу удалить все данные':
        async with aiohttp.ClientSession() as session:
            response = await session.delete(f'{db_url}/users/delete_data/?user_id={message.from_user.id}&apikey={db_apikey}')
        if response.status == 200:
            await message.answer(message_texts['result']['success'])
        else:
            await message.answer(message_texts['result']['error'])
    else:
        await message.answer(message_texts['result']['cancel'])
    
    await state.clear()
    await state.set_data({})