from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_inner_texts import load_message_texts_json

message_texts = load_message_texts_json()


async def abort_message(message: types.Message, state: FSMContext) -> None:
    await state.set_data({})
    await state.clear()
    
    await message.answer(message_texts['edit_db']['abort']['success'])