import aiohttp
from aiogram import types


async def analytics_message(message: types.Message, db_url: str, db_apikey: str):
    async with aiohttp.ClientSession() as session:
        user_data_response = await session.get(f'{db_url}/users/{message.from_user.id}/?apikey={db_apikey}')
        if user_data_response.status == 200:
            user_data = await user_data_response.json()
    
    user_password = user_data['password']

    report_url = f'{db_url}/open/{message.from_user.id}?password={user_password}'
    await message.answer('Отчёт о ваших доходах и расходах здесь: ' + report_url)