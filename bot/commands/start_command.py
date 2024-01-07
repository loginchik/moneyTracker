from aiogram import types

from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['basic']['start']


async def start_message(message: types.Message) -> types.Message:
    return await message.answer(message_texts['start_message'])