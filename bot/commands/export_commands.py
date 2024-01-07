import datetime

import aiohttp
from aiogram import types, Bot
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['export']


async def export_expenses_message(message: types.Message, db_url: str, db_apikey: str, bot: Bot) -> None:
    async with aiohttp.ClientSession() as session:
        user_expenses_resp = await session.get(f'{db_url}/expenses/export/?user_id={message.from_user.id}&apikey={db_apikey}')
        if user_expenses_resp.status == 200:
            user_expenses = await user_expenses_resp.json()
        else:
            user_expenses = []

    if not len(user_expenses) == 0:
        filename = 'Все расходы_' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M') + '.csv'
        file_to_send = types.input_file.BufferedInputFile(file=str.encode(user_expenses), filename=filename)
        return await bot.send_document(chat_id=message.chat.id, caption=message_texts['expense']['caption'], document=file_to_send)
    else:
        return await message.answer(message_texts['expense']['no_data'])
    

async def export_revenues_message(message: types.Message, db_url: str, db_apikey: str, bot: Bot) -> None:
    async with aiohttp.ClientSession() as session:
        user_revenues_resp = await session.get(f'{db_url}/revenues/export/?user_id={message.from_user.id}&apikey={db_apikey}')
        if user_revenues_resp.status == 200:
            user_revenues = await user_revenues_resp.json()
        else:
            user_revenues = []

    if not len(user_revenues) == 0:
        filename = 'Все доходы_' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M') + '.csv'
        file_to_send = types.input_file.BufferedInputFile(file=str.encode(user_revenues), filename=filename)
        return await bot.send_document(chat_id=message.chat.id, caption=message_texts['revenue']['caption'], document=file_to_send)
    else:
        return await message.answer(message_texts['revenue']['no_data'])